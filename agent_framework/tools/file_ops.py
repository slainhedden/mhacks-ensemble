import os
import json

class FileOperations():
    def __init__(self):
        self.directory_path = "agentFiles"
        self.project_folder = os.path.join(self.directory_path, "src")
        os.makedirs(self.directory_path, exist_ok=True)
        os.makedirs(self.project_folder, exist_ok=True)

    def write_file(self, is_project_file: bool, content: str, filename: str) -> str:
        if not content:
            raise ValueError("Empty content: Tried to write empty content to a file")
        if not filename:
            raise ValueError("Empty filename: Tried to write content to an unnamed file")
        
        file_path = os.path.join(self.project_folder, filename) if is_project_file else os.path.join(self.directory_path, filename)
        try:
            with open(file_path, "w") as file:
                file.write(content)
            return f"File '{filename}' created successfully in {'src' if is_project_file else self.directory_path}"
        except Exception as e:
            return f"Error creating file '{filename}': {str(e)}"
    
    # def create_folder(self, folder_name: str) -> str:
    #     if not folder_name:
    #         raise ValueError("Empty folder name: Tried to create a folder with an empty name")
        
    #     folder_path = os.path.join(self.directory_path, folder_name)
    #     try:
    #         os.makedirs(folder_path, exist_ok=True)
    #         return f"Folder '{folder_name}' created successfully in {self.directory_path}"
    #     except Exception as e:
    #         return f"Error creating folder '{folder_name}': {str(e)}"

    def read_codebase(self):
        codebase_structure = {}
        for root, dirs, files in os.walk(self.project_folder):
            relative_path = os.path.relpath(root, self.project_folder)
            if relative_path == '.':
                codebase_structure['src'] = {}
                current_level = codebase_structure['src']
            else:
                current_level = codebase_structure['src']
                for folder in relative_path.split(os.sep):
                    if folder not in current_level:
                        current_level[folder] = {}
                    current_level = current_level[folder]
            
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'r') as f:
                    content = f.read()
                current_level[file] = {
                    'content': content,
                    'path': os.path.relpath(file_path, self.project_folder)
                }
        
        if not codebase_structure.get('src'):
            return json.dumps({"status": "empty", "message": "The codebase is currently empty. You may need to use the write_file function to create the file."})
        
        return json.dumps(codebase_structure)

    def read_file(self, is_project_file: bool, filename: str) -> str:
        file_path = os.path.join(self.project_folder if is_project_file else self.directory_path, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "r") as file:
                return file.read()
        else:
            return f"File not found: {filename}"

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