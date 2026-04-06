"""
消息模型
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class MessageRole(str, Enum):
    """消息角色枚举"""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MessageBase(BaseModel):
    """消息基础模型"""
    role: MessageRole
    content: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
    """创建消息模型"""
    chat_id: int
    model: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class MessageUpdate(BaseModel):
    """更新消息模型"""
    content: Optional[str] = None
    total_tokens: Optional[int] = None


class MessageInDB(MessageBase):
    """数据库中的消息模型"""
    id: int
    chat_id: int
    model: Optional[str] = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    finish_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Message(MessageInDB):
    """消息响应模型"""
    pass


class MessageContext(BaseModel):
    """消息上下文（用于API调用）"""
    role: str
    content: str
