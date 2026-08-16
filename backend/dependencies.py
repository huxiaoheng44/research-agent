# create singletons for services to be used across the application
from services.embedding_service import EmbeddingService
from services.doument_service import DocumentService
from services.vector_store import VectorStore
from services.llm_service import LLMService
from agent.local_evidence_judge import LocalEvidenceJudge

document_service = DocumentService()
embedding_service = EmbeddingService()
vector_store = VectorStore()
llm_service = LLMService()
local_evidence_judge = LocalEvidenceJudge(embedding_service, vector_store, llm_service)

