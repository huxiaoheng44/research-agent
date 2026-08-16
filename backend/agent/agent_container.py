from dependencies import embedding_service, llm_service, vector_store
from agent.local_evidence_judge import LocalEvidenceJudge
from agent.research_agent import ResearchAgent
# it has a dependency on llm_service, so it must be imported after llm_service is created
research_agent = ResearchAgent()
local_evidence_judge = LocalEvidenceJudge(embedding_service, vector_store, llm_service)
