"""
聊天会话模型
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class ChatBase(BaseModel):
    """聊天会话基础模型"""
    title: str = Field(..., min_length=1, max_length=200)
    model: str = "gpt-3.5-turbo"
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2000, ge=1, le=4000)
    system_prompt: Optional[str] = None


class ChatCreate(ChatBase):
    """创建聊天会话模型"""
    user_id: int


class ChatUpdate(BaseModel):
    """更新聊天会话模型"""
    title: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1, le=4000)
    system_prompt: Optional[str] = None
    is_archived: Optional[bool] = None
    is_pinned: Optional[bool] = None


class ChatInDB(ChatBase):
    """数据库中的聊天会话模型"""
    id: int
    user_id: int
    is_archived: bool = False
    is_pinned: bool = False
    message_count: int = 0
    total_tokens: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Chat(ChatInDB):
    """聊天会话响应模型"""
    pass


class ChatWithMessages(Chat):
    """带消息的聊天会话"""
    messages: List['Message'] = []


# 避免循环导入
from app.db.models.message import Message

ChatWithMessages.model_rebuild()