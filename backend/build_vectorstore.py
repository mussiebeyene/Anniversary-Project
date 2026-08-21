import os
import shutil
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from chunk_conversations import group_into_sessions

load_dotenv()

CHROMA_PATH = "data/chroma_db"

def rebuild_vectorstore():
    # 1. Clean up old vector store directory if it exists
    if os.path.exists(CHROMA_PATH):
        print(f"🗑️ Removing old ChromaDB instance at '{CHROMA_PATH}'...")
        shutil.rmtree(CHROMA_PATH)

    # 2. Load fresh chunks from the updated cleaned_chat_history.csv
    print("⏳ Processing chat history into session chunks...")
    raw_documents = group_into_sessions(
        csv_path="data/cleaned_chat_history.csv", 
        gap_minutes=30
    )

    # 3. Convert dicts to LangChain Document objects
    langchain_docs = [
        Document(
            page_content=doc["page_content"],
            metadata=doc["metadata"]
        )
        for doc in raw_documents
    ]

    print(f"📦 Total chunks to embed: {len(langchain_docs)}")

    # 4. Generate Embeddings & Save to ChromaDB
    print("⚡ Generating OpenAI embeddings and indexing in ChromaDB...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Batch process documents into ChromaDB
    vector_store = Chroma.from_documents(
        documents=langchain_docs,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
        collection_name="imessage_memory"
    )

    print("✅ Vector database successfully built and persisted to disk!")

if __name__ == "__main__":
    rebuild_vectorstore()