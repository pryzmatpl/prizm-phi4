import sys
import logging
from pipeline import Pipeline
from agent import Agent
from interface import Interface

def main():
    """
    Main function to process input and generate responses.
    First agent is the main one
    """
    logging.basicConfig(level=logging.INFO)

    _pipeline = Pipeline()
    _interface = Interface()

    agents_list = sys.argv[1:]
    agents = []

    for agent in agents_list:
        agents.append({"name":agent, "agent":Agent(agent)})

    count = 0
    for agent_dict in agents:
        other_agents = agents[:count] + agents[count+1:]
        for other_agent in other_agents:
            agent_dict["agent"].register_agent(other_agent["name"], other_agent["agent"])    

    try:
        pipeline = _pipeline.initialize_pipeline(model_path="./models/phi4")
        print("Agents " + ''.join(agents_list) + " initialized. Awaiting input...")

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue

            # Handle agent-specific requests
            if line.startswith("AGENT:"):
                for responding_agent in agents[1:]:
                    response = responding_agent["agent"].handle_agent_request(line)
                    print(response.strip())
            else:
                messages = _interface.prepare_model_input(line, agents)
                outputs = pipeline(messages, max_new_tokens=20000)
                if isinstance(outputs, list) and len(outputs) > 0:
                    print(outputs[0]["generated_text"].strip())
                else:
                    print("No response generated.")

            sys.stdout.flush()

    except KeyboardInterrupt:
        print("Exiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()