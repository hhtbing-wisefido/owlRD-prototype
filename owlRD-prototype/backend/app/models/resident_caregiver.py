"""
住户-护理员关系模型
Resident-Caregiver Relationship Model

对应源参考文件：
- db/10_resident_caregivers.sql

功能：
1. 表示哪些护理人员主要负责某位住户
2. 替代原始设计中Resident表里的Caregiver1ID..15等多列结构
3. 不存储任何住户PHI，仅存关联与角色信息
4. 用于权限系统的ASSIGNED_ONLY数据范围过滤
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

class ResidentCaregiverBase(BaseModel):
    """住户护理员关系基础模型"""
    tenant_id: UUID = Field(..., description="租户ID")
    resident_id: UUID = Field(..., description="住户ID")
    
    # 最多5个护理人员可同时护理一个住户
    caregiver_id1: Optional[UUID] = Field(None, description="护理人员1 ID")
    caregiver_id2: Optional[UUID] = Field(None, description="护理人员2 ID")
    caregiver_id3: Optional[UUID] = Field(None, description="护理人员3 ID")
    caregiver_id4: Optional[UUID] = Field(None, description="护理人员4 ID")
    caregiver_id5: Optional[UUID] = Field(None, description="护理人员5 ID")
    
    # 护士组标签，如 "NightShift", "Group.A", "FallsExpert" 等
    caregivers_tags: Optional[Dict[str, Any]] = Field(None, description="护理员标签")

class ResidentCaregiverCreate(ResidentCaregiverBase):
    """创建住户护理员关系"""
    pass

class ResidentCaregiverUpdate(BaseModel):
    """更新住户护理员关系"""
    caregiver_id1: Optional[UUID] = None
    caregiver_id2: Optional[UUID] = None
    caregiver_id3: Optional[UUID] = None
    caregiver_id4: Optional[UUID] = None
    caregiver_id5: Optional[UUID] = None
    caregivers_tags: Optional[Dict[str, Any]] = None

class ResidentCaregiver(ResidentCaregiverBase):
    """住户护理员关系完整模型"""
    id: UUID = Field(default_factory=uuid4, description="关系ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "10000000-0000-0000-0000-000000000001",
                "resident_id": "20000000-0000-0000-0000-000000000001",
                "caregiver_id1": "30000000-0000-0000-0000-000000000001",
                "caregiver_id2": "30000000-0000-0000-0000-000000000002",
                "caregiver_id3": None,
                "caregiver_id4": None,
                "caregiver_id5": None,
                "caregivers_tags": {
                    "shift": "NightShift",
                    "group": "A",
                    "specialty": "FallsExpert"
                },
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

    def get_caregiver_ids(self) -> List[UUID]:
        """获取所有分配的护理员ID列表"""
        ids = []
        for i in range(1, 6):
            caregiver_id = getattr(self, f'caregiver_id{i}', None)
            if caregiver_id:
                ids.append(caregiver_id)
        return ids

    def is_caregiver_assigned(self, user_id: UUID) -> bool:
        """检查指定用户是否是该住户的护理员"""
        return user_id in self.get_caregiver_ids()

    def get_primary_caregiver(self) -> Optional[UUID]:
        """获取主要护理员（第一个分配的护理员）"""
        return self.caregiver_id1
