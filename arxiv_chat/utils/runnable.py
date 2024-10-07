from langchain.agents.format_scratchpad import format_log_to_str
from langchain.agents.format_scratchpad.openai_tools import \
    format_to_openai_tool_messages
from langchain_core.runnables import (RunnableAssign, RunnablePassthrough,
                                      RunnableSerializable)

from arxiv_chat.utils import prompt as prompt_utils
from langchain.agents.format_scratchpad.tools import (
    format_to_tool_messages,
)


def format_document_runnable() -> RunnableAssign:
    return RunnablePassthrough.assign(
        context=prompt_utils.format_docs,
    )


def retrieve_documents_for_rag_scratchpad(
    retriever: RunnableSerializable, use_open_ai: bool = False
) -> RunnableAssign:
    _format = format_to_tool_messages if use_open_ai else format_log_to_str
    return RunnablePassthrough.assign(
        agent_scratchpad=lambda x: _format(x["intermediate_steps"]),
        context=retriever.with_config(run_name="retrieve_documents"),
    )
