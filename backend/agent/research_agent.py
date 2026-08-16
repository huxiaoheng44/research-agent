import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any

from agent.tool_definitions import WEB_SEARCH_TOOLS
from dependencies import llm_service, local_evidence_judge


class ResearchAgent:
    """Streams answers with judged local evidence and optional web search."""

    def __init__(self, llm_client=llm_service, evidence_judge=local_evidence_judge):
        self.llm_client = llm_client
        self.evidence_judge = evidence_judge

    async def stream(self, query: str) -> AsyncIterator[str]:
        yield "[LOCAL] Searching uploaded files...\n"
        evidence_packet = await self._assess_local_evidence(query)
        selected_chunks = evidence_packet["selected_chunks"]
        if not selected_chunks:
            yield "[LOCAL] No relevant information was found in uploaded sources.\n"
        else:
            yield f"[LOCAL] Found {len(selected_chunks)} relevant uploaded excerpts.\n"

        input_items = self._build_input(query, evidence_packet)
        stream = await self.llm_client.create_stream(input_items, tools=WEB_SEARCH_TOOLS)
        emitted_text = False

        async for event in stream:
            if event.type == "response.output_text.delta":
                emitted_text = True
                yield event.delta
            elif event.type == "response.web_search_call.in_progress":
                yield "[WEB] Searching the web...\n"
            elif event.type == "response.failed":
                raise RuntimeError(event.response.error.message)

        if not emitted_text:
            raise RuntimeError("Model returned no final text.")

        for source in self._source_names(selected_chunks):
            yield f"\n\nSource: {source}"

    async def _assess_local_evidence(self, query: str) -> dict[str, Any]:
        try:
            return await asyncio.wait_for(self.evidence_judge.assess(query), timeout=8)
        # errors in the local evidence judge do not prevent the research agent from returning a response
        except TimeoutError:
            print("[ERROR] Local evidence judge timed out", flush=True)
            return {"selected_chunks": []}
        except Exception:
            print("[ERROR] Local evidence judge failed", flush=True)
            return {"selected_chunks": []}

    @staticmethod
    def _build_input(
        query: str,
        evidence_packet: dict[str, Any],
    ) -> list[dict[str, str]]:
        content: dict[str, Any] = {"question": query}
        selected_chunks = evidence_packet["selected_chunks"]
        if selected_chunks:
            content["local_evidence"] = selected_chunks
        content["local_evidence_status"] = {
            "is_sufficient": bool(evidence_packet.get("is_sufficient")),
            "selected_count": len(selected_chunks),
        }

        return [{"role": "user", "content": json.dumps(content, ensure_ascii=False)}]

    @staticmethod
    def _source_names(selected_chunks: list[dict[str, Any]]) -> list[str]:
        # Return unique local filenames in their first-seen order.
        return list(dict.fromkeys(chunk["source"] for chunk in selected_chunks if chunk.get("source")))
