#!/usr/bin/env python3
"""
Simple Workflow - AGNT5 Worker

This demonstrates basic AGNT5 worker functionality with function handlers.
"""

import asyncio
import os
import sys
import logging
from agnt5 import Worker

# Import function handlers
import simple_workflow.functions

# Configure logging (this will also control Rust log levels via PyO3-log)
logging.basicConfig(
    level=logging.DEBUG,  # Use DEBUG to see all Rust logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point for the worker."""
    logger.info("Starting simple-workflow worker...")

    # Configuration from environment
    coordinator_endpoint = os.getenv("AGNT5_COORDINATOR_ENDPOINT", "http://localhost:34186")

    logger.info(f"Coordinator: {coordinator_endpoint}")

    try:
        # Create worker with correct API
        worker = Worker(
            service_name="simple-workflow",
            service_version="1.0.0",
            coordinator_endpoint=coordinator_endpoint,
            runtime="standalone"
        )

        # Functions are automatically registered through the @function decorator
        logger.info("Worker created successfully. Function handlers loaded from simple_workflow.functions")

        # Start the worker (this is async and will block until shutdown)
        logger.info("Starting worker and registering with coordinator...")
        await worker.run()

    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure to install agnt5: pip install agnt5")
        return 1
    except Exception as e:
        logger.error(f"Worker error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))