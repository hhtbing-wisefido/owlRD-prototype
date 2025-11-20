"""
卡片管理服务
自动生成和管理ActiveBed/Location卡片
"""

from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from loguru import logger

from app.models.card import Card, CardType, CardCreate
from app.models.iot_data import IOTTimeseries
from app.services.storage import StorageService


class CardManager:
    """卡片管理器"""
    
    def __init__(self):
        """初始化卡片管理器"""
        self.card_storage = StorageService[Card]("cards")
        self.bed_storage = StorageService("beds")
        self.room_storage = StorageService("rooms")
        self.location_storage = StorageService("locations")
        self.resident_storage = StorageService("residents")
        self.device_storage = StorageService("devices")
        self.iot_storage = StorageService[IOTTimeseries]("iot_timeseries")
    
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


    async def get_card_aggregated_data(
        self,
        card_id: UUID,
        tenant_id: UUID,
        hours: int = 24
    ) -> Optional[Dict[str, Any]]:
        """
        获取卡片聚合数据（包含IoT数据、告警、住户信息等）
        
        Args:
            card_id: 卡片ID
            tenant_id: 租户ID
            hours: 数据时间范围（小时）
            
        Returns:
            聚合后的卡片数据
        """
        # 获取卡片基础信息
        card = await self.card_storage.find_all(
            lambda c: str(c.get("card_id")) == str(card_id) and str(c.get("tenant_id")) == str(tenant_id)
        )
        
        if not card:
            return None
        
        card = card[0]
        
        # 聚合数据
        aggregated = {
            "card_info": card,
            "resident_info": None,
            "latest_iot_data": None,
            "recent_alerts": [],
            "statistics": {}
        }
        
        # 获取住户信息（如果是ActiveBed卡片）
        if card.get("card_type") == CardType.ACTIVE_BED and card.get("resident_id"):
            resident = await self.resident_storage.find_all(
                lambda r: str(r.get("resident_id")) == str(card.get("resident_id"))
            )
            if resident:
                aggregated["resident_info"] = resident[0]
        
        # 获取最近的IoT数据
        start_time = datetime.now().timestamp() - (hours * 3600)
        
        # 根据卡片类型查询IoT数据
        if card.get("bed_id"):
            # ActiveBed: 查询床位相关数据
            iot_records = await self.iot_storage.find_all(
                lambda r: (
                    str(r.get("tenant_id")) == str(tenant_id) and
                    r.get("bed_id") and
                    str(r.get("bed_id")) == str(card.get("bed_id"))
                )
            )
        elif card.get("location_id"):
            # Location: 查询位置相关数据
            iot_records = await self.iot_storage.find_all(
                lambda r: (
                    str(r.get("tenant_id")) == str(tenant_id) and
                    r.get("location_id") and
                    str(r.get("location_id")) == str(card.get("location_id"))
                )
            )
        else:
            iot_records = []
        
        # 按时间排序，获取最新数据
        if iot_records:
            iot_records.sort(
                key=lambda x: x.get("timestamp", "1970-01-01"),
                reverse=True
            )
            aggregated["latest_iot_data"] = iot_records[0]
            
            # 统计告警
            recent_alerts = [r for r in iot_records[:100] if r.get("alert_triggered")]
            aggregated["recent_alerts"] = recent_alerts[:10]  # 最近10条告警
            
            # 统计数据
            aggregated["statistics"] = {
                "total_records": len(iot_records),
                "alert_count": len([r for r in iot_records if r.get("alert_triggered")]),
                "time_range_hours": hours
            }
        
        return aggregated
    
    async def update_card_status(
        self,
        card_id: UUID,
        tenant_id: UUID,
        is_active: bool
    ) -> bool:
        """
        更新卡片状态
        
        Args:
            card_id: 卡片ID
            tenant_id: 租户ID
            is_active: 是否激活
            
        Returns:
            是否更新成功
        """
        try:
            cards = await self.card_storage.find_all(
                lambda c: str(c.get("card_id")) == str(card_id) and str(c.get("tenant_id")) == str(tenant_id)
            )
            
            if not cards:
                return False
            
            card = cards[0]
            card["is_active"] = is_active
            card["updated_at"] = datetime.now().isoformat()
            
            await self.card_storage.update(UUID(card["id"]), card)
            logger.info(f"Updated card status: {card_id}, active={is_active}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating card status: {e}")
            return False
    
    async def batch_create_cards(
        self,
        tenant_id: UUID,
        create_for_beds: bool = True,
        create_for_locations: bool = True
    ) -> Dict[str, int]:
        """
        批量创建卡片
        
        Args:
            tenant_id: 租户ID
            create_for_beds: 是否为所有床位创建卡片
            create_for_locations: 是否为所有位置创建卡片
            
        Returns:
            创建统计信息
        """
        result = {
            "beds_created": 0,
            "locations_created": 0,
            "errors": 0
        }
        
        # 为床位创建卡片
        if create_for_beds:
            beds = await self.bed_storage.find_all(
                lambda b: str(b.get("tenant_id")) == str(tenant_id)
            )
            
            for bed in beds:
                try:
                    bed_id = bed.get("bed_id")
                    if bed_id:
                        # 检查是否已存在卡片
                        existing = await self.card_storage.find_all(
                            lambda c: (
                                str(c.get("tenant_id")) == str(tenant_id) and
                                c.get("bed_id") and
                                str(c.get("bed_id")) == str(bed_id)
                            )
                        )
                        
                        if not existing:
                            self.create_activebed_card(UUID(bed_id), tenant_id)
                            result["beds_created"] += 1
                except Exception as e:
                    logger.error(f"Error creating card for bed {bed.get('bed_id')}: {e}")
                    result["errors"] += 1
        
        # 为位置创建卡片
        if create_for_locations:
            locations = await self.location_storage.find_all(
                lambda l: str(l.get("tenant_id")) == str(tenant_id)
            )
            
            for location in locations:
                try:
                    location_id = location.get("location_id")
                    if location_id:
                        # 检查是否已存在卡片
                        existing = await self.card_storage.find_all(
                            lambda c: (
                                str(c.get("tenant_id")) == str(tenant_id) and
                                c.get("location_id") and
                                str(c.get("location_id")) == str(location_id) and
                                c.get("card_type") == CardType.LOCATION
                            )
                        )
                        
                        if not existing:
                            self.create_location_card(UUID(location_id), tenant_id)
                            result["locations_created"] += 1
                except Exception as e:
                    logger.error(f"Error creating card for location {location.get('location_id')}: {e}")
                    result["errors"] += 1
        
        logger.info(f"Batch card creation: {result}")
        return result
    
    async def search_cards(
        self,
        tenant_id: UUID,
        card_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        is_public_space: Optional[bool] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        搜索卡片
        
        Args:
            tenant_id: 租户ID
            card_type: 卡片类型筛选
            is_active: 是否激活筛选
            is_public_space: 是否公共空间筛选
            limit: 返回数量限制
            
        Returns:
            卡片列表
        """
        def filter_func(card: Dict[str, Any]) -> bool:
            # 租户ID必须匹配
            if str(card.get("tenant_id")) != str(tenant_id):
                return False
            
            # 卡片类型筛选
            if card_type and card.get("card_type") != card_type:
                return False
            
            # 激活状态筛选
            if is_active is not None and card.get("is_active") != is_active:
                return False
            
            # 公共空间筛选
            if is_public_space is not None and card.get("is_public_space") != is_public_space:
                return False
            
            return True
        
        cards = await self.card_storage.find_all(filter_func)
        return cards[:limit]


def get_card_manager() -> CardManager:
    """获取卡片管理器单例"""
    return CardManager()
