from typing import Any
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.config import settings


def _split_text_for_cell(
    text, available_width_for_text, font_name, font_size
) -> list[str]:
    """Helper function to wrap text into lines for a given width."""
    if not text:
        return [""]

    lines = []
    # Handle multi-line text input gracefully
    raw_lines = str(text).split("\n")
    words = []
    for line in raw_lines:
        words.extend(line.split(" "))
        words.append("\n") # Use '\n' as a sentinel for forced line breaks
    words.pop() # remove last '\n'

    current_line_words = []
    for word in words:
        if word == "\n":
            lines.append(" ".join(current_line_words))
            current_line_words = []
            continue

        potential_line = " ".join(current_line_words + [word])
        potential_width = pdfmetrics.stringWidth(
            potential_line, font_name, font_size
        )

        if potential_width > available_width_for_text and current_line_words:
            lines.append(" ".join(current_line_words))
            current_line_words = [word]
        else:
            current_line_words.append(word)

    if current_line_words:
        lines.append(" ".join(current_line_words))

    # If the input was empty or just whitespace, ensure we return one empty line
    return lines if lines else [""]

def _guess_the_widths(headers: list[str], font_name, font_size, text_padding, center_table, x):
    widths = []
    for line in headers:
        widths.append( pdfmetrics.stringWidth(line, font_name, font_size) + (2.01* text_padding))
    if center_table:
        if sum(widths) > A4[0]:
            widths[-1] = 19*cm - sum(widths[:-1])
    else:
        if sum(widths) + x > A4[0]:
            widths[-1] = 19*cm - x - sum(widths[:-1])

    return widths

def my_table(
    c: canvas.Canvas,
    data: list[list[str]],
    x: float,
    y: float,
    col_widths: list[float] | None,
    margins: dict[str, float] | int | None | bool= None,
    merge_cells: list[tuple[tuple[int, int], tuple[int, int]]] | None = None,
    has_header: bool = False,
    has_border: bool = True,
    align: str = "Left",
    center_table: bool = False,
    font_size: int = 10,
    padding: int | None | bool = None,
) -> float:
    """
    Draws a table on the canvas with support for merged cells.
    Returns curent_y

    Args:
        c: The ReportLab canvas object.
        data: A list of lists containing the table data as strings.
        x: The left x-coordinate of the table.
        y: The top y-coordinate of the table.
        col_widths: A list of widths for each column.
        margins: A dictionary for page margins, e.g., {"up": 2.5*cm, "down": 2.5*cm}.
        merge_cells: A list of merges, each defined by a tuple of two tuples:
                     ((start_row, start_col), (end_row, end_col)).
        has_header: If True, the first row is styled as a header.
        center_table: Ignores x and centeres the table on canvas
    """
    if margins is None:
        margins = {"left": 1 * cm, "right": 1 * cm, "up": 2.5 * cm, "down": 2.5 * cm}
    if margins == False:
        margins = {"left": 0, "right": 0, "up": 0, "down": 0}


    FONT_NAME = settings.FONT_NAME
    FONT_SIZE = font_size
    LINE_HEIGHT = FONT_SIZE * 1.2
    TEXT_PADDING_H = 2 * mm
    TEXT_PADDING_V = 2.6 * mm

    if padding == False:
        TEXT_PADDING_H = 0

    c.setFont(FONT_NAME, FONT_SIZE)

    # TODO: make it look deeper than first list
    if not col_widths:
        col_widths = _guess_the_widths(data[0], FONT_NAME, FONT_SIZE, TEXT_PADDING_H, center_table, x)
    if center_table and col_widths:
        x = (A4[0] - sum(col_widths)) / 2

    # --- Pre-computation Step: Create maps for merged cells ---
    merge_map = {}  # Maps a start cell (r,c) to its end cell (r,c)
    skip_cells = set()  # A set of all cells to skip drawing
    if merge_cells:
        for start, end in merge_cells:
            start_row, start_col = start
            end_row, end_col = end
            merge_map[(start_row, start_col)] = (end_row, end_col)
            # Add all cells covered by the merge, except the top-left one, to skip_cells
            for r in range(start_row, end_row + 1):
                for col in range(start_col, end_col + 1):
                    if (r, col) != (start_row, start_col):
                        skip_cells.add((r, col))

    # --- Pass 1: Calculate Row Heights ---
    row_heights = [0] * len(data)
    for r_idx, row_data in enumerate(data):
        max_cell_height_in_row = 0
        for c_idx, cell_text in enumerate(row_data):
            if (r_idx, c_idx) in skip_cells:
                continue

            # Check if this cell is the start of a merge
            if (r_idx, c_idx) in merge_map:
                # This is a merged cell, skip height calculation for now
                # It will be handled separately to avoid double counting
                continue
            else:
                # This is a regular cell
                available_width = col_widths[c_idx] - (2 * TEXT_PADDING_H)
                wrapped_lines = _split_text_for_cell(
                    cell_text, available_width, FONT_NAME, FONT_SIZE
                )
                cell_height = len(wrapped_lines) * LINE_HEIGHT + (2 * TEXT_PADDING_V)
                max_cell_height_in_row = max(max_cell_height_in_row, cell_height)

        row_heights[r_idx] = max(row_heights[r_idx], max_cell_height_in_row)

    # Now, handle the heights of vertically merged cells
    for start_cell, end_cell in merge_map.items():
        start_row, start_col = start_cell
        end_row, end_col = end_cell

        # We only need to adjust heights for vertical spans
        if start_row == end_row:
            # For horizontal-only merges, ensure the row is tall enough
            cell_text = data[start_row][start_col]
            merged_width = sum(col_widths[start_col : end_col + 1])
            available_width = merged_width - (2 * TEXT_PADDING_H)
            wrapped_lines = _split_text_for_cell(
                cell_text, available_width, FONT_NAME, FONT_SIZE
            )
            cell_height = len(wrapped_lines) * LINE_HEIGHT + (2 * TEXT_PADDING_V)
            row_heights[start_row] = max(row_heights[start_row], cell_height)
        else:
            # For vertical merges, check if the combined rows are tall enough
            cell_text = data[start_row][start_col]
            merged_width = sum(col_widths[start_col : end_col + 1])
            available_width = merged_width - (2 * TEXT_PADDING_H)
            wrapped_lines = _split_text_for_cell(
                cell_text, available_width, FONT_NAME, FONT_SIZE
            )
            required_height = len(wrapped_lines) * LINE_HEIGHT + (2 * TEXT_PADDING_V)

            current_span_height = sum(row_heights[start_row : end_row + 1])

            if required_height > current_span_height:
                # Distribute the needed extra height to the last row in the span
                extra_height = required_height - current_span_height
                row_heights[end_row] += extra_height

    # --- Pass 2: Drawing ---
    current_y = y
    table_width = sum(col_widths)

    for r_idx, row_data in enumerate(data):
        row_height = row_heights[r_idx]

        # Page break check
        if current_y - row_height < margins["down"]:
            c.showPage()
            c.setFont(FONT_NAME, FONT_SIZE) # Reset font on new page
            current_y = A4[1] - margins["up"]

        # row_y_bottom = current_y - row_height
        current_x = x

        # Draw header background if applicable
        if has_header and r_idx == 0:
            c.setFillColor(colors.lightgrey)
            # We need to calculate header height in case it's part of a merge
            header_end_row = 0
            if (0, 0) in merge_map:
                header_end_row = merge_map[(0, 0)][0]
            header_height = sum(row_heights[0 : header_end_row + 1])
            c.rect(x, current_y - header_height, table_width, header_height, fill=1, stroke=0)
            c.setFillColor(colors.black)

        for c_idx, cell_text in enumerate(row_data):
            col_width = col_widths[c_idx]

            if (r_idx, c_idx) in skip_cells:
                current_x += col_width
                continue

            # Determine cell dimensions
            draw_width = col_width
            draw_height = row_height
            if (r_idx, c_idx) in merge_map:
                end_row, end_col = merge_map[(r_idx, c_idx)]
                draw_width = sum(col_widths[c_idx : end_col + 1])
                draw_height = sum(row_heights[r_idx : end_row + 1])

            # Draw cell border
            if has_border:
                c.setStrokeColor(colors.grey)
                c.rect(current_x, current_y - draw_height, draw_width, draw_height)

            # Draw cell text
            c.setFillColor(colors.black)
            available_text_width = draw_width - (2 * TEXT_PADDING_H)
            wrapped_lines = _split_text_for_cell(
                cell_text, available_text_width, FONT_NAME, FONT_SIZE
            )

            # # Vertically center the text block
            # text_block_height = len(wrapped_lines) * LINE_HEIGHT
            # v_offset = (draw_height - text_block_height) / 2
            # text_y = current_y - v_offset - FONT_SIZE

            # Verticall align topd
            text_y = current_y - FONT_SIZE - TEXT_PADDING_H

            for line in wrapped_lines:
                match align:
                    case "center":
                        c.drawCentredString(current_x + (draw_width / 2), text_y, line)
                    case _:
                        c.drawString(current_x + TEXT_PADDING_H, text_y, line)
                text_y -= LINE_HEIGHT

            current_x += col_width
        current_y -= row_height
    return current_y


# Example Usage:
if __name__ == "__main__":
    c = canvas.Canvas("custom_table_with_merges.pdf", pagesize=A4)

    table_data = [
        ["Product", "Description", "Jan", "Feb"],
        [
            "Super Widget",
            "An amazing widget that will solve all your problems. It's available in several colors and sizes.",
            "100",
            "120",
        ],
        [
            "Mega Gadget",
            "A less amazing, but much cheaper gadget.",
            "80",
            "95",
        ],
        ["Total", "", "180", "215"],
    ]

    col_widths_pts = [3 * cm, 8 * cm, 2 * cm, 2 * cm]
    start_table_x = 2 * cm
    start_table_y = A4[1] - 3 * cm

    # Define cells to merge: ((start_row, start_col), (end_row, end_col))
    merges_to_apply = [
        ((0, 0), (0, 1)),  # Merge "Product" and "Description" in header
        ((3, 0), (3, 1)),  # Merge "Total" and its empty neighbor
    ]

    my_table(
        c,
        table_data,
        start_table_x,
        start_table_y,
        col_widths_pts,
        has_header=True,
        has_border=False,
        merge_cells=merges_to_apply,
    )
    
    # --- Example with vertical merge ---
    data_vertical = [
        ["Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.:with"],
    ]
    
    my_table(
        c,
        data_vertical,
        start_table_x,
        start_table_y - 7*cm, # Start lower on the page
        [12*cm],
        align="center",
        center_table=True
    )

    c.save()
    print("Generated custom_table_with_merges.pdf")
