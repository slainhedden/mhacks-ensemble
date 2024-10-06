import os
import json
import shutil
from typing import List, Dict, Any

class ProjectContext:
    def __init__(self, base_dir: str = "src"):
        self.base_dir = os.path.abspath(os.path.join(os.getcwd(), base_dir))
        self.ensure_directory(self.base_dir)
        self.current_dir = self.base_dir
        print(f"ProjectContext initialized with base_dir: {self.base_dir}")  # Debug print

    def ensure_directory(self, path: str):
        os.makedirs(path, exist_ok=True)
        print(f"Ensured directory exists: {path}")  # Debug print

    def set_current_directory(self, relative_path: str):
        new_path = os.path.join(self.base_dir, relative_path)
        if os.path.isdir(new_path):
            self.current_dir = new_path
        else:
            raise ValueError(f"Invalid directory: {relative_path}")

    def get_current_directory(self) -> str:
        return os.path.relpath(self.current_dir, self.base_dir)

    def list_directory(self, path: str = ".") -> List[str]:
        full_path = os.path.join(self.current_dir, path)
        return os.listdir(full_path)

    def read_file(self, file_path: str) -> str:
        full_path = os.path.join(self.current_dir, file_path)
        with open(full_path, 'r') as f:
            return f.read()

    def write_file(self, file_path: str, content: str) -> None:
        full_path = os.path.join(self.current_dir, file_path)
        self.ensure_directory(os.path.dirname(full_path))
        with open(full_path, 'w') as f:
            f.write(content)
        print(f"File written: {full_path}")  # Debug print

    def append_file(self, file_path: str, content: str) -> None:
        full_path = os.path.join(self.current_dir, file_path)
        with open(full_path, 'a') as f:
            f.write(content)

    def delete_file(self, file_path: str) -> None:
        full_path = os.path.join(self.current_dir, file_path)
        os.remove(full_path)

    def create_directory(self, dir_path: str) -> None:
        full_path = os.path.join(self.current_dir, dir_path)
        self.ensure_directory(full_path)

    def delete_directory(self, dir_path: str) -> None:
        full_path = os.path.join(self.current_dir, dir_path)
        shutil.rmtree(full_path)

    def get_file_structure(self) -> Dict[str, Any]:
        def get_structure(path):
            structure = {}
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    structure[item] = get_structure(item_path)
                else:
                    structure[item] = None
            return structure
        return get_structure(self.base_dir)

    def to_json(self) -> str:
        return json.dumps({
            "base_dir": self.base_dir,
            "current_dir": self.get_current_directory(),
            "structure": self.get_file_structure()
        }, indent=2)