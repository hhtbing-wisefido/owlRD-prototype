"""
JSON存储服务
用于管理数据文件的读写操作，提供通用CRUD操作
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, TypeVar, Generic, Callable
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel

T = TypeVar('T', bound=BaseModel)


class StorageService(Generic[T]):
    """JSON文件存储服务（泛型）"""
    
    def __init__(self, data_dir: str = "app/data", collection: str = "default"):
        """
        初始化存储服务
        
        Args:
            data_dir: 数据目录路径
            collection: 集合名称
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.collection = collection
    
    def _get_file_path(self) -> Path:
        """获取集合文件路径"""
        return self.data_dir / f"{self.collection}.json"
    
    def _serialize(self, obj: Any) -> Any:
        """序列化对象（处理datetime, UUID等）"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, BaseModel):
            return obj.model_dump(mode='json')
        elif isinstance(obj, bytes):
            # bytes转为base64字符串
            import base64
            return base64.b64encode(obj).decode('utf-8')
        return obj
    
    def load_all(self) -> List[Dict[str, Any]]:
        """
        从JSON文件加载所有数据
        
        Returns:
            数据列表
        """
        file_path = self._get_file_path()
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def save_all(self, data: List[Dict[str, Any]]) -> None:
        """
        保存所有数据到JSON文件
        
        Args:
            data: 要保存的数据列表
        """
        file_path = self._get_file_path()
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=self._serialize)
    
    def find_by_id(self, id_field: str, id_value: str | UUID) -> Optional[Dict[str, Any]]:
        """
        根据ID查找单条记录
        
        Args:
            id_field: ID字段名（如 tenant_id, user_id）
            id_value: ID值
            
        Returns:
            找到的记录，如果不存在返回None
        """
        data = self.load_all()
        id_str = str(id_value)
        
        for item in data:
            if str(item.get(id_field)) == id_str:
                return item
        return None
    
    def find_all(self, filter_func: Optional[Callable[[Dict[str, Any]], bool]] = None) -> List[Dict[str, Any]]:
        """
        查找所有符合条件的记录
        
        Args:
            filter_func: 过滤函数，返回True表示符合条件
            
        Returns:
            符合条件的记录列表
        """
        data = self.load_all()
        if filter_func is None:
            return data
        return [item for item in data if filter_func(item)]
    
    def create(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新记录
        
        Args:
            item: 要创建的记录
            
        Returns:
            创建的记录
        """
        data = self.load_all()
        data.append(item)
        self.save_all(data)
        return item
    
    def update(self, id_field: str, id_value: str | UUID, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        更新记录
        
        Args:
            id_field: ID字段名
            id_value: ID值
            updates: 要更新的字段
            
        Returns:
            更新后的记录，如果不存在返回None
        """
        data = self.load_all()
        id_str = str(id_value)
        
        for i, item in enumerate(data):
            if str(item.get(id_field)) == id_str:
                # 更新字段
                item.update(updates)
                # 自动更新updated_at
                if 'updated_at' in item:
                    item['updated_at'] = datetime.utcnow().isoformat()
                data[i] = item
                self.save_all(data)
                return item
        return None
    
    def delete(self, id_field: str, id_value: str | UUID) -> bool:
        """
        删除记录
        
        Args:
            id_field: ID字段名
            id_value: ID值
            
        Returns:
            是否删除成功
        """
        data = self.load_all()
        id_str = str(id_value)
        
        for i, item in enumerate(data):
            if str(item.get(id_field)) == id_str:
                data.pop(i)
                self.save_all(data)
                return True
        return False
    
    def count(self, filter_func: Optional[Callable[[Dict[str, Any]], bool]] = None) -> int:
        """
        统计记录数量
        
        Args:
            filter_func: 过滤函数
            
        Returns:
            记录数量
        """
        data = self.find_all(filter_func)
        return len(data)
    
    def exists(self, id_field: str, id_value: str | UUID) -> bool:
        """
        检查记录是否存在
        
        Args:
            id_field: ID字段名
            id_value: ID值
            
        Returns:
            是否存在
        """
        return self.find_by_id(id_field, id_value) is not None


def init_storage(data_dir: str = "app/data") -> None:
    """
    初始化存储目录和数据文件
    
    Args:
        data_dir: 数据目录路径
    """
    # 创建数据目录
    Path(data_dir).mkdir(parents=True, exist_ok=True)
    Path(f"{data_dir}/iot_timeseries").mkdir(parents=True, exist_ok=True)
    
    # 初始化所有集合文件
    collections = [
        "tenants", "users", "roles",
        "locations", "rooms", "beds",
        "residents", "resident_phi", "resident_contacts", "resident_caregivers",
        "anonymous_name_pool",
        "devices",
        "iot_monitor_alerts",
        "cloud_alert_policies",
        "cards", "card_devices",
        "config_versions", "posture_mapping", "event_mapping"
    ]
    
    for collection in collections:
        file_path = Path(data_dir) / f"{collection}.json"
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump([], f)
