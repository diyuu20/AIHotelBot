import pdfplumber
import qrcode
import os
import re

# --- Configuration ---
INPUT_PDF_FILE = r"F:\Documents\Downloads\Devshree\AIHOTELBOT\AIHOTELBOT\static\active_bookings.pdf"

OUTPUT_QR_DIR = r"F:\Documents\Downloads\Devshree\AIHOTELBOT\AIHOTELBOT\static\QR_CODES"

def sanitize_filename(name):
    """Removes invalid characters and replaces spaces with underscores for filenames."""
    # Remove any character that is not a letter, number, underscore, or space
    name = re.sub(r'[^\w\s-]', '', name).strip()
    # Replace one or more spaces/hyphens with a single underscore
    name = re.sub(r'[-\s]+', '_', name)
    return name

def create_qr_from_pdf(pdf_path, output_dir):
    """
    Reads a PDF, extracts booking data from its tables, and generates QR codes.
    
    Args:
        pdf_path (str): The path to the input PDF file.
        output_dir (str): The directory where QR code images will be saved.
    """
    if not os.path.exists(pdf_path):
        print(f"❌ Error: The file '{pdf_path}' was not found.")
        print("Please run the main PDF generation script first to create it.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"📂 Saving QR codes to '{output_dir}/' directory.")

    generated_count = 0
    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Find the column indexes for "Booking ID" and "Booking Under Name"
            id_col_index = -1
            name_col_index = -1
            
            # Assume the table is on the first page
            page = pdf.pages[0]
            table = page.extract_table()
            
            if not table:
                print("❌ Error: Could not find a table in the PDF.")
                return
            
            headers = table[0]
            try:
                id_col_index = headers.index("Booking ID")
                name_col_index = headers.index("Booking Under Name")
            except (ValueError, IndexError):
                print("❌ Error: Could not find 'Booking ID' or 'Booking Under Name' columns in the PDF table.")
                return

            # Process rows, skipping the header row (table[1:])
            for row in table[1:]:
                booking_id = row[id_col_index]
                booking_name = row[name_col_index]
                
                if booking_id and booking_name:
                    # Sanitize the name to create a valid filename
                    filename = sanitize_filename(booking_name) + ".png"
                    file_path = os.path.join(output_dir, filename)
                    
                    # Generate and save the QR code
                    qr_img = qrcode.make(booking_id)
                    qr_img.save(file_path)
                    
                    print(f"  ✅ Generated QR for {booking_name} -> {filename}")
                    generated_count += 1

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    if generated_count > 0:
        print(f"\n🎉 Successfully generated {generated_count} QR codes.")
    else:
        print("\nNo QR codes were generated. Please check the PDF content.")


if __name__ == "__main__":
    create_qr_from_pdf(INPUT_PDF_FILE, OUTPUT_QR_DIR)
    
