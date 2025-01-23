import json
from typing import Dict
from agent_tools import AgentTools

class Agent:
    def __init__(self) -> None:
        self._agent_tools = AgentTools
        
    
    @staticmethod
    def load_agent(agent_file: str) -> Dict[str, str]:
        """Load system prompt from agents/[filename].json."""
        with open(f"agents/{agent_file}.json", 'r') as file:
            return json.load(file)


    def handle_agent_request(self, input_text: str) -> str:
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
                return self._agent_tools.search_files(file_list)
            except Exception:
                return "AGENT PROMPT INVALID"

        elif input_text.startswith("AGENT: FILECONTENTSEARCHRESULTS"):
            # Extract search phrase and file list from input
            try:
                search_data = input_text.split("[", 1)[1].rsplit("]", 1)[0]
                search_phrase, *file_list = search_data.split(",")
                print("phrase:" + search_phrase)
                return self._agent_tools.search_file_content(search_phrase.strip(), file_list)
            except Exception:
                return "AGENT PROMPT INVALID"

        return "AGENT PROMPT INVALID"