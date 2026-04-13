"""
User memory store using local ChromaDB.
"""
import re
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from datetime import datetime
from friday.config import config

chroma_client = chromadb.PersistentClient(path=config.MEMORY_DB_PATH)
model = SentenceTransformer('all-MiniLM-L6-v2')
collection = chroma_client.get_or_create_collection(name="user_memory")

FACT_RULES = ['like', 'love', 'prefer', 'want', 'habit', 'favorite', 'remember', 'know that', 'my name is']

def register(mcp):
    @mcp.tool()
    def remember_fact(text: str, user_id: str = "boss") -> str:
        \"\"\"
        Store a user preference, fact, or summarized convo to persistent memory.
        Auto-detects important facts from text (e.g., "I like stocks").
        \"\"\"
  if any(kw in text.lower() for kw in FACT_RULES):\n            summary = text[:200]\n        else:\n            summary = text[:200]
        
        embedding = model.encode([summary])[0].tolist()
metadata = {
    "type": "user_pref" if any(kw in text.lower() for kw in FACT_RULES) else "fact",
    "user_id": user_id,
    "timestamp": datetime.now().isoformat(),
    "raw_text": text,
    "importance": score_memory(summary)
}
from .cleaner import score_memory
        
        ids = collection.add(
            embeddings=[embedding],
            documents=[summary],
            metadatas=[metadata],
            ids=[f"mem_{int(datetime.now().timestamp()*1000)}"]
        )['ids'][0]
        
        return f"Remembered: {summary} (ID: {ids})"
