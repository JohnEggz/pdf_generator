# src/cli/commands.py
import argparse
import os
from src.config import settings
from src.project_managment.file_ops import load_json_data
from src.pdf_generation.generator import generate_logbook, generate_certificates

def handle_generate(args):
    """Handler for the 'generate' command."""
    if not os.path.isdir(args.directory):
        print(f"Error: Directory not found at '{args.directory}'")
        return

    json_path = os.path.join(args.directory, settings.DATA_FILENAME)
    data = load_json_data(json_path)

    if not data:
        print(f"Could not load data from {json_path}. Aborting.")
        return

    if args.all or args.logbook:
        print("Generating logbook...")
        generate_logbook(data, args.directory)

    if args.all or args.certificates:
        print("Generating certificates...")
        generate_certificates(data, args.directory)
        # Note: The CLI version doesn't automatically save back timestamps.
        # This would be a feature to add.

    print("Generation complete.")

def setup_cli():
    """Sets up the command-line argument parser."""
    parser = argparse.ArgumentParser(description="Training Data Manager CLI.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate PDF documents.")
    gen_parser.add_argument("directory", type=str, help="Path to the training directory.")
    gen_parser.add_argument("--all", action="store_true", help="Generate all documents.")
    gen_parser.add_argument("--logbook", action="store_true", help="Generate only the logbook.")
    gen_parser.add_argument("--certificates", action="store_true", help="Generate only the certificates.")
    gen_parser.set_defaults(func=handle_generate)

    # To use this:
    # args = parser.parse_args()
    # args.func(args)

# Example of how to run from main.py if you add CLI logic:
# if __name__ == "__main__":
#     setup_cli()
