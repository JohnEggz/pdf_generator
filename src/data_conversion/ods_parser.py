# src/data_conversion/ods_parser.py
import re
from datetime import datetime
from typing import List, Dict, Any

import ezodf
from ezodf import Table
from src.config import settings

current_year = datetime.now().year

polish_map = str.maketrans(
    "ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ"
)

convert_months = {
    "styczen": "01", "luty": "02", "marzec": "03", "kwiecien": "04",
    "maj": "05", "czerwiec": "06", "lipiec": "07", "sierpien": "08",
    "wrzesien": "09", "pazdziernik": "10", "listopad": "11", "grudzien": "12",
}


def fix_date(input_date: Any) -> str:
    """Cleans and standardizes a date string from various formats."""
    if not isinstance(input_date, str) or len(input_date) < 6:
        print(f"Invalid date input (type or length): {input_date}")
        return str(input_date)

    # --- THIS IS THE LINE TO CHANGE ---
    # OLD: parts = re.split(r"[\\-.,_\\s/]", input_date)
    # NEW: Move the hyphen to the end of the character set
    parts = re.split(r"[\\.,_\\s/-]", input_date)
    # --- END OF CHANGE ---

    # Filter out empty strings that can result from multiple delimiters
    parts = [part for part in parts if part]

    if len(parts) < 3:
        print(f"Invalid date format (not enough parts): {parts}")
        return str(input_date)

    day_str, month_str, year_str = parts[0], parts[1], parts[2]

    # Normalize month if it's a name
    translated_month = month_str.lower().translate(polish_map)
    if translated_month in convert_months:
        month_str = convert_months[translated_month]

    try:
        day = int(day_str)
        month = int(month_str)
        year = int(year_str)

        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError("Day or month out of range")
        if not (1900 < year < current_year + 2): # Allow next year
            raise ValueError("Year out of reasonable range")

        return f"{day:02d}.{month:02d}.{year} r."
    except (ValueError, TypeError) as e:
        print(f"Error parsing date parts '{day_str}-{month_str}-{year_str}': {e}")
        return str(input_date)


def read_ods_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads an ODS file, extracts participant data, and handles duplicates.
    """
    spreadsheet = ezodf.opendoc(file_path)
    if len(spreadsheet.sheets) != 1:
        raise ValueError("ODS file must contain exactly one sheet.")
    sheet = spreadsheet.sheets[0]
    if not isinstance(sheet, Table):
        raise TypeError("The sheet is not a valid table.")

    raw_participant_list = []
    for i in range(1, sheet.nrows()):
        imie_nazwisko_raw = sheet[i, 1].value
        if not imie_nazwisko_raw:
            continue

        imie_nazwisko = str(imie_nazwisko_raw).strip()
        miejsce_urodzenia_raw = sheet[i, 3].value
        miejsce_urodzenia = str(miejsce_urodzenia_raw).lower().capitalize()

        new_participant = {
            settings.KEY_IMIE_NAZWISKO: imie_nazwisko,
            settings.KEY_MIEJSCE_URODZENIA: miejsce_urodzenia,
            settings.KEY_DATA_URODZENIA: fix_date(sheet[i, 2].value),
            settings.KEY_SORTING_NAME: imie_nazwisko.lower(),
            settings.KEY_EMAIL: sheet[i, 5].value or None,
            settings.KEY_UUID: None,
            settings.KEY_GENERATED_TIMESTAMP: None,
        }
        raw_participant_list.append(new_participant)

    return _deduplicate_participants(raw_participant_list)


def _deduplicate_participants(
    participants: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Sorts and removes duplicate entries from a list of participants."""
    sorted_list = sorted(
        participants,
        key=lambda x: x.get(settings.KEY_SORTING_NAME, "").split(" ")[-1],
    )

    certain_dupes, uncertain_dupes, indices_to_skip = [], [], set()

    for i in range(1, len(sorted_list)):
        prev = sorted_list[i - 1]
        curr = sorted_list[i]
        if prev.get(settings.KEY_SORTING_NAME) == curr.get(settings.KEY_SORTING_NAME):
            if prev.get(settings.KEY_DATA_URODZENIA) == curr.get(settings.KEY_DATA_URODZENIA):
                certain_dupes.append((i - 1, i))
            else:
                uncertain_dupes.append((i - 1, i))

    for idx1, idx2 in certain_dupes:
        if sorted_list[idx1].get(settings.KEY_EMAIL):
            indices_to_skip.add(idx2)
        else:
            indices_to_skip.add(idx1)

    if uncertain_dupes:
        print(f"Warning: Found uncertain duplicates: {uncertain_dupes}")

    final_list = [p for i, p in enumerate(sorted_list) if i not in indices_to_skip]
    return final_list
