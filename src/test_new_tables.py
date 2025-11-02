
import json
from typing import Any, Dict

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfgen.canvas import Canvas

from src.pdf_generation.generator import draw_certyfikat, draw_dziennik, generate, register_font
from src.pdf_generation.tables import my_table

from src.config import settings


if __name__ == "__main__":
    with open("/home/john/Documents/mom_confidential/first_test/data.json", "r", encoding="utf-8") as f:
        data_json = json.load(f)
    # register_font()
    participants = data_json.get(settings.KEY_PARTICIPANTS, [])[0]
    training = data_json.get(settings.KEY_TRAINING, {})
    #
    # draw_certyfikat(training, participants, "custom_table_with_merges.pdf")
    # print("Generated custom_table_with_merges.pdf")
    generate(data_json, "/tmp/testowe/")

