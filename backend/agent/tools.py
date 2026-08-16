from dependencies import embedding_service, vector_store

def search_uploaded_sources(query: str) -> str:
    print(f"[TOOL] search_uploaded_sources: {query}")
    
    query_embedding = embedding_service.embed_query(query)
    
    results = vector_store.search(query_embedding, top_k=5)
    
    if not results:
        return "No relevant information was found in uploaded sources."
    
    formatted_results = []
    
    for result in results:
        formatted_results.append(
            f"""
            Source: {result['source']} 
            Chunk Index: {result['chunk_index']}
            Similarity Score: {result['score']:.4f}
            {result['text']}
            """.strip()
        )
    
    return "\n".join(formatted_results)