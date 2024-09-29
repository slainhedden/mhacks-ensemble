import json
from typing import List, Dict, Any

class ContextManager:
    def __init__(self):
        self.context = []

    def add_entry(self, entry):
        self.context.append(entry)

    def get_context(self):
        return "\n".join(str(entry) for entry in self.context)

    def get_relevant_context(self, task_description):
        # Implement relevance filtering logic here
        return self.get_context()