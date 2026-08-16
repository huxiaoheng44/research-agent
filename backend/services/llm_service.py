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
                "Use tools when they provide relevant evidence. "
                "Use search_uploaded_sources when the question may depend "
                "on files uploaded by the user. "
                "Do not use tools when they are unnecessary. "
                "When you use uploaded sources, mention the source filename. "
                "Return the final answer in Markdown."
            ),
            input=input_items,
            tools=tools or [],
            previous_response_id=previous_response_id,
            stream=True,
        )
