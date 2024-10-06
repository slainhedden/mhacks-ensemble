from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal

class Agent(BaseModel):
    name: str
    type: str
    attributes: Optional[Dict[str, Any]] = None

class Task(BaseModel):
    task_description: str
    estimated_complexity: Literal["Low", "Medium", "High"]
    file_path: str
    completed: Optional[bool] = None
    assigned_agent: Optional[str] = None

class AgentResponse(BaseModel):
    content: Optional[str] = None
    tool: Optional[str] = None
    tool_input: Optional[Dict[str, Any]] = None

class ReviewResult(BaseModel):
    approved: bool
    feedback: str

class ProgressReview(BaseModel):
    progress: str
    missing: str
    next_steps: str

class AgentList(BaseModel):
    agents: List[Agent]

class TaskList(BaseModel):
    tasks: List[Task]

class TaskAssignment(BaseModel):
    task_description: str
    assigned_agent: str

class TaskAssignmentList(BaseModel):
    assignments: List[TaskAssignment]

class TaskReview(BaseModel):
    approved: bool
    feedback: str