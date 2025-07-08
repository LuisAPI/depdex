import os
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer

# Load embedder
model = SentenceTransformer("all-MiniLM-L6-v2")

# Create Chroma client (persistent)
client = chromadb.PersistentClient(path="vectorstore")
collection = client.get_or_create_collection("txt_knowledge")

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i+chunk_size])
    return chunks

def ingest_txt_folder(folder_path="knowledge"):
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = chunk_text(content)
            embeddings = model.encode(chunks).tolist()
            ids = [f"{filename}-{i}" for i in range(len(chunks))]

            collection.add(
                documents=chunks,
                embeddings=embeddings,
                ids=ids,
                metadatas=[{"source": filename}] * len(chunks)
            )
            print(f"✅ Ingested {filename}: {len(chunks)} chunks")

# Run this when new files are added
if __name__ == "__main__":
    ingest_txt_folder()
