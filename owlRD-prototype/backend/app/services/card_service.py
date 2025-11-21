"""
卡片自动生成服务
实现卡片创建规则和业务逻辑
参考: db/19_card_functions.sql
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
import uuid
from datetime import datetime


class CardService:
    """卡片服务：处理卡片自动生成和维护"""
    
    def __init__(self, storage_service):
        """
        初始化卡片服务
        
        Args:
            storage_service: StorageService实例，用于数据访问
        """
        self.storage = storage_service
    
    def calculate_activebed_address(
        self,
        location_tag: Optional[str],
        location_name: str,
        bed_name: str
    ) -> str:
        """
        计算ActiveBed卡片地址
        
        格式：
        - 有location_tag: "location_tag-location_name-bed_name"
        - 无location_tag: "location_name-bed_name"
        """
        if location_tag:
            return f"{location_tag}-{location_name}-{bed_name}"
        return f"{location_name}-{bed_name}"
    
    def calculate_location_address(
        self,
        location_tag: Optional[str],
        location_name: str
    ) -> str:
        """
        计算Location卡片地址
        
        格式：
        - 有location_tag: "location_tag-location_name"
        - 无location_tag: "location_name"
        """
        if location_tag:
            return f"{location_tag}-{location_name}"
        return location_name
    
    def is_activebed(self, bed_id: str, beds_data: List[Dict], devices_data: List[Dict]) -> bool:
        """
        判断床位是否为ActiveBed
        
        ActiveBed条件：
        1. 有住户（resident_id不为空）
        2. 有激活监护的监控设备（bound_device_count > 0）
        
        Args:
            bed_id: 床位ID
            beds_data: 床位数据列表
            devices_data: 设备数据列表
        
        Returns:
            是否为ActiveBed
        """
        # 查找床位
        bed = next((b for b in beds_data if b.get("bed_id") == bed_id), None)
        if not bed or not bed.get("resident_id"):
            return False
        
        # 统计绑定到该床位的激活设备数量
        bound_device_count = sum(
            1 for d in devices_data
            if d.get("bound_bed_id") == bed_id
            and d.get("monitoring_enabled") is True
            and d.get("installed") is True
        )
        
        return bound_device_count > 0
    
    def regenerate_cards_for_location(
        self,
        location_id: str,
        locations_data: List[Dict],
        beds_data: List[Dict],
        residents_data: List[Dict],
        devices_data: List[Dict],
        cards_storage: Any,
        card_devices_storage: Any,
        card_residents_storage: Any
    ) -> Dict[str, Any]:
        """
        为指定location重新生成所有卡片
        
        实现卡片创建规则的核心逻辑
        
        Args:
            location_id: 位置ID
            locations_data: 位置数据列表
            beds_data: 床位数据列表
            residents_data: 住户数据列表
            devices_data: 设备数据列表
            cards_storage: 卡片存储服务
            card_devices_storage: 卡片设备关联存储服务
            card_residents_storage: 卡片住户关联存储服务
        
        Returns:
            生成结果统计
        """
        # 查找location
        location = next((l for l in locations_data if l.get("location_id") == location_id), None)
        if not location:
            raise ValueError(f"Location not found: {location_id}")
        
        tenant_id = location.get("tenant_id")
        location_tag = location.get("location_tag")
        location_name = location.get("location_name")
        location_type = location.get("location_type")
        is_public_space = location.get("is_public_space", False)
        is_multi_person_room = location.get("is_multi_person_room", False)
        primary_resident_id = location.get("primary_resident_id")
        
        # 删除该location下的所有旧卡片
        location_beds = [b.get("bed_id") for b in beds_data if b.get("location_id") == location_id]
        old_cards = [
            c for c in cards_storage.find_all(lambda x: True)
            if c.get("location_id") == location_id or c.get("bed_id") in location_beds
        ]
        for card in old_cards:
            cards_storage.delete("card_id", card["card_id"])
        
        # 统计ActiveBed数量
        activebeds = [
            b for b in beds_data
            if b.get("location_id") == location_id
            and self.is_activebed(b.get("bed_id"), beds_data, devices_data)
        ]
        activebed_count = len(activebeds)
        
        result = {
            "location_id": location_id,
            "activebed_count": activebed_count,
            "cards_created": []
        }
        
        # 场景A: 只有1个ActiveBed
        if activebed_count == 1:
            result["scenario"] = "A - Single ActiveBed"
            bed = activebeds[0]
            resident = next((r for r in residents_data if r.get("resident_id") == bed.get("resident_id")), None)
            
            if resident:
                card_name = resident.get("last_name", "未知")
                card_address = self.calculate_activebed_address(location_tag, location_name, bed.get("bed_name"))
                
                # 创建ActiveBed卡片
                card_id = str(uuid.uuid4())
                card = {
                    "card_id": card_id,
                    "tenant_id": tenant_id,
                    "card_type": "ActiveBed",
                    "bed_id": bed.get("bed_id"),
                    "location_id": location_id,
                    "card_name": card_name,
                    "card_address": card_address,
                    "resident_id": bed.get("resident_id"),
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                cards_storage.create(card)
                result["cards_created"].append({"type": "ActiveBed", "name": card_name})
        
        # 场景B: 多个ActiveBed (>=2)
        elif activebed_count >= 2:
            result["scenario"] = "B - Multiple ActiveBeds"
            
            # 为每个ActiveBed创建卡片
            for bed in activebeds:
                resident = next((r for r in residents_data if r.get("resident_id") == bed.get("resident_id")), None)
                if resident:
                    card_name = resident.get("last_name", "未知")
                    card_address = self.calculate_activebed_address(location_tag, location_name, bed.get("bed_name"))
                    
                    card_id = str(uuid.uuid4())
                    card = {
                        "card_id": card_id,
                        "tenant_id": tenant_id,
                        "card_type": "ActiveBed",
                        "bed_id": bed.get("bed_id"),
                        "location_id": location_id,
                        "card_name": card_name,
                        "card_address": card_address,
                        "resident_id": bed.get("resident_id"),
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    cards_storage.create(card)
                    result["cards_created"].append({"type": "ActiveBed", "name": card_name})
            
            # 检查是否有未绑床的设备，创建Location卡片
            unbound_devices = [
                d for d in devices_data
                if d.get("location_id") == location_id
                and d.get("bound_bed_id") is None
                and d.get("monitoring_enabled") is True
                and d.get("installed") is True
            ]
            
            if unbound_devices:
                card_name = self._calculate_location_card_name(
                    location_name, location_type, is_public_space,
                    is_multi_person_room, primary_resident_id, residents_data
                )
                card_address = self.calculate_location_address(location_tag, location_name)
                
                card_id = str(uuid.uuid4())
                card = {
                    "card_id": card_id,
                    "tenant_id": tenant_id,
                    "card_type": "Location",
                    "location_id": location_id,
                    "card_name": card_name,
                    "card_address": card_address,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                cards_storage.create(card)
                result["cards_created"].append({"type": "Location", "name": card_name})
        
        # 场景C: 无ActiveBed
        else:
            result["scenario"] = "C - No ActiveBed"
            
            # 检查是否有未绑床的设备
            unbound_devices = [
                d for d in devices_data
                if d.get("location_id") == location_id
                and d.get("bound_bed_id") is None
                and d.get("monitoring_enabled") is True
                and d.get("installed") is True
            ]
            
            if unbound_devices:
                card_name = self._calculate_location_card_name(
                    location_name, location_type, is_public_space,
                    is_multi_person_room, primary_resident_id, residents_data
                )
                card_address = self.calculate_location_address(location_tag, location_name)
                
                card_id = str(uuid.uuid4())
                card = {
                    "card_id": card_id,
                    "tenant_id": tenant_id,
                    "card_type": "Location",
                    "location_id": location_id,
                    "card_name": card_name,
                    "card_address": card_address,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                cards_storage.create(card)
                result["cards_created"].append({"type": "Location", "name": card_name})
        
        return result
    
    def _calculate_location_card_name(
        self,
        location_name: str,
        location_type: str,
        is_public_space: bool,
        is_multi_person_room: bool,
        primary_resident_id: Optional[str],
        residents_data: List[Dict]
    ) -> str:
        """
        计算Location卡片名称（按优先级）
        
        优先级：
        1. Institutional公共空间 -> location_name
        2. Institutional多人房间 -> location_name
        3. HomeCare场景 -> primary_resident的LastName
        4. Institutional单人房间/夫妻套房 -> primary_resident的LastName
        """
        # 优先级1: 公共空间
        if is_public_space:
            return location_name
        
        # 优先级2: 多人房间
        if is_multi_person_room:
            return location_name
        
        # 优先级3&4: 使用primary_resident的LastName
        if primary_resident_id:
            resident = next(
                (r for r in residents_data if r.get("resident_id") == primary_resident_id),
                None
            )
            if resident:
                return resident.get("last_name", location_name)
        
        # 后备: location_name
        return location_name
