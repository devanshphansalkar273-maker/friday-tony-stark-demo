"""
User memory store using local ChromaDB.
"""
import re
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from datetime import datetime
from friday.config import config

# Initialize chroma client lazily or handle errors
try:
    chroma_client = chromadb.PersistentClient(path=config.MEMORY_DB_PATH)
    collection = chroma_client.get_or_create_collection(name="user_memory")
except Exception as e:
    print(f"ChromaDB Init Error: {e}")
    collection = None

# Load model lazily
_model = None
def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

FACT_RULES = ['like', 'love', 'prefer', 'want', 'habit', 'favorite', 'remember', 'know that', 'my name is']

def store_memory(text: str, user_id: str = "boss") -> str:
    """Store a memory or preference."""
    if collection is None:
        return "Memory system unavailable."
    
    summary = text[:200]
    model = get_model()
    embedding = model.encode([summary])[0].tolist()
    
    metadata = {
        "type": "user_pref" if any(kw in text.lower() for kw in FACT_RULES) else "fact",
        "user_id": user_id,
        "timestamp": datetime.now().isoformat(),
        "raw_text": text
    }
    
    mem_id = f"mem_{int(datetime.now().timestamp()*1000)}"
    collection.add(
        embeddings=[embedding],
        documents=[summary],
        metadatas=[metadata],
        ids=[mem_id]
    )
    return f"Remembered: {summary}"

def retrieve_memory(text: str, user_id: str = "boss") -> str:
    """Retrieve relevant memories based on text."""
    if collection is None:
        return ""
    
    model = get_model()
    embedding = model.encode([text])[0].tolist()
    
    results = collection.query(
        query_embeddings=[embedding],
        n_results=3,
        where={"user_id": user_id}
    )
    
    if results['documents'] and results['documents'][0]:
        return " | ".join(results['documents'][0])
    return ""

def register(mcp):
    @mcp.tool()
    def remember_fact(fact: str, user_id: str = "boss") -> str:
        """
        Store an important fact or preference about the user.
        """
        return store_memory(fact, user_id=user_id)
