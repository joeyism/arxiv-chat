from langchain.agents import AgentExecutor, load_tools

from langchain_openai import ChatOpenAI
from arxiv_chat.models.embedding import EmbeddingModel
from arxiv_chat.models.llm import get_llm
from arxiv_chat.utils import prompt as prompt_utils
from arxiv_chat.utils import vectorstore
from arxiv_chat.utils.agent import ReActSingleInputOutputParser
from arxiv_chat.utils.runnable import (format_document_runnable,
                                       retrieve_documents_for_rag_scratchpad)

tools = load_tools(
    ["arxiv"],
)
# vector db
embedding_model = EmbeddingModel()
vector_store = vectorstore.create(embedding_model.embedding_model)
retriever = vector_store.as_retriever(search_kwargs={"k": 10})

# replaces agent creation
agent = (
    retrieve_documents_for_rag_scratchpad((lambda x: x["input"]) | retriever)
    | format_document_runnable()
    | prompt_utils.generate_rag_prompt(tools)
    | get_llm(stop=["\nObservation"])
    | ReActSingleInputOutputParser()
)

agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.invoke(
    {
        "input": "How do people make synthetic population?",
    }
)
