# AI Agent Pipeline for Phi-4

## Overview
Advanced AI agent system leveraging Microsoft's Phi-4 model for intelligent, context-aware conversational interactions.

## Features
- Dynamic agent management
- ROCm/GPU-compatible AI pipeline
- Flexible input processing
- Safety-aligned model interactions

## Prerequisites
- Python 3.8+
- ROCm-compatible environment
- H100 or equivalent GPU recommended

## Setup
1. Install dependencies:
   ```bash
   pip install transformers accelerate
   ```

2. Run script:
   ```bash
   ./run.sh [agent_names]
   ```

## Usage
- Standard input: Conversational queries
- Agent requests: Prefix with `AGENT:`

## Model Characteristics
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