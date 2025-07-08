# utils/knowledge_search.py
import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_or_create_collection(name="faq")
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def search_knowledge(query: str, top_k: int = 2) -> str:
    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )
    if results["documents"]:
        return "\n\n".join([doc for doc in results["documents"][0]])
    return ""
