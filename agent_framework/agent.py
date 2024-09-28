import json
from datetime import datetime
from typing import Dict, Any
from llm.core import OA_LLM, Task
from prompts.solo_agent import SoloAgentPrompt
from tools.file_ops import FileOperations

class Agent:
    def __init__(self, name: str, role: str, attributes: dict):
        self.name = name
        self.role = role
        self.attributes = attributes
        self.context = []
        self.task_tracker: Dict[int, Task] = {}
        self.file_ops = FileOperations()
        self.llm = OA_LLM()

    def add_context(self, entry: Dict[str, Any]):
        """Add a new entry to the agent's context with a timestamp."""
        entry['timestamp'] = datetime.now().isoformat()
        self.context.append(entry)

    def analyze_goal(self, goal: str) -> bool:
        """
        Analyze the given goal and break it down into tasks.
        Returns True if tasks were generated, False otherwise.
        """
        prompt = f"\nGoal: {goal}"
        tasks = self.llm.generate_structured_response(system_prompt=SoloAgentPrompt.GOAL_ANALYSIS.value, user_prompt=prompt)
        
        for i, task in enumerate(tasks, 1):
            self.task_tracker[i] = task
        
        self.add_context({"action": "goal_analysis", "goal": goal, "tasks": [t.model_dump() for t in tasks]})
        return bool(tasks)

    def execute_task(self, task_id: int) -> str:
        """Execute a specific task and return the result."""
        task = self.task_tracker[task_id]
        prompt = SoloAgentPrompt.TASK_EXECUTION.value.format(task=task.task_description)
        result = self.llm.generate_response(prompt)
        
        self.add_context({"action": "task_execution", "task_id": task_id, "task": task.model_dump(), "result": result})
        return result

    def review_task(self, task_id: int, result: str) -> bool:
        """
        Review the result of a task execution.
        Returns True if the task is completed, False otherwise.
        """
        task = self.task_tracker[task_id]
        prompt = SoloAgentPrompt.TASK_REVIEW.value.format(task=task.task_description, result=result)
        review = self.llm.generate_response(prompt)
        
        is_completed = review.lower().startswith("yes")
        self.task_tracker[task_id].completed = is_completed
        
        self.add_context({"action": "task_review", "task_id": task_id, "task": task.model_dump(), "review": review, "is_completed": is_completed})
        return is_completed

    def save_task_output(self, task_id: int, result: str):
        """Save the output of a completed task to a file."""
        filename = f"task_{task_id}_output.txt"
        self.file_ops.write_file(result, filename)
        print(f"Task {task_id} output saved to {filename}")

    def process_goal(self, goal: str):
        """
        Process the given goal by breaking it down into tasks,
        executing each task, and reviewing the results.
        """
        if not self.analyze_goal(goal):
            print("No tasks were generated.")
            return

        print("Tasks generated:")
        for task_id, task in self.task_tracker.items():
            print(f"{task_id}: {task.task_description}")

        for task_id in self.task_tracker:
            attempts = 0
            max_attempts = 3
            while not self.task_tracker[task_id].completed and attempts < max_attempts:
                result = self.execute_task(task_id)
                is_completed = self.review_task(task_id, result)
                
                if is_completed:
                    print(f"Task {task_id} completed successfully.")
                    self.save_task_output(task_id, result)
                else:
                    print(f"Task {task_id} needs further work. Attempt {attempts + 1}/{max_attempts}")
                    attempts += 1

            if not self.task_tracker[task_id].completed:
                print(f"Task {task_id} could not be completed after {max_attempts} attempts.")

        print("All tasks processed.")

# Example usage
if __name__ == "__main__":
    agent = Agent(name="SoloAgent", role="Problem Solver", attributes={"focus": "single-agent"})
    goal = "Create a basic tic-tac-toe game in HTML, CSS, and JavaScript"
    agent.process_goal(goal)
