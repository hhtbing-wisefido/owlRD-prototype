"""
权限服务
实现基于角色和alert_scope的动态权限计算
参考: 源参考文件/docs/24_Card_Permission_Design.md
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from loguru import logger

from app.services.storage import StorageService


class PermissionService:
    """权限服务 - 动态计算用户权限"""
    
    def __init__(self):
        self.user_storage = StorageService("users")
        self.resident_storage = StorageService("residents")
        self.location_storage = StorageService("locations")
        self.caregiver_storage = StorageService("resident_caregivers")
        self.contact_storage = StorageService("resident_contacts")
    
    # ============================================================================
    # 核心权限检查方法
    # ============================================================================
    
    def can_view_card(self, user_id: UUID, card: Dict[str, Any]) -> bool:
        """
        检查用户是否有权限查看某个卡片
        
        参数:
            user_id: 用户ID
            card: 卡片数据
            
        返回:
            bool: 是否有权限
        """
        user = self._get_user(user_id)
        if not user:
            return False
        
        # Admin角色：可以查看租户下所有卡片
        if user.get("role") == "Admin":
            return str(card.get("tenant_id")) == str(user.get("tenant_id"))
        
        alert_scope = user.get("alert_scope", "ASSIGNED_ONLY")
        
        # ALL权限：可以查看租户下所有卡片
        if alert_scope == "ALL":
            return str(card.get("tenant_id")) == str(user.get("tenant_id"))
        
        # LOCATION权限：检查location_tag匹配
        if alert_scope == "LOCATION":
            return self._check_location_permission(user, card)
        
        # ASSIGNED_ONLY权限：只能查看分配给自己的住户卡片
        if alert_scope == "ASSIGNED_ONLY":
            return self._check_assigned_permission(user_id, card)
        
        return False
    
    def get_user_cards(self, user_id: UUID, tenant_id: UUID) -> List[Dict[str, Any]]:
        """
        获取用户可见的卡片列表
        
        参数:
            user_id: 用户ID
            tenant_id: 租户ID
            
        返回:
            List[Dict]: 用户可见的卡片列表
        """
        user = self._get_user(user_id)
        if not user:
            return []
        
        # 获取所有卡片（同租户）
        card_storage = StorageService("cards")
        all_cards = card_storage.find_all(
            lambda c: str(c.get("tenant_id")) == str(tenant_id)
        )
        
        # Admin角色：返回所有卡片
        if user.get("role") == "Admin":
            return all_cards
        
        alert_scope = user.get("alert_scope", "ASSIGNED_ONLY")
        
        # ALL权限：返回所有卡片
        if alert_scope == "ALL":
            return all_cards
        
        # LOCATION权限：按location_tag过滤
        if alert_scope == "LOCATION":
            return self._filter_cards_by_location(user, all_cards)
        
        # ASSIGNED_ONLY权限：只返回分配的住户卡片
        if alert_scope == "ASSIGNED_ONLY":
            return self._filter_cards_by_assignment(user_id, all_cards)
        
        return []
    
    def get_resident_cards(self, resident_id: UUID, tenant_id: UUID) -> List[Dict[str, Any]]:
        """
        获取住户可见的卡片列表
        
        权限规则:
        - ActiveBed卡片: 住户自己的床位卡片
        - Location卡片: 住户所在的门牌号卡片（单人或夫妻同住）
        
        参数:
            resident_id: 住户ID
            tenant_id: 租户ID
            
        返回:
            List[Dict]: 住户可见的卡片列表
        """
        resident = self._get_resident(resident_id)
        if not resident:
            return []
        
        card_storage = StorageService("cards")
        visible_cards = []
        
        # 1. ActiveBed卡片：自己的床位
        if resident.get("bed_id"):
            activebed_cards = card_storage.find_all(
                lambda c: (
                    str(c.get("tenant_id")) == str(tenant_id) and
                    c.get("card_type") == "ActiveBed" and
                    str(c.get("bed_id")) == str(resident.get("bed_id")) and
                    str(c.get("resident_id")) == str(resident_id)
                )
            )
            visible_cards.extend(activebed_cards)
        
        # 2. Location卡片：自己所在的位置（需检查是否单人或夫妻同住）
        if resident.get("location_id"):
            location_cards = self._get_resident_location_cards(resident_id, resident, tenant_id)
            visible_cards.extend(location_cards)
        
        return visible_cards
    
    def get_family_cards(self, contact_id: UUID, tenant_id: UUID) -> List[Dict[str, Any]]:
        """
        获取家属可见的卡片列表
        
        权限规则:
        - 家属权限与住户权限相同
        - 通过resident_contacts表关联住户
        - 需要满足: can_view_status=TRUE 且 is_active=TRUE
        - 一个家属可以关联多个住户
        
        参数:
            contact_id: 家属联系人ID
            tenant_id: 租户ID
            
        返回:
            List[Dict]: 家属可见的卡片列表
        """
        # 获取家属关联的所有住户
        contact_links = self.contact_storage.find_all(
            lambda c: (
                str(c.get("contact_id")) == str(contact_id) and
                c.get("can_view_status") is True and
                c.get("is_active") is True
            )
        )
        
        if not contact_links:
            return []
        
        # 收集所有关联住户的卡片
        all_visible_cards = []
        for link in contact_links:
            resident_id = link.get("resident_id")
            if resident_id:
                resident_cards = self.get_resident_cards(resident_id, tenant_id)
                all_visible_cards.extend(resident_cards)
        
        # 去重（同一个卡片可能被多个住户看到）
        unique_cards = {card["card_id"]: card for card in all_visible_cards}
        return list(unique_cards.values())
    
    # ============================================================================
    # 辅助方法 - 私有
    # ============================================================================
    
    def _get_user(self, user_id: UUID) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        users = self.user_storage.find_all(
            lambda u: str(u.get("user_id")) == str(user_id)
        )
        return users[0] if users else None
    
    def _get_resident(self, resident_id: UUID) -> Optional[Dict[str, Any]]:
        """获取住户信息"""
        residents = self.resident_storage.find_all(
            lambda r: str(r.get("resident_id")) == str(resident_id)
        )
        return residents[0] if residents else None
    
    def _check_location_permission(self, user: Dict[str, Any], card: Dict[str, Any]) -> bool:
        """
        检查LOCATION权限
        
        规则:
        - 匹配 locations.location_tag 和 users.tags
        - location_tag在用户的tags中
        """
        card_location_id = card.get("location_id")
        if not card_location_id:
            return False
        
        # 获取位置信息
        locations = self.location_storage.find_all(
            lambda l: str(l.get("location_id")) == str(card_location_id)
        )
        if not locations:
            return False
        
        location = locations[0]
        location_tag = location.get("location_tag")
        
        if not location_tag:
            return False
        
        # 检查用户tags是否包含location_tag
        user_tags = user.get("tags", {})
        if isinstance(user_tags, dict):
            # tags可能是字典，检查值
            return location_tag in user_tags.values()
        elif isinstance(user_tags, list):
            # tags可能是列表
            return location_tag in user_tags
        
        return False
    
    def _check_assigned_permission(self, user_id: UUID, card: Dict[str, Any]) -> bool:
        """
        检查ASSIGNED_ONLY权限
        
        规则:
        - ActiveBed卡片: 住户分配给该用户
        - Location卡片: 有住户分配给该用户
        """
        # 获取用户负责的所有住户
        assignments = self.caregiver_storage.find_all(
            lambda c: str(c.get("caregiver_id")) == str(user_id) and c.get("is_active") is True
        )
        assigned_resident_ids = [a.get("resident_id") for a in assignments]
        
        card_type = card.get("card_type")
        
        # ActiveBed卡片：检查resident_id
        if card_type == "ActiveBed":
            card_resident_id = card.get("resident_id")
            return str(card_resident_id) in [str(r) for r in assigned_resident_ids]
        
        # Location卡片：检查是否有分配的住户在该位置
        if card_type == "Location":
            card_location_id = card.get("location_id")
            # 查找在该位置的住户
            residents_at_location = self.resident_storage.find_all(
                lambda r: str(r.get("location_id")) == str(card_location_id)
            )
            location_resident_ids = [r.get("resident_id") for r in residents_at_location]
            
            # 检查是否有交集
            return any(
                str(rid) in [str(r) for r in assigned_resident_ids]
                for rid in location_resident_ids
            )
        
        return False
    
    def _filter_cards_by_location(self, user: Dict[str, Any], cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按LOCATION权限过滤卡片"""
        filtered = []
        for card in cards:
            if self._check_location_permission(user, card):
                filtered.append(card)
        return filtered
    
    def _filter_cards_by_assignment(self, user_id: UUID, cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """按ASSIGNED_ONLY权限过滤卡片"""
        filtered = []
        for card in cards:
            if self._check_assigned_permission(user_id, card):
                filtered.append(card)
        return filtered
    
    def _get_resident_location_cards(
        self, 
        resident_id: UUID, 
        resident: Dict[str, Any], 
        tenant_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        获取住户的Location卡片
        
        规则:
        - 情况1(单人居住): 该location_id下住户唯一且为该住户
        - 情况2(夫妻同住): 该location_id下的所有住户都使用相同的family_tag
        """
        location_id = resident.get("location_id")
        if not location_id:
            return []
        
        # 查找该位置的所有住户
        residents_at_location = self.resident_storage.find_all(
            lambda r: str(r.get("location_id")) == str(location_id)
        )
        
        # 情况1: 单人居住
        if len(residents_at_location) == 1:
            card_storage = StorageService("cards")
            return card_storage.find_all(
                lambda c: (
                    str(c.get("tenant_id")) == str(tenant_id) and
                    c.get("card_type") == "Location" and
                    str(c.get("location_id")) == str(location_id)
                )
            )
        
        # 情况2: 夫妻同住（检查family_tag）
        resident_family_tag = resident.get("family_tag")
        if resident_family_tag:
            # 检查是否所有住户都有相同的family_tag
            all_same_family = all(
                r.get("family_tag") == resident_family_tag
                for r in residents_at_location
            )
            
            if all_same_family:
                card_storage = StorageService("cards")
                return card_storage.find_all(
                    lambda c: (
                        str(c.get("tenant_id")) == str(tenant_id) and
                        c.get("card_type") == "Location" and
                        str(c.get("location_id")) == str(location_id)
                    )
                )
        
        # 不符合单人或夫妻同住条件，不返回Location卡片
        return []


# 全局权限服务实例
_permission_service: Optional[PermissionService] = None


def get_permission_service() -> PermissionService:
    """获取权限服务单例"""
    global _permission_service
    if _permission_service is None:
        _permission_service = PermissionService()
    return _permission_service
