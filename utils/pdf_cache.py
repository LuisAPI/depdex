import os
from PyPDF2 import PdfReader

def get_pdf_text_cached(pdf_filename: str) -> str:
    pdf_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pdfs", pdf_filename))
    cache_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "cache", pdf_filename.replace(".pdf", ".txt")))

    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(text)

    return text
