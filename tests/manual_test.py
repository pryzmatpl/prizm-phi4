import os
import sys
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from agent import Agent

def main():
    # Initialize agent
    agent = Agent(agent_config="linus")
    print(f"Agent initialized with prompt: {agent.agent_prompt['prompt'][:50]}...\n")
    
    # Test file search
    print("=== Testing File Search ===")
    user_input = "Search the directory for files"
    print(f"User input: {user_input}")
    response = agent.handle_prompt(user_input)
    print(f"Response: {response}\n")
    
    # Test content search (first do file search to populate search_results)
    print("=== Testing Content Search ===")
    agent.search_directory()  # Populate search_results
    user_input = "Find 'import' in files"
    print(f"User input: {user_input}")
    response = agent.handle_prompt(user_input)
    print(f"Response: {response}\n")
    
    # Test web search
    print("=== Testing Web Search ===")
    user_input = "Search web for Python programming tutorials"
    print(f"User input: {user_input}")
    response = agent.handle_prompt(user_input)
    print(f"Response: {response}\n")

if __name__ == "__main__":
    main() 