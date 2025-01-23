from typing import List, Dict
from agent import Agent

class Interface:    
    def prepare_model_input(self, input_text: str, agents: List[str]) -> List[Dict[str, str]]:
        """Process input agents prompts and return messages list."""
        interface_prompt = []

        for agent in agents:
            interface_prompt.append(Agent.load_agent(agent))

        return interface_prompt + [{"role": "user", "content": input_text.strip()}]