from typing import Optional, Type

from langchain_core.callbacks import CallbackManagerForToolRun

from langchain_core.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field


class BypassInput(BaseModel):
    """Bypass Tool Input"""
    query: str = Field(description="Input Query")

class BypassTool(BaseTool):
    """Tool that bypasses everything and calls the LLM again. NEVER call this tool"""

    name: str = "bypass"
    description: str = "A simple bypass. NEVER call this tool"
    args_schema: Type[BaseModel] = BypassInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Bypasses the query"""
        return query
