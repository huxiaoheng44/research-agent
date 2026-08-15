import asyncio
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

router = APIRouter()

class ResearchRequest(BaseModel):
    request: str


async def generate_response(request: str):
    markdown = f"""

## request

> {request}

## Result

This is a test streaming response.

This is a test streaming response.

This is a test streaming response.

This is a test streaming response.
"""

    for line in markdown.splitlines():
        yield line + "\n"
        await asyncio.sleep(0.1)


@router.post("/research")
async def research(body: ResearchRequest):
    response_generator = generate_response(body.request)
    return StreamingResponse(response_generator, media_type="text/markdown")