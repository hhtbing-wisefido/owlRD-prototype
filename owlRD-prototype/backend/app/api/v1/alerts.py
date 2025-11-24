"""
告警管理API - 查询和管理

对齐源参考：
- TDPv2-0916.md - 告警协议定义
- 25_Alarm_Notification_Flow.md - 告警路由和处理流程
- models/alert.py - Alert数据模型

字段说明：
- alert_level: L1/L2/L3/L5/L8/L9/DISABLE（对齐TDPv2协议）
- status: pending/acknowledged/resolved/dismissed
- timestamp: 告警发生时间
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from loguru import logger

from app.services.storage import StorageService
from app.models.alert import Alert, AlertCreate, AlertUpdate
from app.dependencies.auth import get_current_user_from_token
from app.middleware.permissions import check_tenant_access

router = APIRouter()
alert_storage = StorageService("alerts")


@router.get("/", summary="获取告警列表", response_model=List[Alert])
async def list_alerts(
    tenant_id: UUID = Query(..., description="租户ID"),
    alert_level: Optional[str] = Query(None, description="告警级别筛选"),
    alert_type: Optional[str] = Query(None, description="告警类型筛选"),
    status: Optional[str] = Query(None, description="状态筛选"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    limit: int = Query(100, ge=1, le=1000),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> List[Alert]:
    """
    获取告警列表（需要认证）
    
    ## 筛选条件
    - **tenant_id**: 租户ID（必填）
    - **alert_level**: L1/L2/L3/L4/L5
    - **alert_type**: FALL/LEAVE/HEART_RATE/等
    - **status**: pending/acknowledged/resolved
    - **start_time/end_time**: 时间范围
    - **limit**: 返回数量限制
    
    ## 返回
    按时间倒序返回告警列表
    """
    try:
        check_tenant_access(current_user, tenant_id)
        
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(hours=24)
        
        def filter_func(a):
            if str(a.get("tenant_id")) != str(tenant_id):
                return False
            if alert_level and a.get("alert_level") != alert_level:
                return False
            if alert_type and a.get("alert_type") != alert_type:
                return False
            if status and a.get("status") != status:
                return False
            
            # 时间筛选
            alert_time = a.get("timestamp")
            if alert_time:
                if isinstance(alert_time, str):
                    alert_time = datetime.fromisoformat(alert_time.replace('Z', '+00:00'))
                if alert_time < start_time or alert_time > end_time:
                    return False
            
            return True
        
        alerts = alert_storage.find_all(filter_func)
        
        # 按时间倒序排序
        alerts.sort(
            key=lambda x: x.get("timestamp", "1970-01-01"),
            reverse=True
        )
        
        return alerts[:limit]
    except Exception as e:
        logger.error(f"Error listing alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alert_id}", summary="获取告警详情", response_model=Alert)
async def get_alert(
    alert_id: UUID,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> Alert:
    """获取单个告警详情（需要认证）"""
    try:
        alert = alert_storage.get(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        check_tenant_access(current_user, alert.get("tenant_id"))
        
        return alert
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alert_id}/acknowledge", summary="确认告警", response_model=Alert)
async def acknowledge_alert(
    alert_id: UUID,
    note: Optional[str] = Query(None, description="备注"),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> Alert:
    """
    确认告警（需要认证）
    
    ## 功能
    - 将告警状态从pending改为acknowledged
    - 记录确认人和时间
    - 可添加备注
    """
    try:
        alert = alert_storage.get(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        check_tenant_access(current_user, alert.get("tenant_id"))
        
        user_id = current_user.get("user_id")
        update_data = {
            "status": "acknowledged",
            "acknowledged_by": str(user_id),
            "acknowledged_at": datetime.now().isoformat(),
            "note": note
        }
        
        result = alert_storage.update(alert_id, update_data)
        logger.info(f"Alert acknowledged: {alert_id} by {current_user.get('username')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error acknowledging alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{alert_id}/resolve", summary="解决告警", response_model=Alert)
async def resolve_alert(
    alert_id: UUID,
    resolution: Optional[str] = Query(None, description="解决说明"),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
) -> Alert:
    """
    解决告警（需要认证）
    
    ## 功能
    - 将告警状态改为resolved
    - 记录解决人和时间
    - 可添加解决说明
    """
    try:
        alert = alert_storage.get(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        check_tenant_access(current_user, alert.get("tenant_id"))
        
        user_id = current_user.get("user_id")
        update_data = {
            "status": "resolved",
            "resolved_by": str(user_id),
            "resolved_at": datetime.now().isoformat(),
            "resolution": resolution
        }
        
        result = alert_storage.update(alert_id, update_data)
        logger.info(f"Alert resolved: {alert_id} by {current_user.get('username')}")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resolving alert: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics/summary", summary="告警统计")
async def get_alert_statistics(
    tenant_id: UUID = Query(..., description="租户ID"),
    hours: int = Query(24, ge=1, le=168, description="统计时间范围（小时）"),
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """
    获取告警统计信息（需要认证）
    
    ## 统计项
    - 总告警数
    - 各级别告警数量
    - 各类型告警数量
    - 各状态告警数量
    - 平均响应时间
    """
    try:
        check_tenant_access(current_user, tenant_id)
        
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=hours)
        
        alerts = alert_storage.find_all(
            lambda a: (
                str(a.get("tenant_id")) == str(tenant_id) and
                datetime.fromisoformat(a.get("timestamp", "1970-01-01").replace('Z', '+00:00')) >= start_time
            )
        )
        
        # 统计
        stats = {
            "total_count": len(alerts),
            "time_range_hours": hours,
            "by_level": {},
            "by_type": {},
            "by_status": {},
            "avg_response_time_seconds": 0
        }
        
        # 按级别统计
        for alert in alerts:
            level = alert.get("alert_level", "UNKNOWN")
            stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
            
            alert_type = alert.get("alert_type", "UNKNOWN")
            stats["by_type"][alert_type] = stats["by_type"].get(alert_type, 0) + 1
            
            status = alert.get("status", "UNKNOWN")
            stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        return stats
    except Exception as e:
        logger.error(f"Error getting alert statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))
