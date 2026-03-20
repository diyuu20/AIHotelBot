import pdfplumber
from fpdf import FPDF
import os
from datetime import datetime

PDF_FILE = os.path.join('static', 'active_bookings.pdf')
HEADERS = ["Booking ID", "Booking Under Name", "Check In", "Check Out", "Num People", "Alloted Room","Type of Room","Room Facing","Type of Plan","Special Request"]

class PDF(FPDF):
    """Custom PDF class to handle headers and footers."""
    def header(self):
        self.set_font('Arial', 'B', 12)
        title = "Active Hotel Bookings"
        title_w = self.get_string_width(title) + 6
        self.set_x((self.w - title_w) / 2)
        self.cell(title_w, 10, title, border=1, ln=1, align='C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', align='C')

def read_all_bookings():
    """Reads all existing bookings from the PDF file."""
    if not os.path.exists(PDF_FILE):
        return []
    
    bookings = []
    try:
        with pdfplumber.open(PDF_FILE) as pdf:
            page = pdf.pages[0]
            table = page.extract_table()
            if table and len(table) > 1:
                # Skip the header row
                for row in table[1:]:
                    bookings.append(dict(zip(HEADERS, row)))
    except Exception as e:
        print(f"Error reading PDF: {e}")
    return bookings

def add_booking_to_pdf(new_booking_data):
    """
    Reads the existing PDF, adds a new booking, and overwrites the file.
    """
    existing_bookings = read_all_bookings()
    
    # Convert the new booking dictionary to a list in the correct order
    new_row = [str(new_booking_data.get(header, '')) for header in HEADERS]
    
    # Combine existing data with the new row
    all_data = [list(booking.values()) for booking in existing_bookings]
    all_data.append(new_row)
    
    # --- Recreate the PDF from scratch with the updated data ---
    pdf = PDF()
    pdf.add_page(orientation='L')
    pdf.set_font('Arial', '', 10)
    
    # Calculate column widths dynamically
    col_widths = {}
    temp_data_for_width_calc = [HEADERS] + all_data
    for i, header in enumerate(HEADERS):
        max_width = pdf.get_string_width(header)
        for row_data in temp_data_for_width_calc:
            cell_width = pdf.get_string_width(str(row_data[i]))
            if cell_width > max_width:
                max_width = cell_width
        col_widths[header] = max_width + 8

    # Create Table Header
    pdf.set_fill_color(200, 220, 255)
    pdf.set_font('Arial', 'B', 10)
    for header in HEADERS:
        pdf.cell(col_widths[header], 10, header, border=1, align='C', fill=True)
    pdf.ln()
    
    # Create Table Rows
    pdf.set_font('Arial', '', 9)
    fill = False
    for row in all_data:
        pdf.set_fill_color(240, 240, 240)
        for i, header in enumerate(HEADERS):
            pdf.cell(col_widths[header], 10, str(row[i]), border=1, align='C', fill=fill)
        pdf.ln()
        fill = not fill

    pdf.output(PDF_FILE)
    print(f"✅ Successfully added Booking ID {new_booking_data['Booking ID']} to PDF.")