import time
import logging
import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.background import BackgroundTask
from glob import glob

from utils.rss_cache import get_latest_rss_summaries_cached
from utils.pdf_cache import get_pdf_text_cached
from prompts.system_prompt import get_system_prompt
from utils.knowledge_search import search_knowledge

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

logging.basicConfig(
    filename="chat_audit.log",
    level=logging.INFO,
    format="%(asctime)s | %(message)s",
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_API = "http://localhost:11434/api/chat"

class ChatRequest(BaseModel):
    message: str
    model: str = "llama3"

# --- Utility Checks ---

def should_include_pdf(message: str) -> bool:
    keywords = ["office circular", "OC"]
    return any(kw.lower() in message.lower() for kw in keywords)

def is_rss_used(message: str) -> bool:
    keywords = ["news", "latest updates", "rss", "current events", "headlines"]
    return any(kw.lower() in message.lower() for kw in keywords)

def should_include_pdp(message: str) -> bool:
    keywords = [
        "pdp",
        "philippine development plan",
        "development strategy",
        "socioeconomic agenda",
        "pdp chapter",
        "pillar",
        "enabler",
        "goal",
        "vision",
        "ambisyon natin",
        "pdp target",
        "strategy framework"
    ]
    return any(kw.lower() in message.lower() for kw in keywords)

def get_txt_knowledge(directory="knowledge"):
    knowledge_texts = []
    for file_path in glob(os.path.join(directory, "*.txt")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                knowledge_texts.append(content.strip())
        except Exception as e:
            print(f"⚠️ Error reading {file_path}: {e}")
    return "\n\n".join(knowledge_texts)

# --- Load Chroma for PDP ---

CHROMA_DIR = "chroma_db"
embedding_function = OllamaEmbeddings(model="llama3")
vectorstore = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding_function)

# --- Chat Route ---

@app.post("/chat")
async def chat(req: ChatRequest, request: Request):
    total_start = time.perf_counter()

    print(f"\n🔵 Received message: {req.message}")

    # Load RSS
    rss_used = is_rss_used(req.message)
    latest_news = get_latest_rss_summaries_cached() if rss_used else ""
    print(f"📡 RSS used: {rss_used} | Length: {len(latest_news)}")

    # Load PDF if needed
    pdf_text = ""
    if should_include_pdf(req.message):
        pdf_filename = "oc032025.pdf"
        pdf_path = os.path.join("pdfs", pdf_filename)
        if os.path.exists(pdf_path):
            pdf_text = get_pdf_text_cached(pdf_filename)
            print(f"📄 PDF found: {pdf_filename} | {len(pdf_text)} chars")
        else:
            print(f"❌ PDF not found at {pdf_path}")
    else:
        print("📭 PDF not included for this request.")

    short_pdf_text = pdf_text[:8000]

    # Knowledge base search
    knowledge_text = search_knowledge(req.message)
    print(f"📚 Knowledge match: {bool(knowledge_text)} | {len(knowledge_text)} chars")

    # Text file knowledge
    text_file_knowledge = get_txt_knowledge()
    print(f"📂 Loaded text file knowledge: {len(text_file_knowledge)} chars")

    # PDP knowledge (vector search)
    pdp_knowledge = ""
    if should_include_pdp(req.message):
        try:
            pdp_results = vectorstore.similarity_search(req.message, k=3)
            pdp_knowledge = "\n\n".join([doc.page_content for doc in pdp_results])
            print(f"📘 PDP results found: {len(pdp_results)} docs, {len(pdp_knowledge)} chars")
        except Exception as e:
            print(f"❌ Error searching PDP: {e}")
    else:
        print("📘 PDP not included for this message.")

    # Build system prompt
    combined_knowledge = knowledge_text + "\n\n" + text_file_knowledge
    system_prompt = get_system_prompt(
        latest_news=latest_news,
        pdf_text=short_pdf_text,
        knowledge_text=combined_knowledge,
        pdp_text=pdp_knowledge
    )

    print("🧠 Final System Prompt Preview:\n", system_prompt[:800])

    # Ollama payload
    payload = {
        "model": req.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.message},
        ],
        "stream": True,
    }

    full_answer_container = {"text": ""}
    first_chunk_time = None

    def generator():
        nonlocal first_chunk_time
        try:
            # Add a timeout to the Ollama API call (30 seconds)
            response = requests.post(OLLAMA_API, json=payload, stream=True, timeout=60)
            if response.status_code != 200:
                yield f"⚠️ Ollama error {response.status_code}"
                return

            for line in response.iter_lines():
                if line:
                    try:
                        if first_chunk_time is None:
                            first_chunk_time = time.perf_counter()
                        chunk = line.decode("utf-8")
                        if chunk.startswith("data: "):
                            chunk = chunk[6:]
                        full_answer_container["text"] += chunk
                        yield chunk
                    except Exception as e:
                        yield f"⚠️ Error streaming chunk: {e}"
                        return
        except Exception as e:
            yield f"❌ Could not reach Ollama API: {e}"
            return

    def log_chat():
        total_end = time.perf_counter()
        logging.info(
            f"Chat request | IP: {request.client.host} | Model: {req.model} | "
            f"Message: {req.message} | "
            f"RSS: {rss_used} | "
            f"PDF: {bool(pdf_text)} | "
            f"Knowledge: {bool(knowledge_text)} | "
            f"PDP: {bool(pdp_knowledge)} | "
            f"TXT: {bool(text_file_knowledge)} | "
            f"Total time: {total_end - total_start:.2f}s | "
            f"First chunk in: {(first_chunk_time - total_start) if first_chunk_time else 0:.2f}s | "
            f"Answer length: {len(full_answer_container['text'])}"
        )

    print("🟢 Starting response stream...")
    return StreamingResponse(generator(), media_type="text/event-stream", background=BackgroundTask(log_chat))

# --- Test endpoint for debugging Ollama ---

@app.get("/test")
async def test():
    payload = {
        "model": "llama3",
        "messages": [{"role": "user", "content": "Say hello"}],
        "stream": False,
    }
    try:
        response = requests.post(OLLAMA_API, json=payload)
        if response.status_code == 200:
            return response.json()
        return JSONResponse(status_code=500, content={"error": f"Ollama returned {response.status_code}"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# --- Serve frontend ---

# Serve static files from /static to avoid API route conflicts
app.mount("/static", StaticFiles(directory=".", html=True), name="static")
