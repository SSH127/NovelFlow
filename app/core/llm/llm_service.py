from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from app.config import API_KEY, BASE_URL,DS_BASE_URL,DS_API_KEY

# 1. 初始化客户端
llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=API_KEY,
    model="gpt-5.4",
    default_headers={
        "User-Agent": "vscode-restclient",
        "Accept": "application/json",
    },
)


ds_llm = ChatOpenAI(base_url=DS_BASE_URL, api_key=DS_API_KEY,model="deepseek-chat")


# 2. ask_llm（简单问答继续用它）
def ask_llm(question: str, model_name: str, system_prompt: str = None, is_stream: bool = False):
    try:
        messages = []
        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))
        messages.append(HumanMessage(content=question))

        model = llm.bind(model=model_name) if model_name != llm.model_name else llm

        if is_stream:
            def generator():
                for chunk in model.stream(messages):
                    if chunk.content:
                        yield chunk.content
            return generator()
        else:
            response = model.invoke(messages)
            if response is None or not response.content:
                return "错误: API 未返回有效内容"
            return response.content

    except Exception as e:
        if is_stream:
            def error_gen():
                yield f"请求失败: {e}"
            return error_gen()
        else:
            return f"请求失败: {e}"

# # 3. Agent 用的：绑定工具 + 创建节点函数
def create_agent_llm(tools: list, system_prompt: str = "你是一个有用的助手"):
    """
    传入工具列表，返回两样东西：
    1. llm_with_tools  —— 绑定了工具的模型
    2. llm_call        —— 可以直接当 LangGraph 节点用的函数
    """
    # 把工具绑给你的 llm
    llm_with_tools = ds_llm.bind_tools(tools)

    # 定义节点函数
    def llm_call(state: dict):
        """LangGraph 节点：读状态 → 调LLM → 写状态"""
        response = llm_with_tools.invoke(
            [SystemMessage(content=system_prompt)]
            + state["messages"]
        )
        return {
            "messages": [response],
            "llm_calls": state.get("llm_calls", 0) + 1
        }

    return llm_with_tools, llm_call

if __name__ == "__main__":
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage

    llm = ChatOpenAI(
        base_url=DS_BASE_URL,
        api_key=DS_API_KEY,
        model="deepseek-chat",
        temperature=0,
    )

    resp = llm.invoke([HumanMessage(content="你好")])
    print(resp.content)