from typing import Dict, List, Any

'''
Purpose: Creates or overwrites a file with the specified content. Usage: Use this function to save data either as part of the project code. Should be used creating a new file or when overwriting incorrect code. 
'''

TOOL_DEFINITIONS = [
    {
        "name": "write_file",
        "description": "Write content to a file in the project",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path of the file to write to, relative to the current directory"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "read_file",
        "description": "Read content from a file in the project",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path of the file to read from, relative to the current directory"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "append_file",
        "description": "Append content to a file in the project",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path of the file to append to, relative to the current directory"
                },
                "content": {
                    "type": "string",
                    "description": "The content to append to the file"
                }
            },
            "required": ["file_path", "content"]
        }
    },
    {
        "name": "delete_file",
        "description": "Delete a file from the project",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path of the file to delete, relative to the current directory"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "create_directory",
        "description": "Create a new directory in the project",
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": "The path of the directory to create, relative to the current directory"
                }
            },
            "required": ["dir_path"]
        }
    },
    {
        "name": "delete_directory",
        "description": "Delete a directory from the project",
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": "The path of the directory to delete, relative to the current directory"
                }
            },
            "required": ["dir_path"]
        }
    },
    {
        "name": "list_directory",
        "description": "List the contents of a directory",
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": "The path of the directory to list, relative to the current directory"
                }
            },
            "required": ["dir_path"]
        }
    },
    {
        "name": "set_current_directory",
        "description": "Set the current working directory",
        "parameters": {
            "type": "object",
            "properties": {
                "dir_path": {
                    "type": "string",
                    "description": "The path to set as the current directory, relative to the project root"
                }
            },
            "required": ["dir_path"]
        }
    },
    {
        "name": "get_project_structure",
        "description": "Get the current project structure and working directory",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "run_python_file",
        "description": "Run a Python file in the project",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "The path of the Python file to execute, relative to the current directory"
                },
                "is_unit_test": {
                    "type": "boolean",
                    "description": "Set to true if this is a unit test file",
                    "default": False
                }
            },
            "required": ["file_path"]
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