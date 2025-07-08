from utils.pdf_cache import get_pdf_text_cached

pdf_filename = "oc032025.pdf"
text = get_pdf_text_cached(pdf_filename)
print(f"Read {len(text)} characters from {pdf_filename}")
print(text[:500])  # Print first 500 characters to check
