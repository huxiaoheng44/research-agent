import json
from collections.abc import AsyncIterator
from typing import Any

from dependencies import llm_service, local_evidence_judge


class ResearchAgent:
    """Streams answers using only local evidence selected by LocalEvidenceJudge."""

    def __init__(self, llm_client=llm_service, evidence_judge=local_evidence_judge):
        self.llm_client = llm_client
        self.evidence_judge = evidence_judge

    async def stream(self, query: str) -> AsyncIterator[str]:
        yield "[Agent] Searching uploaded files...\n"
        evidence_packet = await self._assess_local_evidence(query)
        selected_chunks = evidence_packet["selected_chunks"]
        if selected_chunks:
            yield f"[Agent] Found {len(selected_chunks)} relevant excerpts from uploaded files.\n"
        input_items = self._build_input(query, selected_chunks)
        stream = await self.llm_client.create_stream(input_items, tools=[])
        emitted_text = False

        async for event in stream:
            if event.type == "response.output_text.delta":
                emitted_text = True
                yield event.delta
            elif event.type == "response.failed":
                raise RuntimeError(event.response.error.message)

        if not emitted_text:
            raise RuntimeError("Model returned no final text.")

        for source in self._source_names(selected_chunks):
            yield f"\n\nSource: {source}"

    async def _assess_local_evidence(self, query: str) -> dict[str, Any]:
        try:
            return await self.evidence_judge.assess(query)
        except Exception:
            # Local evidence is optional. 
            print("[ERROR] Local evidence judge failed", flush=True)
            return {"selected_chunks": []}

    @staticmethod
    def _build_input(query: str, selected_chunks: list[dict[str, Any]]) -> list[dict[str, str]]:
        content: dict[str, Any] = {"question": query}
        if selected_chunks:
            content["local_evidence"] = selected_chunks

        return [{"role": "user", "content": json.dumps(content, ensure_ascii=False)}]

    @staticmethod
    def _source_names(selected_chunks: list[dict[str, Any]]) -> list[str]:
        # Return unique local filenames in their first-seen order.
        return list(dict.fromkeys(chunk["source"] for chunk in selected_chunks if chunk.get("source")))
