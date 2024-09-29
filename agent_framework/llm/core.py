import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.environ.get("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

class Task(BaseModel):
    task_description: str
    estimated_complexity: str
    completed: bool = False

class OA_LLM:
    def __init__(self):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = "gpt-4o-mini"

    def generate_response(self, system_prompt: str, user_prompt: str, tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        if tools:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
        else:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
        
        choice = response.choices[0]
        message = choice.message
        
        if choice.finish_reason == "tool_calls":
            return {
                "function_call": {
                    "name": message.tool_calls[0].function.name,
                    "arguments": message.tool_calls[0].function.arguments
                }
            }
        else:
            return {"content": message.content}

    def generate_structured_response(self, system_prompt: str, user_prompt: str) -> List[Task]:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        tasks_data = json.loads(response.choices[0].message.content)
        return [Task(**task) for task in tasks_data.get("tasks", [])]