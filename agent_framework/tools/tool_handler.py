import json
import logging
from typing import Dict, Any, Tuple
from .file_ops import FileOperations
from .sandbox import run_python_file

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ToolHandler:
    def __init__(self):
        self.file_ops = FileOperations()

    def handle_tool_call(self, function_call: Dict[str, Any], task_id: int) -> Tuple[str, bool]:
        tool_name = function_call["name"]
        logger.info(f"Handling tool call: {tool_name} for task {task_id}")
        
        try:
            args = json.loads(function_call["arguments"])
            logger.debug(f"Tool arguments: {json.dumps(args, indent=2)}")
        except json.JSONDecodeError:
            error_msg = f"Error: Invalid JSON in function arguments for task {task_id}"
            logger.error(error_msg)
            return error_msg, False

        if tool_name == "write_file":
            return self._handle_write_file(args, task_id)
        elif tool_name == "read_file":
            return self._handle_read_file(args, task_id)
        elif tool_name == "read_codebase":
            return self._handle_read_codebase(task_id)
        elif tool_name == "mark_task_complete":
            return self._handle_mark_task_complete(args, task_id)
        elif tool_name == "run_python_file":
            return self._handle_run_python_file(args, task_id)
        else:
            error_msg = f"Unknown function call: {tool_name} for task {task_id}"
            logger.error(error_msg)
            return error_msg, False

    def _handle_write_file(self, args: Dict[str, Any], task_id: int) -> Tuple[str, bool]:
        try:
            result = self.file_ops.write_file(args["is_project_file"], args["content"], args["filename"])
            logger.info(f"File written successfully: {args['filename']}")
            return result, True
        except KeyError as e:
            error_msg = f"Error: Missing key {str(e)} in function arguments for task {task_id}"
            logger.error(error_msg)
            return error_msg, False
        except Exception as e:
            error_msg = f"Error creating file for task {task_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg, False

    def _handle_read_file(self, args: Dict[str, Any], task_id: int) -> Tuple[str, bool]:
        try:
            content = self.file_ops.read_file(args["is_project_file"], args["filename"])
            return f"Content of file '{args['filename']}': {content}", True
        except KeyError as e:
            error_msg = f"Error: Missing key {str(e)} in function arguments for task {task_id}"
            logger.error(error_msg)
            return error_msg, False
        except Exception as e:
            error_msg = f"Error reading file for task {task_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg, False

    def _handle_read_codebase(self, task_id: int) -> Tuple[str, bool]:
        try:
            codebase = self.file_ops.read_codebase()
            codebase_data = json.loads(codebase)
            if codebase_data.get("status") == "empty":
                return codebase_data["message"], True
            return f"Codebase structure: {json.dumps(codebase_data, indent=2)}", True
        except Exception as e:
            error_msg = f"Error reading codebase for task {task_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg, False

    def _handle_mark_task_complete(self, args: Dict[str, Any], task_id: int) -> Tuple[str, bool]:
        try:
            completed_task_id = args["task_id"]
            summary = args["summary"]
            return f"Task {completed_task_id} marked as complete. Summary: {summary}", True
        except KeyError as e:
            error_msg = f"Error: Missing key {str(e)} in function arguments for task {task_id}"
            logger.error(error_msg)
            return error_msg, False
        except Exception as e:
            error_msg = f"Error marking task as complete for task {task_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg, False

    def _handle_run_python_file(self, args: Dict[str, Any], task_id: int) -> Tuple[str, bool]:
        try:
            file_path = args["file_path"]
            is_unit_test = args["is_unit_test"]

            # Run the Python file
            result = run_python_file(file_path, is_unit_test)
            
            # Analyze the result
            success = result["return_code"] == 0
            output = f"Execution result:\nReturn Code: {result['return_code']}\nOutput: {result['output']}\nErrors: {result['errors']}"
            
            return output, success
        except KeyError as e:
            error_msg = f"Error: Missing key {str(e)} in function arguments for task {task_id}"
            logger.error(error_msg)
            return error_msg, False
        except Exception as e:
            error_msg = f"Error running Python file for task {task_id}: {str(e)}"
            logger.error(error_msg)
            return error_msg, False
