import os
import re
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rank_bm25 import BM25Okapi
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from chunk_conversations import group_into_sessions

load_dotenv(PROJECT_ROOT / ".env", override=True)
load_dotenv(BACKEND_DIR / ".env", override=True)

CHROMA_PATH = str(PROJECT_ROOT / "data" / "chroma_db")
CSV_PATH = str(PROJECT_ROOT / "data" / "cleaned_chat_history.csv")

class HybridChatRetriever:
    def __init__(self):
        # 1. Initialize Vector Database connection
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = Chroma(
            persist_directory=CHROMA_PATH, 
            embedding_function=self.embeddings, 
            collection_name="imessage_memory"
        )
        
        # 2. Build in-memory BM25 Keyword Search index
        self.raw_docs = group_into_sessions(csv_path=CSV_PATH)
        self.corpus = [doc['page_content'] for doc in self.raw_docs]
        tokenized_corpus = [doc.lower().split() for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)
        
    def search(self, query: str, top_k: int = 15):
        # A. Vector Similarity Search
        vector_results = self.vector_store.similarity_search(query, k=top_k)
        
        # B. BM25 Exact Keyword Search
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
        
        # C. Reciprocal Rank Fusion (RRF) Reranking
        rrf_scores = {}
        for rank, doc in enumerate(vector_results):
            content = doc.page_content
            rrf_scores[content] = rrf_scores.get(content, 0) + (1.0 / (60 + rank + 1))
            
        for rank in top_bm25_indices:
            content = self.corpus[rank]
            rrf_scores[content] = rrf_scores.get(content, 0) + (1.0 / (60 + rank + 1))
            
        # Sort combined documents by hybrid score
        sorted_contents = sorted(rrf_scores.keys(), key=lambda c: rrf_scores[c], reverse=True)[:top_k]
        
        # D. Date / Temporal Awareness Sorting
        # D. Date / Temporal Awareness Sorting
        if any(w in query.lower() for w in ['first', 'earliest', 'begin', 'start', 'oldest']):
            def parse_date(content):
                # Search for the date header
                match = re.search(r"Date:\s*([\d\-\:\s]+)", content)
                if match:
                    date_str = match.group(1).strip()
                    try:
                        # Explicitly parse the YYYY-MMWhe-DD HH:MM format from your chunker
                        return datetime.strptime(date_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        pass 
                
                # If no valid date is found, push to the bottom of the list
                return datetime.max 

            # Sort chronologically using the true datetime objects
            sorted_contents.sort(key=parse_date)

        return sorted_contents

def start_hybrid_agent():
    retriever = HybridChatRetriever()
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    prompt = ChatPromptTemplate.from_template("""You are a romantic iMessage chat memory assistant.
Analyze the retrieved conversation fragments below to answer the question.

Rules:
1. Synthesize fragmented context intelligently (messages span back and forth over time).
2. If answering "first" or chronological queries, rely on the date headers attached to each block.
3. If the context contains partial information, state what IS known and what remains unclear.
4. If context gives zero relevance, say "I couldn't find that memory in your chat history."

Chat Context:
{context}

User Question: {question}

Detailed Answer:""")

    print("\n🚀 Hybrid Memory Agent Ready! Type 'quit' to exit.\n")
    while True:
        query = input("You: ")
        if query.lower() in ['quit', 'exit', 'q']: break
        
        retrieved_chunks = retriever.search(query, top_k=12)
        context_str = "\n\n---\n\n".join(retrieved_chunks)
        
        chain = prompt | llm | StrOutputParser()
        response = chain.invoke({"context": context_str, "question": query})
        print(f"\nAI: {response}\n")

if __name__ == "__main__":
    start_hybrid_agent()