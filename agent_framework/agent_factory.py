from typing import List, Dict, Any
from agent import Agent
from prompts.agent_prompts import AgentPrompts
from tools.definitions import TOOL_DEFINITIONS, TOOL_DEFINITIONS_REVIEWER

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
        return [{"id": i+1, **task.model_dump()} for i, task in enumerate(response)]

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
        
        # Ensure sandbox testing is performed
        if isinstance(result, dict) and 'sandbox_result' not in result:
            sandbox_result = self.run_code_in_sandbox(task, result)
            result['sandbox_result'] = sandbox_result
        
        return result

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

    def execute_task(self, task: Dict[str, Any], overall_goal: str) -> str:
        system_prompt = AgentPrompts.TESTING_TASK_SYSTEM.value
        user_prompt = AgentPrompts.TESTING_TASK_USER.value.format(
            task=task['task_description'],
            context=self.get_relevant_context(task['task_description']),
            goal=overall_goal
        )
        # Use both TOOL_DEFINITIONS and TOOL_DEFINITIONS_REVIEWER
        combined_tools = TOOL_DEFINITIONS + TOOL_DEFINITIONS_REVIEWER
        response = self.llm.generate_response(system_prompt, user_prompt, combined_tools)
        return self.handle_tool_call(response, task)

class ReviewAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any]):
        super().__init__(name, "Reviewer", attributes)

    def review_task(self, task: Dict[str, Any], result: str, overall_goal: str) -> Dict[str, Any]:
        system_prompt = AgentPrompts.TASK_REVIEW_SYSTEM.value
        user_prompt = AgentPrompts.TASK_REVIEW_USER.value.format(
            task=task['task_description'],
            result=result,
            context=self.get_relevant_context(task['task_description']),
            goal=overall_goal
        )
        response = self.llm.generate_response(system_prompt, user_prompt)
        review_result = self.parse_review_response(response)
        
        # Consider sandbox results in the review
        if isinstance(result, dict) and 'sandbox_result' in result:
            sandbox_success = "All tests passed" in result['sandbox_result']
            if not sandbox_success:
                review_result['approved'] = False
                review_result['feedback'] += f"\nSandbox tests failed. Please fix the issues and run the tests again. Sandbox result: {result['sandbox_result']}"
        
        return review_result

    def parse_review_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        content = response.get("content", "").strip()
        is_approved = content.lower().startswith("yes")
        feedback = content[4:].strip() if is_approved else content[3:].strip()
        return {
            "approved": is_approved,
            "feedback": feedback
        }