"""
用户模型（Pydantic Schema）
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """创建用户模型"""
    password: str = Field(..., min_length=6)
    openai_api_key: Optional[str] = None
    default_model: str = "gpt-3.5-turbo"


class UserUpdate(BaseModel):
    """更新用户模型"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    openai_api_key: Optional[str] = None
    default_model: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """数据库中的用户模型"""
    id: int
    hashed_password: str
    is_superuser: bool = False
    openai_api_key: Optional[str] = None
    default_model: str = "gpt-3.5-turbo"
    total_tokens: int = 0
    total_chats: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserBase):
    """用户响应模型（不包含敏感信息）"""
    id: int
    is_superuser: bool = False
    default_model: str = "gpt-3.5-turbo"
    total_tokens: int = 0
    total_chats: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserWithStats(User):
    """带统计信息的用户模型"""
    chat_count: int = 0
    message_count: int = 0