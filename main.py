import argparse
import os
import sys
import logging
from pipeline import Pipeline
from pipeline_processor import PipelineProcessor
from agent import Agent
from interface import Interface
from dotenv import load_dotenv
import debugpy

logging.basicConfig(filename="main.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

load_dotenv()

debugpy.listen(("0.0.0.0", 5678))

def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments with support for positional agent names."""
    parser = argparse.ArgumentParser(
        description="Launch an ensemble of agents and the supervisor."
    )

    # Make source_model optional with a default value
    parser.add_argument(
        "--model",
        type=str,
        default="phi4",
        help="Source model path (default: phi4)"
    )

    # Add agents as remaining arguments
    parser.add_argument(
        "agents",
        nargs="*",  # Allow any number of agent names
        help="Names of agents to initialize"
    )

    # Parse known args to handle both script-style and direct launches
    args, unknown = parser.parse_known_args()

    # If there are unknown args, they might be agent names from script-style launch
    if unknown:
        args.agents.extend(unknown)

    return args

def main():
    """
    Main function to process input and generate responses.
    First agent is the main one.
    """
    logging.basicConfig(level=logging.INFO)
    os.environ['PYTORCH_HIP_ALLOC_CONF'] = 'max_split_size_mb:512'  # Prevent fragmentation

    # Parse arguments
    args = parse_arguments()

    # Check model path
    model_path = "./models/"+args.model
    if not os.path.exists(model_path):
        print(f"Error: Source model directory {model_path} does not exist.")
        sys.exit(1)

    # Get agent list (either from script or direct arguments)
    agents_list = args.agents

    if not agents_list:
        print("Error: No agents specified")
        sys.exit(1)

    # Initialize basic components
    _pipeline = Pipeline()
    _interface = Interface()

    # Initialize agents
    agents = Agent.initialize_agents(args.agents)

    try:
        # Initialize the transformer pipeline
        base_pipeline = Pipeline.initialize_pipeline(
            model_path=model_path
        )

        # Create pipeline processor with custom parameters
        processor = PipelineProcessor(
            pipeline=base_pipeline,
            temperature=0.7,
            top_p=0.9,
            top_k=50
        )

        print(f"Agents {' '.join(agents_list)} initialized. Awaiting input...")

        supervisor = agents_list[0]

        Interface.process_supervisor_loop(
            processor,
            supervisor,
            agents
        )

    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        print(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()