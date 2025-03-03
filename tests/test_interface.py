import logging

from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from interface import PipelineProcessor, Interface
from agent import Agent

# Example usage (for testing)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Mock agents and processor for testing
    agents = {"supervisor": Agent(agent_config="supervisor")}
    processor = PipelineProcessor(pipeline=None)  # Assuming this works with None for testing

    # Test the interface
    while True:
        user_input = Interface.get_user_input()
        if user_input.lower() in ["exit", "quit"]:
            break
        response = agents["supervisor"].handle_prompt(user_input)
        final_response = Interface.process_agent_collaboration(
            processor, agents["supervisor"], agents, response
        )
        Interface.display_response(final_response or response)