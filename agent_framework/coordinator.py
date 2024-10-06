import logging
from typing import List, Dict, Any
from collections import Counter
from llm.core import OA_LLM, Task, Agent, AgentResponse, ProgressReview
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Coordinator:
    def __init__(self, cli=None):
        self.cli = cli
        self.llm = OA_LLM()
        self.overall_goal = ""
        self.tool_usage = Counter()

    def process_goal(self, goal: str):
        try:
            self.overall_goal = goal
            logger.info(f"Processing goal: {goal}")
            
            # Create agents
            agents = self.llm.create_agents(goal)
            logger.info(f"Created {len(agents)} agents")
            
            # Create tasks
            tasks = self.llm.create_tasks(goal)
            logger.info(f"Created {len(tasks)} tasks")
            
            # Assign tasks
            assigned_tasks = self.llm.assign_tasks()
            logger.info("Tasks assigned to agents")
            
            # Process tasks
            for task in assigned_tasks:
                self._process_task(task)

            self._output_tool_usage_stats()
            self.review_overall_progress()
        except ValueError as ve:
            logger.error(f"Value error occurred while processing the goal: {str(ve)}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while processing the goal: {str(e)}", exc_info=True)

    def _process_task(self, task: Task, retry_count: int = 0):
        if retry_count >= 3:
            logger.warning(f"Failed to complete task after 3 attempts: {task.task_description}")
            return

        try:
            logger.info(f"Processing task: {task.task_description}")
            logger.info(f"Assigned to agent: {task.assigned_agent}")
            
            result = self.llm.execute_task(task)
            
            result_str = json.dumps(result.dict())
            logger.info(f"Task execution result: {result_str[:100]}...")
            if self.cli:
                self.cli.update('output', result_str)
            
            # Update tool usage
            if result.tool:
                self.tool_usage[result.tool] += 1
            
            approved = self.llm.review_task(task, result)

            if not approved:
                self.handle_unapproved_task(task, retry_count)
            else:
                logger.info(f"Task completed successfully")
                task.completed = True
        except Exception as e:
            logger.error(f"An error occurred while processing task: {str(e)}", exc_info=True)
            self.handle_unapproved_task(task, retry_count)

    def handle_unapproved_task(self, task: Task, retry_count: int):
        logger.warning(f"Task not approved: {task.task_description}")
        self._process_task(task, retry_count + 1)

    def _output_tool_usage_stats(self):
        logger.info("Tool Usage Statistics:")
        for tool, count in self.tool_usage.items():
            logger.info(f"{tool}: used {count} times")
        logger.info(f"Total tool uses: {sum(self.tool_usage.values())}")
        
        completed_tasks = sum(1 for task in self.llm.tasks if task.completed)
        logger.info(f"Completed tasks: {completed_tasks}/{len(self.llm.tasks)}")

    def review_overall_progress(self):
        progress_review = self.llm.review_progress(self.overall_goal)
        logger.info(f"Overall Progress Review: {progress_review.model_dump()}")
        self._adjust_plan_based_on_review(progress_review)

    def _adjust_plan_based_on_review(self, progress_review: ProgressReview):
        # Implement logic to adjust the plan or create new tasks based on the progress review
        # This could involve creating new tasks or modifying existing ones
        pass

    def review_task(self, task, result):
        is_approved = self.llm.review_task(task, result)
        if not is_approved:
            feedback = "Task not approved. Please ensure you're creating or modifying files as required. Avoid repeatedly checking the project structure without making changes."
            logger.warning(f"Task not approved: {task['task_description']}. Feedback: {feedback}")
            return False, feedback

        return True, "Task approved."