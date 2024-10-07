from langchain_core.prompts import (BasePromptTemplate, PromptTemplate,
                                    format_document)
from langchain_core.tools import BaseTool
from langchain_core.tools.render import render_text_description

rag_prompt = PromptTemplate(
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

You MUST reply using the following format:

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

document_prompt = PromptTemplate.from_template(
    """Title: {title}
Authors: {authors}
Published: {published}
Text: {page_content}"""
)


def format_docs(inputs: dict) -> str:
    return "\n\n".join(
        format_document(doc, document_prompt) for doc in inputs["context"]
    )


def generate_rag_prompt(tools: list[BaseTool]) -> BasePromptTemplate:
    return rag_prompt.partial(
        tools=render_text_description(list(tools)),
        tool_names=", ".join([t.name for t in tools]),
    )
