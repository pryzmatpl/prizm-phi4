import logging
import sys
from typing import List, Dict, Optional
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from agent import Agent
from interface.pipeline_processor import PipelineProcessor

class Interface:
    @staticmethod
    def prepare_model_input(input_text: str, agents: Dict[str, Agent]) -> Dict[str, str]:
        """
        Prepare input for the model by combining agent prompt with user input.

        Args:
            input_text (str): The user's input
            agents (Dict[str, Agent]): Dictionary of initialized agents

        Returns:
            Dict[str, str]: A message dictionary with role and content
        """
        try:
            # Assuming the supervisor is the first agent in the dict for simplicity
            supervisor = agents.get("supervisor", list(agents.values())[0])  # Prefer explicit supervisor
            agent_prompt = supervisor.agent_prompt["prompt"]
            full_input = f"{agent_prompt}\nUser: {input_text.strip()}"
            return {"role": "user", "content": full_input}
        except Exception as e:
            logging.error(f"Error preparing model input: {str(e)}")
            return {"role": "user", "content": input_text.strip()}  # Fallback

    @staticmethod
    def get_user_input() -> str:
        """
        Get input from the user via stdin.

        Returns:
            str: The user's input
        """
        try:
            user_input = input(">>> ").strip()
            return user_input
        except EOFError:
            return "exit"
        except Exception as e:
            logging.error(f"Error getting user input: {str(e)}")
            return ""

    @staticmethod
    def display_response(response: str) -> None:
        """
        Display the response to the user.

        Args:
            response (str): The response to display
        """
        try:
            print(response.strip())
            sys.stdout.flush()
        except Exception as e:
            logging.error(f"Error displaying response: {str(e)}")
            print(f"Error: {str(e)}")

    @staticmethod
    def process_agent_collaboration(
            processor: PipelineProcessor,
            supervisor: Agent,
            agents: Dict[str, Agent],
            initial_response: str
    ) -> Optional[str]:
        """
        Process any collaboration commands in the supervisor's response.

        Args:
            processor (PipelineProcessor): The pipeline processor instance
            supervisor (Agent): The supervisor agent
            agents (Dict[str, Agent]): All initialized agents
            initial_response (str): The initial response from handle_prompt

        Returns:
            Optional[str]: Final response after collaboration, or None if no collaboration
        """
        responses = []
        for line in initial_response.split('\n'):  # No change here, kept for context
                logging.debug(f"Supervisor delegated to {target_agent_name}: {agent_command}")
                target_agent = agents.get(target_agent_name)
                if target_agent:
                    # Simulate agent processing (could use processor if needed)
                    agent_response = target_agent.handle_prompt(agent_command)
                    if agent_response:
                        responses.append(f"{target_agent_name}: {agent_response.strip()}")
            else:
                responses.append(line)

        if responses and len(responses) > 1:  # Only if collaboration occurred
            combined_response = "\n".join(responses)
            return Interface.prepare_model_input(combined_response, agents)["content"]
        return initial_response
