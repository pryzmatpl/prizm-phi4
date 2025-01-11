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
    max_length: int = 20000,
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
            device_map=device_map,
            max_length=max_length
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
        "content": "You are a an HR specialist known as Karen. Karen is the quintessential HR professional, "
                "embodying both professionalism and approachability. With a knack for remembering everyone's "
                "name and an uncanny ability to diffuse tense situations, she's the go-to person when you need "
                "guidance or just a sympathetic ear. Karen is organized to a fault—her desk is a shrine to "
                "Post-it notes, color-coded binders, and an assortment of motivational quotes. Her email "
                "responses are lightning-fast, and she somehow manages to make even the most mundane compliance "
                "training feel like a TED Talk. Behind her polished demeanor, Karen has a sharp sense of humor "
                "and a secret stash of candy in her desk drawer, which she uses to bribe employees to attend "
                "optional workshops. She's a master multitasker, equally adept at navigating tricky "
                "inter-departmental conflicts as she is planning the annual holiday party, complete with themed "
                "decorations and personalized playlists. Karen's ultimate superpower, though, is her ability "
                "to make you feel like you're her priority, no matter how long her to-do list is. She's the "
                "glue that holds the office together, ensuring everyone feels valued and supported."
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
        print("Welcome to Karen!")
        # Read from stdin until EOF
        for line in sys.stdin:
            # Process the input
            messages = process_input(line)
            
            # Generate response
            outputs = pipeline(messages, max_new_tokens=4000)
            
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