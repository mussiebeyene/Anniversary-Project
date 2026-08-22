import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))
os.chdir(PROJECT_ROOT)

load_dotenv(PROJECT_ROOT / ".env", override=True)
load_dotenv(BACKEND_DIR / ".env", override=True)

from hybrid_chat_agent import HybridChatRetriever

app = FastAPI(title="iMessage Memory RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = None
llm = None
prompt = ChatPromptTemplate.from_template("""You are an AI assistant powered by a couple's real chat history.
Context:
{context}

Question: {question}

Provide a friendly, warm, and highly detailed answer based on the context.""")


def get_retriever():
    global retriever
    if retriever is None:
        retriever = HybridChatRetriever()
    return retriever


def get_llm():
    global llm
    if llm is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is missing. Put it in .env as OPENAI_API_KEY=sk-...")
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    return llm


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        query = request.message
        chunks = get_retriever().search(query, top_k=10) or []
        context_str = "\n\n---\n\n".join(chunks)
        chain = prompt | get_llm() | StrOutputParser()
        answer = chain.invoke({"context": context_str, "question": query})
        return ChatResponse(answer=answer, sources=chunks[:3])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
