from typing import Dict, Any

'''
Purpose: Creates or overwrites a file with the specified content. Usage: Use this function to save data either as part of the project code. Should be used creating a new file or when overwriting incorrect code. 

'''


TOOL_DEFINITIONS: Dict[str, Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file in the directory for context to the other agents, or to a project file in the src folder if the file is part of the project code. Use the is_project_file boolean to determine where to write the file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "is_project_file": {
                        "type": "boolean",
                        "description": "Whether the file is in the project folder"
                    },
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to write (including extension), the file must be a valid file name and not attempt to create a folder. No file names can include a forward slash."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file"
                    }
                },
                "required": ["is_project_file", "filename", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the content of a file from either the project folder or the agent files directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "is_project_file": {
                        "type": "boolean",
                        "description": "Whether the file is in the project folder"
                    },
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to read (including extension)"
                    }
                },
                "required": ["is_project_file", "filename"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_codebase",
            "description": "Read and return the entire codebase structure including file contents from the project folder.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "mark_task_complete",
            "description": "Mark the current task as complete and update the context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to mark as complete"
                    },
                    "summary": {
                        "type": "string",
                        "description": "A brief summary of what was accomplished in the task"
                    }
                },
                "required": ["task_id", "summary"]
            }
        }
    }
]

TOOL_DEFINITIONS_REVIEWER = [
    {
        "type": "function",
        "function": 
        {
            "name": "run_python_file",
            "description": "Run a Python file in a sandbox environment, either as a unit test or as a standard script.",
            "parameters": 
            {
                "type": "object",
                "properties": 
                {
                    "file_path": 
                    {
                        "type": "string",
                        "description": "The path to the Python file to be run."
                    },
                    "is_unit_test": 
                    {
                        "type": "boolean",
                        "description": "Flag to indicate if the file should be run as a unit test."
                    }
                },
                "required": ["file_path", "is_unit_test"]
            }
        }
    }
]