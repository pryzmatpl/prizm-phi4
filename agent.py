import json
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

    def register_agent(self, other_agent_name: str, other_agent: "Agent") -> None:
        """
        Register another agent to enable inter-agent communication.

        Args:
            other_agent_name: The name of the other agent.
            other_agent: The other agent instance.
        """
        self.other_agents[other_agent_name] = other_agent

    @staticmethod
    def load_agent(agent_file: Dict) -> Dict[str, str]:
        """
        Load system prompt from agents/[filename].json.
        """
        try:
            file_path = os.path.normpath(f'agents/{agent_file["name"]}.json')
            with open(file_path, "r", encoding="utf-8") as file:
                return json.load(file)
        except Exception as e:
            raise ValueError(f'Error loading agent file {agent_file["name"]}: {str(e)}')

    def handle_agent_request(self, input_text: str) -> str:
        """
        Process AGENT requests and simulate the corresponding actions.
        """
        try:
            if input_text.startswith("AGENT: FILESEARCHRESULTS"):
                file_data = input_text.split("[", 1)[1].rsplit("]", 1)[0]
                file_list = file_data.split(",")
                return self._agent_tools.search_files(file_list)

            elif input_text.startswith("AGENT: FILECONTENTSEARCHRESULTS"):
                search_data = input_text.split("[", 1)[1].rsplit("]", 1)[0]
                search_phrase, *file_list = search_data.split(",")
                return self._agent_tools.search_file_content(search_phrase.strip(), file_list)

            elif input_text.startswith("AGENT: TALKTO"):
                # Parse the target agent and message
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

        except Exception as e:
            return f"AGENT PROMPT INVALID: {str(e)}"
        return "AGENT PROMPT INVALID"