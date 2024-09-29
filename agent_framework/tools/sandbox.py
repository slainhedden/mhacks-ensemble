import subprocess
import os

def run_python_file(file_path: str, is_unit_test: bool = False) -> dict:
    """
    Run a Python file, either as a unit test or as a standard script.
    
    Args:
    file_path (str): Path to the Python file to be run.
    is_unit_test (bool): Flag to indicate if the file should be run as a unit test.
    
    Returns:
    dict: A dictionary containing the execution results, including return code, output, and errors.
    """
    try:
        # Ensure the file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Prepare the command
        if is_unit_test:
            command = ["python", "-m", "unittest", file_path]
        else:
            command = ["python", file_path]

        # Run the file
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30  # Set a timeout to prevent infinite loops
        )

        return {
            "return_code": result.returncode,
            "output": result.stdout,
            "errors": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {
            "return_code": -1,
            "output": "",
            "errors": "Execution timed out after 30 seconds."
        }
    except Exception as e:
        return {
            "return_code": -1,
            "output": "",
            "errors": f"An error occurred while running the file: {str(e)}"
        }

# Example usage
if __name__ == "__main__":
    file_path = "tools/testing/test.py"
    
    # Run as a unit test
    result = run_python_file(file_path, is_unit_test=True)
    print("Unit Test Results:")
    print(f"Return Code: {result['return_code']}")
    print(f"Output:\n{result['output']}")
    print(f"Errors:\n{result['errors']}")

    # Run as a standard script
    result = run_python_file(file_path)
    print("\nStandard Script Results:")
    print(f"Return Code: {result['return_code']}")
    print(f"Output:\n{result['output']}")
    print(f"Errors:\n{result['errors']}")
