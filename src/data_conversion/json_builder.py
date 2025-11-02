# src/data_conversion/json_builder.py
import json
from src.config import settings
from src.data_conversion.ods_parser import read_ods_file


def create_initial_json(ods_path: str, output_json_path: str):
    """
    Creates the initial data.json file from an ODS spreadsheet.
    """
    participants = read_ods_file(ods_path)

    data = {
        settings.KEY_PARTICIPANTS: participants,
        settings.KEY_TRAINING: {
            settings.KEY_NUMER_SZKOLENIA: "",
            settings.KEY_NAZWA_SZKOLENIA: "",
            settings.KEY_MIEJSCE_SZKOLENIA: "",
            settings.KEY_DATA_SZKOLENIA: "",
            settings.KEY_PROWADZACY: "",
            settings.KEY_CZAS_TRWANIA: "",
            settings.KEY_CZAS_TRWANIA_OD_DO: "",
            settings.KEY_TEMATYKA: "",
        },
    }

    try:
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"File created at: {output_json_path}")
    except IOError as e:
        print(f"Error writing JSON file: {e}")
