"""
用户数据访问层（Supabase版本）
"""
from typing import Optional, Dict, Any
from supabase import Client
from app.db.repository.base import BaseRepository
from app.db.models.user import User, UserCreate, UserUpdate
from app.utils.logger import get_logger

logger = get_logger(__name__)


class UserRepository(BaseRepository[User]):
    """用户Repository"""

    def __init__(self, client: Client):
        super().__init__("users", client)

    def get_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """根据用户名获取用户"""
        try:
            response = self.table.select("*").eq("username", username).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by username {username}: {e}")
            return None

    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """根据邮箱获取用户"""
        try:
            response = self.table.select("*").eq("email", email).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None

    def create_user(self, user_data: UserCreate, hashed_password: str) -> Optional[Dict[str, Any]]:
        """创建用户"""
        try:
            user_dict = user_data.model_dump(exclude={"password"})
            user_dict["hashed_password"] = hashed_password
            user_dict["total_tokens"] = 0
            user_dict["total_chats"] = 0

            return self.create(user_dict)
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[Dict[str, Any]]:
        """更新用户信息"""
        update_dict = user_data.model_dump(exclude_unset=True)
        return self.update(user_id, update_dict)

    def update_tokens(self, user_id: int, tokens: int) -> Optional[Dict[str, Any]]:
        """更新用户token消耗"""
        try:
            user = self.get(user_id)
            if not user:
                return None

            new_total = user.get("total_tokens", 0) + tokens
            return self.update(user_id, {"total_tokens": new_total})
        except Exception as e:
            logger.error(f"Error updating tokens for user {user_id}: {e}")
            return None

    def increment_chat_count(self, user_id: int) -> Optional[Dict[str, Any]]:
        """增加聊天会话计数"""
        try:
            user = self.get(user_id)
            if not user:
                return None

            new_count = user.get("total_chats", 0) + 1
            return self.update(user_id, {"total_chats": new_count})
        except Exception as e:
            logger.error(f"Error incrementing chat count for user {user_id}: {e}")
            return None

    def verify_user_exists(self, username: str = None, email: str = None) -> bool:
        """验证用户名或邮箱是否已存在"""
        if username and self.get_by_username(username):
            return True
        if email and self.get_by_email(email):
            return True
        return False

    def get_user_stats(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户统计信息"""
        try:
            # 获取用户信息
            user = self.get(user_id)
            if not user:
                return None

            # 获取聊天会话数
            chat_count = self.client.table("chats").select("id", count="exact").eq("user_id", user_id).execute().count

            # 获取消息总数
            message_count = (
                self.client.table("messages")
                .select("id", count="exact")
                .in_("chat_id",
                     self.client.table("chats")
                     .select("id")
                     .eq("user_id", user_id)
                     .execute().data
                     )
                .execute().count
            )

            return {
                **user,
                "chat_count": chat_count or 0,
                "message_count": message_count or 0
            }
        except Exception as e:
            logger.error(f"Error getting stats for user {user_id}: {e}")
            return None