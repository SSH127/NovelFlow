"""
Agent 业务层：给 API 路由调用
"""

from app.core.agent.builder import build_math_agent,build_rag_agent
from app.core.agent.executor import AgentExecutor

# ═══════════════════════════════════════
# 单例缓存（避免每次请求都重建 graph）
# ═══════════════════════════════════════
_agents = {}


def get_agent(agent_type: str = "math") -> AgentExecutor:
    if agent_type not in _agents:
        if agent_type == "math":
            graph = build_math_agent()
        elif agent_type == "rag":
            graph = build_rag_agent()
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        _agents[agent_type] = AgentExecutor(graph)

    return _agents[agent_type]


async def handle_agent_chat(query: str, agent_type: str = "math") -> str:
    """
    API 层调用这个函数
    """
    executor = get_agent(agent_type)
    return await executor.arun(query)