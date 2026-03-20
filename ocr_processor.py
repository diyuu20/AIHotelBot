import cv2
import pytesseract
import numpy as np
import re
from aadhaar_read import front_data, back_data
import os
import string as st
from dateutil import parser
import matplotlib.image as mpimg
from passporteye import read_mrz
import json
import easyocr
import warnings

warnings.filterwarnings('ignore')

# --- CONFIGURATION ---
# Update this path if your Tesseract installation is different
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
reader = easyocr.Reader(lang_list=['en'], gpu=False)

with open('country_codes.json') as f:
    country_codes = json.load(f)

# --- HELPER FUNCTIONS for Passport ---
def parse_date(string):
    try:
        date = parser.parse(string, yearfirst=True).date()
        return date.strftime('%d/%m/%Y')
    except parser.ParserError:
        return string # Return original string if parsing fails

def clean(string):
    return ''.join(i for i in string if i.isalnum()).upper()

def get_country_name(country_code):
    for country in country_codes:
        if country['alpha-3'] == country_code:
            return country['name'].upper()
    return country_code

def get_sex(code):
    if code in ['M', 'F']:
        return code
    return 'M' if code == '0' else 'F'

# --- OCR FUNCTIONS ---
def process_aadhaar(image_path):
    try:
        img = cv2.imread(image_path)
        gr = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        mask = gr <= 180
        gray = np.ones_like(gr) * 255
        gray[mask] = gr[mask]
        
        regex_name, regex_gender, regex_dob, regex_aadhaar_number = front_data(gray)
        
        return {
            "name": " ".join(regex_name[:3]),
            "document_number": regex_aadhaar_number,
            "dob": regex_dob,
            "gender": regex_gender
        }
    except Exception as e:
        print(f"Aadhaar processing error: {e}")
        return {"error": "Could not process Aadhaar card."}

def process_passport(image_path):
    try:
        user_info = {}
        tmp_img_path = 'tmp_mrz.png'
        mrz = read_mrz(image_path, save_roi=True)

        if not mrz:
            return {"error": "Could not read MRZ from passport."}

        mpimg.imsave(tmp_img_path, mrz.aux['roi'], cmap='gray')
        img = cv2.imread(tmp_img_path)
        img = cv2.resize(img, (1110, 140))
        
        allowlist = st.ascii_letters + st.digits + '< '
        code = reader.readtext(img, paragraph=False, detail=0, allowlist=allowlist)
        a, b = code[0].upper(), code[1].upper()
        
        a = a.ljust(44, '<')
        b = b.ljust(44, '<')
        
        surname, names = (a[5:44].split('<<', 1) + [''])[:2]
        
        user_info['name'] = names.replace('<', ' ').strip()
        user_info['surname'] = surname.replace('<', ' ').strip()
        user_info['sex'] = get_sex(clean(b[20]))
        user_info['date_of_birth'] = parse_date(b[13:19])
        user_info['passport_number'] = clean(b[0:9])
        
        os.remove(tmp_img_path)

        return {
            "name": f"{user_info.get('name', '')} {user_info.get('surname', '')}".strip(),
            "gender": user_info.get('sex', ''),
            "dob": user_info.get('date_of_birth', ''),
            "document_number": user_info.get('passport_number', ''),
        }
    except Exception as e:
        print(f"Passport processing error: {e}")
        os.remove(tmp_img_path) if os.path.exists(tmp_img_path) else None
        return {"error": "Could not process passport."}

def process_driving_licence(image_path):
    # Placeholder for driving licence logic
    return {
        "error": "Driving Licence OCR is not yet implemented.",
        "name": "N/A", "dob": "N/A", "document_number": "N/A"
    }

def process_document(image_path, doc_type):
    """Main function to route to the correct OCR processor."""
    if doc_type == 'aadhaar':
        return process_aadhaar(image_path)
    elif doc_type == 'passport':
        return process_passport(image_path)
    elif doc_type == 'driving_licence':
        return process_driving_licence(image_path)
    else:
        return {"error": "Invalid document type selected."}