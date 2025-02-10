import json
import logging
import os
from typing import Dict, List
from agent_tools import AgentTools


class Agent:
    def __init__(self, agent_name: str) -> None:
        """
        Initialize the agent with a name and a reference to other agents.
        """
        self.agent_name = agent_name
        self._agent_tools = AgentTools
        self.other_agents = {}

    @staticmethod
    def initialize_agents(agents_list: List[str]) -> List[Dict]:
        """Initialize and cross-register agents."""
        agents = [{"name": agent, "agent": Agent(agent)} for agent in agents_list]

        # Register other agents with each agent
        for i, agent_dict in enumerate(agents):
            other_agents = agents[:i] + agents[i+1:]
            for other_agent in other_agents:
                agent_dict["agent"].register_agent(
                    other_agent["name"],
                    other_agent["agent"]
                )

        return agents

    def register_agent(self, other_agent_name: str, other_agent: "Agent") -> None:
        """
        Register another agent to enable inter-agent communication.

        Args:
            other_agent_name: The name of the other agent.
            other_agent: The other agent instance.
        """
        self.other_agents[other_agent_name] = other_agent

    @staticmethod
    def load_agent_config_file(agent_file: str) -> Dict[str, str]:
        """
        Load system prompt from agents/[filename].json.
        """
        try:
            file_path = os.path.normpath(f'agents/{agent_file}.json')
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise ValueError(f'Error loading agent file {agent_file}: {str(e)}')

    def handle_agent_request(self, input_text: str) -> str:
        """
        Process AGENT requests and simulate the corresponding actions.
        """
        logging.debug(f"Text input for agent: {input_text}")
        print("Agent working...")

        try:
            if "You are Agent" in input_text:
                # Prevent Karen from echoing system rules
                return "I’m here to help! What do you need?"

            if input_text.startswith("AGENT: FILESEARCHRESULTS"):
                # Extract file names
                try:
                    file_data = input_text.split("[", 1)[1].rsplit("]", 1)[0]
                    file_list = file_data.split(",")
                    return self._agent_tools.search_files(file_list)
                except Exception as e:
                    return f"Error processing FILESEARCHRESULTS: {str(e)}"

            elif input_text.startswith("AGENT: FILECONTENTSEARCHRESULTS"):
                # Extract search phrase and file names
                try:
                    search_data = input_text.split("[", 1)[1].rsplit("]", 1)[0]
                    search_phrase, *file_list = search_data.split(",")
                    return self._agent_tools.search_file_content(search_phrase.strip(), file_list)
                except Exception as e:
                    return f"Error processing FILECONTENTSEARCHRESULTS: {str(e)}"

            elif input_text.startswith("AGENT: TALKTO"):
                # Extract target agent and message
                try:
                    target_agent_name, message = input_text.split("[", 1)[1].rsplit("]", 1)[0].split(",", 1)
                    target_agent_name = target_agent_name.strip()
                    message = message.strip()

                    if target_agent_name in self.other_agents:
                        target_agent = self.other_agents[target_agent_name]
                        return target_agent.handle_agent_request(message)
                    else:
                        return f"Error: Agent {target_agent_name} not found."
                except Exception as e:
                    return f"Error processing TALKTO request: {str(e)}"

            elif input_text.startswith("AGENT: WEBSEARCH"):
                # Extract search query
                try:
                    query = input_text.split("[", 1)[1].rsplit("]", 1)[0].strip()
                    return self._agent_tools.search_web(query)
                except Exception as e:
                    return f"Error processing WEBSEARCH request: {str(e)}"

        except Exception as e:
            logging.error(f"Exception in agent request handling: {str(e)}")
            return f"AGENT PROMPT INVALID EXCEPTION: {str(e)}"

        return "AGENT PROMPT INVALID FOR OTHER REASONS"

