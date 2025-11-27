"""
JSON存储服务
用于管理数据文件的读写操作，提供通用CRUD操作
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, TypeVar, Generic
from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel
from loguru import logger

T = TypeVar('T', bound=BaseModel)

try:
    from app.utils.validation import get_validator, ValidationError
except ImportError:
    # 如果validation模块不存在，创建空类
    class ValidationError(Exception):
        pass
    def get_validator(collection):
        return None


class StorageService(Generic[T]):
    """JSON文件存储服务（泛型）"""
    
    def __init__(self, collection: str = "default", data_dir: str = "app/data"):
        """
        初始化存储服务
        
        Args:
            collection: 集合名称
            data_dir: 数据目录路径
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.collection = collection
        self.validator = get_validator(collection)
    
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
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建新记录
        
        Args:
            data: 要创建的数据
            
        Returns:
            创建的记录（包含生成的ID和时间戳）
        """
        # 数据验证
        if self.validator:
            try:
                self.validator.validate_or_raise(data)
            except ValidationError as e:
                logger.error(f"Validation error in {self.collection}: {e}")
                raise
        
        # 生成ID和时间戳
        record = data.copy()
        id_field = f"{self.collection[:-1]}_id"  # users -> user_id
        record[id_field] = str(uuid4())
        record["created_at"] = datetime.now().isoformat()
        record["updated_at"] = datetime.now().isoformat()
        
        # 读取现有数据
        all_data = self.load_all()
        
        # 检查唯一性约束
        self._check_unique_constraints(record, all_data)
        
        # 添加新记录
        all_data.append(record)
        
        # 保存
        self.save_all(all_data)
        
        logger.info(f"Created {self.collection} record: {record.get(id_field)}")
        return record
    
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
                # 合并数据用于验证
                updated_item = item.copy()
                updated_item.update(updates)
                
                # 数据验证
                if self.validator:
                    try:
                        self.validator.validate_or_raise(updated_item)
                    except ValidationError as e:
                        logger.error(f"Validation error in {self.collection}: {e}")
                        raise
                
                # 更新字段
                item.update(updates)
                # 自动更新updated_at
                item['updated_at'] = datetime.now().isoformat()
                data[i] = item
                self.save_all(data)
                logger.info(f"Updated {self.collection} record: {id_str}")
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
    
    def _check_unique_constraints(self, record: Dict[str, Any], all_data: List[Dict[str, Any]]):
        """检查唯一性约束"""
        id_field = f"{self.collection[:-1]}_id"
        record_id = record.get(id_field)
        
        # 用户名唯一性
        if self.collection == "users" and "username" in record:
            for existing in all_data:
                if existing.get(id_field) != record_id and existing.get("username") == record["username"]:
                    raise ValidationError(f"用户名 '{record['username']}' 已存在")
        
        # 邮箱唯一性
        if self.collection == "users" and "email" in record:
            for existing in all_data:
                if existing.get(id_field) != record_id and existing.get("email") == record["email"]:
                    raise ValidationError(f"邮箱 '{record['email']}' 已存在")
        
        # 设备编码唯一性
        if self.collection == "devices" and "device_code" in record:
            for existing in all_data:
                if existing.get(id_field) != record_id and existing.get("device_code") == record["device_code"]:
                    raise ValidationError(f"设备编码 '{record['device_code']}' 已存在")


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
