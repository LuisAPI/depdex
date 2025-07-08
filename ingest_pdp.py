from sentence_transformers import SentenceTransformer
import chromadb
from utils.pdf_splitter import extract_pdf_text, chunk_text

pdf_path = "pdfs/pdp.pdf"
text = extract_pdf_text(pdf_path)
chunks = chunk_text(text)

embedder = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = embedder.encode(chunks)

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="faq")

# Clear existing PDP entries if needed
collection.delete(where={"source": "pdp"})

# Add new PDP entries
for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
    collection.add(
        documents=[chunk],
        embeddings=[embedding],
        ids=[f"pdp-{i}"],
        metadatas=[{"source": "pdp"}]
    )

print(f"✅ PDP chunks saved to ChromaDB: {len(chunks)}")
