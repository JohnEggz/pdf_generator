from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont # For registering custom fonts if needed
# from src.config.settings import FONT_NAME


def _split_text_for_cell(text, available_width_for_text, font_name, font_size):
    if not text:
        return [""]

    lines = []
    words = str(text).split(" ") # Ensure text is a string
    current_line_words = []

    for word in words:
        potential_line = " ".join(current_line_words + [word])
        potential_width = pdfmetrics.stringWidth(potential_line, font_name, font_size)

        if potential_width > available_width_for_text and current_line_words:
            lines.append(" ".join(current_line_words))
            current_line_words = [word]
        else:
            current_line_words.append(word)

    if current_line_words:
        lines.append(" ".join(current_line_words))

    return lines

def my_table(
        c: canvas.Canvas,
        data: list[list[str]],
        x: float,
        y: float,
        col_widths: list[float],
        margins: dict[str,float] = {"left":1*cm, "right":1*cm, "up":2.5*cm, "down":2.5*cm},
        merge_cells: list[tuple[tuple[int, int]]]|None = None,
        has_header: bool = True
):
    """Draws table on specific coordinates"""
    FONT_NAME = "Helvetica"
    FONT_SIZE = 12
    LINE_HEIGHT = FONT_SIZE * 1.2
    TEXT_PADDING_H = 2*mm
    TEXT_PADDING_V = 2

    c.setFont(FONT_NAME, FONT_SIZE)
    c.setFillColor(colors.black)
    c.setStrokeColor(colors.grey)

    current_y = y
    table_width = sum(col_widths)

    for row_idx, row_data in enumerate(data):
        # finds row height
        max_row_height = 0
        wrapped_row_content = []

        for col_idx, cell_text in enumerate(row_data):
            col_width = col_widths[col_idx]
            available_text_width = col_width - (2 * TEXT_PADDING_H)
            
            wrapped_lines = _split_text_for_cell(
                cell_text,
                available_text_width,
                FONT_NAME,
                FONT_SIZE
            )
            wrapped_row_content.append(wrapped_lines)
            
            cell_content_height = max(1, len(wrapped_lines)) * LINE_HEIGHT
            max_row_height = max(max_row_height, cell_content_height)
        
        row_height = max_row_height + (2 * TEXT_PADDING_V)
        row_y_bottom = current_y - row_height

        if row_y_bottom - margins["down"] < 0:
            c.showPage()
            current_y = A4[1] - margins["up"]
            row_y_bottom = current_y - row_height

        if has_header and row_idx == 0:
            c.setFillColor(colors.lightgrey)
            c.rect(x, row_y_bottom, table_width, row_height, fill=1)
            c.setFillColor(colors.black)

        # Cell drawing
        current_x_for_cells = x
        for col_idx, wrapped_lines in enumerate(wrapped_row_content):
            col_width = col_widths[col_idx]

            c.rect(current_x_for_cells, row_y_bottom, col_width, row_height, fill=0)

            text_start_y_for_line = current_y - TEXT_PADDING_V - FONT_SIZE
            for line in wrapped_lines:
                c.drawString(current_x_for_cells + TEXT_PADDING_H, text_start_y_for_line, line)
                text_start_y_for_line -= LINE_HEIGHT

            current_x_for_cells += col_width
        
        current_y = row_y_bottom
    # c.line(start_x, start_y, start_x + table_width, start_y)

# Example Usage:
if __name__ == "__main__":
    from reportlab.lib.pagesizes import A4

    # It's good practice to register the font if it's not a standard ReportLab font
    # For this example, 'Helvetica' is standard, so no explicit registration is needed.
    # If you wanted a custom font, you'd do:
    # try:
    #     pdfmetrics.registerFont(TTFont('CustomFont', 'path/to/your/font.ttf'))
    # except Exception as e:
    #     print(f"Could not register font: {e}. Using Helvetica.")


    c = canvas.Canvas("custom_table_on_canvas.pdf", pagesize=A4)

    # Some example data
    table_data = [
        ["Product ID", "Item Name", "Description", "Price"],
        ["Product ID", "Item Name", "Description", "Price"],
        ["Product ID", "Item Name", "Description", "Price"],
        ["Product ID", "Item Name", "Description", "Price"],
        ["001", "Apple", "Fresh green apples, juicy and crisp. Great for snacking or pies.", "1.25"],
        ["002", "Banana", "Organic yellow bananas, perfect for smoothies or a quick energy boost.", "0.79"],
        ["003", "Orange Juice", "Freshly squeezed orange juice, no pulp. Contains vitamin C. Large bottle.", "4.99"],
        ["004", "Milk", "Dairy milk, 2% reduced fat. Locally sourced from happy cows.", "3.50"],
        ["005", "Bread", "Whole wheat bread, baked fresh daily. A staple for any meal.", "2.80"],
        ["001", "Apple", "Fresh green apples, juicy and crisp. Great for snacking or pies.", "1.25"],
        ["002", "Banana", "Organic yellow bananas, perfect for smoothies or a quick energy boost.", "0.79"],
        ["003", "Orange Juice", "Freshly squeezed orange juice, no pulp. Contains vitamin C. Large bottle.", "4.99"],
        ["004", "Milk", "Dairy milk, 2% reduced fat. Locally sourced from happy cows.", "3.50"],
        ["005", "Bread", "Whole wheat bread, baked fresh daily. A staple for any meal.", "2.80"],
        ["001", "Apple", "Fresh green apples, juicy and crisp. Great for snacking or pies.", "1.25"],
        ["002", "Banana", "Organic yellow bananas, perfect for smoothies or a quick energy boost.", "0.79"],
        ["Product ID", "Item Name", "Description", "Price"],
        ["001", "Apple", "Fresh green apples, juicy and crisp. Great for snacking or pies.", "1.25"],
        ["002", "Banana", "Organic yellow bananas, perfect for smoothies or a quick energy boost.", "0.79"],
        ["003", "Orange Juice", "Freshly squeezed orange juice, no pulp. Contains vitamin C. Large bottle.", "4.99"],
        ["004", "Milk", "Dairy milk, 2% reduced fat. Locally sourced from happy cows.", "3.50"],
        ["005", "Bread", "Whole wheat bread, baked fresh daily. A staple for any meal.", "2.80"],
        ["001", "Apple", "Fresh green apples, juicy and crisp. Great for snacking or pies.", "1.25"],
        ["002", "Banana", "Organic yellow bananas, perfect for smoothies or a quick energy boost.", "0.79"],
        ["003", "Orange Juice", "Freshly squeezed orange juice, no pulp. Contains vitamin C. Large bottle.", "4.99"],
        ["004", "Milk", "Dairy milk, 2% reduced fat. Locally sourced from happy cows.", "3.50"],
        ["005", "Bread", "Whole wheat bread, baked fresh daily. A staple for any meal.", "2.80"],
        ["001", "Apple", "Fresh green apples, juicy and crisp. Great for snacking or pies.", "1.25"],
        ["002", "Banana", "Organic yellow bananas, perfect for smoothies or a quick energy boost.", "0.79"],
        ["003", "Orange Juice", "Freshly squeezed orange juice, no pulp. Contains vitamin C. Large bottle.", "4.99"],
        ["004", "Milk", "Dairy milk, 2% reduced fat. Locally sourced from happy cows.", "3.50"],
        ["005", "Bread", "Whole wheat bread, baked fresh daily. A staple for any meal.", "2.80"],
    ]

    # Column widths in points (e.g., 1 cm = 28.35 points)
    # Total A4 width approx 21 cm, so 21 * 28.35 = 595 points
    # Let's say we want it to start at 2cm from left, so 2 * cm = 56.7 points
    # And have a table width of maybe 17 cm = 481.95 points
    col_widths_pts = [
        2 * cm, # Product ID
        3.5 * cm, # Item Name
        8 * cm,   # Description
        2 * cm    # Price
    ]

    # Starting position (top-left of the table)
    start_table_x = 2 * cm
    start_table_y = A4[1] - 3 * cm # 3cm from the top of the page

    my_table(c, table_data, start_table_x, start_table_y, col_widths_pts, has_header=True)
    c.save()
    print("Generated custom_table_on_canvas.pdf")

