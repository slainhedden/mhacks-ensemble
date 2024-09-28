import os

class FileOperations():
    def __init__(self):
        self.directory_path = "agentFiles"
        os.makedirs(self.directory_path, exist_ok=True)

    def write_file(self, data, name):
        if len(data) == 0:
            raise ValueError("Empty data: Tried to write empty data to a file")
        elif len(name) == 0:
            raise ValueError("Empty name: Tried to write data to a unnamed file")
            
        file_path = os.path.join(self.directory_path, name)
        if os.path.exists(file_path):
            raise FileExistsError("File already exists: Tried to write to an existing file")
        else:    
            with open(file_path, "w") as file:
                file.write(data)

    def read_file(self, name):
        file_path = os.path.join(self.directory_path, name)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, "r") as file:
                return file.read()
        else:
            raise FileNotFoundError("File not found: Tried to read a non-existent file")
            
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