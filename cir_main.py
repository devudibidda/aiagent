#!/usr/bin/env python3
"""
Vestas CIR Analysis System - Main Entry Point
"""

import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    
    logger.info("Starting Vestas CIR Analysis System...")
    
    # Import after logging is configured
    from cir_system.cir_dashboard import build_cir_dashboard
    
    # Launch dashboard
    interface = build_cir_dashboard()
    logger.info("Launching Gradio dashboard on http://127.0.0.1:7861")
    interface.launch(server_name="127.0.0.1", server_port=7861, show_error=True)


if __name__ == "__main__":
    main()
