"""
User memory retrieval using ChromaDB semantic search.
"""
import chromadb
from sentence_transformers import SentenceTransformer
from friday.config import config

chroma_client = chromadb.PersistentClient(path=config.MEMORY_DB_PATH)
model = SentenceTransformer('all-MiniLM-L6-v2')
collection = chroma_client.get_collection(name="user_memory")

def register(mcp):
    @mcp.tool()
    def recall(query: str, top_k: int = 3, user_id: str = "boss") -> str:
        """
        Retrieve top relevant memories semantically.
        """
        query_emb = model.encode([query])[0].tolist()
        
        results = collection.query(
            query_embeddings=[query_emb],
            n_results=top_k,
            where={"user_id": user_id}
        )
        
        if not results['documents'][0]:
            return "No relevant memories found, boss."
        
        memories = []
        for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
            memories.append(f"[{meta['type'].upper()}] {doc}")
        
        return '\\n'.join(memories)
