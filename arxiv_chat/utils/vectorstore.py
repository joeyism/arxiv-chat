from langchain_postgres.vectorstores import PGVector
from langchain_core.embeddings import Embeddings
from . import postgres

collection_name = "arxiv_docs"


def create(embedding_model: Embeddings) -> PGVector:
    return PGVector(
        embeddings=embedding_model,
        collection_name=collection_name,
        connection=postgres.connection,
        use_jsonb=True,
    )
