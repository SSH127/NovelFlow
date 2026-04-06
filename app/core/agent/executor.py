"""
Agent 执行器：负责调用 agent 并处理结果
"""

from langchain_core.messages import HumanMessage, AnyMessage
from typing import Optional


class AgentExecutor:
    def __init__(self, agent):
        self.agent = agent

    def run(self, query: str, history: Optional[list[AnyMessage]] = None) -> str:
        """
        同步执行 Agent
        """
        messages = history or []
        messages.append(HumanMessage(content=query))

        result = self.agent.invoke({"messages": messages, "llm_calls": 0})

        return result["messages"][-1].content

    async def arun(self, query: str, history: Optional[list[AnyMessage]] = None) -> str:
        """
        异步执行 Agent
        """
        messages = history or []
        messages.append(HumanMessage(content=query))

        result = await self.agent.ainvoke({"messages": messages, "llm_calls": 0})

        return result["messages"][-1].content

    def run_with_trace(self, query: str) -> dict:
        """
        执行并返回完整的执行轨迹（调试用）
        """
        messages = [HumanMessage(content=query)]
        result = self.agent.invoke({"messages": messages, "llm_calls": 0})

        trace = []
        for m in result["messages"]:
            trace.append({
                "type": m.type,
                "content": m.content,
            })

        return {
            "answer": result["messages"][-1].content,
            "trace": trace,
            "total_messages": len(result["messages"]),
        }