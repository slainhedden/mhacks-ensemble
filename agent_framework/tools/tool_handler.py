import json
import logging
from typing import Dict, Any, Tuple
from utils.project_context import ProjectContext
from .sandbox import run_python_file
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ToolHandler:
    def __init__(self):
        self.project_context = ProjectContext()
        logger.info(f"ToolHandler initialized with ProjectContext base_dir: {self.project_context.base_dir}")

    def handle_tool_call(self, function_call: Dict[str, Any], task_description: str) -> Tuple[str, bool]:
        tool_name = function_call["name"]
        logger.info(f"Handling tool call: {tool_name} for task: {task_description}")
        
        try:
            args = json.loads(function_call["arguments"])
            logger.debug(f"Tool arguments: {json.dumps(args, indent=2)}")
        except json.JSONDecodeError:
            error_msg = f"Error: Invalid JSON in function arguments for task: {task_description}"
            logger.error(error_msg)
            return error_msg, False

        try:
            if tool_name == "write_file":
                return self._handle_write_file(args), True
            elif tool_name == "read_file":
                return self._handle_read_file(args), True
            elif tool_name == "append_file":
                return self._handle_append_file(args), True
            elif tool_name == "delete_file":
                return self._handle_delete_file(args), True
            elif tool_name == "create_directory":
                return self._handle_create_directory(args), True
            elif tool_name == "delete_directory":
                return self._handle_delete_directory(args), True
            elif tool_name == "list_directory":
                return self._handle_list_directory(args), True
            elif tool_name == "set_current_directory":
                return self._handle_set_current_directory(args), True
            elif tool_name == "get_project_structure":
                logger.warning("get_project_structure called. Consider creating or modifying files instead.")
                return self._handle_get_project_structure(), True
            elif tool_name == "run_python_file":
                return self._handle_run_python_file(args)
            else:
                error_msg = f"Unknown function call: {tool_name} for task: {task_description}"
                logger.error(error_msg)
                return error_msg, False
        except Exception as e:
            error_msg = f"Error executing {tool_name} for task: {task_description}: {str(e)}"
            logger.error(error_msg)
            return error_msg, False

    def _handle_write_file(self, args: Dict[str, Any]) -> str:
        file_path = args["file_path"]
        content = args["content"]
        self.project_context.write_file(file_path, content)
        logger.info(f"File written: {file_path}")
        return f"File written successfully: {file_path}"

    def _handle_read_file(self, args: Dict[str, Any]) -> str:
        content = self.project_context.read_file(args["file_path"])
        return f"Content of file '{args['file_path']}': {content}"

    def _handle_append_file(self, args: Dict[str, Any]) -> str:
        self.project_context.append_file(args["file_path"], args["content"])
        return f"Content appended successfully to file: {args['file_path']}"

    def _handle_delete_file(self, args: Dict[str, Any]) -> str:
        self.project_context.delete_file(args["file_path"])
        return f"File deleted successfully: {args['file_path']}"

    def _handle_create_directory(self, args: Dict[str, Any]) -> str:
        self.project_context.create_directory(args["dir_path"])
        return f"Directory created successfully: {args['dir_path']}"

    def _handle_delete_directory(self, args: Dict[str, Any]) -> str:
        self.project_context.delete_directory(args["dir_path"])
        return f"Directory deleted successfully: {args['dir_path']}"

    def _handle_list_directory(self, args: Dict[str, Any]) -> str:
        files = self.project_context.list_directory(args.get("dir_path", "."))
        return f"Directory contents: {', '.join(files)}"

    def _handle_set_current_directory(self, args: Dict[str, Any]) -> str:
        self.project_context.set_current_directory(args["dir_path"])
        return f"Current directory set to: {self.project_context.get_current_directory()}"

    def _handle_get_project_structure(self) -> str:
        return self.project_context.to_json()

    def _handle_run_python_file(self, args: Dict[str, Any]) -> Tuple[str, bool]:
        file_path = os.path.join(self.project_context.current_dir, args["file_path"])
        result = run_python_file(file_path, args.get("is_unit_test", False))
        success = result["return_code"] == 0
        output = f"Execution result:\nReturn Code: {result['return_code']}\nOutput: {result['output']}\nErrors: {result['errors']}"
        return output, success