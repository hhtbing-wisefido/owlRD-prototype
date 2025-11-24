"""
房间模型
Room Model

对应源参考文件：
- db/05_rooms.sql

业务规则：
1. 每个Location创建时，应用层应自动生成一个IsDefault=TRUE的Room
2. Bed和Device总是绑定到Room（绑定路径：Location → Room → Bed/Device）
3. 当客户细分房间时，Default Room保持Active，但不再接受新的Bed/Device绑定
4. 当客户取消细分时，可以重新将所有Bed/Device挂回到Default Room
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

class RoomBase(BaseModel):
    """房间基础模型"""
    tenant_id: UUID = Field(..., description="租户ID")
    location_id: UUID = Field(..., description="位置ID")
    room_name: str = Field(..., max_length=100, description="房间名称")
    is_default: bool = Field(False, description="是否为默认房间")
    is_active: bool = Field(True, description="是否激活")
    
    # 房间布局配置（可选，用于房间级独立布局）
    # 如果使用统一楼层布局（locations.layout_config），此字段可为 NULL
    # 如果使用房间级独立布局，此字段存储该房间的独立布局
    # 布局JSON结构（vue_radar canvasData）：
    # {
    #   "params": CanvasParams,   // 画布参数，包含devices列表等
    #   "objects": BaseObject[],  // 所有对象（Bed/Radar/Furniture/Wall...）
    #   "timestamp": "ISO8601"
    # }
    layout_config: Optional[Dict[str, Any]] = Field(None, description="房间布局配置")

class RoomCreate(RoomBase):
    """创建房间"""
    pass

class RoomUpdate(BaseModel):
    """更新房间"""
    room_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    layout_config: Optional[Dict[str, Any]] = None

class Room(RoomBase):
    """房间完整模型"""
    room_id: UUID = Field(default_factory=uuid4, description="房间ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "room_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "10000000-0000-0000-0000-000000000001",
                "location_id": "20000000-0000-0000-0000-000000000001",
                "room_name": "E203",
                "is_default": True,
                "is_active": True,
                "layout_config": {
                    "params": {
                        "devices": ["device1", "device2"]
                    },
                    "objects": [
                        {"type": "Bed", "x": 100, "y": 100},
                        {"type": "Radar", "x": 200, "y": 200}
                    ],
                    "timestamp": "2024-01-01T00:00:00Z"
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

    def has_custom_layout(self) -> bool:
        """是否有自定义布局"""
        return self.layout_config is not None and bool(self.layout_config)

class RoomSummary(BaseModel):
    """房间摘要（用于列表显示）"""
    room_id: UUID
    room_name: str
    is_default: bool
    is_active: bool
    has_layout: bool = Field(False, description="是否有自定义布局")
    
    class Config:
        from_attributes = True
