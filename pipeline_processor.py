from typing import Dict, List, Optional, Union
import torch
from transformers import Pipeline as TransformersPipeline
import json
import os

class PipelineProcessor:
    def __init__(
            self,
            pipeline: TransformersPipeline,
            max_length: int = 2048,
            temperature: float = 0.7,
            top_p: float = 0.9,
            top_k: int = 50
    ):
        """
        Initialize the pipeline processor with a transformers pipeline and generation parameters.

        Args:
            pipeline: Initialized transformers pipeline
            max_length: Maximum length of generated text
            temperature: Sampling temperature for generation
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
        """
        self.pipeline = pipeline
        self.max_length = max_length
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.conversation_history: List[Dict[str, str]] = []

    def _format_prompt(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Format the prompt with optional system prompt and conversation history.
        """
        formatted_prompt = ""
        if system_prompt:
            formatted_prompt += f"{system_prompt}\n\n"

        for message in self.conversation_history[-5:]:  # Keep last 5 messages for context
            role = message["role"]
            content = message["content"]
            formatted_prompt += f"{role}: {content}\n"

        formatted_prompt += f"User: {prompt}\nAssistant:"
        return formatted_prompt

    def _generate_response(self, prompt: str) -> str:
        """
        Generate response using the pipeline.
        """
        try:
            generation_config = {
                "max_length": self.max_length,
                "temperature": self.temperature,
                "top_p": self.top_p,
                "top_k": self.top_k,
                "pad_token_id": self.pipeline.tokenizer.eos_token_id,
                "do_sample": True
            }

            outputs = self.pipeline(
                prompt,
                return_full_text=False,
                **generation_config
            )

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
            input_text: str,
            agent: 'Agent',
            system_prompt: Optional[str] = None
    ) -> str:
        """
        Process input through the pipeline and agent.

        Args:
            input_text: User input text
            agent: Agent instance to handle requests
            system_prompt: Optional system prompt to prepend

        Returns:
            Generated response or agent action result
        """
        try:
            # Format input with conversation history
            formatted_input = self._format_prompt(input_text, system_prompt)

            # Generate initial response
            response = self._generate_response(formatted_input)

            # Update conversation history
            self.update_conversation("user", input_text)
            self.update_conversation("assistant", response)

            # Check if response contains agent action
            if response.startswith("AGENT:"):
                agent_result = agent.handle_agent_request(response, self)
                self.update_conversation("agent", agent_result)
                return agent_result

            return response

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