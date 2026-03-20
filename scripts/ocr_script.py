import cv2
import pytesseract
import numpy as np
import re
from aadhaar_read import front_data, back_data
import os
import string as st
from dateutil import parser
import matplotlib.image as mpimg
import cv2
from passporteye import read_mrz
import json
import easyocr
import warnings
warnings.filterwarnings('ignore')

# Path to tesseract executable (Windows only)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Update if needed




def adhaar(front):
    img = cv2.imread(front)
    #Replace with tesseract path on your system
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    # Convert to GrayScale
    gr = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Create a binary mask for dark black regions
    mask = gr <= 180
    # Create an all-white image
    gray = np.ones_like(gr) * 255
    # Apply the mask to keep dark black regions
    gray[mask] = gr[mask]
    # getting all values (except address) from Front Aadhaar Card Image
    regex_name,regex_gender,regex_dob,regex_aadhaar_number = front_data(gray)
    regex_name = " ".join(regex_name[:3])
    #print("Name :", regex_name)
    #print("Gender :",regex_gender)
    #print("DOB/Year :",regex_dob)
    #print("Aadhaar Number :",regex_aadhaar_number)

    # gr = cv2.cvtColor(back, cv2.COLOR_BGR2GRAY)
    # # Create a binary mask for dark black regions
    # mask = gr <= 180
    # # Create an all-white image
    # gray = np.ones_like(gr) * 255
    # # Apply the mask to keep dark black regions
    # gray[mask] = gr[mask]
    # # # Keep only the english address part of the image, below we kept only right half
    # # crop_img = gray[:, int(gray.shape[1]/2):]
    # height, width = gray.shape[:2]

    # # Crop from 30% height to the bottom, and right half horizontally
    # crop_img = gray[int(height * 0.3):, int(width / 2):]
    # # getting address back
    # regex_address = back_data(crop_img)
    # #print("Address :", regex_address)
    
    return {
    "name": regex_name,
    "document_number": regex_aadhaar_number,
    "dob": regex_dob,
    "gender": regex_gender
}


# lOAD OCR ENGINE (easyOCR)
reader=easyocr.Reader(lang_list=['en'], gpu=False)  # Enable gpu if available


with open('country_codes.json') as f:
    country_codes = json.load(f)
    
def parse_date(string, iob=True):
    date = parser.parse(string, yearfirst=True).date() 
    return date.strftime('%d/%m/%Y')

def clean(string):
    return ''.join(i for i in string if i.isalnum()).upper()

def get_country_name(country_code):
    country_name = ''
    for country in country_codes:
        if country['alpha-3'] == country_code:
            country_name = country['name']
            return country_name.upper()
    return country_code

def get_sex(code):
    if code in ['M', 'm', 'F', 'f']:
        sex = code.upper() 
    elif code == '0':
        sex = 'M'
    else:
        sex = 'F'
    return sex

def print_data(data):
    for key in data.keys():
        info = key.replace('_', ' ').capitalize()
        print(f'{info}\t:\t{data[key]}')
    return
  
def passport(img_name):

    user_info = {}    
    new_im_path = 'tmp.png'
    im_path = img_name
    # Crop image to Machine Readable Zone(MRZ)
    mrz = read_mrz(im_path, save_roi=True)

    if mrz:
        mpimg.imsave(new_im_path, mrz.aux['roi'], cmap='gray')
    
        img = cv2.imread(new_im_path)
        img = cv2.resize(img, (1110, 140))
        
        allowlist = st.ascii_letters+st.digits+'< '
        code = reader.readtext(img, paragraph=False, detail=0, allowlist=allowlist)
        a, b = code[0].upper(), code[1].upper()
        
        if len(a) < 44:
            a = a + '<'*(44 - len(a))
        if len(b) < 44:
                b = b + '<'*(44 - len(b))
                
        surname_names = a[5:44].split('<<', 1)
        if len(surname_names) < 2:
            surname_names += ['']
        surname, names = surname_names
        
        user_info['name'] = names.replace('<', ' ').strip().upper()
        user_info['surname'] = surname.replace('<', ' ').strip().upper()
        user_info['sex'] = get_sex(clean(b[20]))
        user_info['date_of_birth'] = parse_date(b[13:19])
        user_info['nationality'] = get_country_name(clean(b[10:13]))
        user_info['passport_type'] = clean(a[0:2])
        user_info['passport_number']  = clean(b[0:9])
        user_info['issuing_country'] = get_country_name(clean(a[2:5]))
        user_info['expiration_date'] = parse_date(b[21:27])
        user_info['personal_number'] = clean(b[28:42])
        
    else:
        return print(f'Machine cannot read image {img_name}.')
    
    os.remove(new_im_path)
    
    return {
        "name": user_info.get('name', ''),
        "surname": user_info.get('surname', ''),
        "gender": user_info.get('sex', ''), # Mapped 'sex' to 'gender' for consistency
        "dob": user_info.get('date_of_birth', ''), # Mapped 'date_of_birth' to 'dob' for consistency
        "document_number": user_info.get('passport_number', ''), # Mapped 'passport_number' to 'document_number'
        "issuing_country": user_info.get('issuing_country', '')
        # You can add other fields from user_info if your app.py or PDF generation needs them, e.g.:
        # "nationality": user_info.get('nationality', ''),
        # "passport_type": user_info.get('passport_type', ''),
        # "expiration_date": user_info.get('expiration_date', ''),
        # "personal_number": user_info.get('personal_number', '')
    }



def drivingLicence(img):
    
    return "name","dob","valid_till","address","issuing_authority"


# print(adhaar("./adhaar_front.jpg"))
# print(passport("./passport.jpg"))
# print(drivingLicence("./driving_licence.jpg"))
