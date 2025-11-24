"""
卡片管理API
用于管理ActiveBed和Location卡片
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from loguru import logger

from app.models.card import Card, CardCreate, CardType
from app.services.card_manager import get_card_manager
from app.services.storage import StorageService
from app.services.permission_service import get_permission_service
from app.dependencies.auth import get_current_user_from_token

router = APIRouter()
card_manager = get_card_manager()
card_storage = StorageService[Card]("cards")


@router.get("/", response_model=List[dict], summary="获取卡片列表")
async def list_cards(
    tenant_id: UUID = Query(..., description="租户ID"),
    card_type: Optional[str] = Query(None, description="卡片类型(ActiveBed/Location)"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    is_public_space: Optional[bool] = Query(None, description="是否公共空间"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制"),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    获取卡片列表（带权限过滤）
    
    ## 功能
    - 按租户查询卡片
    - 支持类型、状态、空间类型筛选
    - 分页限制
    - **自动根据用户权限过滤卡片**
    
    ## 权限规则
    - **Admin角色**: 可查看租户下所有卡片
    - **alert_scope=ALL**: 可查看租户下所有卡片
    - **alert_scope=LOCATION**: 只能查看匹配location_tag的卡片
    - **alert_scope=ASSIGNED_ONLY**: 只能查看分配给自己的住户卡片
    
    ## 参数
    - **tenant_id**: 租户ID（必需）
    - **card_type**: 卡片类型筛选（ActiveBed/Location）
    - **is_active**: 是否激活
    - **is_public_space**: 是否公共空间
    - **limit**: 返回数量（1-1000）
    
    ## 返回
    - 用户有权查看的卡片列表
    """
    try:
        # 验证用户租户权限
        if str(current_user.get("tenant_id")) != str(tenant_id):
            raise HTTPException(
                status_code=403,
                detail="无权访问其他租户的数据"
            )
        
        # 使用权限服务获取用户可见的卡片
        permission_service = get_permission_service()
        user_id = current_user.get("user_id")
        cards = permission_service.get_user_cards(user_id, tenant_id)
        
        # 应用额外过滤条件
        if card_type:
            cards = [c for c in cards if c.get("card_type") == card_type]
        if is_active is not None:
            cards = [c for c in cards if c.get("is_active") == is_active]
        if is_public_space is not None:
            cards = [c for c in cards if c.get("is_public_space") == is_public_space]
        
        # 限制返回数量
        cards = cards[:limit]
        
        logger.info(f"User {user_id} accessed {len(cards)} cards (role: {current_user.get('role')}, alert_scope: {current_user.get('alert_scope')})")
        return cards
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{card_id}", response_model=dict, summary="获取单个卡片详情")
async def get_card(
    card_id: UUID,
    tenant_id: UUID = Query(..., description="租户ID"),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    获取单个卡片的详细信息（带权限检查）
    
    ## 参数
    - **card_id**: 卡片ID
    - **tenant_id**: 租户ID
    
    ## 权限
    - 只能查看自己有权限的卡片
    
    ## 返回
    - 卡片详细信息
    """
    try:
        # 验证用户租户权限
        if str(current_user.get("tenant_id")) != str(tenant_id):
            raise HTTPException(
                status_code=403,
                detail="无权访问其他租户的数据"
            )
        
        cards = card_storage.find_all(
            lambda c: str(c.get("card_id")) == str(card_id) and str(c.get("tenant_id")) == str(tenant_id)
        )
        
        if not cards:
            raise HTTPException(status_code=404, detail="Card not found")
        
        card = cards[0]
        
        # 权限检查
        permission_service = get_permission_service()
        user_id = current_user.get("user_id")
        if not permission_service.can_view_card(user_id, card):
            raise HTTPException(
                status_code=403,
                detail="无权查看此卡片"
            )
        
        return card
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting card: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{card_id}/aggregated", response_model=dict, summary="获取卡片聚合数据")
async def get_card_aggregated(
    card_id: UUID,
    tenant_id: UUID = Query(..., description="租户ID"),
    hours: int = Query(24, ge=1, le=168, description="数据时间范围（小时）")
):
    """
    获取卡片聚合数据
    
    ## 功能
    - 卡片基础信息
    - 关联住户信息（如有）
    - 最新IoT数据
    - 近期告警列表
    - 数据统计
    
    ## 参数
    - **card_id**: 卡片ID
    - **tenant_id**: 租户ID
    - **hours**: 数据时间范围（1-168小时）
    
    ## 返回
    - 聚合后的完整卡片数据
    """
    try:
        aggregated = await card_manager.get_card_aggregated_data(
            card_id=card_id,
            tenant_id=tenant_id,
            hours=hours
        )
        
        if not aggregated:
            raise HTTPException(status_code=404, detail="Card not found")
        
        return aggregated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting aggregated card data: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=dict, summary="创建卡片")
async def create_card(card: CardCreate):
    """
    创建新卡片
    
    ## 功能
    - 创建ActiveBed卡片
    - 创建Location卡片
    
    ## 参数
    - **card**: 卡片创建数据
    
    ## 返回
    - 创建的卡片
    """
    try:
        if card.card_type == CardType.ACTIVE_BED:
            if not card.bed_id:
                raise HTTPException(status_code=400, detail="bed_id required for ActiveBed card")
            
            result = card_manager.create_activebed_card(
                bed_id=card.bed_id,
                tenant_id=card.tenant_id
            )
        elif card.card_type == CardType.LOCATION:
            if not card.location_id:
                raise HTTPException(status_code=400, detail="location_id required for Location card")
            
            result = card_manager.create_location_card(
                location_id=card.location_id,
                tenant_id=card.tenant_id
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid card_type")
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create card")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating card: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-create", response_model=dict, summary="批量创建卡片")
async def batch_create_cards(
    tenant_id: UUID = Query(..., description="租户ID"),
    create_for_beds: bool = Query(True, description="是否为床位创建卡片"),
    create_for_locations: bool = Query(True, description="是否为位置创建卡片")
):
    """
    批量创建卡片
    
    ## 功能
    - 为租户下所有床位创建ActiveBed卡片
    - 为租户下所有位置创建Location卡片
    - 自动跳过已存在的卡片
    
    ## 参数
    - **tenant_id**: 租户ID
    - **create_for_beds**: 是否为床位创建
    - **create_for_locations**: 是否为位置创建
    
    ## 返回
    - 创建统计信息
    """
    try:
        result = await card_manager.batch_create_cards(
            tenant_id=tenant_id,
            create_for_beds=create_for_beds,
            create_for_locations=create_for_locations
        )
        return result
    except Exception as e:
        logger.error(f"Error batch creating cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{card_id}/status", response_model=dict, summary="更新卡片状态")
async def update_card_status(
    card_id: UUID,
    tenant_id: UUID = Query(..., description="租户ID"),
    is_active: bool = Query(..., description="是否激活")
):
    """
    更新卡片激活状态
    
    ## 参数
    - **card_id**: 卡片ID
    - **tenant_id**: 租户ID
    - **is_active**: 是否激活
    
    ## 返回
    - 更新结果
    """
    try:
        success = await card_manager.update_card_status(
            card_id=card_id,
            tenant_id=tenant_id,
            is_active=is_active
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="Card not found or update failed")
        
        return {"status": "success", "card_id": str(card_id), "is_active": is_active}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating card status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{card_id}", response_model=dict, summary="删除卡片")
async def delete_card(
    card_id: UUID,
    tenant_id: UUID = Query(..., description="租户ID")
):
    """
    删除卡片
    
    ## 参数
    - **card_id**: 卡片ID
    - **tenant_id**: 租户ID
    
    ## 返回
    - 删除结果
    """
    try:
        # 查找卡片
        cards = card_storage.find_all(
            lambda c: str(c.get("card_id")) == str(card_id) and str(c.get("tenant_id")) == str(tenant_id)
        )
        
        if not cards:
            raise HTTPException(status_code=404, detail="Card not found")
        
        # 删除卡片
        card = cards[0]
        card_storage.delete(UUID(card["id"]))
        
        logger.info(f"Deleted card: {card_id}")
        return {"status": "success", "card_id": str(card_id)}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting card: {e}")
        raise HTTPException(status_code=500, detail=str(e))
