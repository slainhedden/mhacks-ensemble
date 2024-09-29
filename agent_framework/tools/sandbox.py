import subprocess
import os
import tempfile
import sys

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

def run_c_code(file_path: str, is_unit_test: bool = False) -> dict:
    """
    Run a C code file, either as a unit test or as a standard script.

    Args:
        file_path (str): Path to the C file to be run.
        is_unit_test (bool): Flag to indicate if the file should be run as a unit test.

    Returns:
        dict: A dictionary containing the execution results, including return code, output, and errors.
    """
    binary_name = ""
    try:
        # Ensure the file exists
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Prepare the compilation command
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            binary_name = tmp_file.name

        is_windows = sys.platform.startswith('win')
        if is_windows:
            binary_name += ".exe"

        compile_command = ["gcc", "-Wall", "-O2", "-o", binary_name, file_path]
        run_command = [binary_name]  # Use the absolute path directly

        # Compile the code
        compile_result = subprocess.run(
            compile_command,
            capture_output=True,
            text=True,
            timeout=30
        )

        if compile_result.returncode != 0:
            return {
                "return_code": compile_result.returncode,
                "output": "",
                "errors": compile_result.stderr
            }

        # Make the binary executable (Unix systems)
        if not is_windows:
            os.chmod(binary_name, 0o755)

        # Run the compiled binary
        run_result = subprocess.run(
            run_command,
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "return_code": run_result.returncode,
            "output": run_result.stdout,
            "errors": run_result.stderr
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
            "errors": f"An error occurred: {str(e)}"
        }
    finally:
        if binary_name and os.path.exists(binary_name):
            try:
                os.remove(binary_name)
            except Exception as e:
                pass  # Optionally log the error


def run_cpp_code(file_name: str, is_unit_test: bool = False) -> dict:
    """
    Compile and run a C++ code file, either as a unit test or as a standard script.

    Args:
        file_name (str): Path to the C++ file to be compiled and run.
        is_unit_test (bool): Flag to indicate if the file should be run as a unit test.

    Returns:
        dict: A dictionary containing the execution results, including return code, output, and errors.
    """
    binary_name = ""
    try:
        if not os.path.isfile(file_name):
            raise FileNotFoundError(f"File not found: {file_name}")

        # Create a unique temporary file for the binary
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            binary_name = tmp_file.name

        is_windows = sys.platform.startswith('win')
        if is_windows:
            binary_name += ".exe"

        # Prepare the compilation command
        compile_command = ["g++", "-Wall", "-O2", "-std=c++17", "-o", binary_name, file_name]
        if is_unit_test:
            # Add any unit test specific flags or libraries here
            compile_command.append("-DUNIT_TEST")

        # Compile the code
        compile_result = subprocess.run(
            compile_command,
            capture_output=True,
            text=True,
            timeout=30
        )

        if compile_result.returncode != 0:
            return {
                "return_code": compile_result.returncode,
                "output": compile_result.stdout,
                "errors": compile_result.stderr
            }

        # Make the binary executable (Unix systems)
        if not is_windows:
            os.chmod(binary_name, 0o755)

        # Prepare the run command
        run_command = [binary_name]  # Use the absolute path directly

        # Run the compiled binary
        run_result = subprocess.run(
            run_command,
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "return_code": run_result.returncode,
            "output": run_result.stdout,
            "errors": run_result.stderr
        }
    except subprocess.TimeoutExpired as e:
        return {
            "return_code": -1,
            "output": e.stdout or "",
            "errors": "Execution timed out after 30 seconds."
        }
    except Exception as e:
        return {
            "return_code": -1,
            "output": "",
            "errors": f"An error occurred: {str(e)}"
        }
    finally:
        if binary_name and os.path.exists(binary_name):
            try:
                os.remove(binary_name)
            except Exception:
                pass  # Optionally log the error

def run_java_code(file_name: str, is_unit_test: bool = False) -> dict:
    """
    Compile and run a Java code file, either as a unit test or as a standard script.
    
    Args:
        file_name (str): Path to the Java file to be compiled and run.
        is_unit_test (bool): Flag to indicate if the file should be run as a unit test.
    
    Returns:
        dict: A dictionary containing the execution results, including return code, output, and errors.
    """
    # Initialize class_name and package_name
    class_name = os.path.splitext(os.path.basename(file_name))[0]
    package_name = ""
    
    try:
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"File not found: {file_name}")

        # Read the source file to check for package declaration
        with open(file_name, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line.startswith('package '):
                    # Extract package name
                    package_line = stripped_line[len('package '):].strip(';').strip()
                    package_name = package_line
                    break
                elif stripped_line.startswith('public class'):
                    # No package declaration found
                    break

        # Prepare the compilation command
        compile_command = ["javac"]
        if is_unit_test:
            # Include any unit test specific compile options here
            pass  # e.g., set classpath to include testing libraries

        compile_command.append(file_name)

        # Compile the Java code
        compile_result = subprocess.run(
            compile_command,
            capture_output=True,
            text=True,
            timeout=30
        )

        if compile_result.returncode != 0:
            return {
                "return_code": compile_result.returncode,
                "output": compile_result.stdout,
                "errors": compile_result.stderr
            }

        # Prepare the fully qualified class name
        if package_name:
            full_class_name = f"{package_name}.{class_name}"
        else:
            full_class_name = class_name

        # Prepare the run command
        run_command = ["java"]
        if is_unit_test:
            # Include any unit test specific run options here
            pass  # e.g., set classpath to include testing libraries

        run_command.append(full_class_name)

        # Run the Java program
        run_result = subprocess.run(
            run_command,
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            "return_code": run_result.returncode,
            "output": run_result.stdout,
            "errors": run_result.stderr
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
    finally:
        # Clean up compiled .class files
        # Handle package directories if necessary
        class_file_path = os.path.join(*package_name.split('.'), f"{class_name}.class") if package_name else f"{class_name}.class"
        try:
            if os.path.exists(class_file_path):
                os.remove(class_file_path)
        except Exception as cleanup_error:
            pass  # Optionally log cleanup errors


# Example usage
if __name__ == "__main__":
    # file_path = "tools/testing/test.py"
    
    # # Run as a unit test
    # result = run_python_file(file_path, is_unit_test=True)
    # print("Unit Test Results:")
    # print(f"Return Code: {result['return_code']}")
    # print(f"Output:\n{result['output']}")
    # print(f"Errors:\n{result['errors']}")

    # # Run as a standard script
    # result = run_python_file(file_path)
    # print("\nStandard Script Results:")
    # print(f"Return Code: {result['return_code']}")
    # print(f"Output:\n{result['output']}")
    # print(f"Errors:\n{result['errors']}")
    # Call the run_c_code function
    result = run_c_code('hello.c', False)

    # Check the result and print output or errors
    if result['return_code'] == 0:
        print("C Program Output:\n", result['output'])
    else:
        print("C Program Errors:\n", result['errors'])

