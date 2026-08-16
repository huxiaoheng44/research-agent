from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.agent_container import research_agent


router = APIRouter()

class ResearchRequest(BaseModel):
    request: str


async def generate_response(request: str):
    try:
        async for chunk in research_agent.stream(request):
            yield chunk
    except Exception:
        # Headers have already been sent once streaming starts, so surface a safe
        # Markdown error to the existing streaming client and keep details in logs.
        print("[ERROR] Research stream failed", flush=True)
        yield "\n\n> **Research failed.** Please try again later.\n"


@router.post("/research")
async def research(body: ResearchRequest):
    if not body.request.strip():
        raise HTTPException(status_code=400, detail="Research request must not be empty.")

    return StreamingResponse(
        generate_response(body.request),
        media_type="text/markdown; charset=utf-8",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
