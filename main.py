import sys
from pipeline import Pipeline
from agent import Agent
from interface import Interface

def main():
    """Main function to process input and generate responses."""

    _pipeline: Pipeline = Pipeline()
    _agent: Agent = Agent()
    _interface: Interface = Interface()

    try:
        # Initialize the pipeline
        pipeline = _pipeline.initialize_pipeline(model_path="./models/phi4")
        agents = sys.argv[1:]
        print("Welcome to ", agents)
        
        # Read from stdin until EOF
        for line in sys.stdin:
            # Ensure line is a string
            if isinstance(line, list):
                line = " ".join(line)
            line = line.strip()

            # Process input based on whether it's an agent request
            if line.startswith("AGENT:"):
                response = _agent.handle_agent_request(line)
                print(response.strip())
            else:
                messages = _interface.prepare_model_input(line, agents)
                outputs = pipeline(messages, max_new_tokens=20000)
                print(outputs)

            sys.stdout.flush()  # Ensure output is written immediately

    except KeyboardInterrupt:
        print("\nExiting...", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
