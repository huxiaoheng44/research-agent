# create singletons for services to be used across the application
from services.embedding_service import EmbeddingService
from services.doument_service import DocumentService
from services.vector_store import VectorStore

document_service = DocumentService()
embedding_service = EmbeddingService()
vector_store = VectorStore()
