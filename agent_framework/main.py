from coordinator import Coordinator
import logging
from cli.base import BasicCLI
import threading
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info(f"Current working directory: {os.getcwd()}")
    # cli = BasicCLI()
    coordinator = Coordinator()
    
    # cli_thread = threading.Thread(target=cli.start)
    # cli_thread.start()

    goal = """
    Create a Tic-Tac-Toe web application using HTML, CSS, and JavaScript with the following features:
    1. Implement a 3x3 game board using HTML and CSS
    2. Create the game logic in JavaScript, including turn-taking and win condition checking
    3. Add a reset button to start a new game
    4. Implement a score tracking system for X and O
    5. Add basic animations for placing X's and O's
    6. Make the game responsive for different screen sizes
    7. Implement a simple AI for single-player mode (optional)
    8. Add sound effects for game actions (optional)
    """
    try:
        coordinator.process_goal(goal)
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Stopping the program.")
    # finally:
        # cli.stop()
        # cli_thread.join()

if __name__ == "__main__":
    main()