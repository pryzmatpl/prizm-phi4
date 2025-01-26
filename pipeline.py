import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import sys

class Pipeline:
    @staticmethod
    def initialize_pipeline(
        model_path: str = "./",
        load_in_8bit: bool = False,
        device_map: str = "auto",
    ) -> transformers.Pipeline:
        """
        Initialize the text generation pipeline with a locally sharded model.
        """
        try:
            print(f'Device name [0]: {torch.cuda.get_device_name(0)}', file=sys.stderr)

            tokenizer = AutoTokenizer.from_pretrained(
                model_path, trust_remote_code=True, local_files_only=True
            )

            model_kwargs = {
                "torch_dtype": "auto",
                "device_map": device_map,
                "trust_remote_code": True,
                "local_files_only": True,
            }
            if load_in_8bit:
                model_kwargs["load_in_8bit"] = True

            model = AutoModelForCausalLM.from_pretrained(model_path, **model_kwargs)

            pipeline = transformers.pipeline(
                "text-generation", model=model, tokenizer=tokenizer, device_map=device_map
            )

            print(f"Successfully loaded model from {model_path}", file=sys.stderr)
            return pipeline

        except Exception as e:
            print(f"Error loading model from {model_path}: {str(e)}", file=sys.stderr)
            raise
