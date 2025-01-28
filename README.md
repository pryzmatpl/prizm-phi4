# AI Agent Pipeline for Phi-4

## Overview
Advanced AI agent system leveraging Microsoft's Phi-4 model for intelligent, context-aware conversational interactions.

## Features
- Dynamic agent management
- ROCm/GPU-compatible AI pipeline
- Flexible input processing
- Safety-aligned model interactions

## Prerequisites
- Python 3.10 (based on conda env in AMD's **rocm/pytorch:rocm6.1.3_ubuntu22.04_py3.10_pytorch_release-2.1.2**)
- ROCm-compatible environment (Tested on 7900 XTX / gfx1100)

## Setup
1. Install dependencies:
   ```bash
   pip install transformers accelerate bitsandbytes
   ```

2. Run script:
   ```bash
   ./run.sh [model_path] [agent_name1] [agent_name2] ...
   ```

## Usage
- Standard input: Conversational queries
- Agent requests: Prefixed by supervisor with `AGENT:`
- For testing, may aim to start messages with `AGENT:`

## Model Characteristics (just phi4)
- 14B parameters
- 16K token context
- English-focused reasoning
- Synthetic dataset training

## Responsible AI Considerations
- Potential for biased or inaccurate outputs
- Not suitable for high-stakes decision-making
- Requires careful context monitoring

## License
Prizm License (MIT License until you are a 5 Million USD ARR company - then you need to reach out to Prizm to discuss further steps regarding technological cooperation)