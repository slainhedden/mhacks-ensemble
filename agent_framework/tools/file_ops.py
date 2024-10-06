import os
import json

class FileOperations():
    def __init__(self):
        self.base_dir = os.path.join(os.getcwd(), "src")
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    def write_file(self, is_project_file: bool, content: str, file_path: str) -> str:
        if is_project_file:
            full_path = file_path  # file_path is already absolute in ToolHandler
        else:
            full_path = os.path.join(self.base_dir, file_path)
        
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
        return f"File written successfully: {full_path}"

    def read_file(self, is_project_file: bool, file_path: str) -> str:
        if is_project_file:
            full_path = file_path  # file_path is already absolute in ToolHandler
        else:
            full_path = os.path.join(self.base_dir, file_path)
        
        with open(full_path, 'r') as f:
            return f.read()

    def read_codebase(self) -> str:
        codebase_structure = self._get_directory_structure(self.base_dir)
        return json.dumps(codebase_structure)

    def _get_directory_structure(self, rootdir):
        structure = {}
        for root, dirs, files in os.walk(rootdir):
            relative_path = os.path.relpath(root, rootdir)
            if relative_path == ".":
                structure = {file: None for file in files}
            else:
                path = structure
                for dir in relative_path.split(os.sep):
                    path = path.setdefault(dir, {})
                path.update({file: None for file in files})
        return structure

    def append_file(self, data, name):
        if len(data) == 0:
            raise ValueError("Empty data: Tried to write empty data to a file")
        elif len(name) == 0:
            raise ValueError("Empty name: Tried to write data to a unnamed file") 

        file_path = os.path.join(self.directory_path, name)
        if os.path.exists(file_path):
            with open(os.path.join(self.directory_path, name), "a") as file:
                file.write(data)
        else:
            raise FileNotFoundError("File not found: Tried to append to a non-existent file")
    
    def list_files(self):
        return os.listdir(self.directory_path) # returns a list of all files and subdirectories

    def delete_file(self, name):
        file_path = os.path.join(self.directory_path, name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"File {name} deleted successfully")
            except OSError as e:
                print(f"Error deleting file: {e.strerror}")
        else:
            raise FileNotFoundError("File not found: Tried to delete a non-existent file")
    
    @staticmethod
    def delete_all_files(self): 
        for file in os.listdir(self.directory_path):
            file_path = os.path.join(self.directory_path, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
        print("All files deleted successfully")