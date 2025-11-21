"""
住户数据模型
对应 residents (07_residents.sql), resident_phi (08_resident_phi.sql),
    resident_contacts (09_resident_contacts.sql), resident_caregivers (10_resident_caregivers.sql) 表
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from pydantic import Field, EmailStr, field_validator

from app.models.base import BaseModel, generate_uuid


# ============================================================================
# Resident Models (住户模型 - 完全匿名化)
# ============================================================================

class ResidentBase(BaseModel):
    """住户基础模型（完全匿名化，无PII）"""
    
    # 外部HIS系统同步字段（不包含PII）
    HIS_resident_id: Optional[str] = Field(None, max_length=100, description="HIS系统住户ID（外部标识）")
    HIS_resident_bed_id: Optional[str] = Field(None, max_length=100, description="HIS系统床位ID")
    HIS_resident_status: Optional[str] = Field(None, max_length=100, description="HIS系统住户状态")
    
    # 住户账号（机构内部唯一标识，不包含姓名）
    resident_account: str = Field(..., max_length=100, description="住户账号（内部标识）")
    
    # 虚拟姓名字段（用匿名代称填充）
    first_name: Optional[str] = Field(None, max_length=100, description="名字（可空）")
    last_name: str = Field(..., max_length=100, description="姓氏（匿名代称）")
    
    # 机构或在家模式
    is_institutional: bool = Field(default=False, description="机构模式或在家模式")
    
    # 位置信息
    location_id: Optional[UUID] = Field(None, description="当前地址/门牌号")
    bed_id: Optional[UUID] = Field(None, description="当前床位（必须唯一）")
    
    # 入住信息
    admission_date: date = Field(..., description="入住日期/服务开始日期")
    status: str = Field(default="active", max_length=50, description="状态：active, discharged, transferred")
    
    # 元数据（仅非PII信息）
    metadata: Optional[Dict[str, Any]] = Field(None, description="元数据（仅非PII）")
    
    # 家庭标签
    family_tag: Optional[str] = Field(None, max_length=100, description="家庭标识符（同一家庭成员使用相同标签）")
    family_member_account_1: Optional[str] = Field(None, max_length=100, description="家庭成员账号")
    
    # 是否允许家属查看状态
    can_view_status: bool = Field(default=True, description="是否允许家属查看状态")
    
    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        allowed = ["active", "discharged", "transferred"]
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v


class ResidentCreate(ResidentBase):
    """创建住户请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class ResidentUpdate(BaseModel):
    """更新住户请求模型"""
    
    HIS_resident_id: Optional[str] = Field(None, max_length=100)
    HIS_resident_bed_id: Optional[str] = Field(None, max_length=100)
    HIS_resident_status: Optional[str] = Field(None, max_length=100)
    resident_account: Optional[str] = Field(None, max_length=100)
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    is_institutional: Optional[bool] = None
    location_id: Optional[UUID] = None
    bed_id: Optional[UUID] = None
    admission_date: Optional[date] = None
    status: Optional[str] = Field(None, max_length=50)
    metadata: Optional[Dict[str, Any]] = None
    family_tag: Optional[str] = Field(None, max_length=100)
    family_member_account_1: Optional[str] = Field(None, max_length=100)
    can_view_status: Optional[bool] = None


class Resident(ResidentBase):
    """完整住户模型（包含系统生成字段）"""
    
    resident_id: UUID = Field(default_factory=generate_uuid, description="住户唯一ID")
    tenant_id: UUID = Field(..., description="所属租户ID")
    
    # 匿名代称（可选，向后兼容）
    anonymous_name: Optional[str] = Field(None, max_length=100, description="匿名代称（与last_name相同）")
    
    # 哈希字段（仅内部验证，不对外暴露）
    phone_hash: Optional[bytes] = Field(None, description="手机号哈希", exclude=True)
    email_hash: Optional[bytes] = Field(None, description="邮箱哈希", exclude=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "resident_id": "550e8400-e29b-41d4-a716-446655440020",
                "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                "HIS_resident_id": "HIS-12345",
                "resident_account": "RES-001",
                "first_name": None,
                "last_name": "锅匠",
                "anonymous_name": "锅匠",
                "is_institutional": True,
                "location_id": "550e8400-e29b-41d4-a716-446655440010",
                "bed_id": "550e8400-e29b-41d4-a716-446655440012",
                "admission_date": "2025-01-01",
                "status": "active",
                "family_tag": None,
                "can_view_status": True
            }
        }


# ============================================================================
# ResidentPHI Models (住户健康信息 - 加密存储)
# ============================================================================

class ResidentPHIBase(BaseModel):
    """住户PHI基础模型（包含个人健康信息）"""
    
    # 基本PHI
    first_name: Optional[str] = Field(None, max_length=100, description="真实名字（Given Name）")
    last_name: Optional[str] = Field(None, max_length=100, description="真实姓氏（Surname）")
    gender: Optional[str] = Field(None, max_length=10, description="性别：Male/Female/Other/Unknown")
    date_of_birth: Optional[date] = Field(None, description="出生日期")
    resident_phone: Optional[str] = Field(None, max_length=25, description="住户个人电话")
    resident_email: Optional[EmailStr] = Field(None, description="住户个人邮箱")
    
    # 生物特征PHI
    weight_lb: Optional[Decimal] = Field(None, description="体重（磅）")
    height_ft: Optional[Decimal] = Field(None, description="身高（英尺）")
    height_in: Optional[Decimal] = Field(None, description="身高（英寸）")
    
    # 功能性活动能力
    mobility_level: Optional[int] = Field(None, ge=0, le=5, description="活动能力：0无行动能力 ~ 5完全独立")
    
    # 功能性健康状态
    tremor_status: Optional[str] = Field(None, max_length=20, description="颤抖状态：None/Mild/Severe")
    mobility_aid: Optional[str] = Field(None, max_length=20, description="行走辅助：Cane/Wheelchair/None")
    adl_assistance: Optional[str] = Field(None, max_length=20, description="日常活动协助：Independent/NeedsHelp")
    comm_status: Optional[str] = Field(None, max_length=20, description="沟通状态：Normal/SpeechDifficulty")
    
    # 慢性病史
    has_hypertension: Optional[bool] = Field(None, description="高血压")
    has_hyperlipaemia: Optional[bool] = Field(None, description="高血脂")
    has_hyperglycaemia: Optional[bool] = Field(None, description="高血糖/糖尿病")
    has_stroke_history: Optional[bool] = Field(None, description="既往脑卒中史")
    has_paralysis: Optional[bool] = Field(None, description="肢体瘫痪/偏瘫")
    has_alzheimer: Optional[bool] = Field(None, description="阿尔茨海默病/痴呆")
    medical_history: Optional[str] = Field(None, description="其他病史说明")
    
    # HIS系统同步字段（包含PII）
    HIS_resident_name: Optional[str] = Field(None, max_length=100, description="HIS系统真实姓名")
    HIS_resident_admission_date: Optional[date] = Field(None, description="HIS入院日期")
    HIS_resident_discharge_date: Optional[date] = Field(None, description="HIS出院日期")
    HIS_resident_metadata: Optional[Dict[str, Any]] = Field(None, description="HIS其他元数据")
    
    # HomeCare场景家庭地址（PHI）
    home_address_street: Optional[str] = Field(None, max_length=255, description="街道地址")
    home_address_city: Optional[str] = Field(None, max_length=100, description="城市")
    home_address_state: Optional[str] = Field(None, max_length=50, description="州/省")
    home_address_postal_code: Optional[str] = Field(None, max_length=20, description="邮编")
    plus_code: Optional[str] = Field(None, max_length=32, description="Google Plus Code")


class ResidentPHICreate(ResidentPHIBase):
    """创建住户PHI请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")
    resident_id: UUID = Field(..., description="关联住户ID")


class ResidentPHIUpdate(ResidentPHIBase):
    """更新住户PHI请求模型"""
    pass


class ResidentPHI(ResidentPHIBase):
    """住户PHI完整模型"""
    
    phi_id: UUID = Field(default_factory=generate_uuid, description="PHI唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    resident_id: UUID = Field(..., description="关联住户ID")


# ============================================================================
# ResidentContact Models (住户联系人/家属账号)
# ============================================================================

class ResidentContactBase(BaseModel):
    """住户联系人基础模型"""
    
    slot: str = Field(..., max_length=1, description="槽位：A/B/C/D/E")
    contact_resident_id: Optional[UUID] = Field(None, description="关联的家属住户ID")
    can_view_status: bool = Field(default=True, description="是否允许查看状态")
    can_receive_alert: bool = Field(default=True, description="是否接收告警")
    relationship: Optional[str] = Field(None, max_length=50, description="关系：Child/Spouse/Friend/Caregiver")
    
    # 可选PHI
    contact_first_name: Optional[str] = Field(None, max_length=100, description="联系人名字")
    contact_last_name: Optional[str] = Field(None, max_length=100, description="联系人姓氏")
    contact_phone: Optional[str] = Field(None, max_length=25, description="联系人电话")
    contact_email: Optional[EmailStr] = Field(None, description="联系人邮箱")
    contact_sms: bool = Field(default=False, description="是否接收短信")
    
    is_active: bool = Field(default=True, description="是否启用")
    
    @field_validator("slot")
    @classmethod
    def validate_slot(cls, v: str) -> str:
        allowed = ["A", "B", "C", "D", "E"]
        if v not in allowed:
            raise ValueError(f"slot must be one of {allowed}")
        return v


class ResidentContactCreate(ResidentContactBase):
    """创建住户联系人请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")
    resident_id: UUID = Field(..., description="关联住户ID")


class ResidentContactUpdate(BaseModel):
    """更新住户联系人请求模型"""
    
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
    
    contact_id: UUID = Field(default_factory=generate_uuid, description="联系人唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    resident_id: UUID = Field(..., description="关联住户ID")
    
    # 哈希字段（不对外暴露）
    phone_hash: Optional[bytes] = Field(None, exclude=True)
    email_hash: Optional[bytes] = Field(None, exclude=True)


# ============================================================================
# ResidentCaregiver Models (住户-护士关联)
# ============================================================================

class ResidentCaregiverBase(BaseModel):
    """住户-护士关联基础模型"""
    
    # 护理人员（最多5个）
    caregiver_id1: UUID = Field(..., description="护理人员1 ID")
    caregiver_id2: Optional[UUID] = Field(None, description="护理人员2 ID")
    caregiver_id3: Optional[UUID] = Field(None, description="护理人员3 ID")
    caregiver_id4: Optional[UUID] = Field(None, description="护理人员4 ID")
    caregiver_id5: Optional[UUID] = Field(None, description="护理人员5 ID")
    
    # 护士组标签
    caregivers_tags: Optional[Dict[str, Any]] = Field(None, description="护士组标签（如NightShift, Group.A）")


class ResidentCaregiverCreate(ResidentCaregiverBase):
    """创建住户-护士关联请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")
    resident_id: UUID = Field(..., description="关联住户ID")


class ResidentCaregiverUpdate(BaseModel):
    """更新住户-护士关联请求模型"""
    
    caregiver_id1: Optional[UUID] = None
    caregiver_id2: Optional[UUID] = None
    caregiver_id3: Optional[UUID] = None
    caregiver_id4: Optional[UUID] = None
    caregiver_id5: Optional[UUID] = None
    caregivers_tags: Optional[Dict[str, Any]] = None


class ResidentCaregiver(ResidentCaregiverBase):
    """住户-护士关联完整模型"""
    
    id: UUID = Field(default_factory=generate_uuid, description="关联唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    resident_id: UUID = Field(..., description="关联住户ID")


# ============================================================================
# AnonymousNamePool Models (匿名代称池 - 300个)
# ============================================================================

class AnonymousNamePoolBase(BaseModel):
    """匿名代称池基础模型"""
    
    anonymous_name: str = Field(..., max_length=100, description="匿名代称（如锅匠、哆啦A梦、水豚）")
    category: str = Field(..., max_length=50, description="分类：profession/character/animal/item")
    is_assigned: bool = Field(default=False, description="是否已分配")
    assigned_to_resident_id: Optional[UUID] = Field(None, description="分配给的住户ID")
    assigned_at: Optional[datetime] = Field(None, description="分配时间")
    
    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        allowed = ["profession", "character", "animal", "item"]
        if v not in allowed:
            raise ValueError(f"category must be one of {allowed}")
        return v


class AnonymousNamePoolCreate(AnonymousNamePoolBase):
    """创建匿名代称请求模型"""
    tenant_id: UUID = Field(..., description="所属租户ID")


class AnonymousNamePoolUpdate(BaseModel):
    """更新匿名代称请求模型"""
    
    is_assigned: Optional[bool] = None
    assigned_to_resident_id: Optional[UUID] = None
    assigned_at: Optional[datetime] = None


class AnonymousNamePool(AnonymousNamePoolBase):
    """匿名代称池完整模型"""
    
    name_id: UUID = Field(default_factory=generate_uuid, description="代称唯一标识")
    tenant_id: UUID = Field(..., description="所属租户ID")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
