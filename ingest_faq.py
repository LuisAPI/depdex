# scripts/ingest_faq.py
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="faq")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def load_faqs(path="knowledge/depdev.txt"):
    with open(path, "r", encoding="utf-8") as f:
        blocks = f.read().split("\n\n")
        docs = [b.strip() for b in blocks if b.strip()]
    return docs

docs = load_faqs()
embeddings = embedder.encode(docs).tolist()

collection.add(documents=docs, embeddings=embeddings, ids=[f"id_{i}" for i in range(len(docs))])
print("✅ FAQ knowledge ingested.")
