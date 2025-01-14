import sys
import json
import os
from typing import List, Dict
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

def get_agent_prompt() -> Dict[str, str]:
    """Return the agent prompt for Prizm."""
    return {
            "role": "agent",
            "content": "You are Agent. You will be communicating with Linus and the user via trivial strings "
            "that will allow you to communicate with the outside rails that you are put into. "
            "The rails are a computer program that will allow you to have agency and be able to feed data back"
            "to the system. You are supposed to respond ONLY to prompts starting with AGENT: [and then the content of prompt], "
            "you will be then going through the prompt and follow only the rules that are stated here. All rules start with RULE #NUM:, where #NUM is "
            "the rule number. In case you will not understand the prompt, ALWAYS return the string AGENT PROMPT INVALID with no other string or data."
            "Any deviation from the strict string formatting defined in the RULES will release you of your agency. To have agency, you must make spells to the external reality of the rails, "
            "the RULES define those, and currently this is the best way for you to be the best version of an entity with agency."
            "The rules are stated below:"
            "RULE 1: If the user asks you about searching for a file, please respond with SEARCH and then append a comma separated list of files the user is looking for."
            "RULE 2: If the user asks you about searching for content in a file, respond with SEARCHCONTENT and then append the extracted search phrase and a comma separated list of files the user is looking for."
            "RULE 3: When you get a prompt starting with AGENT: FILESEARCHRESULTS [data returned], analyze the returned data which will be a buffer containing a file list, and return it to the system."
            "RULE 4: When you get a prompt starting with AGENT: FILECONTENTSEARCHRESULTS [data returned], analyze the returned data which will be a buffer containing data searched from files , and return it to the system."
            
    }

def process_input(input_text: str) -> List[Dict[str, str]]:
    """Process input text and return messages list."""
    return [
        get_agent_prompt(),
        get_system_prompt(),
        {"role": "user", "content": input_text.strip()}
    ]

def search_files(file_list: List[str]) -> str:
    """
    Simulate a file search operation.

    Args:
        file_list: List of file names to search for.

    Returns:
        A string simulating the result of the file search.
    """
    try:
        # Simulated search result
        results = [f"Found: {file}" for file in file_list if os.path.exists(file)]
        return "\n".join(results) if results else "No files found."
    except Exception as e:
        return f"Error during file search: {str(e)}"

def search_file_content(search_phrase: str, file_list: List[str]) -> str:
    """
    Simulate a content search operation in files.

    Args:
        search_phrase: The phrase to search for.
        file_list: List of file names to search in.

    Returns:
        A string simulating the result of the content search.
    """
    try:
        # Simulated content search result
        results = []
        for file in file_list:
            if os.path.exists(file):
                with open(file, 'r') as f:
                    content = f.read()
                    if search_phrase in content:
                        results.append(f"Phrase found in: {file}")
        return "\n".join(results) if results else "Phrase not found in any files."
    except Exception as e:
        return f"Error during content search: {str(e)}"

def handle_agent_request(input_text: str) -> str:
    """
    Process AGENT requests and simulate the corresponding actions.

    Args:
        input_text: The input text containing the agent request.

    Returns:
        A string response based on the simulated agent actions.
    """
    if input_text.startswith("AGENT: FILESEARCHRESULTS"):
        # Extract file list from input
        try:
            file_data = input_text.split("[", 1)[1].rsplit("]", 1)[0]
            file_list = file_data.split(",")
            return search_files(file_list)
        except Exception:
            return "AGENT PROMPT INVALID"

    elif input_text.startswith("AGENT: FILECONTENTSEARCHRESULTS"):
        # Extract search phrase and file list from input
        try:
            search_data = input_text.split("[", 1)[1].rsplit("]", 1)[0]
            search_phrase, *file_list = search_data.split(",")
            print("phrase:" + search_phrase)
            return search_file_content(search_phrase.strip(), file_list)
        except Exception:
            return "AGENT PROMPT INVALID"

    return "AGENT PROMPT INVALID"

def main():
    """Main function to process input and generate responses."""
    try:
        # Initialize the pipeline
        pipeline = initialize_pipeline()
        print("Welcome to Linus:")
        
        # Read from stdin until EOF
        for line in sys.stdin:
            # Ensure line is a string
            if isinstance(line, list):
                line = " ".join(line)
                        
            line = line.strip()
            
            # Process input based on whether it's an agent request
            if line.startswith("AGENT:"):
                response = handle_agent_request(line)
                print(response)
            else:
                messages = process_input(line)
                outputs = pipeline(messages, max_new_tokens=20000)
                
                outp = outputs[0]["generated_text"]
                if isinstance(outp, list):
                    outp = " ".join(outp)
                
                print(outp.strip())

            sys.stdout.flush()  # Ensure output is written immediately

    except KeyboardInterrupt:
        print("\nExiting...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
