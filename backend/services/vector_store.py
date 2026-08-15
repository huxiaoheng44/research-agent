import numpy as np

# use in-memory vector store first
class VectorStore:
    def __init__(self):
        self.items = []
    
    def add(self, texts, embeddings, source: str):
        for index, (text, embedding) in enumerate(zip(texts, embeddings)):
            self.items.append({
                "text": text,
                "embedding": embedding,
                "source": source,
                "chunk_index": index,
            })
            
    def search(self, query_embedding, top_k=5):
        if not self.items:
            return []
        
        query_embedding = np.array(query_embedding)
        
        scored_items = []
        
        for item in self.items:
            embedding = item["embedding"]
            
            score = np.dot(query_embedding, embedding)
            
            scored_items.append({
                "text": item["text"],
                "source": item["source"],
                "chunk_index": item["chunk_index"],
                "score": float(score),
            })
            
        scored_items.sort(key=lambda x: x["score"], reverse=True)
        
        return scored_items[:top_k]