from fastapi import APIRouter
from app.services.agent_service import handle_agent_chat

router = APIRouter()

@router.post("/agent/chat")
async def agent_chat(payload: dict):  # 直接收原生 dict
    answer = await handle_agent_chat(
        query=payload.get("query"),
        agent_type=payload.get("agent_type", "default"),
    )
    return answer