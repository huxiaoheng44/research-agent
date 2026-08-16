import json

from agent.tool_definitions import TOOLS
from agent.tools import search_uploaded_sources
from dependencies import llm_service

class ResearchAgent:
    async def run(self, query: str) -> str:
        input_items = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await llm_service.create_response(input_items, tools=TOOLS)

        # Limit tool round trips to prevent an accidental infinite tool loop.
        for _ in range(5):
            
            # DEBUG: print the model's response
            print(f"[DEBUG] Model response: {response.output_text}")
            
            # Responses API emits function calls with type="function_call".
            tool_calls = [item for item in response.output if item.type == "function_call"]
            
            # final answer
            if not tool_calls:
                if response.output_text:
                    return response.output_text
                
                raise Exception("Model returned no tool call and no final text.")
            
            tool_outputs = []
            
            for tool_call in tool_calls:
                result = await self._execute_tool(tool_call)
                
                tool_outputs.append({
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": result,
                })
            
            # Continue from this response so the model receives its own function
            # call plus the corresponding outputs.  The resulting response must
            # be processed by the next loop iteration (rather than discarded).
            response = await llm_service.create_response(
                tool_outputs,
                tools=TOOLS,
                previous_response_id=response.id,
            )
        
        raise Exception("Exceeded maximum iterations without reaching a final answer.")
    
    async def _execute_tool(self, tool_call) -> str:
        arguments = json.loads(tool_call.arguments)
        
        if tool_call.name == "search_uploaded_sources":
            return search_uploaded_sources(query=arguments["query"])
        
        raise Exception(f"Unknown tool: {tool_call.name}")
