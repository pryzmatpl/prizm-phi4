import logging
from typing import Any, List, Dict, Optional, Union
import sys
import torch
from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '..')))
from transformers import Pipeline as TransformersPipeline
from agent import Agent
from interface.pipeline_processor.memory_manager import MemoryManager
import inspect

class PipelineProcessor:
    """
    A processor for text generation pipelines, supporting both HuggingFace Transformers
    and tinygrad-based pipelines.
    """
    
    def __init__(
        self,
        pipeline: Any,
        temperature: float = 0.7,
        top_p: float = 0.9,
        top_k: int = 50,
        max_new_tokens: int = 1024,
        stop_sequences: Optional[List[str]] = None
    ):
        """
        Initialize the pipeline processor.
        
        Args:
            pipeline: Either a HuggingFace transformers pipeline or a tinygrad pipeline
            temperature: Sampling temperature (higher = more random)
            top_p: Top-p sampling parameter (nucleus sampling)
            top_k: Top-k sampling parameter
            max_new_tokens: Maximum number of new tokens to generate
            stop_sequences: List of sequences that will stop generation when generated
        """
        self.pipeline = pipeline
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.max_new_tokens = max_new_tokens
        self.stop_sequences = stop_sequences or []
        
        # Detect if this is a HuggingFace pipeline or a tinygrad pipeline
        if hasattr(pipeline, 'model') and hasattr(pipeline, 'tokenizer'):
            self.pipeline_type = "huggingface"
        else:
            self.pipeline_type = "tinygrad"
        
        logging.info(f"Initialized PipelineProcessor with {self.pipeline_type} pipeline")
        
        self.conversation_history: List[Dict[str, str]] = []
        self.memory_manager = MemoryManager()

    def _is_huggingface(self) -> bool:
        """Check if we're using a HuggingFace pipeline."""
        return self.pipeline_type == "huggingface"
    
    def generate(
        self,
        prompt: str,
        max_new_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        **kwargs
    ) -> str:
        """
        Generate text using the pipeline.
        
        Args:
            prompt: The input prompt
            max_new_tokens: Maximum number of new tokens to generate (overrides instance default)
            temperature: Sampling temperature (overrides instance default)
            top_p: Top-p sampling parameter (overrides instance default)
            top_k: Top-k sampling parameter (overrides instance default)
            stop_sequences: List of sequences that will stop generation when generated (overrides instance default)
            **kwargs: Additional keyword arguments to pass to the pipeline
            
        Returns:
            The generated text
        """
        temp = temperature if temperature is not None else self.temperature
        p = top_p if top_p is not None else self.top_p
        k = top_k if top_k is not None else self.top_k
        max_tokens = max_new_tokens if max_new_tokens is not None else self.max_new_tokens
        stop = stop_sequences if stop_sequences is not None else self.stop_sequences
        
        if self._is_huggingface():
            # Use HuggingFace pipeline
            response = self.pipeline(
                prompt,
                do_sample=True,
                temperature=temp,
                top_p=p,
                top_k=k,
                max_new_tokens=max_tokens,
                pad_token_id=self.pipeline.tokenizer.eos_token_id,
                **kwargs
            )
            
            # Extract and process the generated text
            generated_text = response[0]["generated_text"]
            
            # Apply stop sequences
            if stop:
                for sequence in stop:
                    if sequence in generated_text:
                        generated_text = generated_text[:generated_text.find(sequence)]
            
            return generated_text
        else:
            # Use tinygrad pipeline
            response_params = {
                "temperature": temp,
                "max_length": max_tokens,
                **kwargs
            }
            
            # Add top_p and top_k if the pipeline supports them
            pipeline_sig = inspect.signature(self.pipeline.__call__)
            if "top_p" in pipeline_sig.parameters:
                response_params["top_p"] = p
            if "top_k" in pipeline_sig.parameters:
                response_params["top_k"] = k
                
            response = self.pipeline(prompt, **response_params)
            
            # Extract and process the generated text
            if isinstance(response, list) and len(response) > 0 and "generated_text" in response[0]:
                generated_text = response[0]["generated_text"]
            else:
                # Handle custom pipeline response format
                generated_text = str(response)
            
            # Apply stop sequences
            if stop:
                for sequence in stop:
                    if sequence in generated_text:
                        generated_text = generated_text[:generated_text.find(sequence)]
            
            return generated_text

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
            response = self.generate(formatted_input)
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