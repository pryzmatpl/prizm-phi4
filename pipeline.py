import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import sys
import logging

class Pipeline:
    """Class to initialize and manage a transformers text-generation pipeline."""

    @staticmethod
    def initialize_pipeline(
            model_path: str = "./",
            load_in_4bit: bool = True,
            device_map: str = "auto",
    ) -> transformers.Pipeline:
        """
        Initialize the text generation pipeline with a locally sharded model.

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
