"""
Supabase数据库配置
"""
from supabase import create_client, Client
from app.config import get_settings
from logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SupabaseClient:
    """Supabase客户端单例"""
    _instance: Client = None

    @classmethod
    def get_client(cls) -> Client:
        """获取Supabase客户端实例"""
        if cls._instance is None:
            try:
                cls._instance = create_client(
                    supabase_url=settings.SUPABASE_URL,
                    supabase_key=settings.SUPABASE_KEY
                )
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                raise
        return cls._instance

    @classmethod
    def close(cls):
        """关闭连接（如果需要）"""
        cls._instance = None


# 便捷函数
def get_supabase() -> Client:
    """获取Supabase客户端"""
    return SupabaseClient.get_client()