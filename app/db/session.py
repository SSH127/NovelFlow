"""
数据库会话管理（Supabase版本）
"""
from contextlib import contextmanager
from supabase import Client
from app.db.base import get_supabase
from app.utils.logger import get_logger

logger = get_logger(__name__)


def get_db() -> Client:
    """
    获取数据库客户端（用于FastAPI依赖注入）

    使用示例:
        @app.get("/users")
        def get_users(db: Client = Depends(get_db)):
            return db.table('users').select("*").execute()
    """
    try:
        yield get_supabase()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        raise


@contextmanager
def get_db_context() -> Client:
    """
    数据库客户端上下文管理器

    使用示例:
        with get_db_context() as db:
            result = db.table('users').select("*").execute()
    """
    client = get_supabase()
    try:
        yield client
    except Exception as e:
        logger.error(f"Database context error: {e}")
        raise


class DatabaseSession:
    """数据库会话管理类"""

    def __init__(self):
        self.client = get_supabase()

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            logger.error(f"Database error: {exc_val}")
        return False