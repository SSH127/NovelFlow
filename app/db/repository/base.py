"""
Supabase Repository基类
"""
from typing import TypeVar, Generic, List, Optional, Dict, Any
from supabase import Client
from pydantic import BaseModel
from app.utils.logger import get_logger

logger = get_logger(__name__)

SchemaType = TypeVar("SchemaType", bound=BaseModel)


class BaseRepository(Generic[SchemaType]):
    """Supabase基础Repository类"""

    def __init__(self, table_name: str, client: Client):
        self.table_name = table_name
        self.client = client
        self.table = client.table(table_name)

    def get(self, id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取单个记录"""
        try:
            response = self.table.select("*").eq("id", id).single().execute()
            return response.data if response.data else None
        except Exception as e:
            logger.error(f"Error getting {self.table_name} by id {id}: {e}")
            return None

    def get_multi(
            self,
            skip: int = 0,
            limit: int = 100,
            order_by: str = "created_at",
            ascending: bool = False
    ) -> List[Dict[str, Any]]:
        """获取多个记录"""
        try:
            query = self.table.select("*")

            if ascending:
                query = query.order(order_by, desc=False)
            else:
                query = query.order(order_by, desc=True)

            response = query.range(skip, skip + limit - 1).execute()
            return response.data if response.data else []
        except Exception as e:
            logger.error(f"Error getting multiple {self.table_name}: {e}")
            return []

    def create(self, obj_in: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """创建记录"""
        try:
            response = self.table.insert(obj_in).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error creating {self.table_name}: {e}")
            raise

    def update(self, id: int, obj_in: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新记录"""
        try:
            # 移除None值
            update_data = {k: v for k, v in obj_in.items() if v is not None}
            response = self.table.update(update_data).eq("id", id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error updating {self.table_name} id {id}: {e}")
            return None

    def delete(self, id: int) -> bool:
        """删除记录"""
        try:
            response = self.table.delete().eq("id", id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting {self.table_name} id {id}: {e}")
            return False

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """统计记录数"""
        try:
            query = self.table.select("id", count="exact")

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            response = query.execute()
            return response.count if hasattr(response, 'count') else 0
        except Exception as e:
            logger.error(f"Error counting {self.table_name}: {e}")
            return 0

    def exists(self, id: int) -> bool:
        """检查记录是否存在"""
        return self.get(id) is not None