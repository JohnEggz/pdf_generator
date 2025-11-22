# src/config/settings.py
"""
Central configuration file for the application.
Contains constants, file paths, and UI definitions.
"""
from pathlib import Path
import platform
from platformdirs import user_documents_dir

# --- DIRECTORY AND FILE CONFIGURATION ---
# Use pathlib for more robust path handling
# Assuming the script runs from the project root. Adjust if needed.
PROJECT_ROOT = Path(__file__).parent.parent.parent
ASSETS_DIR = Path(__file__).parent.parent / "pdf_generation" / "assets"
# This path might need to be adjusted based on where you store data
DEFAULT_TRAINING_ROOT = f"{user_documents_dir()}/generated_certificates"

ARCHIVE_SUBDIR = "archiwum"
LISTA_OBECNOSCI_FILENAME = "lista_obecnosci.ods"
ANKIETA_EWALUACYJNA_FILENAME = "ankieta_ewaluacyjna.ods"
ANKIETA_EWALUACYJNA_OUTPUT = "ankieta_ewaluacyjna_output.txt"
SURVEY_FILENAME = "ankieta.ods"
DATA_FILENAME = "data.json"
DATA_COMPARE_FILENAME = "data.json.old"
CERTIFICATES_DIR_NAME = "certyfikaty"
LOGBOOK_FILENAME = "dziennik.pdf"
FONT_PATH = str(ASSETS_DIR / "DejaVuSans.ttf")
FONT_NAME = "DejaVuSans"
IMAGE_LOGO_PATH = str(ASSETS_DIR / "logo.png")
IMAGE_STAMP_PATH = str(ASSETS_DIR / "podpis.png")


# --- JSON DATA KEYS ---
# Participant keys
KEY_IMIE_NAZWISKO = "imie_nazwisko"
KEY_MIEJSCE_URODZENIA = "miejsce_urodzenia"
KEY_DATA_URODZENIA = "data_urodzenia"
KEY_GENERATED_TIMESTAMP = "generated"
KEY_SORTING_NAME = "sorting_name"
KEY_EMAIL = "email"
KEY_UUID = "UUID"

# Training keys
KEY_NUMER_SZKOLENIA = "numer_szkolenia"
KEY_NAZWA_SZKOLENIA = "nazwa_szkolenia"
KEY_MIEJSCE_SZKOLENIA = "miejsce_szkolenia"
KEY_DATA_SZKOLENIA = "data_szkolenia"
KEY_PROWADZACY = "prowadzacy"
KEY_CZAS_TRWANIA = "czas_trwania"
KEY_CZAS_TRWANIA_OD_DO = "czas_trwania_od_do"
KEY_DATA_WYSTAWIENIA = "data_wystawienia"
KEY_TEMATYKA = "tematyka"

# Top-level keys
KEY_TRAINING = "Szkolenie"
KEY_PARTICIPANTS = "Osoby"


# --- UI DEFINITIONS ---
# Field names for the training information form
TRAINING_FIELDS = {
    KEY_NUMER_SZKOLENIA: "Training Number (e.g., SzRP/25/1)",
    KEY_NAZWA_SZKOLENIA: "Training Name (e.g., Teacher Support)",
    KEY_MIEJSCE_SZKOLENIA: "Location (e.g., SP 34)",
    KEY_DATA_SZKOLENIA: "Date (e.g., 10.10.2025)",
    KEY_PROWADZACY: "Instructor (e.g., John Doe)",
    KEY_CZAS_TRWANIA: "Duration (e.g., 3h)",
    KEY_CZAS_TRWANIA_OD_DO: "Time Range (e.g., 17:00 - 19:00)",
    KEY_DATA_WYSTAWIENIA: "Data wystawienia zaświadczenia"
}

# Column headers and corresponding keys for the participants table
PARTICIPANT_TABLE_HEADERS = {
    KEY_IMIE_NAZWISKO: "Full Name",
    KEY_MIEJSCE_URODZENIA: "Place of Birth",
    KEY_DATA_URODZENIA: "Date of Birth",
}
