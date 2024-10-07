from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings
from transformers import AutoTokenizer


class EmbeddingModel:

    def __init__(self, source: str="openai", embedding_model_name: str="", model_kwargs: dict={}):
        self.embedding_model_name = embedding_model_name
        if source ==  "huggingface":
            embedding_model_name = embedding_model_name or "thenlper/gte-small"
            self.embedding_model = HuggingFaceEmbeddings(
                model_name=embedding_model_name,
                multi_process=False,
                model_kwargs=model_kwargs,
                encode_kwargs={
                    "normalize_embeddings": True,   # Set `True` for cosine similarity
                },
            )
        elif source == "openai":
            embedding_model_name = embedding_model_name or "text-embedding-3-small"
            self.embedding_model = OpenAIEmbeddings(
                model=embedding_model_name,
                model_kwargs=model_kwargs,
            )
        else:
            raise Exception(f"Source {source} not found")

    def embed_query(self, query: str):
        return self.embedding_model.embed_query(query)
