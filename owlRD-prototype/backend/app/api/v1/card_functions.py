"""
卡片函数API端点
提供卡片自动生成和维护功能
"""

from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Query

from app.services.card_service import CardService
from app.services.storage import StorageService

router = APIRouter()

# 初始化存储服务
cards_storage = StorageService("cards")
locations_storage = StorageService("locations")
beds_storage = StorageService("beds")
residents_storage = StorageService("residents")
devices_storage = StorageService("devices")
card_devices_storage = StorageService("card_devices")
card_residents_storage = StorageService("card_residents")

# 初始化卡片服务
card_service = CardService(cards_storage)


@router.post("/regenerate/{location_id}")
async def regenerate_cards_for_location(
    location_id: UUID,
    tenant_id: UUID = Query(..., description="租户ID")
):
    """
    为指定location重新生成所有卡片
    
    **使用场景**：
    - 住户入住/出院时
    - 设备安装/移除时
    - 设备监护状态变化时
    - 地址信息变化时
    
    **卡片创建规则**：
    - 场景A: 1个ActiveBed -> 创建1个ActiveBed卡片
    - 场景B: 多个ActiveBed -> 为每个创建ActiveBed卡片 + 可能的Location卡片
    - 场景C: 无ActiveBed -> 可能创建Location卡片
    
    **ActiveBed定义**：
    - 有住户
    - 有激活监护的监控设备
    """
    try:
        # 加载所有必要数据
        locations_data = locations_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        beds_data = beds_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        residents_data = residents_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        devices_data = devices_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        
        # 调用服务生成卡片
        result = card_service.regenerate_cards_for_location(
            str(location_id),
            locations_data,
            beds_data,
            residents_data,
            devices_data,
            cards_storage,
            card_devices_storage,
            card_residents_storage
        )
        
        return {
            "success": True,
            "message": "Cards regenerated successfully",
            "result": result
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate cards: {str(e)}")


@router.post("/regenerate-all")
async def regenerate_all_cards(
    tenant_id: UUID = Query(..., description="租户ID")
):
    """
    为所有location重新生成所有卡片
    
    **使用场景**：
    - 初始化系统
    - 批量更新卡片
    - 修复数据不一致
    
    **警告**：此操作会删除所有现有卡片并重新生成
    """
    try:
        # 加载所有必要数据
        locations_data = locations_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        beds_data = beds_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        residents_data = residents_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        devices_data = devices_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        
        results = []
        
        # 为每个激活的location生成卡片
        for location in locations_data:
            if location.get("is_active", True):
                try:
                    result = card_service.regenerate_cards_for_location(
                        location.get("location_id"),
                        locations_data,
                        beds_data,
                        residents_data,
                        devices_data,
                        cards_storage,
                        card_devices_storage,
                        card_residents_storage
                    )
                    results.append(result)
                except Exception as e:
                    results.append({
                        "location_id": location.get("location_id"),
                        "error": str(e)
                    })
        
        total_cards = sum(len(r.get("cards_created", [])) for r in results if "error" not in r)
        
        return {
            "success": True,
            "message": "All cards regenerated successfully",
            "total_locations": len(results),
            "total_cards_created": total_cards,
            "results": results
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to regenerate all cards: {str(e)}")


@router.get("/preview/{location_id}")
async def preview_cards_for_location(
    location_id: UUID,
    tenant_id: UUID = Query(..., description="租户ID")
):
    """
    预览指定location将生成的卡片（不实际创建）
    
    **用途**：在实际生成前检查卡片创建规则的执行结果
    """
    try:
        # 加载数据
        locations_data = locations_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        beds_data = beds_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        residents_data = residents_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        devices_data = devices_storage.find_all(lambda x: str(x.get("tenant_id")) == str(tenant_id))
        
        # 查找location
        location = next((l for l in locations_data if l.get("location_id") == str(location_id)), None)
        if not location:
            raise HTTPException(status_code=404, detail="Location not found")
        
        # 统计ActiveBed
        activebeds = [
            b for b in beds_data
            if b.get("location_id") == str(location_id)
            and card_service.is_activebed(b.get("bed_id"), beds_data, devices_data)
        ]
        
        # 统计未绑床设备
        unbound_devices = [
            d for d in devices_data
            if d.get("location_id") == str(location_id)
            and d.get("bound_bed_id") is None
            and d.get("monitoring_enabled") is True
            and d.get("installed") is True
        ]
        
        # 确定场景
        activebed_count = len(activebeds)
        if activebed_count == 1:
            scenario = "A - Single ActiveBed"
        elif activebed_count >= 2:
            scenario = "B - Multiple ActiveBeds"
        else:
            scenario = "C - No ActiveBed"
        
        return {
            "location_id": str(location_id),
            "location_name": location.get("location_name"),
            "scenario": scenario,
            "activebed_count": activebed_count,
            "activebeds": [
                {
                    "bed_id": b.get("bed_id"),
                    "bed_name": b.get("bed_name"),
                    "resident_id": b.get("resident_id")
                }
                for b in activebeds
            ],
            "unbound_devices_count": len(unbound_devices),
            "estimated_cards": {
                "activebed_cards": activebed_count,
                "location_cards": 1 if (activebed_count >= 2 or activebed_count == 0) and unbound_devices else 0
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preview cards: {str(e)}")
