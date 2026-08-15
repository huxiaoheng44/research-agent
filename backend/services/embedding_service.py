from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        
        return self.model.encode(texts, normalize_embeddings=True)
    
    def embed_query(self, query: str) -> list[float]:
        if not query:
            return []
        
        return self.model.encode(query, normalize_embeddings=True)