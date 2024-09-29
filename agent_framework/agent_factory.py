from typing import List, Dict, Any, Union
from agent import Agent
from prompts.agent_prompts import AgentPrompts
from tools.definitions import TOOL_DEFINITIONS, TOOL_DEFINITIONS_REVIEWER
from tools.artifacts import run_artifact_review
import json
import os

class AgentFactory:
    @staticmethod
    def create_agent(agent_type: str, name: str, attributes: Dict[str, Any]) -> Agent:
        if agent_type == "planner":
            return PlannerAgent(name, attributes)
        elif agent_type == "coding":
            return CodingAgent(name, attributes)
        elif agent_type == "testing":
            return TestingAgent(name, attributes)
        elif agent_type == "review":
            return ReviewAgent(name, attributes)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

class PlannerAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any]):
        super().__init__(name, "Planner", attributes)

    def analyze_goal(self, goal: str) -> List[Dict[str, Any]]:
        system_prompt = AgentPrompts.GOAL_ANALYSIS_SYSTEM.value
        user_prompt = AgentPrompts.GOAL_ANALYSIS_USER.value.format(goal=goal, context=self.get_context())
        response = self.llm.generate_structured_response(system_prompt, user_prompt)
        
        tasks = []
        if isinstance(response, dict) and 'tasks' in response:
            for i, task in enumerate(response['tasks']):
                task_type = self._determine_task_type(task['task_description'])
                file_path = self._extract_file_path(task['task_description'])
                tasks.append({
                    "id": i+1,
                    "task_description": task['task_description'],
                    "estimated_complexity": task.get('estimated_complexity', 'Medium'),
                    "task_type": task_type,
                    "file_path": file_path
                })
        else:
            self.logger.error(f"Invalid response format from LLM: {response}")
        
        if not tasks:
            self.logger.warning("No valid tasks were created. Using a default task.")
            tasks = [{
                "id": 1,
                "task_description": "Analyze the goal and create a plan",
                "estimated_complexity": "Medium",
                "task_type": "planning",
                "file_path": ""
            }]

        self.logger.info(f"Created {len(tasks)} tasks")
        return tasks

    def _determine_task_type(self, task_description: str) -> str:
        if any(keyword in task_description.lower() for keyword in ['implement', 'code', 'write']):
            return 'coding'
        elif any(keyword in task_description.lower() for keyword in ['test', 'verify']):
            return 'testing'
        elif any(keyword in task_description.lower() for keyword in ['review', 'check']):
            return 'review'
        else:
            return 'other'

    def _extract_file_path(self, task_description: str) -> str:
        # Simple extraction of file path from task description
        words = task_description.split()
        for word in words:
            if word.endswith(('.js', '.html', '.css', '.py')):
                return word
        return ""

    def _load_task_templates(self) -> Dict[str, Dict[str, Any]]:
        # Load task templates from a configuration file or database
        # For now, we'll use a simple dictionary
        return {
            "coding": {
                "steps": ["Plan implementation", "Write code", "Write unit tests", "Refactor and optimize"],
                "tools": ["write_file", "read_file", "run_python_file"]
            },
            "testing": {
                "steps": ["Design test cases", "Implement tests", "Run tests", "Analyze results"],
                "tools": ["read_file", "write_file", "run_python_file"]
            },
            # Add more task types and templates as needed
        }

class CodingAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any]):
        super().__init__(name, "Coder", attributes)

    def execute_task(self, task: Dict[str, Any], overall_goal: str) -> Dict[str, Any]:
        system_prompt = AgentPrompts.CODING_TASK_SYSTEM.value
        user_prompt = AgentPrompts.CODING_TASK_USER.value.format(
            task=task['task_description'],
            context=self.get_relevant_context(task['task_description']),
            goal=overall_goal
        )
        response = self.llm.generate_response(system_prompt, user_prompt, TOOL_DEFINITIONS + TOOL_DEFINITIONS_REVIEWER)
        result = self.handle_tool_call(response, task)
        
        # Ensure result is always a dictionary
        if isinstance(result, str):
            result = {'content': result}
        
        file_type = self._determine_file_type(task)
        if file_type == 'python':
            sandbox_result = self.run_code_in_sandbox(task, result)
            result['sandbox_result'] = sandbox_result
        else:
            result['manual_testing_strategy'] = self._generate_manual_testing_strategy(file_type)
        
        return result

    def _determine_file_type(self, task: Dict[str, Any]) -> str:
        task_description = task['task_description'].lower()
        if '.py' in task_description:
            return 'python'
        elif '.html' in task_description:
            return 'html'
        elif '.css' in task_description:
            return 'css'
        elif '.js' in task_description:
            return 'javascript'
        else:
            return 'unknown'

    def _generate_manual_testing_strategy(self, file_type: str) -> str:
        strategies = {
            'html': "1. Open the HTML file in multiple browsers to check for compatibility.\n2. Verify the structure and content of the page.\n3. Check for responsive design by resizing the browser window.",
            'css': "1. Inspect the styles in the browser's developer tools.\n2. Verify that the styles are applied correctly to the HTML elements.\n3. Test responsiveness at different screen sizes.",
            'javascript': "1. Open the browser's console to check for any errors.\n2. Test all interactive elements and verify they work as expected.\n3. Check that the game logic functions correctly for all possible scenarios."
        }
        return strategies.get(file_type, "Please review the file manually and provide feedback on its functionality and appearance.")

    def run_code_in_sandbox(self, task: Dict[str, Any], result: Dict[str, Any]) -> str:
        # Implement sandbox execution logic here
        # Use the run_python_file function from the ToolHandler
        file_path = result.get('file_path', '')
        is_unit_test = result.get('is_unit_test', False)
        
        if file_path:
            sandbox_result = self.tool_handler.run_python_file(file_path, is_unit_test)
            return f"Sandbox execution result:\nReturn Code: {sandbox_result['return_code']}\nOutput: {sandbox_result['output']}\nErrors: {sandbox_result['errors']}"
        else:
            return "No file path provided for sandbox execution."

class TestingAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any]):
        super().__init__(name, "Tester", attributes)

    def execute_task(self, task: Dict[str, Any], overall_goal: str) -> Dict[str, Any]:
        system_prompt = AgentPrompts.TESTING_TASK_SYSTEM.value
        user_prompt = AgentPrompts.TESTING_TASK_USER.value.format(
            task=task['task_description'],
            context=self.get_relevant_context(task['task_description']),
            goal=overall_goal
        )
        combined_tools = TOOL_DEFINITIONS + TOOL_DEFINITIONS_REVIEWER
        response = self.llm.generate_response(system_prompt, user_prompt, combined_tools)
        result = self.handle_tool_call(response, task)
        
        # Ensure result is always a dictionary
        if isinstance(result, str):
            result = {'content': result}
        
        return result

class ReviewAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any]):
        super().__init__(name, "Review", attributes)

    def review_task(self, task: Dict[str, Any], result: Union[str, Dict[str, Any]], overall_goal: str) -> Dict[str, Any]:
        if isinstance(result, str):
            result = {'content': result}
        
        system_prompt = AgentPrompts.TASK_REVIEW_SYSTEM.value
        user_prompt = AgentPrompts.TASK_REVIEW_USER.value.format(
            task=json.dumps(task),
            result=json.dumps(result),
            overall_goal=overall_goal
        )

        response = self.llm.generate_response(system_prompt, user_prompt)
        review_result = response["content"].strip()

        return self._process_review_result(review_result)

    def _process_review_result(self, review_result: str) -> Dict[str, Any]:
        lines = review_result.split('\n')
        approval = lines[0].lower().startswith("approved")
        feedback = self._summarize_feedback('\n'.join(lines[1:]).strip())

        return {
            "approved": approval,
            "feedback": feedback
        }

    def _summarize_feedback(self, feedback: str) -> str:
        # Summarize the feedback to focus on key points
        key_points = []
        if "Error:" in feedback:
            key_points.append(feedback.split("Error:")[1].split('\n')[0].strip())
        if "Missing:" in feedback:
            key_points.append(feedback.split("Missing:")[1].split('\n')[0].strip())
        if "Improvement:" in feedback:
            key_points.append(feedback.split("Improvement:")[1].split('\n')[0].strip())
        
        if not key_points:
            return feedback[:100] + "..." if len(feedback) > 100 else feedback
        
        return " | ".join(key_points)

    def review_overall_progress(self, task_history: List[Dict[str, Any]], overall_goal: str) -> str:
        system_prompt = AgentPrompts.PROGRESS_REVIEW_SYSTEM.value
        user_prompt = AgentPrompts.PROGRESS_REVIEW_USER.value.format(
            task_history=json.dumps(task_history),
            overall_goal=overall_goal
        )

        response = self.llm.generate_response(system_prompt, user_prompt)
        return self._summarize_progress_review(response["content"].strip())

    def _summarize_progress_review(self, review: str) -> str:
        # Summarize the progress review to focus on key points
        summary = []
        if "Progress:" in review:
            summary.append(review.split("Progress:")[1].split('\n')[0].strip())
        if "Missing:" in review:
            summary.append(review.split("Missing:")[1].split('\n')[0].strip())
        if "Next steps:" in review:
            summary.append(review.split("Next steps:")[1].split('\n')[0].strip())
        
        if not summary:
            return review[:150] + "..." if len(review) > 150 else review
        
        return " | ".join(summary)