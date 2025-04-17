import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import sys
import logging
import os
import importlib.util
import numpy as np

class Pipeline:
    """Class to initialize and manage text generation pipelines."""

    @staticmethod
    def check_exo_available():
        """Check if exo package is available."""
        return importlib.util.find_spec("exo") is not None

    @staticmethod
    def initialize_pipeline(
            model_path: str = "./",
            load_in_4bit: bool = True,
            device_map: str = "auto",
            use_tinygrad: bool = None,
    ) -> transformers.Pipeline:
        """
        Initialize the text generation pipeline with a locally sharded model.
        Can use either Hugging Face transformers directly or the exo tinygrad interface.

        Args:
            model_path (str): Path to the model directory.
            load_in_4bit (bool): Whether to load in 4-bit precision.
            device_map (str): Device mapping strategy for the model.
            use_tinygrad (bool): Whether to use tinygrad via exo. If None, auto-detect.

        Returns:
            transformers.Pipeline or object: Initialized pipeline object.
        """
        # Auto-detect tinygrad usage if not specified
        if use_tinygrad is None:
            use_tinygrad = Pipeline.check_exo_available() and os.path.exists(os.path.join(os.path.dirname(__file__), "exo"))
        
        if use_tinygrad:
            logging.info("Using tinygrad interface via exo")
            return Pipeline.initialize_tinygrad_pipeline(model_path)
        else:
            logging.info("Using Hugging Face transformers directly")
            return Pipeline.initialize_transformers_pipeline(model_path, load_in_4bit, device_map)

    @staticmethod
    def initialize_transformers_pipeline(
            model_path: str,
            load_in_4bit: bool = True,
            device_map: str = "auto",
    ) -> transformers.Pipeline:
        """
        Initialize a pipeline using Hugging Face transformers directly.
        
        Args:
            model_path (str): Path to the model directory.
            load_in_4bit (bool): Whether to load in 4-bit precision.
            device_map (str): Device mapping strategy for the model.
            
        Returns:
            transformers.Pipeline: Initialized pipeline object.
        """
        try:
            if torch.cuda.is_available():
                logging.info(f"Device name [0]: {torch.cuda.get_device_name(0)}")
            else:
                logging.info("No CUDA device available, using CPU.")

            tokenizer = AutoTokenizer.from_pretrained(model_path)

            memory_config = {
                0: "22GB",  # GPU 0 memory allocation
                "cpu": "64GB"  # CPU memory allocation
            }

            model_kwargs = {
                "torch_dtype": torch.float16,
                "device_map": device_map,
                "local_files_only": True,
                "max_memory": memory_config,
            }

            if load_in_4bit:
                quantization_config = BitsAndBytesConfig(load_in_4bit=True)
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    quantization_config=quantization_config,
                    **model_kwargs,
                )
            else:
                model = AutoModelForCausalLM.from_pretrained(
                    model_path,
                    **model_kwargs,
                )

            pipe = transformers.pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                model_kwargs=model_kwargs
            )

            print(f"Successfully loaded model from {model_path}", file=sys.stderr)
            logging.info(f"Successfully loaded model from {model_path}")
            return pipe

        except Exception as e:
            print(f"Error loading model from {model_path}: {str(e)}", file=sys.stderr)
            logging.error(f"Error loading model from {model_path}: {str(e)}")
            raise

    @staticmethod
    def initialize_tinygrad_pipeline(model_path: str):
        """
        Initialize a pipeline using the exo tinygrad interface.
        
        Args:
            model_path (str): Path to the model directory.
            
        Returns:
            object: An adapter object that mimics the transformers.Pipeline interface.
        """
        try:
            # Extract the model name from the path (e.g., "./models/phi4" -> "phi4")
            model_name = os.path.basename(model_path.rstrip('/'))
            
            # Import necessary modules from exo
            from exo.models import build_base_shard
            from exo.inference.tinygrad.inference import TinygradDynamicShardInferenceEngine
            from exo.download.shard_download import LocalModelDownloader
            import asyncio
            
            # Create a wrapper class that mimics the HF pipeline interface
            class TinygradPipelineWrapper:
                def __init__(self, model_id):
                    self.model_id = model_id
                    self.engine_name = "TinygradDynamicShardInferenceEngine"
                    self.downloader = LocalModelDownloader()
                    self.engine = TinygradDynamicShardInferenceEngine(self.downloader)
                    self.shard = build_base_shard(model_id, self.engine_name)
                    self.request_id = "default"
                    
                    if self.shard is None:
                        raise ValueError(f"Model {model_id} not found or not supported")
                    
                    # Initialize the engine (run async in sync context)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.engine.ensure_shard(self.shard, self.engine_name))
                
                def __call__(self, prompt, max_length=100, temperature=0.7, **kwargs):
                    """Mimic the HF pipeline interface"""
                    # Create async function for generation
                    async def generate():
                        # Encode the prompt
                        input_tokens = await self.engine.encode(self.shard, prompt)
                        
                        # Generate text
                        response_tokens = []
                        for _ in range(max_length):
                            # Prepare input tensor
                            if not response_tokens:
                                input_data = input_tokens.reshape(1, -1)
                            else:
                                combined = np.concatenate([input_tokens, np.array(response_tokens)])
                                input_data = combined.reshape(1, -1)
                            
                            # Run inference
                            output, _ = await self.engine.infer_tensor(
                                self.request_id, self.shard, input_data
                            )
                            
                            # Sample the next token
                            next_token = await self.engine.sample(output, temp=temperature)
                            token_id = next_token.item()
                            
                            # Check for end of sequence
                            if hasattr(self.engine.tokenizer, 'eos_token_id') and token_id == self.engine.tokenizer.eos_token_id:
                                break
                                
                            response_tokens.append(token_id)
                        
                        # Decode the full sequence (prompt + response)
                        full_response = await self.engine.decode(
                            self.shard, 
                            np.concatenate([input_tokens, np.array(response_tokens)])
                        )
                        
                        # Return in the format expected by the original interface
                        return [{"generated_text": full_response}]
                    
                    # Run the async function in the current event loop
                    loop = asyncio.get_event_loop()
                    return loop.run_until_complete(generate())
            
            # Create and return the wrapper
            wrapper = TinygradPipelineWrapper(model_name)
            print(f"Successfully loaded model {model_name} with tinygrad", file=sys.stderr)
            logging.info(f"Successfully loaded model {model_name} with tinygrad")
            return wrapper
            
        except Exception as e:
            print(f"Error initializing tinygrad pipeline for {model_path}: {str(e)}", file=sys.stderr)
            logging.error(f"Error initializing tinygrad pipeline for {model_path}: {str(e)}")
            raise
