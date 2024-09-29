import json
from collections import deque
from typing import List, Dict, Any

class ContextManager:
    def __init__(self, max_entries: int = 50):
        self.context = deque(maxlen=max_entries)

    def add_entry(self, entry: Dict[str, Any]):
        self.context.append(entry)

    def get_context(self) -> str:
        return "\n".join(str(entry) for entry in self.context)

    def get_relevant_context(self, task_description: str) -> str:
        # Implement logic to return relevant context based on the task description
        # For now, we'll return the entire context
        return self.get_context()