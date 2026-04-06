"""
聊天数据访问层（Supabase版本）
"""
from typing import List, Optional, Dict, Any
from supabase import Client
from app.db.repository.base import BaseRepository
from app.db.models.chat import Chat, ChatCreate, ChatUpdate
from app.db.models.message import MessageCreate, MessageRole, MessageContext
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatRepository(BaseRepository[Chat]):
    """聊天Repository"""

    def __init__(self, client: Client):
        super().__init__("chats", client)

    def get_user_chats(
            self,
            user_id: int,
            include_archived: bool = False,
            skip: int = 0,
            limit: int = 50
    ) -> List[Dict[str, Any]]:
        """获取用户的所有聊天会话"""
        try:
            query = self.table.select("*").eq("user_id", user_id)

            if not include_archived:
                query = query.eq("is_archived", False)

            # 置顶的在前，然后按更新时间排序
            query = query.order("is_pinned", desc=True).order("updated_at", desc=True)

            response = query.range(skip, skip + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting chats for user {user_id}: {e}")
            return []

    def create_chat(self, chat_data: ChatCreate) -> Optional[Dict[str, Any]]:
        """创建聊天会话"""
        try:
            chat_dict = chat_data.model_dump()
            chat_dict["message_count"] = 0
            chat_dict["total_tokens"] = 0
            chat_dict["is_archived"] = False
            chat_dict["is_pinned"] = False

            chat = self.create(chat_dict)

            # 更新用户聊天计数
            if chat:
                from app.db.repository.user_repo import UserRepository
                user_repo = UserRepository(self.client)
                user_repo.increment_chat_count(chat_data.user_id)

            return chat
        except Exception as e:
            logger.error(f"Error creating chat: {e}")
            raise

    def update_chat(self, chat_id: int, chat_data: ChatUpdate) -> Optional[Dict[str, Any]]:
        """更新聊天会话"""
        update_dict = chat_data.model_dump(exclude_unset=True)
        return self.update(chat_id, update_dict)

    def add_message(self, message_data: MessageCreate) -> Optional[Dict[str, Any]]:
        """添加消息到聊天会话"""
        try:
            # 创建消息
            message_dict = message_data.model_dump()
            message_table = self.client.table("messages")
            message_response = message_table.insert(message_dict).execute()

            if not message_response.data:
                return None

            message = message_response.data[0]

            # 更新聊天统计
            chat = self.get(message_data.chat_id)
            if chat:
                new_message_count = chat.get("message_count", 0) + 1
                new_total_tokens = chat.get("total_tokens", 0) + message_data.total_tokens

                self.update(message_data.chat_id, {
                    "message_count": new_message_count,
                    "total_tokens": new_total_tokens
                })

                # 更新用户token统计
                from app.db.repository.user_repo import UserRepository
                user_repo = UserRepository(self.client)
                user_repo.update_tokens(chat["user_id"], message_data.total_tokens)

            return message
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise

    def get_messages(
            self,
            chat_id: int,
            limit: int = 100,
            skip: int = 0
    ) -> List[Dict[str, Any]]:
        """获取聊天消息"""
        try:
            response = (
                self.client.table("messages")
                .select("*")
                .eq("chat_id", chat_id)
                .order("created_at", desc=False)
                .range(skip, skip + limit - 1)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting messages for chat {chat_id}: {e}")
            return []

    def get_chat_with_messages(self, chat_id: int, message_limit: int = 50) -> Optional[Dict[str, Any]]:
        """获取聊天会话及其消息"""
        try:
            chat = self.get(chat_id)
            if not chat:
                return None

            messages = self.get_messages(chat_id, limit=message_limit)
            chat["messages"] = messages

            return chat
        except Exception as e:
            logger.error(f"Error getting chat with messages {chat_id}: {e}")
            return None

    def archive_chat(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """归档聊天（验证所有权）"""
        chat = self.get(chat_id)
        if not chat or chat.get("user_id") != user_id:
            return None
        return self.update(chat_id, {"is_archived": True})

    def unarchive_chat(self, chat_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """取消归档"""
        chat = self.get(chat_id)
        if not chat or chat.get("user_id") != user_id:
            return None
        return self.update(chat_id, {"is_archived": False})

    def pin_chat(self, chat_id: int, user_id: int, pinned: bool = True) -> Optional[Dict[str, Any]]:
        """置顶/取消置顶聊天"""
        chat = self.get(chat_id)
        if not chat or chat.get("user_id") != user_id:
            return None
        return self.update(chat_id, {"is_pinned": pinned})

    def delete_chat(self, chat_id: int, user_id: int) -> bool:
        """删除聊天（验证所有权）"""
        chat = self.get(chat_id)
        if not chat or chat.get("user_id") != user_id:
            return False

        # Supabase会通过外键级联删除相关消息
        return self.delete(chat_id)

    def get_chat_context(self, chat_id: int, max_messages: int = 20) -> List[MessageContext]:
        """
        获取聊天上下文（用于OpenAI API调用）
        返回最近的N条消息
        """
        try:
            messages = (
                self.client.table("messages")
                .select("role, content")
                .eq("chat_id", chat_id)
                .order("created_at", desc=True)
                .limit(max_messages)
                .execute()
            )

            if not messages.data:
                return []

            # 反转顺序（最早的在前）
            messages.data.reverse()

            return [
                MessageContext(role=msg["role"], content=msg["content"])
                for msg in messages.data
            ]
        except Exception as e:
            logger.error(f"Error getting context for chat {chat_id}: {e}")
            return []

    def search_chats(self, user_id: int, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """搜索用户的聊天会话"""
        try:
            response = (
                self.table
                .select("*")
                .eq("user_id", user_id)
                .ilike("title", f"%{query}%")
                .order("updated_at", desc=True)
                .limit(limit)
                .execute()
            )
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error searching chats for user {user_id}: {e}")
            return []