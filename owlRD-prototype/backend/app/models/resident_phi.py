"""
住户PHI(个人健康信息)模型
Resident Protected Health Information Model

对应源参考文件：
- db/08_resident_phi.sql

重要说明：
1. 仅在需要存储PHI的部署中启用
2. 必须在DB层面加密存储，不存储明文
3. 需要严格的权限控制，符合HIPAA要求
4. 物理上与residents表分离，减少PHI泄露风险

功能：
- 存储可选的个人健康信息
- 支持机构和居家护理场景
- 包含生物特征、健康状态、慢性病史等
- HomeCare场景的真实地址信息
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, date
from decimal import Decimal

class ResidentPHIBase(BaseModel):
    """住户PHI基础模型"""
    tenant_id: UUID = Field(..., description="租户ID")
    resident_id: UUID = Field(..., description="住户ID")
    
    # 基础个人信息
    first_name: Optional[str] = Field(None, max_length=100, description="名字")
    last_name: Optional[str] = Field(None, max_length=100, description="姓氏")
    gender: Optional[str] = Field(None, max_length=10, description="性别: Male/Female/Other/Unknown")
    date_of_birth: Optional[date] = Field(None, description="出生日期")
    resident_phone: Optional[str] = Field(None, max_length=25, description="住户电话")
    resident_email: Optional[EmailStr] = Field(None, description="住户邮箱")
    
    # 生物特征数据
    weight_lb: Optional[Decimal] = Field(None, ge=0, le=999.99, description="体重(磅)")
    height_ft: Optional[Decimal] = Field(None, ge=0, le=9.99, description="身高(英尺)")
    height_in: Optional[Decimal] = Field(None, ge=0, le=11.99, description="身高(英寸)")
    
    # 功能性活动能力
    mobility_level: Optional[int] = Field(None, ge=0, le=5, description="活动能力等级 0-5")
    
    # 功能性健康状态
    tremor_status: Optional[str] = Field(None, max_length=20, description="颤抖状态: None/Mild/Severe")
    mobility_aid: Optional[str] = Field(None, max_length=20, description="行走辅助: Cane/Wheelchair/None")
    adl_assistance: Optional[str] = Field(None, max_length=20, description="日常活动协助: Independent/NeedsHelp")
    comm_status: Optional[str] = Field(None, max_length=20, description="沟通状态: Normal/SpeechDifficulty")
    
    # 慢性病史标志
    has_hypertension: Optional[bool] = Field(None, description="高血压")
    has_hyperlipaemia: Optional[bool] = Field(None, description="高血脂")
    has_hyperglycaemia: Optional[bool] = Field(None, description="高血糖/糖尿病")
    has_stroke_history: Optional[bool] = Field(None, description="既往脑卒中史")
    has_paralysis: Optional[bool] = Field(None, description="肢体瘫痪/偏瘫")
    has_alzheimer: Optional[bool] = Field(None, description="阿尔茨海默病/痴呆")
    
    # 其他病史
    medical_history: Optional[str] = Field(None, description="其他病史说明")
    
    # HIS系统同步字段
    HIS_resident_name: Optional[str] = Field(None, max_length=100, description="HIS系统住户姓名")
    HIS_resident_admission_date: Optional[date] = Field(None, description="HIS入院日期")
    HIS_resident_discharge_date: Optional[date] = Field(None, description="HIS出院日期")
    HIS_resident_metadata: Optional[Dict[str, Any]] = Field(None, description="HIS其他元数据")
    
    # HomeCare场景的家庭地址（PHI）
    home_address_street: Optional[str] = Field(None, max_length=255, description="街道地址")
    home_address_city: Optional[str] = Field(None, max_length=100, description="城市")
    home_address_state: Optional[str] = Field(None, max_length=50, description="州/省")
    home_address_postal_code: Optional[str] = Field(None, max_length=20, description="邮编")
    plus_code: Optional[str] = Field(None, max_length=32, description="Plus Code全球编码")

class ResidentPHICreate(ResidentPHIBase):
    """创建住户PHI"""
    pass

class ResidentPHIUpdate(BaseModel):
    """更新住户PHI（所有字段可选）"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    gender: Optional[str] = Field(None, max_length=10)
    date_of_birth: Optional[date] = None
    resident_phone: Optional[str] = Field(None, max_length=25)
    resident_email: Optional[EmailStr] = None
    
    weight_lb: Optional[Decimal] = None
    height_ft: Optional[Decimal] = None
    height_in: Optional[Decimal] = None
    
    mobility_level: Optional[int] = Field(None, ge=0, le=5)
    
    tremor_status: Optional[str] = Field(None, max_length=20)
    mobility_aid: Optional[str] = Field(None, max_length=20)
    adl_assistance: Optional[str] = Field(None, max_length=20)
    comm_status: Optional[str] = Field(None, max_length=20)
    
    has_hypertension: Optional[bool] = None
    has_hyperlipaemia: Optional[bool] = None
    has_hyperglycaemia: Optional[bool] = None
    has_stroke_history: Optional[bool] = None
    has_paralysis: Optional[bool] = None
    has_alzheimer: Optional[bool] = None
    
    medical_history: Optional[str] = None
    
    HIS_resident_name: Optional[str] = Field(None, max_length=100)
    HIS_resident_admission_date: Optional[date] = None
    HIS_resident_discharge_date: Optional[date] = None
    HIS_resident_metadata: Optional[Dict[str, Any]] = None
    
    home_address_street: Optional[str] = Field(None, max_length=255)
    home_address_city: Optional[str] = Field(None, max_length=100)
    home_address_state: Optional[str] = Field(None, max_length=50)
    home_address_postal_code: Optional[str] = Field(None, max_length=20)
    plus_code: Optional[str] = Field(None, max_length=32)

class ResidentPHI(ResidentPHIBase):
    """住户PHI完整模型"""
    phi_id: UUID = Field(default_factory=uuid4, description="PHI记录ID")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "phi_id": "550e8400-e29b-41d4-a716-446655440000",
                "tenant_id": "10000000-0000-0000-0000-000000000001",
                "resident_id": "20000000-0000-0000-0000-000000000001",
                "first_name": "John",
                "last_name": "Doe",
                "gender": "Male",
                "date_of_birth": "1940-01-01",
                "resident_phone": "+1-555-0100",
                "resident_email": "john.doe@example.com",
                "weight_lb": 165.5,
                "height_ft": 5.0,
                "height_in": 10.0,
                "mobility_level": 3,
                "tremor_status": "None",
                "mobility_aid": "Cane",
                "adl_assistance": "NeedsHelp",
                "comm_status": "Normal",
                "has_hypertension": True,
                "has_hyperlipaemia": False,
                "has_hyperglycaemia": True,
                "has_stroke_history": False,
                "has_paralysis": False,
                "has_alzheimer": False,
                "medical_history": "Type 2 Diabetes, managed with medication",
                "home_address_street": "123 Main St",
                "home_address_city": "Springfield",
                "home_address_state": "IL",
                "home_address_postal_code": "62701",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

    def get_full_name(self) -> str:
        """获取完整姓名"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""

    def get_full_address(self) -> str:
        """获取完整地址"""
        parts = []
        if self.home_address_street:
            parts.append(self.home_address_street)
        if self.home_address_city:
            parts.append(self.home_address_city)
        if self.home_address_state:
            parts.append(self.home_address_state)
        if self.home_address_postal_code:
            parts.append(self.home_address_postal_code)
        return ", ".join(parts)

    def has_chronic_conditions(self) -> bool:
        """是否有慢性病"""
        return any([
            self.has_hypertension,
            self.has_hyperlipaemia,
            self.has_hyperglycaemia,
            self.has_stroke_history,
            self.has_paralysis,
            self.has_alzheimer
        ])

    def get_chronic_conditions_list(self) -> list[str]:
        """获取慢性病列表"""
        conditions = []
        if self.has_hypertension:
            conditions.append("高血压")
        if self.has_hyperlipaemia:
            conditions.append("高血脂")
        if self.has_hyperglycaemia:
            conditions.append("高血糖/糖尿病")
        if self.has_stroke_history:
            conditions.append("脑卒中史")
        if self.has_paralysis:
            conditions.append("肢体瘫痪")
        if self.has_alzheimer:
            conditions.append("阿尔茨海默病")
        return conditions

class ResidentPHISummary(BaseModel):
    """住户PHI摘要（用于列表显示，脱敏）"""
    phi_id: UUID
    resident_id: UUID
    has_phi_data: bool = Field(True, description="是否有PHI数据")
    has_chronic_conditions: bool = Field(False, description="是否有慢性病")
    chronic_conditions_count: int = Field(0, description="慢性病数量")
    
    class Config:
        from_attributes = True
