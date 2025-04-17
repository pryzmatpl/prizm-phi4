#!/bin/bash
# Initialize with tinygrad for phi4 model loading

# Import environment variables
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

# Default model to use
MODEL=${1:-"phi4"}

# Check if the model exists
if [ ! -d "./models/$MODEL" ]; then
  echo "Error: Model directory './models/$MODEL' does not exist."
  exit 1
fi

echo "Initializing with tinygrad for model: $MODEL"

# Export necessary environment variables
export PYTHONPATH="$(pwd):$PYTHONPATH"

# Verify exo and codex are available
if [ ! -d "./exo" ]; then
  echo "Error: exo directory not found."
  exit 1
fi

if [ ! -d "./codex" ]; then
  echo "Error: codex directory not found."
  exit 1
fi

# Run the main application with the specified model
# This will automatically use the exo/tinygrad interface for loading the model
python main.py --model $MODEL $@

# For debugging purposes
echo "Session completed." 