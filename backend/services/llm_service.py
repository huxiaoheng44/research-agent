import os

from openai import AsyncOpenAI


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI()
        
    async def create_stream(self, input_items, tools=None, previous_response_id=None):
        return await self.client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-5.6"),
            instructions=(
                "You are a research agent. "
                "Answer research questions accurately and concisely. "
                "The user message may contain vetted excerpts from uploaded "
                "files. Use them only when they directly support the answer, "
                "but do not add a source list. Do not claim to have "
                "consulted uploaded files when no excerpts were provided. "
                "Return the final answer in Markdown."
            ),
            input=input_items,
            tools=tools or [],
            previous_response_id=previous_response_id,
            stream=True,
        )

    async def create_judgment_response(self, input_items, instructions: str):
        """Create a small non-streaming response for internal agent decisions."""
        return await self.client.responses.create(
            model=os.getenv("LOCAL_JUDGE_MODEL", "gpt-5.6-luna"),
            instructions=instructions,
            input=input_items,
        )
