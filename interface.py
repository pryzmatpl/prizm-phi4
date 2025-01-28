import logging
import sys
from typing import List, Dict
from agent import Agent
from pipeline_processor import PipelineProcessor

class Interface:
    @staticmethod
    def prepare_model_input(input_text: str, agents: List[str]) -> List[Dict[str, str]]:
        """
        Process input agents prompts and return messages list.
        """
        interface_prompt = []
        for agent in agents:
            try:
                interface_prompt.append(Agent.load_agent_config_file(agent))
            except ValueError as e:
                print(str(e), file=sys.stderr)
                continue
        interface_prompt.append({"role": "user", "content": input_text.strip()})
        return interface_prompt

    @staticmethod
    def process_supervisor_loop(
            processor: PipelineProcessor,
            supervisor_agent: Agent,
            agents: List[Dict]
    ) -> None:
        """
        Main processing loop where supervisor coordinates all agent interactions.
        """
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            try:
                # First, have the supervisor process the input
                logging.debug(agents)
                supervisor_messages = Interface.prepare_model_input(line, agents)
                supervisor_response = processor.process(
                    input_text=supervisor_messages,
                    agent=supervisor_agent
                )

                if not supervisor_response:
                    print("Supervisor generated no response.")
                    continue

                # Log supervisor's thinking
                logging.debug(f"Supervisor response: {supervisor_response}")

                # Process any agent commands in supervisor's response
                responses = []
                for command in supervisor_response.split('\n'):
                    if command.startswith("AGENT:"):
                        # Extract target agent and command
                        parts = command.split(":", 2)
                        if len(parts) < 3:
                            continue

                        target_agent_name = parts[1].strip()
                        agent_command = parts[2].strip()

                        logging.debug(f"Target agent name: {target_agent_name}")
                        logging.debug(f"Target agent cmd: {agent_command}")

                        # Find the target agent
                        target_agent = next(
                            (a["agent"] for a in agents if a["name"] == target_agent_name),
                            None
                        )

                        if target_agent:
                            # Have the agent process the command
                            agent_response = target_agent.handle_agent_request(
                                f"AGENT: {agent_command}",
                                processor
                            )
                            if agent_response:
                                responses.append(f"{target_agent_name}: {agent_response.strip()}")
                    else:
                        # Non-agent responses go directly to output
                        responses.append(command)

                # Final processing of all responses by supervisor
                if responses:
                    final_response = processor.process(
                        input_text=Interface.prepare_model_input(
                            "\n".join(responses),
                            agents
                        ),
                        agent=supervisor_agent
                    )
                    print(final_response.strip() if final_response else "No final response generated.")
                else:
                    print(supervisor_response.strip())

                sys.stdout.flush()

            except Exception as e:
                logging.error(f"Error in processing loop: {str(e)}")
                print(f"Error: {str(e)}")
                continue