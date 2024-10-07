from typing import Iterator

from langchain_core.messages.ai import AIMessageChunk
from langchain.agents import AgentExecutor
from langchain.chains.query_constructor.schema import AttributeInfo
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_core.output_parsers.transform import BaseTransformOutputParser

from arxiv_chat.models.embedding import EmbeddingModel
from arxiv_chat.models.llm import get_llm
from arxiv_chat.utils import prompt as prompt_utils
from arxiv_chat.utils import vectorstore
from arxiv_chat.utils.agent import ReActSingleInputOutputParser
from arxiv_chat.utils.runnable import (format_document_runnable,
                                       retrieve_documents_for_rag_scratchpad)
from arxiv_chat.utils.tools import BypassTool

metadata_field_info = [
    AttributeInfo(
        name="title",
        description="Title of the paper",
        type="string",
    ),
    AttributeInfo(
        name="authors",
        description="Authors of the paper",
        type="list[string]",
    ),
    AttributeInfo(
        name="updated",
        description="Date of last update",
        type="string",
    ),
    AttributeInfo(
        name="published",
        description="Date of published",
        type="string",
    ),
    AttributeInfo(
        name="page",
        description="page of the document",
        type="string",
    ),
    AttributeInfo(
        name="source",
        description="URL of the document",
        type="string",
    ),
    AttributeInfo(
        name="categories",
        description="Paper category",
        type="list[string]",
    ),
]


class StrOutputParser(BaseTransformOutputParser[str]):
    """OutputParser that parses LLMResult into the top likely string."""

    @classmethod
    def is_lc_serializable(cls) -> bool:
        """Return whether this class is serializable."""
        return True

    @classmethod
    def get_lc_namespace(cls) -> list[str]:
        """Get the namespace of the langchain object."""
        return ["langchain", "schema", "output_parser"]

    @property
    def _type(self) -> str:
        """Return the output parser type for serialization."""
        return "default"

    def parse(self, text: str) -> str:
        """Returns the input text with no changes."""
        return text[len("\n\nSystem: ") :] if text.startswith("\n\nSystem: ") else text


class RAG:

    def __init__(self, num_docs: int = 10, model_name: str | None = None, streaming: bool=False):
        tools = load_tools(
            ["arxiv"],
        )
        tools.append(BypassTool())

        # vector db
        embedding_model = EmbeddingModel()
        vector_store = vectorstore.create(embedding_model.embedding_model)
        retriever = vector_store.as_retriever(search_kwargs={"k": num_docs})

        # replaces agent creation
        agent = (
            retrieve_documents_for_rag_scratchpad((lambda x: x["input"]) | retriever)
            | format_document_runnable()
            | prompt_utils.generate_rag_prompt(tools)
            | get_llm(
                tools=tools if model_name else None,
                stop=["\nObservation"],
                model_name=model_name,
                streaming=streaming,
            )
            | ReActSingleInputOutputParser()
        )

        self.agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

    def query(self, query: str, streaming: bool = False) -> Iterator | dict:
        if not streaming:
            return self.agent_executor.invoke({"input": query})
        res = self.agent_executor.invoke({"input": query})
        return (a for a in res.get("output", ""))



if __name__ == "__main__":
    import argparse
    import asyncio

    parser = argparse.ArgumentParser()
    parser.add_argument("query")
    parser.add_argument("-n", "--num-docs", type=int, default=10)
    parser.add_argument("-m", "--model-name", type=str, default=None)
    parser.add_argument("-s", "--streaming", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    rag = RAG(num_docs=args.num_docs, model_name=args.model_name, streaming=args.streaming)
    if args.streaming:
        rag.query(query=args.query, streaming=args.streaming)
    else:
        res = rag.query(query=args.query, streaming=args.streaming)
    import ipdb

    ipdb.set_trace()
    1
