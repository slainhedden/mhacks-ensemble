from typing import List, Dict, Any, Union
from agent import Agent
from prompts.agent_prompts import AgentPrompts
from tools.definitions import TOOL_DEFINITIONS
import json
import os
from models import TaskList, AgentResponse, ReviewResult, ProgressReview
from llm.core import OA_LLM

class AgentFactory:
    def __init__(self):
        self.agent_registry = {}
        self.collaborative_memory = {}
        self.llm = OA_LLM()

    def create_agent(self, agent_type: str, name: str, attributes: Dict[str, Any]) -> Agent:
        # Dynamically create agents and register them in the agent registry
        agent = self._initialize_agent(agent_type, name, attributes)
        self.agent_registry[agent.name] = agent
        return agent

    def _initialize_agent(self, agent_type: str, name: str, attributes: Dict[str, Any]) -> Agent:
        agent_class = self._get_agent_class(agent_type)
        return agent_class(name, attributes, self.collaborative_memory)

    def _get_agent_class(self, agent_type: str) -> type:
        agent_classes = {
            "planner": PlannerAgent,
            "coding": CodingAgent,
            "testing": TestingAgent,
            "review": ReviewAgent,
            "research": ResearchAgent,
            "debug": DebugAgent,
            "optimization": OptimizationAgent,
        }
        if agent_type not in agent_classes:
            raise ValueError(f"Unknown agent type: {agent_type}")
        return agent_classes[agent_type]

    def remove_agent(self, name: str):
        # Remove an agent from the registry once it has finished its task
        if name in self.agent_registry:
            del self.agent_registry[name]

    def get_agent(self, name: str) -> Agent:
        # Retrieve a specific agent by name
        return self.agent_registry.get(name, None)

    def list_agents(self) -> Dict[str, Agent]:
        # List all currently active agents
        return self.agent_registry

    def update_collaborative_memory(self, key: str, value: Any):
        self.collaborative_memory[key] = value

    def get_collaborative_memory(self, key: str) -> Any:
        return self.collaborative_memory.get(key)

class PlannerAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any], collaborative_memory: Dict[str, Any]):
        super().__init__(name, "Planner", attributes)
        self.collaborative_memory = collaborative_memory
        self.llm = OA_LLM()

    def analyze_goal(self, goal: str) -> List[Dict[str, Any]]:
        system_prompt = AgentPrompts.GOAL_ANALYSIS_SYSTEM.value
        user_prompt = AgentPrompts.GOAL_ANALYSIS_USER.value.format(
            goal=goal,
            context=self.get_relevant_context(goal)
        )
        response = self.llm.generate_structured_response(system_prompt, user_prompt)
        
        task_list = TaskList(**response)
        return [task.dict() for task in task_list.tasks]

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
    def __init__(self, name: str, attributes: Dict[str, Any], collaborative_memory: Dict[str, Any]):
        super().__init__(name, "Coder", attributes)
        self.collaborative_memory = collaborative_memory

    def execute_task(self, task: Dict[str, Any], overall_goal: str) -> Dict[str, Any]:
        system_prompt = AgentPrompts.CODING_TASK_SYSTEM.value
        user_prompt = AgentPrompts.CODING_TASK_USER.value.format(
            task=task['task_description'],
            context=self.get_relevant_context(task['task_description']),
            goal=overall_goal
        )
        response = self.llm.generate_response(system_prompt, user_prompt, tools=TOOL_DEFINITIONS)
        try:
            agent_response = AgentResponse.parse_obj(response)
            result = self.handle_tool_call(agent_response.dict(), task)
            return result
        except ValueError as e:
            raise ValueError(f"Invalid response format: {e}")

class TestingAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any], collaborative_memory: Dict[str, Any]):
        super().__init__(name, "Tester", attributes)
        self.collaborative_memory = collaborative_memory

    def execute_task(self, task: Dict[str, Any], overall_goal: str) -> Dict[str, Any]:
        system_prompt = AgentPrompts.TESTING_TASK_SYSTEM.value
        user_prompt = AgentPrompts.TESTING_TASK_USER.value.format(
            task=task['task_description'],
            context=self.get_relevant_context(task['task_description']),
            goal=overall_goal
        )
        response = self.llm.generate_response(system_prompt, user_prompt, tools=TOOL_DEFINITIONS)
        result = self.handle_tool_call(response, task)
        
        # Ensure result is always a dictionary
        if isinstance(result, str):
            result = {'content': result}
        
        return result       

class ReviewAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any], collaborative_memory: Dict[str, Any]):
        super().__init__(name, "Review", attributes)
        self.collaborative_memory = collaborative_memory
        self.llm = OA_LLM()

    def review_task(self, task: Dict[str, Any], result: Dict[str, Any], overall_goal: str) -> Dict[str, Any]:
        system_prompt = AgentPrompts.TASK_REVIEW_SYSTEM.value
        user_prompt = AgentPrompts.TASK_REVIEW_USER.value.format(
            task=json.dumps(task),
            result=json.dumps(result),
            overall_goal=overall_goal
        )
        response = self.llm.generate_structured_response(system_prompt, user_prompt)
        
        review_result = ReviewResult(**response)
        return review_result.dict()

    def review_overall_progress(self, task_history: List[Dict[str, Any]], overall_goal: str) -> str:
        system_prompt = AgentPrompts.PROGRESS_REVIEW_SYSTEM.value
        user_prompt = AgentPrompts.PROGRESS_REVIEW_USER.value.format(
            task_history=json.dumps(task_history),
            overall_goal=overall_goal
        )
        response = self.llm.generate_structured_response(system_prompt, user_prompt)
        
        progress_review = ProgressReview(**response)
        return progress_review.dict()

class ResearchAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any], collaborative_memory: Dict[str, Any]):
        super().__init__(name, "Research", attributes)
        self.collaborative_memory = collaborative_memory

    def execute_task(self, task: Dict[str, Any], overall_goal: str) -> Dict[str, Any]:
        system_prompt = AgentPrompts.RESEARCH_TASK_SYSTEM.value
        user_prompt = AgentPrompts.RESEARCH_TASK_USER.value.format(
            task=task['task_description'],
            context=self.get_relevant_context(task['task_description']),
            goal=overall_goal
        )
        response = self.llm.generate_response(system_prompt, user_prompt, tools=TOOL_DEFINITIONS)
        result = self.handle_tool_call(response, task)
        
        if isinstance(result, str):
            result = {'content': result}
        
        self.collaborative_memory[f"research_task_{task['id']}"] = result
        return result

class DebugAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any], collaborative_memory: Dict[str, Any]):
        super().__init__(name, "Debug", attributes)
        self.collaborative_memory = collaborative_memory

    def execute_task(self, task: Dict[str, Any], overall_goal: str) -> Dict[str, Any]:
        system_prompt = AgentPrompts.DEBUG_TASK_SYSTEM.value
        user_prompt = AgentPrompts.DEBUG_TASK_USER.value.format(
            task=task['task_description'],
            context=self.get_relevant_context(task['task_description']),
            goal=overall_goal
        )
        response = self.llm.generate_response(system_prompt, user_prompt, tools=TOOL_DEFINITIONS)
        result = self.handle_tool_call(response, task)
        
        if isinstance(result, str):
            result = {'content': result}
        
        self.collaborative_memory[f"debug_task_{task['id']}"] = result
        return result

class OptimizationAgent(Agent):
    def __init__(self, name: str, attributes: Dict[str, Any], collaborative_memory: Dict[str, Any]):
        super().__init__(name, "Optimization", attributes)
        self.collaborative_memory = collaborative_memory

    def execute_task(self, task: Dict[str, Any], overall_goal: str) -> Dict[str, Any]:
        system_prompt = AgentPrompts.OPTIMIZATION_TASK_SYSTEM.value
        user_prompt = AgentPrompts.OPTIMIZATION_TASK_USER.value.format(
            task=task['task_description'],
            context=self.get_relevant_context(task['task_description']),
            goal=overall_goal
        )
        response = self.llm.generate_response(system_prompt, user_prompt, tools=TOOL_DEFINITIONS)
        result = self.handle_tool_call(response, task)
        
        if isinstance(result, str):
            result = {'content': result}
        
        self.collaborative_memory[f"optimization_task_{task['id']}"] = result
        return result