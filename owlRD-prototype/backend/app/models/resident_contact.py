"""
住户紧急联系人/家属账号模型
Resident Contact / Family Account Model

对应源参考文件：
- db/09_resident_contacts.sql

重要说明：
1. 为避免不必要的PHI暴露，姓名/电话/邮箱均为可选字段
2. 默认前端不开放姓名/电话/邮箱，仅在ToC/非HIPAA场景下，由用户自愿填写
3. 家属/联系人通过contact_resident_id关联到residents表（家属本身也是住户）
4. 默认开放的槽位为A/B/C，槽位D/E为扩展账号
5. 登录方式：家属通过residents表的账号登录
6. 系统只保存phone_hash/email_hash，不保存明文手机号/邮箱
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID, uuid4
from datetime import datetime

class ResidentContactBase(BaseModel):
    """住户联系人基础模型"""
    tenant_id: UUID = Field(..., description="租户ID")
    resident_id: UUID = Field(..., description="住户ID")
    slot: str = Field(..., min_length=1, max_length=1, description="槽位: A/B/C/D/E")
    
    # 关联的家属/联系人（可选）
    contact_resident_id: Optional[UUID] = Field(None, description="关联的家属账号ID")
    
    # 授权设置
    can_view_status: bool = Field(True, description="是否允许访问住户状态")
    can_receive_alert: bool = Field(True, description="是否接收告警")
    
    # 关系
    relationship: Optional[str] = Field(None, max_length=50, description="关系: Child/Spouse/Friend/Caregiver")
    
    # 可选的PHI（姓名/联系方式）
    contact_first_name: Optional[str] = Field(None, max_length=100, description="联系人名字")
    contact_last_name: Optional[str] = Field(None, max_length=100, description="联系人姓氏")
    contact_phone: Optional[str] = Field(None, max_length=25, description="联系人电话")
    contact_email: Optional[EmailStr] = Field(None, description="联系人邮箱")
    contact_sms: bool = Field(False, description="是否接收短信")
    
    # 登录/重置用的联系方式哈希
    phone_hash: Optional[bytes] = Field(None, description="电话号码哈希（SHA-256）")
    email_hash: Optional[bytes] = Field(None, description="邮箱哈希（SHA-256）")
    
    is_active: bool = Field(True, description="是否激活")

class ResidentContactCreate(ResidentContactBase):
    """创建住户联系人"""
    pass

class ResidentContactUpdate(BaseModel):
    """更新住户联系人"""
    contact_resident_id: Optional[UUID] = None
    can_view_status: Optional[bool] = None
    can_receive_alert: Optional[bool] = None
    relationship: Optional[str] = Field(None, max_length=50)
    contact_first_name: Optional[str] = Field(None, max_length=100)
    contact_last_name: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, max_length=25)
    contact_email: Optional[EmailStr] = None
    contact_sms: Optional[bool] = None
    is_active: Optional[bool] = None

class ResidentContact(ResidentContactBase):
    """住户联系人完整模型"""
    contact_id: UUID = Field(default_factory=uuid4, description="联系人ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "contact_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "10000000-0000-0000-0000-000000000001",
                "resident_id": "20000000-0000-0000-0000-000000000001",
                "slot": "A",
                "contact_resident_id": "30000000-0000-0000-0000-000000000001",
                "can_view_status": True,
                "can_receive_alert": True,
                "relationship": "Child",
                "contact_first_name": "Jane",
                "contact_last_name": "Doe",
                "contact_phone": "+1-555-0100",
                "contact_email": "jane.doe@example.com",
                "contact_sms": True,
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

    def get_full_name(self) -> str:
        """获取完整姓名"""
        if self.contact_first_name and self.contact_last_name:
            return f"{self.contact_first_name} {self.contact_last_name}"
        elif self.contact_first_name:
            return self.contact_first_name
        elif self.contact_last_name:
            return self.contact_last_name
        return f"联系人{self.slot}"

    def get_slot_name(self) -> str:
        """获取槽位描述"""
        slot_names = {
            "A": "主要联系人",
            "B": "次要联系人",
            "C": "备用联系人",
            "D": "扩展联系人1",
            "E": "扩展联系人2"
        }
        return slot_names.get(self.slot, f"联系人{self.slot}")

    def can_receive_notifications(self) -> bool:
        """是否可以接收通知"""
        return self.is_active and self.can_receive_alert

class ResidentContactSummary(BaseModel):
    """住户联系人摘要（用于列表显示）"""
    contact_id: UUID
    slot: str
    relationship: Optional[str]
    full_name: str
    can_view_status: bool
    can_receive_alert: bool
    is_active: bool
    
    class Config:
        from_attributes = True
