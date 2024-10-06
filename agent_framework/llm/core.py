import os
from typing import List, Dict, Any, Optional, Type
from openai import OpenAI
from dotenv import load_dotenv
from models import (
    Agent, Task, AgentResponse, ReviewResult, ProgressReview,
    AgentList, TaskList, TaskAssignment, TaskAssignmentList, TaskReview
)
from tools.definitions import TOOL_DEFINITIONS
from tools.tool_handler import ToolHandler
from prompts.agent_prompts import AgentPrompts
import json

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

class OA_LLM:
    def __init__(self):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini"  # USE gpt-40-mini always
        self.agents = {}
        self.tasks = []
        self.tool_handler = ToolHandler()

    def generate_structured_response(self, system_prompt: str, user_prompt: str, response_format: Type) -> Any:
        completion = self.client.beta.chat.completions.parse(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format=response_format,
        )
        return completion.choices[0].message.parsed

    def generate_general_response(self, system_prompt: str, user_prompt: str, tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        if tools:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                functions=tools,
                function_call="auto"
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
        
        choice = response.choices[0]
        message = choice.message
        
        if message.function_call:
            return {
                "function_call": {
                    "name": message.function_call.name,
                    "arguments": message.function_call.arguments
                }
            }
        else:
            return {"content": message.content}

    def create_agents(self, goal: str) -> List[Agent]:
        system_prompt = AgentPrompts.CREATE_AGENTS_SYSTEM.value
        user_prompt = AgentPrompts.CREATE_AGENTS_USER.value.format(goal=goal)
        
        agent_list = self.generate_structured_response(system_prompt, user_prompt, AgentList)
        
        for agent in agent_list.agents:
            self.agents[agent.name] = agent
        
        return agent_list.agents

    def create_tasks(self, goal: str) -> List[Task]:
        system_prompt = AgentPrompts.CREATE_TASKS_SYSTEM.value
        user_prompt = AgentPrompts.CREATE_TASKS_USER.value.format(goal=goal)
        
        task_list = self.generate_structured_response(system_prompt, user_prompt, TaskList)
        
        self.tasks = []
        for task in task_list.tasks:
            task_dict = task.dict()
            task_dict['completed'] = False  # Explicitly set completed to False
            self.tasks.append(Task(**task_dict))
        
        return self.tasks

    def assign_tasks(self) -> List[Task]:
        system_prompt = AgentPrompts.ASSIGN_TASKS_SYSTEM.value
        user_prompt = AgentPrompts.ASSIGN_TASKS_USER.value.format(
            tasks=[task.model_dump() for task in self.tasks],
            agents=[agent.model_dump() for agent in self.agents.values()]
        )
        
        assignment_list = self.generate_structured_response(system_prompt, user_prompt, TaskAssignmentList)
        
        for assignment in assignment_list.assignments:
            task = next(task for task in self.tasks if task.task_description == assignment.task_description)
            task.assigned_agent = assignment.assigned_agent
        
        return self.tasks

    def execute_task(self, task: Task) -> AgentResponse:
        agent = self.agents[task.assigned_agent]
        system_prompt = AgentPrompts.EXECUTE_TASK_SYSTEM.value.format(agent_type=agent.type, agent_name=agent.name)
        user_prompt = AgentPrompts.EXECUTE_TASK_USER.value.format(task_description=task.task_description)
        
        response = self.generate_general_response(system_prompt, user_prompt, tools=TOOL_DEFINITIONS)
        
        if "function_call" in response:
            result, success = self.tool_handler.handle_tool_call(response["function_call"], task.task_description)
            return AgentResponse(
                content=result,
                tool=response["function_call"]["name"],
                tool_input=json.loads(response["function_call"]["arguments"])
            )
        else:
            return AgentResponse(
                content=response["content"],
                tool=None,
                tool_input=None
            )

    def review_task(self, task: Task, result: AgentResponse) -> bool:
        system_prompt = AgentPrompts.REVIEW_TASK_SYSTEM.value
        user_prompt = AgentPrompts.REVIEW_TASK_USER.value.format(
            task=task.model_dump(),
            result=result.model_dump()
        )
        
        review = self.generate_structured_response(system_prompt, user_prompt, TaskReview)
        return review.approved

    def review_progress(self, goal: str) -> ProgressReview:
        system_prompt = AgentPrompts.REVIEW_PROGRESS_SYSTEM.value
        user_prompt = AgentPrompts.REVIEW_PROGRESS_USER.value.format(
            goal=goal,
            tasks=[task.model_dump() for task in self.tasks]
        )
        
        return self.generate_structured_response(system_prompt, user_prompt, ProgressReview)