# Multi-Agent Framework

## Overview

The Multi-Agent Framework is an advanced AI-powered system designed to break down complex tasks into manageable subtasks and execute them using specialized agents. This framework leverages OpenAI's language model(gpt-4o-mini) to analyze goals, plan tasks, write code, perform testing, and conduct reviews.

## Key Features

- Goal Analysis: Breaks down user-defined goals into specific, actionable tasks.
- Multi-Agent Collaboration: Utilizes specialized agents for planning, coding, testing, and reviewing.
- Sandbox Execution: Runs code in a secure sandbox environment for testing and validation.
- Progress Tracking: Monitors and reports on task completion and overall project progress.
- CLI Interface: Provides a user-friendly command-line interface for interaction and monitoring.

## Project Structure

- `agent_framework/`: Core framework components
  - `agents/`: Individual agent implementations
  - `cli/`: Command-line interface
  - `llm/`: Language model integration
  - `prompts/`: Prompt templates for agents
  - `tools/`: Utility functions and tools
  - `utils/`: Helper classes and functions
- `main.py`: Entry point for the application
- `coordinator.py`: Orchestrates the multi-agent workflow
- `agent_factory.py`: Creates and manages different types of agents

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/slainhedden/mhacks-ensemble.git
   cd mhacks-ensemble
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   - Create a `.env` file in the project root
   - Add your API key: `OPENAI_API_KEY=your_api_key_here`

## Usage

1. Run the main application:
   ```
   python main.py
   ```

2. When prompted, enter your goal or project description. Be as specific as possible about what you want to achieve. For example:
   ```
   Create a simple web-based tic-tac-toe game using HTML, CSS, and JavaScript
   ```

3. The system will analyze your goal and break it down into smaller, manageable tasks. You'll see these tasks displayed in the CLI interface.

4. The Multi-Agent Framework will automatically start working on the tasks in order. You'll see real-time updates in the CLI as each agent completes its assigned task.

5. For certain tasks, especially those involving HTML, CSS, or JavaScript, the system may ask for your review or input. Follow the prompts to provide feedback or approve the generated artifacts.

6. Once all tasks are completed, the system will provide a final progress review and summary of the achieved goal.
    
7. After the process is complete, you can find the generated files in the `src/` directory within the project folder.

9. To run or test the created application (if applicable):
   - For web applications, open the main HTML file (usually `index.html`) in a web browser.
   - For Python scripts, run them using the Python interpreter:
     ```
     python src/your_script_name.py
     ```

10. If you want to start a new project or modify the existing one, simply run the main application again and enter a new goal or modification request.

Remember that the Multi-Agent Framework is designed to assist with coding tasks and project creation. While it can generate functional code and project structures, it's always a good practice to review the output and make any necessary adjustments to fit your specific needs.
