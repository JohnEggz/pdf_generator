# src/pdf_generation/generator.py
"""
A standalone module for generating all PDF documents for the training program.
It contains all necessary helpers, styles, components, and generation logic.
"""
import PIL.Image
import os
import json
from datetime import datetime
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
# from typing import List, Dict, Any, Callable


# --- Consolidated Imports ---
# from reportlab.pdfgen import canvas
# from reportlab.pdfgen.canvas import Canvas
# from reportlab.pdfbase import pdfmetrics
# from reportlab.pdfbase.ttfonts import TTFont
# from reportlab.lib import colors
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import cm
# from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
# from reportlab.platypus import (
#     BaseDocTemplate, Flowable, Frame, FrameBreak, NextPageTemplate,
#     PageTemplate, Spacer, Paragraph, Table, TableStyle
# )

from src.config import settings
from src.pdf_generation.tables import my_table

# ==============================================================================
# SECTION: UTILITIES (from former utils.py)
# ==============================================================================

def register_font():
    """Registers the DejaVuSans font for use in ReportLab."""
    font_path = settings.FONT_PATH
    font_name = settings.FONT_NAME
    if not os.path.exists(font_path):
        print(f"Error: Font file not found at {font_path}.")
        return False

    pdfmetrics.registerFont(TTFont(font_name, font_path))
    pdfmetrics.registerFontFamily(
        font_name,
        normal=font_name,
        bold="DejaVuSans-Bold",
        italic="DejaVuSans-Italic",
        boldItalic="DejaVuSans-BoldItalic",
    )
    return True


# ==============================================================================
# SECTION: PAGE-SPECIFIC DRAWING FUNCTIONS
# ==============================================================================

def draw_dziennik(
    training: dict[str, Any],
    participants: list[dict[str, Any]],
    output_path: str,
):

    c = canvas.Canvas(output_path, pagesize=A4)

    page_width, top = A4; middle = page_width/2; left = 2.72*cm
    c.setFont(settings.FONT_NAME, 28)
    c.drawCentredString(middle, 18.3*cm, "Dziennik zajęć")
    c.setFont(settings.FONT_NAME, 16)
    current_y = my_table(
        c,
        [[f"Tytuł: {training.get(settings.KEY_NAZWA_SZKOLENIA, 'PLACEHOLDER')}"]],
        0,
        15.8*cm,
        None,
        has_border=False,
        center_table=True,
        font_size=20,
        margins=False,
        padding=False,
        align="center"
    )
    my_table(
        c,
        [["KOD SZKOLENIA: ", training.get(settings.KEY_NUMER_SZKOLENIA, "PLACEHOLDER")]],
        0,
        current_y,
        None,
        has_border=False,
        center_table=True,
        font_size=20
    )
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, 9*cm, f"Data: {training.get(settings.KEY_DATA_SZKOLENIA, 'PLACEHOLDER')}")
    my_table(
        c,
        [["Miejsce: ", training.get(settings.KEY_MIEJSCE_SZKOLENIA, "PLACEHOLDER")]],
        left,
        8.4*cm,
        None,
        has_border=False,
        font_size=12,
        margins=False,
        padding=False
    )
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, 6.5*cm, f"Prowadzący: {training.get(settings.KEY_PROWADZACY, 'PLACEHOLDER')}")
    # Logo
    w, h = 6.2*cm, 2.5*cm; x = page_width - 0.8*cm - w; y = top - 0.8*cm - h
    c.drawImage(
        ImageReader(PIL.Image.open(settings.IMAGE_LOGO_PATH)),
        x,
        y,
        width=w,
        height=h
    )

    # PAGE 2
    c.showPage()
    current_y = top-3*cm
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, current_y, "Plan szkolenia:")
    current_y -= 0.5*cm

    current_y = my_table(
        c,
        [
            ["Tematyka", "Liczba\ngodzin", "Podpis\nTrenera"],
            [training.get(settings.KEY_TEMATYKA, "PLACEHOLDER"), training.get(settings.KEY_CZAS_TRWANIA, "PLACEHOLDER"), ""],
        ],
        left,
        current_y,
        [12.5*cm, 2*cm, 3*cm],
        center_table=True,
    )

    current_y -= 1.5*cm
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, current_y, "Program szkolenia:")
    current_y -= 0.5*cm
    current_y = my_table(
        c,
        [
            ["Data", "Tematyka", "Czas\nod - do", "Liczba\ngodzin", "Podpis\nTrenera"],
            [
                training.get(settings.KEY_DATA_SZKOLENIA,"PLACEHOLDER"),
                training.get(settings.KEY_TEMATYKA, "PLACEHOLDER"),
                training.get(settings.KEY_CZAS_TRWANIA_OD_DO,"PLACEHOLDER"),
                training.get(settings.KEY_CZAS_TRWANIA, "PLACEHOLDER"),
                "",
            ],
        ],
        left,
        current_y,
        [2.8*cm, 8*cm, 2.2*cm, 2.2*cm, 2.9*cm],
        center_table=True,
    )

    # PAGE 3
    c.showPage()
    current_y = top-3*cm
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, current_y, "Lista uczestników:")
    current_y -= 0.5*cm

    uczestnicy_data:list[list[Any]] = [[
        "",
        "Imie i nazwisko",
        "Data urodzenia",
        "Miejsce urodzenia",
        "Placówka",
    ]]
    uczestnicy_data.extend([[
        i+1,
        p.get(settings.KEY_IMIE_NAZWISKO, "MISSING"),
        p.get(settings.KEY_DATA_URODZENIA, "MISSING"),
        p.get(settings.KEY_MIEJSCE_URODZENIA, "MISSING"),
        training.get(settings.KEY_MIEJSCE_SZKOLENIA, "PLACEHOLDER")
    ] for i, p in enumerate(participants)])

    my_table(
        c,
        uczestnicy_data,
        0,
        current_y,
        [
            1*cm,
            6*cm,
            3*cm,
            4*cm,
            5*cm,
        ],
        center_table=True
    )

    # PAGE 4
    c.showPage()
    current_y = top-3*cm
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, current_y, "Wydane zaświadczenia:")
    current_y -= 0.5*cm

    wydane_data:list[list[Any]] = [["", "Imie i Nazwisko", "Numer Zaswiadczenia"]]
    wydane_data.extend(
        [
            [
                i + 1,
                p.get(settings.KEY_IMIE_NAZWISKO, "PLACEHOLDER"),
                f"{training.get(settings.KEY_NUMER_SZKOLENIA, 'PLACEHOLDER')}/{i + 1}",
            ]
            for i, p in enumerate(participants)
        ]
    )

    my_table(
        c,
        wydane_data,
        0,
        current_y,
        [
            1*cm,
            7.5*cm,
            7.5*cm,
        ],
        center_table=True
    )

    # PAGE 5
    c.showPage()
    current_y = top-3*cm
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, current_y, "ORGANIZACJA KURSU:")
    current_y -= 2*cm
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, current_y, "Nazwa instytucji organizującej:")
    current_y -= 0.5*cm
    c.setFont(settings.FONT_NAME, 10)
    c.drawString(left, current_y, "Małopolski Niepubliczny Ośrodek Doskonalenia Nauczycieli Best Practice Edukacja")
    current_y -= 2*cm
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, current_y, "Opiekun: Małgorzata Cużytek")
    current_y -= 3*cm
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, current_y, "SPRAWOZDANIE Z KURSU:")
    current_y -= 1.5*cm
    
    sprawozdanie_data = [
        [
            "Czas trwania kursu",
            "",
            "Liczba",
            "",
            "Liczba uczestników",
            "Liczba wydanych zaświadczeń",
            "Uwagi",
        ],
        [
            "od",
            "do",
            "dni",
            "godzin",
            "",
            "",
            "",
        ],
        [
            training.get(settings.KEY_DATA_SZKOLENIA, "PLACEHOLDER"),
            training.get(settings.KEY_DATA_SZKOLENIA, "PLACEHOLDER"),
            "1",
            training.get(settings.KEY_CZAS_TRWANIA, "PLACEHOLDER"),
            len(participants) or "PLACEHOLDER",
            len(participants) or "PLACEHOLDER",
            "-"
        ]
    ]

    my_table(
        c,
        sprawozdanie_data,
        0,
        current_y,
        [
            3*cm,
            3*cm,
            1.5*cm,
            2*cm,
            3*cm,
            3*cm,
            2*cm,
        ],
        center_table=True,
        align="center",
        merge_cells=[
            ((0,0),(0,1)),
            ((0,2),(0,3)),
            ((0,4),(1,4)),
            ((0,5),(1,5)),
            ((0,6),(1,6)),
        ]
    )

    c.setFont(settings.FONT_NAME, 12)
    # c.drawString(left, 5*cm, f"Wieliczka, {datetime.now().strftime("%d.%m.%Y")}")
    c.drawString(left, 5*cm, f"Wieliczka, {training.get(settings.KEY_DATA_WYSTAWIENIA, "PLACEHOLDER")}")

    c.save()

def draw_certyfikat(
    training: dict[str, Any],
    participant: dict[str, Any],
    output_path: str,
):
    # imie_nazwisko = data.get(settings.KEY_IMIE_NAZWISKO, "")
    # data_urodzenia = data.get(settings.KEY_DATA_URODZENIA, "")
    # nazwa_szkolenia = data.get(settings.KEY_NAZWA_SZKOLENIA, "")
    # dzien_ukonczenia = data.get(settings.KEY_DATA_SZKOLENIA, "")
    # w_wymiarze = data.get(settings.KEY_CZAS_TRWANIA, "")
    # wydano = data.get("wydano", "")
    c = canvas.Canvas(output_path, pagesize=A4)

    c.setFont(settings.FONT_NAME, 12)
    c.drawImage(
        ImageReader(PIL.Image.open(settings.IMAGE_LOGO_PATH)),
        1.5*cm,
        26*cm,
        width=6.2*cm,
        height=2.5*cm
    )
    c.drawImage(
        ImageReader(PIL.Image.open(settings.IMAGE_STAMP_PATH)),
        12.1*cm,
        26.4*cm,
        width=7.5*cm,
        height=2.2*cm
    )
    c.drawString(1.2*cm, 23.1*cm, participant.get(settings.KEY_UUID, "PLACEHOLDER"))
    c.setStrokeColor(colors.HexColor("#7B9FF3"))
    c.setFillColor(colors.HexColor("#7B9FF3"))
    c.line(2.8*cm, 22.4*cm, 18.2*cm, 22.4*cm)
    c.setFont(settings.FONT_NAME, 22)
    c.drawCentredString(A4[0]/2, 21.3*cm, "ZAŚWIADCZENIE")
    c.setFont(settings.FONT_NAME, 12)
    c.drawCentredString(A4[0]/2, 20.5*cm, "O UKOŃCZENIU FORMY DOSKONALENIA ZAWODOWEGO")
    c.line(2.8*cm, 20.1*cm, 18.2*cm, 20.1*cm)
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.black)
    c.drawCentredString(A4[0]/2, 18.9*cm, "Pan/i")

    my_table(
        c,
        [[f"{participant.get(settings.KEY_IMIE_NAZWISKO, "PLACEHOLDER")}"]],
        0,
        18.4*cm,
        None,
        has_border=False,
        center_table=True,
        font_size=20,
        margins=False,
        padding=False,
        align="center"
    )


    c.setFont(settings.FONT_NAME, 12)
    c.drawCentredString(A4[0]/2, 16.6*cm, f"urodzony/a: {participant.get(settings.KEY_DATA_URODZENIA, "PLACEHOLDER")}, {participant.get(settings.KEY_MIEJSCE_URODZENIA, 'PLACEHOLDER')}")
    current_y = 15 * cm
    c.drawCentredString(A4[0] / 2, current_y, "ukończył/a szkolenie:")

    current_y -= 0.5 * cm
    my_table(
        c,
        [[f"„{training.get(settings.KEY_NAZWA_SZKOLENIA, 'PLACEHOLDER')}”"]],
        0,
        current_y,
        None,
        has_border=False,
        center_table=True,
        font_size=20,
        margins=False,
        padding=False,
        align="center"
    )

    c.setFont(settings.FONT_NAME, 12)

    current_y -= 3.0 * cm
    c.drawString(5.4 * cm, current_y, f"w dniu: {training.get(settings.KEY_DATA_SZKOLENIA, 'PLACEHOLDER')}")

    c.drawString(
        11.4 * cm,
        current_y,
        f"w wymiarze: {training.get(settings.KEY_CZAS_TRWANIA, 'PLACEHOLDER')}"
    )

    current_y -= 1.8 * cm
    c.drawCentredString(
        A4[0] / 2,
        current_y,
        "zorganizowane przez Niepubliczną Placówkę Doskonalenia Nauczycieli"
    )

    current_y -= 0.6 * cm
    c.drawCentredString(A4[0] / 2, current_y, "Best Practice Edukacja w Wieliczce")

    current_y = 5.6*cm
    c.drawString(3 * cm, current_y, "Zaświadczenie wydano:")

    current_y -= 0.8 * cm
    c.drawString(3 * cm, current_y, f"Wieliczka, {training.get(settings.KEY_DATA_WYSTAWIENIA, "PLACEHOLDER")} r.")

    # PAGE 2
    left = 2.72*cm
    c.showPage()
    current_y = A4[1]-3*cm
    c.setFont(settings.FONT_NAME, 12)
    c.drawString(left, current_y, "Plan szkolenia:")
    current_y -= 0.5*cm

    current_y = my_table(
        c,
        [
            [
                "Tematyka",
            ],
            [
                training.get(settings.KEY_TEMATYKA, "PLACEHOLDER"),
            ],
        ],
        left,
        current_y,
        [17.5*cm],
        center_table=True,
    )

    c.save()

# ==============================================================================
# SECTION: INTERNAL GENERATION LOGIC
# ==============================================================================

def _generate_all_certificates(data_json, output_dir, force):
    participants = data_json.get(settings.KEY_PARTICIPANTS, [])
    training = data_json.get(settings.KEY_TRAINING, {})

    for i, person in enumerate(participants):
        person[settings.KEY_UUID] = f"{training.get(settings.KEY_NUMER_SZKOLENIA)}/{i+1}"
        file_path = os.path.join(output_dir, f"certyfikat_{i+1}.pdf")
        draw_certyfikat(training, person, file_path)
        print("-> created:", file_path)

def _generate_logbook(data_json, output_path):
    participants = data_json.get(settings.KEY_PARTICIPANTS, [])
    training = data_json.get(settings.KEY_TRAINING, {})
    draw_dziennik(training, participants, output_path)
    print("-> created:", output_path)


# ==============================================================================
# SECTION: PUBLIC API
# ==============================================================================

def generate(data_json: Dict[str, Any], output_dir: str, **kwargs):
    """
    Main PDF generation orchestrator.
    Generates a logbook and all required certificates.
    """
    force = kwargs.get('force', False)
    register_font()

    os.makedirs(output_dir, exist_ok=True)

    # 1. Generate Certificates
    print("Generating certificates...")
    certs_dir = os.path.join(output_dir, settings.CERTIFICATES_DIR_NAME)
    os.makedirs(certs_dir, exist_ok=True)
    _generate_all_certificates(data_json, certs_dir, force)

    # 2. Generate Logbook
    print("Generating logbook...")
    logbook_path = os.path.join(output_dir, settings.LOGBOOK_FILENAME)
    _generate_logbook(data_json, logbook_path)
