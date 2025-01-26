import sys
from typing import List, Dict
from agent import Agent

class Interface:
    @staticmethod
    def prepare_model_input(input_text: str, agents: List[str]) -> List[Dict[str, str]]:
        """
        Process input agents prompts and return messages list.
        """
        interface_prompt = []
        for agent in agents:
            try:
                interface_prompt.append(Agent.load_agent(agent))
            except ValueError as e:
                print(str(e), file=sys.stderr)
                continue
        interface_prompt.append({"role": "user", "content": input_text.strip()})
        return interface_prompt