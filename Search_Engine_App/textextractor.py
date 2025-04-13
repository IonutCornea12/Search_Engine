# textextractor.py

import os
from PIL import Image
import pytesseract
import fitz

class TextExtractor:
    def extract(self, file_path):
        _, ext = os.path.splitext(file_path.lower())

        if ext == ".txt":
            return self._extract_txt(file_path)
        elif ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext in [".png", ".jpg", ".jpeg", ".bmp"]:
            return self._extract_image(file_path)
        else:
            return ""

    def _extract_txt(self, file_path):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        except Exception as e:
            print(f"Failed to extract text file {file_path}: {e}")
            return ""

    def _extract_pdf(self, file_path):
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            print(f"Failed to extract from PDF {file_path}: {e}")
        return text

    def _extract_image(self, file_path):
        text = ""
        try:
            with Image.open(file_path) as img:
                text = pytesseract.image_to_string(img)
        except Exception as e:
            print(f"Failed to extract image {file_path}: {e}")
        return text