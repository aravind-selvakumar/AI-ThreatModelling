from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from sqlalchemy import create_engine, text

from app.config import settings

COLLECTION_NAME = "threatmod_standards"


def get_embeddings() -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.embedding_model,
        base_url=settings.ollama_base_url,
    )


def _connection_string() -> str:
    return settings.pgvector_connection_string


def _sync_engine():
    return create_engine(_connection_string())


def get_vectorstore() -> PGVector:
    return PGVector(
        connection_string=_connection_string(),
        embedding_function=get_embeddings(),
        collection_name=COLLECTION_NAME,
        pre_delete_collection=False,
    )


def add_documents(documents: list[Document]) -> list[str]:
    vs = get_vectorstore()
    return vs.add_documents(documents)


def delete_documents(file_ids: list[str]) -> None:
    vs = get_vectorstore()
    vs.delete(ids=file_ids)


def get_retriever(k: int = 5) -> VectorStoreRetriever:
    vs = get_vectorstore()
    return vs.as_retriever(search_kwargs={"k": k})


def similarity_search(query: str, k: int = 5) -> list[Document]:
    vs = get_vectorstore()
    return vs.similarity_search(query, k=k)


def get_collection_stats() -> dict:
    engine = _sync_engine()
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT COUNT(*) FROM langchain_pg_embedding WHERE collection_id = (SELECT uuid FROM langchain_pg_collection WHERE name = :name)"),
                {"name": COLLECTION_NAME},
            )
            count = result.scalar() or 0
    except Exception:
        count = 0
    finally:
        engine.dispose()
    return {"collection": COLLECTION_NAME, "chunk_count": count}


def clear_collection() -> None:
    vs = get_vectorstore()
    vs.delete_collection()
