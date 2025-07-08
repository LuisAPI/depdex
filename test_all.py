import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from tqdm import tqdm

# --- Configuration ---
CHROMA_DIR = "chroma_db"
PDP_PATH = "pdp.txt"
EMBED_MODEL = "llama3"

# --- Load PDP text ---
if not os.path.exists(PDP_PATH):
    print(f"❌ PDP file not found at {PDP_PATH}")
    exit(1)

loader = TextLoader(PDP_PATH, encoding="utf-8")
docs = loader.load()
print(f"📄 Loaded {len(docs)} document(s) from {PDP_PATH}")

# --- Split text into chunks ---
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.split_documents(docs)
print(f"🔖 Split into {len(chunks)} chunks")

# --- Prepare embedding function ---
embedding_function = OllamaEmbeddings(model=EMBED_MODEL)

# --- Manual embedding with progress ---
print("⚙️ Now embedding chunks into Chroma DB...")

texts = []
for doc in tqdm(chunks, desc="🔄 Embedding PDP Chunks", unit="chunk"):
    texts.append(doc.page_content)

# --- Load or create Chroma vectorstore ---
vectorstore = Chroma(
    embedding_function=embedding_function,
    persist_directory=CHROMA_DIR
)

# --- Add new texts and persist ---
vectorstore.add_texts(texts)
vectorstore.persist()

print("✅ Done! PDP chunks were appended and saved to Chroma DB.")
