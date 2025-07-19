"""Main entry point for Thought Bubble Camera App."""

import sys
import logging
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.config import APP_NAME, VERSION
from utils.logging_setup import setup_logging
from ui.main_window import MainWindow


def main():
    """Main application entry point."""
    # Setup logging
    logger = setup_logging(logging.INFO)
    logger.info(f"Starting {APP_NAME} v{VERSION}")
    
    try:
        # Create and run the main window
        app = MainWindow()
        app.run()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Application shutting down")


if __name__ == "__main__":
    main()