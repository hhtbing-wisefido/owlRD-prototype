"""
卡片函数模型
Card Function Model

对应源参考文件：
- db/19_card_functions.sql
- docs/20_Card_Creation_Rules_Final.md

用途：
1. 根据卡片创建规则自动生成和维护卡片
2. 计算卡片地址
3. 判断ActiveBed条件
4. 为指定location重新生成所有卡片

卡片创建规则：
- ActiveBed卡片: 有住户 + 有激活监护的监控设备
- Location卡片: 位置级别的卡片
- PublicSpace卡片: 公共空间卡片
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from enum import Enum

class CardType(str, Enum):
    """卡片类型枚举"""
    ACTIVEBED = "ActiveBed"
    LOCATION = "Location"
    PUBLIC_SPACE = "PublicSpace"

class CardAddressConfig(BaseModel):
    """卡片地址配置"""
    location_tag: Optional[str] = Field(None, description="位置标签")
    location_name: str = Field(..., description="位置名称")
    bed_name: Optional[str] = Field(None, description="床位名称")
    
    def calculate_activebed_address(self) -> str:
        """计算ActiveBed卡片地址"""
        if self.location_tag and self.bed_name:
            return f"{self.location_tag}-{self.location_name}-{self.bed_name}"
        elif self.bed_name:
            return f"{self.location_name}-{self.bed_name}"
        else:
            raise ValueError("bed_name is required for ActiveBed address")
    
    def calculate_location_address(self) -> str:
        """计算Location卡片地址"""
        if self.location_tag:
            return f"{self.location_tag}-{self.location_name}"
        else:
            return self.location_name

class ActiveBedCondition(BaseModel):
    """ActiveBed判断条件"""
    bed_id: UUID
    resident_id: Optional[UUID]
    bound_device_count: int
    
    def is_activebed(self) -> bool:
        """判断是否为ActiveBed"""
        return (
            self.resident_id is not None 
            and self.bound_device_count > 0
        )

class CardGenerationRule(BaseModel):
    """卡片生成规则"""
    rule_name: str = Field(..., description="规则名称")
    card_type: CardType = Field(..., description="卡片类型")
    conditions: Dict[str, Any] = Field(..., description="生成条件")
    priority: int = Field(0, description="优先级")
    is_active: bool = Field(True, description="是否激活")
    
    class Config:
        use_enum_values = True

class CardRegenerationRequest(BaseModel):
    """卡片重新生成请求"""
    location_id: UUID = Field(..., description="位置ID")
    tenant_id: UUID = Field(..., description="租户ID")
    force: bool = Field(False, description="是否强制重新生成")
    card_types: Optional[List[CardType]] = Field(None, description="指定卡片类型")

class CardRegenerationResult(BaseModel):
    """卡片重新生成结果"""
    location_id: UUID
    cards_created: int = Field(0, description="创建的卡片数")
    cards_updated: int = Field(0, description="更新的卡片数")
    cards_deleted: int = Field(0, description="删除的卡片数")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    success: bool = Field(True, description="是否成功")
    timestamp: datetime = Field(default_factory=datetime.now)

class CardFunctionConfig(BaseModel):
    """卡片函数配置"""
    tenant_id: UUID
    auto_generate_cards: bool = Field(True, description="是否自动生成卡片")
    auto_update_cards: bool = Field(True, description="是否自动更新卡片")
    generation_rules: List[CardGenerationRule] = Field(default_factory=list)
    address_format: Dict[str, str] = Field(
        default_factory=lambda: {
            "activebed": "{location_tag}-{location_name}-{bed_name}",
            "location": "{location_tag}-{location_name}",
            "public_space": "{location_name}-PublicSpace"
        },
        description="地址格式配置"
    )

class CardFunctionStatus(BaseModel):
    """卡片函数状态"""
    tenant_id: UUID
    total_cards: int = Field(0, description="总卡片数")
    activebed_cards: int = Field(0, description="ActiveBed卡片数")
    location_cards: int = Field(0, description="Location卡片数")
    public_space_cards: int = Field(0, description="公共空间卡片数")
    last_regeneration: Optional[datetime] = Field(None, description="最后重新生成时间")
    auto_generation_enabled: bool = Field(True, description="自动生成是否启用")

# 辅助函数类
class CardFunctionHelper:
    """卡片函数辅助类"""
    
    @staticmethod
    def calculate_address(config: CardAddressConfig, card_type: CardType) -> str:
        """根据卡片类型计算地址"""
        if card_type == CardType.ACTIVEBED:
            return config.calculate_activebed_address()
        elif card_type == CardType.LOCATION:
            return config.calculate_location_address()
        elif card_type == CardType.PUBLIC_SPACE:
            return f"{config.calculate_location_address()}-PublicSpace"
        else:
            raise ValueError(f"Unknown card type: {card_type}")
    
    @staticmethod
    def check_activebed_condition(
        resident_id: Optional[UUID],
        bound_device_count: int
    ) -> bool:
        """检查ActiveBed条件"""
        return resident_id is not None and bound_device_count > 0
    
    @staticmethod
    def should_generate_card(
        card_type: CardType,
        location_type: str,
        is_public_space: bool,
        is_multi_person_room: bool,
        activebed_count: int
    ) -> bool:
        """判断是否应该生成卡片"""
        if card_type == CardType.PUBLIC_SPACE:
            return is_public_space
        elif card_type == CardType.ACTIVEBED:
            return activebed_count > 0
        elif card_type == CardType.LOCATION:
            # Location卡片生成条件
            if is_public_space:
                return False  # 公共空间不生成Location卡片
            if is_multi_person_room and activebed_count > 1:
                return True  # 多人房间且有多个ActiveBed
            if activebed_count == 0:
                return True  # 无ActiveBed时生成Location卡片
            return False
        return False
