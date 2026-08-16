import json
from collections.abc import AsyncIterator
import asyncio

from agent.tool_definitions import TOOLS
from agent.tools import search_uploaded_sources
from dependencies import llm_service

class ResearchAgent:
    async def stream(self, query: str) -> AsyncIterator[str]:
        """Stream the final model answer while handling any function-call rounds."""
        input_items = [{"role": "user", "content": query}]
        previous_response_id = None

        # Limit tool round trips to prevent an accidental infinite tool loop.
        for _ in range(5):
            stream = await llm_service.create_stream(
                input_items,
                tools=TOOLS,
                previous_response_id=previous_response_id,
            )
            tool_calls = []
            response_id = None
            emitted_text = False

            async for event in stream:
                if event.type == "response.output_text.delta":
                    emitted_text = True
                    yield event.delta
                elif event.type == "response.output_item.done":
                    item = event.item
                    if item.type == "function_call":
                        tool_calls.append(item)
                        # Forward the raw local-tool request 
                        try:
                            query = json.loads(item.arguments).get("query", item.arguments)
                        except json.JSONDecodeError:
                            query = item.arguments
                        yield f"[TOOL] {item.name}: {query}\n"
                elif event.type == "response.completed":
                    response_id = event.response.id
                elif event.type == "response.failed":
                    raise RuntimeError(event.response.error.message)

            # A response without function calls is the final response.
            if not tool_calls:
                if emitted_text:
                    return
                raise RuntimeError("Model returned no tool call and no final text.")

            if not response_id:
                raise RuntimeError("Tool-call response completed without a response ID.")

            tool_outputs = await asyncio.gather(
                *(self._execute_tool(tool_call) for tool_call in tool_calls)
            )
            input_items = [
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": output,
                }
                for tool_call, output in zip(tool_calls, tool_outputs)
            ]
            previous_response_id = response_id

        raise RuntimeError("Exceeded maximum tool rounds without reaching a final answer.")

    async def _execute_tool(self, tool_call) -> str:
        arguments = json.loads(tool_call.arguments)
        
        if tool_call.name == "search_uploaded_sources":
            # Run outside the event loop so a streaming request stays responsive.
            return await asyncio.to_thread(search_uploaded_sources, query=arguments["query"])
        
        raise Exception(f"Unknown tool: {tool_call.name}")
