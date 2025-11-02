# src/project_managment/manager.py
import os
import platform
import subprocess
import json
from typing import Dict, Any, Tuple

from src.config import settings
from src.project_managment.file_ops import load_json_data, save_json_data, copy_file
from src.data_conversion.json_builder import create_initial_json
from src.pdf_generation.generator import generate
from src.data_conversion.ankieta_ods import parse_ankieta_ewaluacyjna


class ProjectManager:
    """Handles all non-GUI logic for a training project directory."""

    def __init__(self):
        self.directory: str | None = None

    def set_project_directory(self, path: str):
        """Sets the current working directory for the project."""
        if not os.path.isdir(path):
            raise FileNotFoundError(f"Directory not found: {path}")
        self.directory = path

    def load_project_data(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Loads data.json and data.json.old from the current directory."""
        if not self.directory:
            return {}, {}

        json_path = os.path.join(self.directory, settings.DATA_FILENAME)
        compare_path = os.path.join(self.directory, settings.DATA_COMPARE_FILENAME)

        data = load_json_data(json_path) or {}
        data_compare = load_json_data(compare_path) or {}
        
        return data, data_compare

    def save_project_data(self, data: Dict[str, Any], save_as_compare: bool = False) -> bool:
        """Saves the given data dictionary to data.json."""
        if not self.directory:
            return False
            
        json_path = os.path.join(self.directory, settings.DATA_FILENAME)
        success = save_json_data(data, json_path)
        
        if save_as_compare:
            compare_path = os.path.join(self.directory, settings.DATA_COMPARE_FILENAME)
            success = save_json_data(data, compare_path) and success
            
        return success

    def open_explorer(self):
        """Open the system's file explorer in the given directory."""
        path = self.directory
        path = os.path.abspath(path)

        if not os.path.isdir(path):
            raise ValueError(f"Path does not exist or is not a directory: {path}")

        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(path)  # native and simple
            elif system == "Darwin":
                subprocess.Popen(["open", path])  # macOS
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            print(f"Could not open file explorer: {e}")

    def ankieta_work(self, source_ods_path: str) -> bool:
        """
        Initializes a project from an ODS file: copies it, creates a new
        data.json, and returns the newly loaded data.
        """
        if not self.directory:
            raise ValueError("Project directory not set.")

        archive_dir = os.path.join(self.directory, settings.ARCHIVE_SUBDIR)
        os.makedirs(archive_dir, exist_ok=True)
        
        destination_path = os.path.join(archive_dir, settings.ANKIETA_EWALUACYJNA_FILENAME)
        
        if not copy_file(source_ods_path, destination_path):
            # Failed to copy, return existing data
            print("Something went wrong")

        # Create new json from the copied ODS
        json_path = os.path.join(self.directory, settings.ANKIETA_EWALUACYJNA_OUTPUT)
        # create_initial_json(destination_path, json_path)
        parse_ankieta_ewaluacyjna(destination_path, json_path)
        
        # Load and return the newly created data
        return True
    
    def initialize_from_ods(self, source_ods_path: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Initializes a project from an ODS file: copies it, creates a new
        data.json, and returns the newly loaded data.
        """
        if not self.directory:
            raise ValueError("Project directory not set.")

        archive_dir = os.path.join(self.directory, settings.ARCHIVE_SUBDIR)
        os.makedirs(archive_dir, exist_ok=True)
        
        destination_path = os.path.join(archive_dir, settings.LISTA_OBECNOSCI_FILENAME)
        
        if not copy_file(source_ods_path, destination_path):
            # Failed to copy, return existing data
            return self.load_project_data()

        # Create new json from the copied ODS
        json_path = os.path.join(self.directory, settings.DATA_FILENAME)
        create_initial_json(destination_path, json_path)
        
        # Load and return the newly created data
        return self.load_project_data()
        
    def run_generation(self, data: Dict[str, Any], force: bool = False) -> Dict[str, Any]:
        """
        Runs the PDF generator and saves the updated data file with new timestamps.
        """
        if not self.directory:
            raise ValueError("Project directory not set.")

        updated_data = generate(
            data_json=data,
            output_dir=self.directory,
            force=force
        )

        # Save the data back to file if timestamps were added/changed
        # if updated_data != data:
        #     self.save_project_data(updated_data)

        # return updated_data
