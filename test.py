from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent, load_tools
from langchain.agents.format_scratchpad import format_log_to_str
from langchain_core.prompts import BasePromptTemplate, format_document
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.tools.render import ToolsRenderer, render_text_description
from langchain_openai import ChatOpenAI
import re
from typing import Union

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException

from langchain.agents.agent import AgentOutputParser
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS

FINAL_ANSWER_ACTION = "Final Answer:"
MISSING_ACTION_AFTER_THOUGHT_ERROR_MESSAGE = (
    "Invalid Format: Missing 'Action:' after 'Thought:"
)
MISSING_ACTION_INPUT_AFTER_ACTION_ERROR_MESSAGE = (
    "Invalid Format: Missing 'Action Input:' after 'Action:'"
)
FINAL_ANSWER_AND_PARSABLE_ACTION_ERROR_MESSAGE = (
    "Parsing LLM output produced both a final answer and a parse-able action:"
)

from arxiv_chat.models.embedding import EmbeddingModel
from arxiv_chat.utils import vectorstore

llm = ChatOpenAI(temperature=0.0)
tools = load_tools(
    ["arxiv"],
)
prompt = PromptTemplate(
    input_variables=["agent_scratchpad", "input"],
    partial_variables={
        "tools": "arxiv - A wrapper around Arxiv.org Useful for when you need to answer questions about Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, Statistics, Electrical Engineering, and Economics from scientific articles on arxiv.org. Input should be a search query.",
        "tool_names": "arxiv",
    },
    metadata={
        "lc_hub_owner": "hwchase17",
        "lc_hub_repo": "react",
        "lc_hub_commit_hash": "d15fe3c426f1c4b3f37c9198853e4a86e20c425ca7f4752ec0c9b0e97ca7ea4d",
    },
    template="""You are an assistant for question-answering tasks.
Use the following context, which are pieces of retrieved papers, to answer the question.
Each piece of retrieved paper is a part of a larger paper
The data is provided in the following format:
```
Title: the title of the larger paper
Authors: the author of the larger paper
Published: the date the larger paper is published
Text: the actual text of the paper
```

The 'Text' is the real information you should use to answer the question, and include the other information only to provide context. Do not use anything else, and it should be the only piece of information used to form your response. If you do answer, always display all the papers' information (Title, Published date) but without 'Text' from which you got the information. Provide as much information as possible in your answers.
The following pieces of retrieved paper is your only source of truth, only answer the question with the provided context

Context:
{context}
You have access to the following tools:

{tools}

Reply using the following format:

```
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, can be one of [{tool_names}], but doesn't need to be if the answer exists in the context
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat 3 times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question, with sources of the paper you got the information from
```

When you source the papers, use the following format:
```
Title: the title of the larger paper
Authors: the author of the larger paper
Published: the date the larger paper is published
```

Begin!

Question: {input}
Thought: {agent_scratchpad}""",
)

# vector db
embedding_model = EmbeddingModel()
vector_store = vectorstore.create(embedding_model.embedding_model)
retriever = vector_store.as_retriever(search_kwargs={"k": 10})


# replaces agent creation

class ReActSingleInputOutputParser(AgentOutputParser):

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        import ipdb; ipdb.set_trace()
        includes_answer = FINAL_ANSWER_ACTION in text
        regex = (
            r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        )
        action_match = re.search(regex, text, re.DOTALL)
        if action_match:
            if includes_answer:
                raise OutputParserException(
                    f"{FINAL_ANSWER_AND_PARSABLE_ACTION_ERROR_MESSAGE}: {text}"
                )
            action = action_match.group(1).strip()
            action_input = action_match.group(2)
            tool_input = action_input.strip(" ")
            tool_input = tool_input.strip('"')

            return AgentAction(action, tool_input, text)

        elif includes_answer:
            return AgentFinish(
                {"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text
            )

        if not re.search(r"Action\s*\d*\s*:[\s]*(.*?)", text, re.DOTALL):
            import ipdb; ipdb.set_trace()
            raise OutputParserException(
                f"Could not parse LLM output: `{text}`",
                observation=MISSING_ACTION_AFTER_THOUGHT_ERROR_MESSAGE,
                llm_output=text,
                send_to_llm=True,
            )
        elif not re.search(
            r"[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)", text, re.DOTALL
        ):
            import ipdb; ipdb.set_trace()
            raise OutputParserException(
                f"Could not parse LLM output: `{text}`",
                observation=MISSING_ACTION_INPUT_AFTER_ACTION_ERROR_MESSAGE,
                llm_output=text,
                send_to_llm=True,
            )
        else:
            return AgentFinish(
                {"output": text}, text
            )

    @property
    def _type(self) -> str:
        return "react-single-input"

document_prompt = PromptTemplate.from_template(
    """Title: {title}
Authors: {authors}
Published: {published}
Text: {page_content}"""
)

def format_docs(inputs: dict) -> str:
    return "\n\n".join(
        format_document(doc, document_prompt)
        for doc in inputs["context"]
    )

retrieval_docs = (lambda x: x["input"]) | retriever
output_parser = ReActSingleInputOutputParser()
tools_renderer = render_text_description
prompt = prompt.partial(
    tools=tools_renderer(list(tools)),
    tool_names=", ".join([t.name for t in tools]),
)
stop = ["\nObservation"]
llm = llm.bind(stop=stop)
agent = (
    RunnablePassthrough.assign(
        agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
        context=retrieval_docs.with_config(run_name="retrieve_documents"),
    )
    | RunnablePassthrough.assign(
        context=format_docs,
    )
    | prompt
    | llm
    | output_parser
)


agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
agent_executor.invoke(
    {
        "input": "How do people make synthetic population?",
    }
)
