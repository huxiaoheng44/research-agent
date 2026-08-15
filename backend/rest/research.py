import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dependencies import embedding_service, vector_store

router = APIRouter()

class ResearchRequest(BaseModel):
    request: str


async def generate_response(request: str):
    
    query_embedding = embedding_service.embed_query(request)
    
    results = vector_store.search(query_embedding, top_k=5)
    
    yield f"## Research Results for: {request}\n\n"
    
    if not results:
        yield "No relevant documents found.\n"
        return

    for result in results:
        yield f"### Source: {result['source']} (Chunk Index: {result['chunk_index']})\n"
        yield f"Score: {result['score']:.4f}\n\n"
        yield f"{result['text']}\n\n"


@router.post("/research")
async def research(body: ResearchRequest):
    response_generator = generate_response(body.request)
    return StreamingResponse(response_generator, media_type="text/markdown")