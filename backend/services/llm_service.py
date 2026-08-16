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
                "You have a web search tool and should decide whether to use "
                "it: use it when local evidence is absent or insufficient, "
                "when the user requests external/current information, or when "
                "verification would materially improve accuracy. "
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
