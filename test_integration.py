#!/usr/bin/env python3
"""
Test script to verify the integration between codex and exo for loading phi4 model.
This tests the whole pipeline from model loading to inference.
"""

import os
import logging
import argparse
from pipeline import Pipeline
from interface.pipeline_processor import PipelineProcessor
from exo.download.shard_download import LocalModelDownloader
from exo.models import build_base_shard

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_tinygrad_pipeline():
    """Test loading and using the phi4 model with the tinygrad interface."""
    logger.info("Testing tinygrad pipeline integration...")
    
    # Initialize the pipeline with tinygrad
    model_path = "./models/phi4"
    logger.info(f"Initializing pipeline from {model_path}")
    
    pipeline = Pipeline.initialize_pipeline(
        model_path=model_path,
        use_tinygrad=True
    )
    
    # Initialize processor
    processor = PipelineProcessor(
        pipeline=pipeline,
        temperature=0.7,
        top_p=0.9,
        top_k=50
    )
    
    # Test generation
    test_prompt = "What is the capital of France?"
    logger.info(f"Testing generation with prompt: {test_prompt}")
    
    response = processor.generate(test_prompt, max_new_tokens=100)
    
    logger.info(f"Generated response: {response}")
    
    return True

def test_direct_tinygrad_interface():
    """Test the tinygrad interface directly."""
    logger.info("Testing direct tinygrad interface...")
    
    model_id = "phi-4"
    engine_name = "TinygradDynamicShardInferenceEngine"
    
    # Initialize components
    downloader = LocalModelDownloader()
    shard = build_base_shard(model_id, engine_name)
    
    if shard is None:
        logger.error(f"Could not build shard for model {model_id}")
        return False
    
    # Import necessary module
    from exo.inference.tinygrad.inference import TinygradDynamicShardInferenceEngine
    import asyncio
    import numpy as np
    
    # Create an async test function
    async def run_test():
        # Initialize engine
        engine = TinygradDynamicShardInferenceEngine(downloader)
        
        # Ensure the shard is loaded
        await engine.ensure_shard(shard, engine_name)
        
        # Test encoding
        prompt = "What is the capital of France?"
        encoded = await engine.encode(shard, prompt)
        logger.info(f"Encoded prompt to {len(encoded)} tokens")
        
        # Test inference
        input_data = encoded.reshape(1, -1)  # Add batch dimension
        request_id = "test_request"
        
        output, _ = await engine.infer_tensor(request_id, shard, input_data)
        logger.info(f"Inference output shape: {output.shape}")
        
        # Test sampling
        next_token = await engine.sample(output, temp=0.7)
        logger.info(f"Sampled token: {next_token.item()}")
        
        # Test decoding
        decoded = await engine.decode(shard, np.array([next_token.item()]))
        logger.info(f"Decoded token: {decoded}")
        
        return True
    
    # Run the async test
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run_test())

def main():
    """Main entry point for the test script."""
    parser = argparse.ArgumentParser(description="Test the integration between codex and exo")
    parser.add_argument("--test", choices=["pipeline", "tinygrad", "all"], default="all",
                      help="Which test to run: pipeline, tinygrad, or all")
    
    args = parser.parse_args()
    
    # Check if models directory exists
    if not os.path.exists("./models/phi4"):
        logger.error("Models directory './models/phi4' not found. Please check your installation.")
        return False
    
    success = True
    
    # Run the selected tests
    if args.test in ["pipeline", "all"]:
        try:
            pipeline_success = test_tinygrad_pipeline()
            if pipeline_success:
                logger.info("Pipeline test passed!")
            else:
                logger.error("Pipeline test failed!")
                success = False
        except Exception as e:
            logger.error(f"Pipeline test failed with error: {str(e)}")
            success = False
    
    if args.test in ["tinygrad", "all"]:
        try:
            tinygrad_success = test_direct_tinygrad_interface()
            if tinygrad_success:
                logger.info("Direct tinygrad interface test passed!")
            else:
                logger.error("Direct tinygrad interface test failed!")
                success = False
        except Exception as e:
            logger.error(f"Direct tinygrad interface test failed with error: {str(e)}")
            success = False
    
    if success:
        logger.info("All tests passed! The integration is working correctly.")
        return True
    else:
        logger.error("Some tests failed. Please check the logs for details.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 