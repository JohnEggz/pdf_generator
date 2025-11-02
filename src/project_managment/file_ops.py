# src/project_managment/file_ops.py
import os
import shutil
import json
from typing import Optional, Dict, Any

def copy_file(source_path: str, destination_path: str) -> bool:
    """Copies a file from source to destination."""
    try:
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        shutil.copy2(source_path, destination_path)
        print(f"Copied '{source_path}' to '{destination_path}'")
        return True
    except Exception as e:
        print(f"Error copying file: {e}")
        return False

def load_json_data(file_path: str) -> Optional[Dict[str, Any]]:
    """Loads and parses a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Could not load or parse {os.path.basename(file_path)}: {e}")
        return None

def save_json_data(data: Dict[str, Any], file_path: str) -> bool:
    """Saves a dictionary to a JSON file."""
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data successfully saved to {file_path}")
        return True
    except IOError as e:
        print(f"Error saving data to {file_path}: {e}")
        return False
