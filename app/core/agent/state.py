from typing_extensions import TypedDict, Annotated
from langchain_core.messages import AnyMessage
import operator


class AgentState(TypedDict):
    """Agent 运行状态"""
    messages: Annotated[list[AnyMessage], operator.add]
    llm_calls: int          # 追踪 LLM 调用次数
    # 未来可扩展:
    # current_plan: str
    # user_id: str
    # session_id: str