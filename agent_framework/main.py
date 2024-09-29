from coordinator import Coordinator
import logging
from cli.base import BasicCLI
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    # cli = BasicCLI()
    coordinator = Coordinator()
    
    # cli_thread = threading.Thread(target=cli.start)
    # cli_thread.start()

    goal = """
    Create a simple task management system with the following features:
    1. Implement a Task class with attributes: id, title, description, status (todo, in_progress, done)
    2. Create a TaskManager class to handle adding, updating, and listing tasks
    3. Implement a simple command-line interface to interact with the TaskManager
    4. Add functionality to save tasks to a JSON file and load them on startup
    5. Implement basic error handling and input validation
    6. Write unit tests for the Task and TaskManager classes
    7. Add a feature to set due dates for tasks and list tasks by due date
    8. Implement a simple priority system (low, medium, high) for tasks
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