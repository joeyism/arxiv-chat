from langchain_openai import ChatOpenAI
from langchain_core.utils.function_calling import convert_to_openai_tool


def get_llm(tools: list | None=None, stop: list[str]=[], model_name: str | None=None, **kwargs):
    llm = ChatOpenAI(temperature=0.0, model=model_name, **kwargs) if model_name else ChatOpenAI(temperature=0.0, **kwargs)
    if tools:
        llm = llm.bind_tools([convert_to_openai_tool(tool) for tool in tools])
    if stop:
        llm = llm.bind(stop=stop)
    return llm
