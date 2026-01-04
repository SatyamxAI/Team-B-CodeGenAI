import pytesseract
import cv2
import numpy as np
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_file):
    image = Image.open(image_file).convert("RGB")
    img = np.array(image)

    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = cv2.medianBlur(gray, 3)

    custom_config = r"""
    --oem 3
    --psm 6
    -c preserve_interword_spaces=1
    -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_()[]{}.,:+-*/="'<>
    """

    return pytesseract.image_to_string(gray, config=custom_config).strip()