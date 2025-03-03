import argparse
import os
import sys
import logging
from pipeline import Pipeline  # Assuming this handles model loading
from interface import PipelineProcessor  # Assuming this processes model outputs
from agent import Agent
from interface import Interface  # Assuming this handles user I/O
from dotenv import load_dotenv
import debugpy

# Configure logging
logging.basicConfig(
    filename="main.log",
    format='%(asctime)s %(message)s',
    filemode='w',
    level=logging.INFO
)

load_dotenv()

# Set up debugger
debugpy.listen(("0.0.0.0", 5678))

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments with support for positional agent names."""
    parser = argparse.ArgumentParser(
        description="Launch an ensemble of agents with a supervisor."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="phi4",
        help="Source model path (default: phi4)"
    )
    parser.add_argument(
        "agents",
        nargs="+",  # Require at least one agent
        help="Names of agents to initialize (first agent is supervisor)"
    )
    args = parser.parse_args()
    return args

def main():
    """
    Main function to initialize agents and process user input.
    The first agent is the supervisor, others are available for collaboration.
    """
    os.environ['PYTORCH_HIP_ALLOC_CONF'] = 'max_split_size_mb:512'  # Prevent fragmentation

    # Parse arguments
    args = parse_arguments()
    model_path = f"./models/{args.model}"

    if not os.path.exists(model_path):
        logging.error(f"Source model directory {model_path} does not exist.")
        print(f"Error: Source model directory {model_path} does not exist.")
        sys.exit(1)

    agents_list = args.agents
    if not agents_list:
        logging.error("No agents specified.")
        print("Error: No agents specified.")
        sys.exit(1)

    # Initialize components
    pipeline = Pipeline()
    interface = Interface()

    # Initialize all agents
    agents_dict = {}
    for agent_name in agents_list:
        try:
            agents_dict[agent_name] = Agent(agent_config=agent_name)
        except ValueError as e:
            logging.error(f"Failed to initialize agent {agent_name}: {e}")
            print(f"Error: Failed to initialize agent {agent_name}: {e}")
            sys.exit(1)

    # Register agents with each other
    for name, agent in agents_dict.items():
        for other_name, other_agent in agents_dict.items():
            if name != other_name:
                agent.register_agent(other_name, other_agent)

    try:
        # Initialize the transformer pipeline
        base_pipeline = Pipeline.initialize_pipeline(model_path=model_path)

        # Create pipeline processor
        processor = PipelineProcessor(
            pipeline=base_pipeline,
            temperature=0.7,
            top_p=0.9,
            top_k=50
        )

        supervisor_name = agents_list[0]
        supervisor = agents_dict[supervisor_name]

        logging.info(f"Agents {' '.join(agents_list)} initialized. Supervisor: {supervisor_name}")
        print(f"Agents {' '.join(agents_list)} initialized. Supervisor: {supervisor_name}")
        print("Awaiting input...")

        # Main loop to process user input
        while True:
            try:
                user_input = interface.get_user_input()  # Assuming Interface has this method
                if user_input.lower() in ["exit", "quit"]:
                    break

                # Supervisor processes the prompt
                response = supervisor.handle_prompt(user_input)

                # Output response to user
                interface.display_response(response)  # Assuming Interface has this method
                logging.info(f"User: {user_input}\nResponse: {response}")

            except Exception as e:
                error_msg = f"Error processing input: {str(e)}"
                logging.error(error_msg)
                interface.display_response(error_msg)

    except KeyboardInterrupt:
        logging.info("Program terminated by user.")
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()