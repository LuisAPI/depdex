# utils/pdf_ingest.py

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import CharacterTextSplitter

import os

PDF_FOLDER = "pdfs"
DB_FOLDER = "vectorstore"

def ingest_pdfs():
    docs = []
    for filename in os.listdir(PDF_FOLDER):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(PDF_FOLDER, filename))
            docs.extend(loader.load())

    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    split_docs = text_splitter.split_documents(docs)

    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    db = FAISS.from_documents(split_docs, embedding_model)
    db.save_local(DB_FOLDER)
    print("✅ PDFs processed and stored in vector DB.")
