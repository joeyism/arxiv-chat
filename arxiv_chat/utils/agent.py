import json
import re

from langchain.agents.agent import AgentOutputParser
from langchain.agents.mrkl.prompt import FORMAT_INSTRUCTIONS
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.exceptions import OutputParserException
from langchain_core.outputs import Generation

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


class ReActSingleInputOutputParser(AgentOutputParser):

    def parse_result(self, result: list[Generation], *, partial: bool = False):
        if not result[0].text and getattr(result[0], "message") and getattr(result[0].message, "additional_kwargs") and result[0].message.additional_kwargs["tool_calls"]: # type: ignore
            tool_call = result[0].message.additional_kwargs["tool_calls"][0] # type: ignore
            text = f"""Action: {tool_call["function"]["name"]}
            Action Input: {json.loads(tool_call["function"]["arguments"])["query"]}
            """
            return self.parse(text)

        return self.parse(result[0].text)

    def get_format_instructions(self) -> str:
        return FORMAT_INSTRUCTIONS

    def parse(self, text: str):
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

            return AgentFinish({"output": text}, text)
        elif not re.search(
            r"[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)", text, re.DOTALL
        ):
            action_match = re.search(r"Action\s*\d*\s*:[\s]*(.*?)", text, re.DOTALL)
            action = action_match.group(1).strip() or "bypass"
            tool_input = ""
            return AgentAction(action, tool_input, text)
        else:
            return AgentFinish({"output": text}, text)

    @property
    def _type(self) -> str:
        return "react-single-input"
