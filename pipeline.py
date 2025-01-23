import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import sys

class Pipeline:
    def initialize_pipeline(
        self,
        model_path: str = "./",  # Path to your local model directory
        load_in_8bit: bool = False,
        device_map: str = "auto",
    ) -> transformers.Pipeline:
        """
        Initialize the text generation pipeline with a locally sharded model.
        
        Args:
            model_path: Path to the directory containing model shards
            load_in_8bit: Whether to load the model in 8-bit precision
            device_map: Device mapping strategy ("auto", "balanced", etc.)
        """
        print(f'device name [0]: {torch.cuda.get_device_name(0)}', file=sys.stderr)
        
        try:
            # Load tokenizer from local path
            tokenizer = AutoTokenizer.from_pretrained(
                model_path,
                trust_remote_code=True,
                local_files_only=True
            )
            
            # Configure model loading parameters
            model_kwargs = {
                "torch_dtype": "auto",
                "device_map": device_map,
                "trust_remote_code": True,
                "local_files_only": True,
            }
            
            if load_in_8bit:
                model_kwargs["load_in_8bit"] = True
            
            # Load the model from local shards
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                **model_kwargs
            )
            
            # Create the pipeline with the loaded model and tokenizer
            pipeline = transformers.pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                device_map=device_map
            )
            
            print(f"Successfully loaded model from {model_path}", file=sys.stderr)
            return pipeline
            
        except Exception as e:
            print(f"Error loading model from {model_path}: {str(e)}", file=sys.stderr)
            raise