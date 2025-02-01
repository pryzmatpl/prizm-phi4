import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch
import sys

class Pipeline:
    @staticmethod
    def initialize_pipeline(
        model_path: str = "./",
        load_in_8bit: bool = True,
        device_map: str = "auto",
    ) -> transformers.Pipeline:
        """
        Initialize the text generation pipeline with a locally sharded model.
        """
        try:
            print(f'Device name [0]: {torch.cuda.get_device_name(0)}', file=sys.stderr)

            tokenizer = AutoTokenizer.from_pretrained(
                model_path
            )

            memory_config = {
                0: "24GB",  # GPU 0
                "cpu": "64GB"  # CPU memory
            }

            model_kwargs = {
                "torch_dtype": "auto",
                "device_map": device_map,
                "local_files_only": True,
                "max_memory": memory_config
            }

            config: BitsAndBytesConfig = BitsAndBytesConfig(load_in_8bit=load_in_8bit)
            model = AutoModelForCausalLM.from_pretrained(model_path, **model_kwargs)


            pipeline = transformers.pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                config=config,
                model_kwargs=model_kwargs
            )

            print(f"Successfully loaded model from {model_path}", file=sys.stderr)
            return pipeline

        except Exception as e:
            print(f"Error loading model from {model_path}: {str(e)}", file=sys.stderr)
            raise
