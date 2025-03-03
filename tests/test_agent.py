import os, sys

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from agent import Agent

# Example usage
if __name__ == "__main__":
    # Assuming agents/expert.json exists with {"prompt": "I'm an expert agent...", "capabilities": [...]}
    agent = Agent(agent_config="linus")

    # Test cases
    prompts = [
        "Can you search the directory?",
        "Find python in files",
        "Search web for python courses",
        "Hello, how are you?"
    ]

    for prompt in prompts:
        print(f"\nUser prompt: {prompt}")
        print(agent.handle_prompt(prompt))