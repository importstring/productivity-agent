"""
Main entry point for the Productivity Agent system.
"""

import asyncio
import logging
from pathlib import Path
from system import MultiAgentSystem

async def main():
    """Main entry point."""
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "main.log"),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger("main")
    logger.info("Starting Productivity Agent system")
    
    try:
        # Initialize system
        system = MultiAgentSystem("src/config/system_config.json")
        
        # Start system
        await system.start()
        
        # Keep the system running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        # Stop system
        await system.stop()
        logger.info("System stopped")

if __name__ == "__main__":
    asyncio.run(main()) 