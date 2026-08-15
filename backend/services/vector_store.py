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