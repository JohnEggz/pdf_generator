
import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

from src.pdf_generation.generator import generate

def main():
    """Main command-line entry point for the PDF generator."""
    parser = argparse.ArgumentParser(
        description="Generate training logbooks and certificates from a JSON file."
    )
    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to the input data.json file.",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=None,
        help="Directory to save the generated PDFs. (Defaults to a temporary directory)",
    )
    parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="Force regeneration of all certificates, even if they have a timestamp.",
    )
    args = parser.parse_args()

    # --- 1. Validate Input ---
    if not args.json_file.is_file():
        print(f"Error: Input file not found at '{args.json_file}'")
        sys.exit(1)

    try:
        with open(args.json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON from '{args.json_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        sys.exit(1)

    # --- 2. Determine Output Directory ---
    if args.output_dir:
        output_directory = args.output_dir
        os.makedirs(output_directory, exist_ok=True)
        run_in_temp = False
    else:
        # Use a temporary directory that cleans itself up
        temp_dir_manager = tempfile.TemporaryDirectory()
        output_directory = Path(temp_dir_manager.name)
        run_in_temp = True
        print(f"No output directory specified. Using temporary directory: {output_directory}")

    # --- 3. Run the Generator ---
    print("-" * 50)
    updated_data = generate(
        data_json=data,
        output_dir=str(output_directory),
        force=args.force
    )
    print("-" * 50)

    # --- 4. Handle Output ---
    # If the original data was changed (e.g., new timestamps), save it back.
    if updated_data != data:
        try:
            with open(args.json_file, "w", encoding="utf-8") as f:
                json.dump(updated_data, f, indent=4, ensure_ascii=False)
            print(f"Successfully updated timestamps in '{args.json_file}'")
        except IOError as e:
            print(f"Warning: Could not save updated timestamps back to source file: {e}")

    print(f"✅ Generation complete. Files are located in: {output_directory}")

    # If we used a temp directory, we need to keep the program alive to inspect files
    if run_in_temp:
        input("Press Enter to delete the temporary directory and exit.")
        temp_dir_manager.cleanup()

if __name__ == "__main__":
    main()
