from langchain_core.messages import ToolMessage
from app.core.tools.math import add, multiply, divide

# ═══════════════════════════════════════
# 工具注册表：所有工具在这里集中管理
# ═══════════════════════════════════════

ALL_TOOLS = [add, multiply, divide]

# 后续加新工具只需:
# from app.core.tools.web import search_web
# ALL_TOOLS.append(search_web)

TOOLS_BY_NAME = {t.name: t for t in ALL_TOOLS}


def tool_node(state: dict) -> dict:
    """
    通用工具执行节点
    读取最后一条消息的 tool_calls，逐个执行，返回 ToolMessage
    """
    results = []
    for tool_call in state["messages"][-1].tool_calls:
        tool_fn = TOOLS_BY_NAME[tool_call["name"]]
        observation = tool_fn.invoke(tool_call["args"])
        results.append(
            ToolMessage(
                content=str(observation),
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": results}