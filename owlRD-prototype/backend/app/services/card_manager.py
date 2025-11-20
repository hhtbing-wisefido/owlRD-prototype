"""
卡片管理服务
自动生成和管理ActiveBed/Location卡片
"""

from typing import Dict, List, Any, Optional
from uuid import UUID

from app.models.card import Card, CardType, CardCreate
from app.services.storage import StorageService


class CardManager:
    """卡片管理器"""
    
    def __init__(self):
        """初始化卡片管理器"""
        self.card_storage = StorageService(collection="cards")
        self.bed_storage = StorageService(collection="beds")
        self.location_storage = StorageService(collection="locations")
        self.resident_storage = StorageService(collection="residents")
    
    def create_activebed_card(self, bed_id: UUID, tenant_id: UUID) -> Optional[Dict[str, Any]]:
        """
        为ActiveBed创建卡片
        
        Args:
            bed_id: 床位ID
            tenant_id: 租户ID
            
        Returns:
            创建的卡片
        """
        # 查找床位
        bed = self.bed_storage.find_by_id("bed_id", bed_id)
        if not bed:
            return None
        
        # 查找绑定的住户
        resident = None
        if bed.get("resident_id"):
            resident = self.resident_storage.find_by_id("resident_id", bed["resident_id"])
        
        # 生成卡片名称和地址
        card_name = resident.get("last_name", "未分配") if resident else "未分配"
        card_address = self._generate_card_address(bed, tenant_id)
        
        # 创建卡片
        card_data = {
            "card_id": str(UUID.uuid4()),
            "tenant_id": str(tenant_id),
            "card_type": CardType.ACTIVE_BED,
            "bed_id": str(bed_id),
            "location_id": bed.get("location_id"),
            "card_name": card_name,
            "card_address": card_address,
            "resident_id": bed.get("resident_id"),
            "is_public_space": False,
            "is_active": True
        }
        
        return self.card_storage.create(card_data)
    
    def create_location_card(self, location_id: UUID, tenant_id: UUID) -> Optional[Dict[str, Any]]:
        """
        为Location创建卡片
        
        Args:
            location_id: 位置ID
            tenant_id: 租户ID
            
        Returns:
            创建的卡片
        """
        # 查找位置
        location = self.location_storage.find_by_id("location_id", location_id)
        if not location:
            return None
        
        # 生成卡片
        card_data = {
            "card_id": str(UUID.uuid4()),
            "tenant_id": str(tenant_id),
            "card_type": CardType.LOCATION,
            "location_id": str(location_id),
            "card_name": location.get("location_name", ""),
            "card_address": location.get("door_number", ""),
            "is_public_space": location.get("is_public_space"),
            "routing_alert_user_ids": location.get("alert_user_ids"),
            "routing_alert_tags": location.get("alert_tags"),
            "is_active": True
        }
        
        return self.card_storage.create(card_data)
    
    def _generate_card_address(self, bed: Dict[str, Any], tenant_id: UUID) -> str:
        """
        生成卡片地址
        
        格式：Location > Room > Bed
        例如：Building A > Room 101 > Bed 1
        """
        parts = []
        
        # 获取房间信息
        room_id = bed.get("room_id")
        if room_id:
            room = self.room_storage.find_by_id("room_id", room_id)
            if room:
                parts.append(room.get("room_name", "Unknown Room"))
                
                # 获取位置信息
                location_id = room.get("location_id")
                if location_id:
                    location = self.location_storage.find_by_id("location_id", location_id)
                    if location:
                        parts.insert(0, location.get("location_name", "Unknown Location"))
        
        # 添加床位名称
        parts.append(bed.get("bed_name", "Unknown Bed"))
        
        # 组合地址
        address = " > ".join(parts) if parts else "Unknown Address"
        return address


def get_card_manager() -> CardManager:
    """获取卡片管理器单例"""
    return CardManager()
