import os
from typing import List
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
    completed: bool = False

class OA_LLM:
    def __init__(self):
        self.client = OpenAI(api_key=openai_api_key)

    def generate_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    
    def generate_structured_response(self, system_prompt: str, user_prompt: str) -> List[Task]:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        tasks_data = json.loads(response.choices[0].message.content)
        return [Task(**task) for task in tasks_data.get("tasks", [])]