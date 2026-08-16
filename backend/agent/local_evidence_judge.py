import asyncio
import json
from typing import Any


JUDGE_INSTRUCTIONS = """
You judge whether retrieved excerpts from private uploaded files provide enough
evidence to answer a user's question. Return JSON only, with this exact shape:
{
  "is_sufficient": boolean,
  "confidence": "low" | "medium" | "high",
  "selected_indices": [0, 3],
  "reason": "short explanation",
  "missing_information": "short explanation or empty string"
}

Set is_sufficient to true only if the selected excerpts directly support a
useful answer to the question. Semantic similarity alone is not enough. Select
only excerpts that directly support the answer. selected_indices must contain
only zero-based positions from the candidate_excerpts list. Do not use outside
knowledge.
""".strip()


class LocalEvidenceJudge:
    """Retrieve local chunks and decide whether they are useful evidence."""

    def __init__(self, embedding_service, vector_store, llm_service):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service

    async def assess(self, query: str) -> dict[str, Any]:
        """Return an evidence packet suitable for a later synthesis agent."""
        results = await asyncio.to_thread(self._retrieve, query)

        if not results:
            return {
                "is_sufficient": False,
                "confidence": "low",
                "selected_indices": [],
                "selected_chunks": [],
                "reason": "No relevant uploaded-file excerpts were found.",
                "missing_information": "No uploaded sources are available for this question.",
            }

        candidates = [
            {
                "index": index,
                "source": result["source"],
                "chunk_index": result["chunk_index"],
                "similarity": round(result["score"], 4),
                "text": result["text"],
            }
            for index, result in enumerate(results)
        ]

        response = await self.llm_service.create_judgment_response(
            [
                {
                    "role": "user",
                    "content": json.dumps(
                        {"question": query, "candidate_excerpts": candidates},
                        ensure_ascii=False,
                    ),
                }
            ],
            instructions=JUDGE_INSTRUCTIONS,
        )

        decision = self._parse_decision(response.output_text)
        selected_indices = self._valid_indices(decision["selected_indices"], len(candidates))
        selected_chunks = self.select_chunks(results, selected_indices)
        is_sufficient = bool(decision["is_sufficient"] and selected_chunks)

        return {
            "is_sufficient": is_sufficient,
            "confidence": decision["confidence"],
            "selected_indices": selected_indices if is_sufficient else [],
            # Only these chunks should be passed to the later synthesis agent.
            "selected_chunks": selected_chunks if is_sufficient else [],
            "reason": decision["reason"],
            "missing_information": decision["missing_information"],
        }

    def _retrieve(self, query: str) -> list[dict[str, Any]]:
        query_embedding = self.embedding_service.embed_query(query)
        return self.vector_store.search(query_embedding, top_k=5)

    @staticmethod
    def select_chunks(
        candidates: list[dict[str, Any]], selected_indices: list[int]
    ) -> list[dict[str, Any]]:
        """Load only the candidate chunks selected by the judge."""
        return [candidates[index] for index in selected_indices]

    @staticmethod
    def _valid_indices(selected_indices: list[int], candidate_count: int) -> list[int]:
        valid_indices = []
        for index in selected_indices:
            if type(index) is int and 0 <= index < candidate_count and index not in valid_indices:
                valid_indices.append(index)
        return valid_indices

    @staticmethod
    def _parse_decision(output_text: str) -> dict[str, Any]:
        try:
            parsed = json.loads(output_text.removeprefix("```json").removesuffix("```").strip())
        except json.JSONDecodeError as error:
            raise RuntimeError("Local evidence judge returned invalid JSON.") from error

        confidence = parsed.get("confidence", "low")
        if confidence not in {"low", "medium", "high"}:
            confidence = "low"

        selected_indices = parsed.get("selected_indices", [])
        if not isinstance(selected_indices, list):
            selected_indices = []

        return {
            "is_sufficient": bool(parsed.get("is_sufficient", False)),
            "confidence": confidence,
            "selected_indices": selected_indices,
            "reason": str(parsed.get("reason", "No explanation provided.")),
            "missing_information": str(parsed.get("missing_information", "")),
        }
