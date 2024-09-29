import json
from datetime import datetime
from typing import Dict, Any, List
from llm.core import OA_LLM
from tools.file_ops import FileOperations
from tools.tool_handler import ToolHandler
from utils.context_manager import ContextManager
from utils.code_reviewer import CodeReviewer
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Agent:
    def __init__(self, name: str, role: str, attributes: dict):
        self.name = name
        self.role = role
        self.attributes = attributes
        self.context_manager = ContextManager()
        self.file_ops = FileOperations()
        self.tool_handler = ToolHandler()
        self.llm = OA_LLM()
        self.output_log = []
        self.code_reviewer = CodeReviewer()
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

    def add_context(self, entry: Dict[str, Any]):
        entry['timestamp'] = datetime.now().isoformat()
        self.context_manager.add_entry(entry)
        self.logger.info(f"Added context: {json.dumps(entry)}")

    def log_output(self, message: str):
        self.output_log.append(message)
        self.logger.info(message)

    def execute_task(self, task: Dict[str, Any], overall_goal: str) -> str:
        try:
            self.logger.info(f"Executing task: {task['task_description']}")
            # This method should be implemented by subclasses
            raise NotImplementedError("Subclasses must implement execute_task method")
        except Exception as e:
            self.logger.error(f"Error executing task: {str(e)}")
            return f"Error: {str(e)}"

    def get_context(self) -> str:
        return self.context_manager.get_context()

    def get_relevant_context(self, task_description: str) -> str:
        return self.context_manager.get_relevant_context(task_description)

    def handle_tool_call(self, response: Dict[str, Any], task: Dict[str, Any]) -> str:
        self.logger.info(f"Handling tool call for task {task['id']}")
        self.logger.debug(f"Response: {json.dumps(response, indent=2)}")
        
        if "function_call" in response:
            function_call = response["function_call"]
            self.logger.info(f"Function call detected: {function_call['name']}")
            result, success = self.tool_handler.handle_tool_call(function_call, task['id'])
            if success:
                self.add_context({"action": "tool_usage", "task": task['id'], "result": result, "tool": function_call['name']})
                self.logger.info(f"Tool call successful: {result}")
            else:
                self.logger.error(f"Tool call failed: {result}")
            return result
        elif "content" in response:
            self.logger.info("No function call, returning content")
            return response["content"]
        else:
            error_msg = "No content or function call generated"
            self.logger.error(error_msg)
            return error_msg

    def review_task(self, task: Dict[str, Any], result: str, overall_goal: str) -> Dict[str, Any]:
        # This method should be implemented by the ReviewAgent subclass
        raise NotImplementedError("ReviewAgent must implement review_task method")