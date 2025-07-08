import os
import PyPDF2
import chromadb
from sentence_transformers import SentenceTransformer

# --- Settings ---
PDF_FILE = "pdfs/pdp.pdf"
COLLECTION_NAME = "faq"
CHUNK_SIZE = 500
OVERLAP = 50

# --- Step 1: Load PDF ---
def extract_pdf_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text

# --- Step 2: Chunk the text ---
def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap
    return chunks

# --- Step 3: Embed and store in Chroma ---
text = extract_pdf_text(PDF_FILE)
chunks = chunk_text(text, CHUNK_SIZE, OVERLAP)

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name=COLLECTION_NAME)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Add the chunks to Chroma
collection.add(
    documents=chunks,
    metadatas=[{"source": "pdp"} for _ in chunks],
    ids=[f"pdp_{i}" for i in range(len(chunks))]
)

print(f"✅ Added {len(chunks)} PDP chunks to '{COLLECTION_NAME}' collection.")
