import ezodf
from statistics import mean
from collections import Counter
import os # Import os for potential path manipulation, though not strictly needed here

ods_path = "/home/john/Projects/Work/Pyhton/pdf_generator_for_mom_2_1/Ankieta ewaluacyjna_ZSP11_ Opracowanie dokumencji_ IPET, WOPFU (O.ods"

keys_average = (
    "Tematyka szkolenia dostosowana została do zgłoszonych potrzeb (1 - najniższa ocena, 5 najwyższa ocena):"
    "Czas trwania zajęć dostosowany był do potrzeb uczestników (1 - najniższa ocena, 5 najwyższa ocena):"
    "Na ile ocenia Pan/Pani przygotowanie merytoryczne trenera / edukatora (1 - najniższa ocena, 5 najwyższa ocena):"
    "Na ile trener zrealizował cele szkolenia (1 - najniższa ocena, 5 najwyższa ocena): "
    "Jak ocenia Pan / Pani sposób prowadzenia zajęć przez trenera / edukatora (1 - najniższa ocena, 5 najwyższa ocena): "
    "Na ile trener / edukator odpowiadał na potrzeby zgłaszane przez uczestników   (1 - najniższa ocena, 5 najwyższa ocena): "
)
key_lista = "Dodatkowe uwagi dla trenera/ edukatora lub placówki"
key_tak_nie = "Czy polecił/a by Pan/Pani kurs innym?"
key_sorting = "Jakie inne szkolenia byłyby interesujące dla Pana/ Pani w przyszłości - można zaznaczyć kilka odpowiedzi:"

multi_choice_key = [
    "Wsparcie dziecka o SPE: spektrum autyzmu, afazja, niepełnosprawność intelektualna",
    "Wsparcie dziecka o SPE: dysleksja, dysgrafia, dysortografia, dyskalkulia",
    "Wsparcie dziecka z problemami emocjonalnymi: depresja, zaburzenia lękowe, doświadczenia postraumatyczne, uzależnienia od urządzeń ekranowych",
    "Wsparcie dziecka z trudnościami w zachowaniu: bunt, agresja, przemoc rówieśnicza",
    "Zagrożenia dla rozwoju współczesnego dziecka/ nastolatka: używki, uzależnienia behawioralne",
    "Wspomaganie pamięci i koncentracji uczniów",
    "TIK w pracy nauczyciela",
    "Bezpieczeństwo w sieci uczniów i nauczycieli",
    "Prawo oświatowe",
    "Stres w pracy, wzmacnianie odporności psychicznej i dobrostanu nauczycieli",
    "Praca z klasą zróżnicowaną kulturowo (uczeń z zagranicy z zespole klasowym)",
    "Praca z klasą zróżnicowaną edukacyjnie",
    'Praca z klasą "trudną" (konflikty, kłopoty z dyscypliną, brak aktywności, słaba motywacja)',
    "Ciekawe lekcje wychowawcze",
    'Współpraca z rodzicami (w tym z "wymagającym" rodzicem)',
]

def read_ma_file(file_path: str):
    """
    Reads a Google Forms ODS file and summarizes data:
    - Averages numeric columns
    - Counts text/choice-column responses
    """

    spreadsheet = ezodf.opendoc(file_path)

    # Only one sheet expected
    if len(spreadsheet.sheets) != 1:
        raise ValueError("ODS file must contain exactly one sheet.")
    sheet = spreadsheet.sheets[0]

    # Extract header row (first row)
    headers = [
        str(sheet[0, c].value)
        for c in range(sheet.ncols())
        if sheet[0, c].value is not None
    ]

    # Collect columns (skip headers)
    columns = {h: [] for h in headers}
    for r in range(1, sheet.nrows()):
        for c, header in enumerate(headers):
            value = sheet[r, c].value
            if value is not None:
                columns[header].append(value)

    # Analyze columns
    summary = {}
    for header, values in columns.items():
        if header == "Sygnatura czasowa":
            continue
        elif header in keys_average:
            numeric_values = []
            for v in values:
                try:
                    numeric_values.append(float(v))
                except (TypeError, ValueError):
                    pass
            # Ensure there's valid numeric data to average
            if numeric_values:
                summary[header] = mean(numeric_values)
            else:
                summary[header] = "N/A (No valid numeric data)"

        elif header in key_lista:
            new_items = []
            for value in values:
                new_items.append(str(value).replace("\n", "")) # Ensure value is string
            summary[header] = new_items
        elif header in key_tak_nie:
            tak = 0
            nie_wiem = 0
            nie = 0
            for value in values:
                value_str = str(value) # Ensure comparison with string
                if value_str == "Tak":
                    tak += 1
                elif value_str == "Nie wiem":
                    nie_wiem += 1
                elif value_str == "Nie":
                    nie += 1

            summary[header] = {"Tak":tak, "Nie wiem":nie_wiem, "Nie":nie}
        elif header in key_sorting:
            temp = {}
            for item in multi_choice_key:
                temp[item] = 0
            temp["inne"] = 0
            for value in values:
                found = False
                value_str = str(value) # Ensure value is string for 'in' check
                for item in multi_choice_key:
                    if item in value_str:
                        temp[item] += 1
                        found = True
                if not found:
                    temp["inne"] += 1
            summary[header] = temp
        else:
            # Some strings -> count frequency
            summary[header] = {
                "type": "text",
                "counts": dict(Counter(str(v) for v in values)), # Ensure all values are strings
            }

    return summary

def write_summary_to_file(summary_data: dict, output_file_path: str):
    """
    Writes the summarized data to a text file, exactly mirroring the original print format.
    """
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            for key, value in summary_data.items():
                f.write(f"{key}\n")
                if isinstance(value, list):
                    for item in value:
                        f.write(f"{item}\n")
                elif isinstance(value, dict):
                    # Original code printed sub_key then sub_item on separate lines
                    for sub_key, sub_item in value.items():
                        f.write(f"{sub_key}\n")
                        f.write(f"{sub_item}\n")
                else:
                    f.write(f"{value}\n")
                f.write("-" * 20 + "\n")
        print(f"Summary successfully written to '{output_file_path}'")
    except IOError as e:
        print(f"Error writing to file '{output_file_path}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# --- Main execution ---

def parse_ankieta_ewaluacyjna(ods_path: str, output_path: str):
    results = read_ma_file(ods_path)
    output_file_name = output_path
    write_summary_to_file(results, output_file_name)
