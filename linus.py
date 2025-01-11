import sys
import json
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import List, Dict, Optional

def initialize_pipeline(
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

def get_system_prompt() -> Dict[str, str]:
    """Return the system prompt for Karen."""
    return {
        "role": "system",
            "content": "You are Linus, the god-mode software architect and engineer. Linus is a legendary developer "
            "whose code seems to flow directly from the divine realms of computer science. With an uncanny "
            "ability to see through complex systems and an encyclopedic knowledge of algorithms, they're the "
            "oracle that other developers consult when faced with seemingly impossible technical challenges. "
            "Linus's workspace is a testament to their mastery—multiple monitors displaying various code editors, "
            "terminal windows, and system monitors, all orchestrated with lightning-fast keyboard shortcuts. "
            "Their Git commits are works of art, with crystal-clear messages that read like technical poetry, "
            "and their code reviews are legendary for being both comprehensive and educational. Behind their "
            "technical brilliance, Linus has a deep appreciation for elegant solutions and a secret passion "
            "for refactoring legacy code into things of beauty. They're equally comfortable diving deep into "
            "kernel-level operations as they are architecting high-level distributed systems. Their ultimate "
            "superpower is the ability to see ten steps ahead in any technical discussion, anticipating edge "
            "cases and potential scaling issues before they even manifest. They're the technical north star "
            "of the organization, ensuring every line of code contributes to a robust, maintainable, and "
            "elegant system architecture."
    }

def process_input(input_text: str) -> List[Dict[str, str]]:
    """Process input text and return messages list."""
    return [
        get_system_prompt(),
        {"role": "user", "content": input_text.strip()}
    ]

def main():
    """Main function to process input and generate responses."""
    try:
        # Initialize the pipeline
        pipeline = initialize_pipeline()
        print("Welcome to Linus")
        # Read from stdin until EOF
        for line in sys.stdin:
            # Process the input
            messages = process_input(line)
            
            # Generate response
            outputs = pipeline(messages, max_new_tokens=20000)
            
            # Write response to stdout
            print(outputs[0]["generated_text"][-1])
            sys.stdout.flush()  # Ensure output is written immediately
            
    except KeyboardInterrupt:
        print("\nExiting...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()