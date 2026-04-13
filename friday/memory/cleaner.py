import chromadb
from friday.config import config

client = chromadb.PersistentClient(path=config.MEMORY_DB_PATH)
collection = client.get_collection("user_memory")

def score_memory(doc: str) -> float:
    score = len(doc.split()) * 0.1  # Length
    if any(kw in doc.lower() for kw in ['like', 'prefer', 'remember']):
        score += 2
    return score

def cleanup(low_threshold=1.0):
    results = collection.query(query_texts=[""], n_results=1000)
    docs = results['documents'][0]
    ids = []
    for i, doc in enumerate(docs):
        if score_memory(doc) < low_threshold:
            ids.append(results['ids'][0][i])
    if ids:
        collection.delete(ids=ids)
        print(f"Cleaned {len(ids)} low-score memories.")

