"""
基础数据模型
提供所有模型的共同基类和混入
"""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from pydantic import BaseModel as PydanticBaseModel, Field, ConfigDict


class BaseModel(PydanticBaseModel):
    """基础Pydantic模型配置"""
    
    model_config = ConfigDict(
        # 允许从ORM对象填充
        from_attributes=True,
        # 使用枚举值
        use_enum_values=True,
        # JSON序列化配置
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        },
        # 严格模式
        strict=False,
        # 验证赋值
        validate_assignment=True,
    )


class TimestampMixin(BaseModel):
    """时间戳混入 - 提供created_at和updated_at字段"""
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class UUIDMixin(BaseModel):
    """UUID主键混入"""
    
    id: UUID = Field(default_factory=uuid4, description="唯一标识符")


def generate_uuid() -> str:
    """生成UUID字符串"""
    return str(uuid4())
