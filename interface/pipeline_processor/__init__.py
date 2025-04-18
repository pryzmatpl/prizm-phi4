import logging
from typing import Dict, List, Union
import sys
import torch
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from transformers import Pipeline as TransformersPipeline
from agent import Agent
from interface.pipeline_processor.memory_manager import MemoryManager

class PipelineProcessor:
    def __init__(
            self,
            pipeline: TransformersPipeline,
            temperature: float = 0.7,
            top_p: float = 0.9,
            top_k: int = 50
    ):
        """
        Initialize the pipeline processor with a transformers pipeline and generation parameters.

        Args:
            pipeline: Initialized transformers pipeline
            temperature: Sampling temperature for generation
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
        """
        self.pipeline = pipeline
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.conversation_history: List[Dict[str, str]] = []
        self.memory_manager = MemoryManager()

    def _format_prompt(self, _input: List[Dict[str,str]]) -> str:
        """
        Format the prompt with optional system prompt and conversation history.
        """
        formatted_prompt = ""

        for message in _input:
            role = message["role"]
            content = message["content"]
            formatted_prompt += f"{role}: {content}\n"

        # Context expansion here
        # for message in self.conversation_history[-3:]:  # Keep last 3 messages for context
        #     role = message["role"]
        #     content = message["content"]
        #     formatted_prompt += f"{role}: {content}\n"


        return formatted_prompt

    def _generate_response(self, prompt: str) -> str:
        """
        Generate response using the pipeline.
        """
        try:
            generation_config = {
                "max_new_tokens": 4096,  # Limit output size
                "truncation": True,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "pad_token_id": self.pipeline.tokenizer.eos_token_id,
                "do_sample": True
            }

            outputs = self.pipeline(
                prompt,
                **generation_config
            )

            logging.debug(f"++++++\n\nRaw outputs: \n\n {outputs} \n\n")

            return outputs[0]["generated_text"].strip()

        except Exception as e:
            return f"Error in generation: {str(e)}"

    def process_agent_action(self, agent_response: str) -> Dict[str, Union[str, List[str]]]:
        """
        Process agent actions and prepare appropriate responses.

        Args:
            agent_response: Response string from the agent

        Returns:
            Dictionary containing action type and parameters
        """
        if agent_response.startswith("SEARCH"):
            files = agent_response[7:].strip().split(",")
            return {
                "action": "search",
                "files": [f.strip() for f in files]
            }
        elif agent_response.startswith("SEARCHCONTENT"):
            content = agent_response[13:].strip()
            search_phrase, *files = content.split(",")
            return {
                "action": "search_content",
                "search_phrase": search_phrase.strip(),
                "files": [f.strip() for f in files]
            }
        else:
            return {
                "action": "invalid",
                "message": "Unknown agent action"
            }

    def update_conversation(self, role: str, content: str) -> None:
        """
        Update the conversation history.
        """
        self.conversation_history.append({
            "role": role,
            "content": content
        })

    def process(
            self,
            _input: List[Dict[str,str]],
            supervisor_agent: Agent
    ) -> str:
        """
        Process input through the pipeline and agent.

        Args:
            _input: User input + system prompt dict
            supervisor_agent: Main agent (ie Karen or Linus)
        Returns:
            Generated response or agent action result
        """
        try:
            self.memory_manager.clear_memory()

            formatted_input = self._format_prompt(_input)
            response = self._generate_response(formatted_input)
            self.update_conversation("agent", response)

            if response.startswith("AGENT:"):
                agent_result = supervisor_agent.handle_agent_request(response)
                logging.debug(f"Agent response: {response}")
                self.update_conversation(supervisor_agent.agent_name, agent_result)
                return agent_result

            return response

        except RuntimeError as e:
            if "out of memory" in str(e):
                self.memory_manager.clear_memory()
                # Could retry with smaller context/generation limits
                return "Memory error occurred. Try with shorter input."
        except Exception as e:
            error_msg = f"Pipeline processing error: {str(e)}"
            self.update_conversation("system", error_msg)
            return error_msg

    def reset_conversation(self) -> None:
        """
        Reset the conversation history.
        """
        self.conversation_history = []

    @property
    def device(self) -> torch.device:
        """
        Get the current device of the pipeline.
        """
        return self.pipeline.device