"""
Agent 构建器：负责组装 LangGraph
"""

from langgraph.graph import StateGraph, START, END

from app.core.agent.state import AgentState
from app.core.tools.base import ALL_TOOLS, tool_node
from app.core.router.tool_router import should_continue
from app.core.llm.llm_service import create_agent_llm


def build_math_agent():
    """构建数学计算 Agent"""

    # 1. 创建绑定工具的 LLM
    llm_with_tools, llm_call = create_agent_llm(
        tools=ALL_TOOLS,
        system_prompt="你是一个做算术的助手，请用中文回答。"
    )

    # 2. 组装 Graph
    builder = StateGraph(AgentState)

    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)

    builder.add_edge(START, "llm_call")
    builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    builder.add_edge("tool_node", "llm_call")

    return builder.compile()


def build_rag_agent():
    """构建 RAG Agent（未来扩展）"""
    from app.core.tools.rag_tool import rag_search

    rag_tools = ALL_TOOLS + [rag_search]

    llm_with_tools, llm_call = create_agent_llm(
        tools=rag_tools,
        system_prompt="你是一个知识问答助手，优先使用知识库搜索。"
    )

    builder = StateGraph(AgentState)
    builder.add_node("llm_call", llm_call)
    builder.add_node("tool_node", tool_node)
    builder.add_edge(START, "llm_call")
    builder.add_conditional_edges("llm_call", should_continue, ["tool_node", END])
    builder.add_edge("tool_node", "llm_call")

    return builder.compile()