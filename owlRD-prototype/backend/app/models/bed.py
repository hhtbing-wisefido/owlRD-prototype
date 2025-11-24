"""
床位模型
Bed Model

对应源参考文件：
- db/06_beds.sql

业务规则：
1. Bed必须绑定到Room（RoomID NOT NULL），绑定路径：Location → Room → Bed
2. 当客户从Default Room迁移到细分Room时，应先在业务层迁移Bed
3. 若夫妻同床但使用2套独立监测设备，可在同一物理床上建2个护理床位（BedA/BedB）
4. 若仅有1套监测设备，则视为1个护理床位（单一Bed）

重要概念：
- ActiveBed: 同时绑定Resident（有人）+ 至少一个监控设备 + monitoring_enabled=TRUE
- NonActiveBed: 其他情况（仅有人 / 仅设备 / 暂未启用监控）
- 住户出院后，设备应进入Dormant模式（monitoring_enabled=FALSE）
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class BedBase(BaseModel):
    """床位基础模型"""
    tenant_id: UUID = Field(..., description="租户ID")
    room_id: UUID = Field(..., description="房间ID")
    location_id: UUID = Field(..., description="位置ID（冗余，加速查询）")
    
    # 床位配置
    bed_name: str = Field(..., max_length=50, description="床位名称（建议使用A/B/C或Bed1/Bed2等技术编号）")
    bed_type: str = Field(..., max_length=20, description="床位类型: ActiveBed/NonActiveBed")
    
    # 床垫信息（可选）
    mattress_material: Optional[str] = Field(None, max_length=50, description="床垫材质/类型")
    mattress_thickness: Optional[str] = Field(None, max_length=20, description="床垫厚度: <7in/7-10in/11-14in/14in+")
    
    # 住户关联
    resident_id: Optional[UUID] = Field(None, description="绑定的住户ID")
    
    # 设备计数（由数据库触发器自动维护）
    bound_device_count: int = Field(0, ge=0, description="绑定的激活监护设备数量")

class BedCreate(BedBase):
    """创建床位"""
    pass

class BedUpdate(BaseModel):
    """更新床位"""
    bed_name: Optional[str] = Field(None, max_length=50)
    bed_type: Optional[str] = Field(None, max_length=20)
    mattress_material: Optional[str] = Field(None, max_length=50)
    mattress_thickness: Optional[str] = Field(None, max_length=20)
    resident_id: Optional[UUID] = None

class Bed(BedBase):
    """床位完整模型"""
    bed_id: UUID = Field(default_factory=uuid4, description="床位ID")
    # is_active由数据库自动计算: bound_device_count > 0
    is_active: bool = Field(False, description="床位是否激活（自动计算）")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "bed_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "10000000-0000-0000-0000-000000000001",
                "room_id": "20000000-0000-0000-0000-000000000001",
                "location_id": "30000000-0000-0000-0000-000000000001",
                "bed_name": "A",
                "bed_type": "ActiveBed",
                "mattress_material": "Memory Foam",
                "mattress_thickness": "7-10in",
                "resident_id": "40000000-0000-0000-0000-000000000001",
                "bound_device_count": 2,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

    def is_occupied(self) -> bool:
        """床位是否有住户"""
        return self.resident_id is not None

    def has_monitoring_devices(self) -> bool:
        """是否有监控设备"""
        return self.bound_device_count > 0

    def is_active_bed(self) -> bool:
        """是否为激活床位（有人+有设备）"""
        return self.is_occupied() and self.has_monitoring_devices()

    def get_bed_status(self) -> str:
        """获取床位状态描述"""
        if self.is_active_bed():
            return "激活监护中"
        elif self.is_occupied():
            return "有住户但未启用监控"
        elif self.has_monitoring_devices():
            return "有设备但无住户"
        else:
            return "空床位"

class BedSummary(BaseModel):
    """床位摘要（用于列表显示）"""
    bed_id: UUID
    bed_name: str
    bed_type: str
    resident_id: Optional[UUID]
    is_active: bool
    bound_device_count: int
    status_text: str = Field("", description="床位状态描述")
    
    class Config:
        from_attributes = True

class BedWithResident(Bed):
    """床位及住户信息（扩展模型）"""
    resident_name: Optional[str] = Field(None, description="住户名称")
    resident_tag: Optional[str] = Field(None, description="住户标签")
    
    class Config:
        from_attributes = True
