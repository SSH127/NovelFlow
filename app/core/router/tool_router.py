"""
路由层：决定 Agent 下一步去哪个节点
"""

from typing import Literal
from langgraph.graph import END
from app.core.agent.state import AgentState


def should_continue(state: AgentState) -> Literal["tool_node", "__end__"]:
    """
    检查 LLM 的最后回复：
    - 如果有 tool_calls → 去 tool_node 执行工具
    - 否则 → 结束
    """
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tool_node"
    return END


# ═══════════════════════════════════════
# 未来可以在这里加更多路由策略
# ═══════════════════════════════════════

def route_by_confidence(state: AgentState) -> Literal["tool_node", "human_review", "__end__"]:
    """
    进阶路由：根据置信度决定是否需要人工审核
    """
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        # 高危工具 → 走人工审批
        dangerous_tools = {"delete_file", "send_email", "execute_sql"}
        called_tools = {tc["name"] for tc in last_message.tool_calls}
        if called_tools & dangerous_tools:
            return "human_review"
        return "tool_node"

    return END