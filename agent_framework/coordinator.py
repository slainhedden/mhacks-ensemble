import logging
from typing import List, Dict, Any
from collections import Counter
from agent_factory import AgentFactory

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Coordinator:
    def __init__(self, cli=None):
        self.cli = cli
        self.agents = {
            "planner": AgentFactory.create_agent("planner", "PlannerAgent", {}),
            "coding": AgentFactory.create_agent("coding", "CodingAgent", {}),
            "testing": AgentFactory.create_agent("testing", "TestingAgent", {}),
            "review": AgentFactory.create_agent("review", "ReviewAgent", {})
        }
        self.task_history = []
        self.overall_goal = ""
        self.tool_usage = Counter()

    def process_goal(self, goal: str):
        try:
            self.overall_goal = goal
            logger.info(f"Processing goal: {goal}")
            tasks = self.agents["planner"].analyze_goal(goal)
            self.task_history = tasks
            logger.info(f"Goal broken down into {len(tasks)} tasks")

            for task in tasks:
                self._process_task(task)
                if self.cli:
                    self.cli.update('task', task['task_description'])

            self._output_tool_usage_stats()
        except Exception as e:
            logger.error(f"An error occurred while processing the goal: {str(e)}", exc_info=True)
            raise

    def _process_task(self, task: Dict[str, Any], retry_count: int = 0):
        if retry_count >= 3:
            logger.warning(f"Failed to complete task after 3 attempts: {task['task_description']}")
            return

        try:
            logger.info(f"Processing task {task['id']}: {task['task_description']}")
            agent_type = self.determine_agent_type(task)
            logger.info(f"Assigned to {agent_type} agent")
            
            result = self.agents[agent_type].execute_task(task, self.overall_goal)
            
            # Handle the new dictionary return type
            if isinstance(result, dict):
                result_str = result.get('result', str(result))
                logger.info(f"Task execution result: {result_str[:100]}...")
                if self.cli:
                    self.cli.update('output', result_str)
                
                # Update tool usage
                if 'tool' in result:
                    self.tool_usage[result['tool']] += 1
                
                # Log sandbox result if available
                if 'sandbox_result' in result:
                    logger.info(f"Sandbox result: {result['sandbox_result'][:100]}...")  # Log first 100 chars of sandbox result
            else:
                logger.info(f"Task execution result: {str(result)[:100]}...")
                if self.cli:
                    self.cli.update('output', str(result))
            
            review_result = self.agents["review"].review_task(task, str(result), self.overall_goal)
            logger.info(f"Review result: {review_result}")

            if not review_result["approved"]:
                self.handle_unapproved_task(task, review_result["feedback"], retry_count)
            else:
                logger.info(f"Task {task['id']} completed successfully")
                task['completed'] = True
        except Exception as e:
            logger.error(f"An error occurred while processing task {task['id']}: {str(e)}", exc_info=True)
            self.handle_unapproved_task(task, f"Error: {str(e)}", retry_count)

    def determine_agent_type(self, task: Dict[str, Any]) -> str:
        task_description = task['task_description'].lower()
        if "implement" in task_description or "code" in task_description:
            return "coding"
        elif "test" in task_description or "execute" in task_description or "run" in task_description:
            return "testing"
        return "coding"  # Default to coding agent

    def handle_unapproved_task(self, task: Dict[str, Any], feedback: str, retry_count: int):
        logger.warning(f"Task {task['id']} not approved: {task['task_description']}")
        logger.warning(f"Feedback: {feedback}")
        
        updated_task = task.copy()
        updated_task['task_description'] += f"\nPrevious attempt feedback: {feedback}"
        
        self._process_task(updated_task, retry_count + 1)

    def _output_tool_usage_stats(self):
        logger.info("Tool Usage Statistics:")
        for tool, count in self.tool_usage.items():
            logger.info(f"{tool}: used {count} times")
        logger.info(f"Total tool uses: {sum(self.tool_usage.values())}")
        
        completed_tasks = sum(1 for task in self.task_history if task.get('completed', False))
        logger.info(f"Completed tasks: {completed_tasks}/{len(self.task_history)}")

    def run_in_sandbox(self, task: Dict[str, Any], result: Dict[str, Any]) -> str:
        # Implement sandbox execution logic here
        # This should use the run_code_in_sandbox function from the ToolHandler
        # Return the sandbox execution result as a string
        pass