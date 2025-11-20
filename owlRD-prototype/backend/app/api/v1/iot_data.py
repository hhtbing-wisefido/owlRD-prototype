"""
IoT数据接收和查询API
支持TDP协议数据上报和历史数据查询
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
from datetime import datetime, timedelta
from uuid import UUID
from loguru import logger

from app.models.tdp import TDPEvent
from app.models.iot_data import IOTTimeseries, IOTTimeseriesCreate
from app.services.tdp_processor import TDPProcessor
from app.services.storage import StorageService
from app.services.alert_engine import AlertEngine

router = APIRouter()

# 初始化服务
tdp_processor = TDPProcessor()
iot_storage = StorageService[IOTTimeseries]("iot_timeseries")
alert_engine = AlertEngine()


@router.post("/tdp/upload", response_model=dict, summary="接收TDP协议数据")
async def upload_tdp_data(
    event: TDPEvent,
    background_tasks: BackgroundTasks,
):
    """
    接收IoT设备上报的TDP协议数据
    
    ## 功能
    - 解析TDP事件数据
    - 提取Person/Object Matrix
    - 生成IoT时序数据
    - 触发告警检测
    - 异步持久化存储
    
    ## 参数
    - **event**: TDP事件数据（包含完整的Person和Object矩阵）
    
    ## 返回
    - 处理状态和生成的数据记录数量
    """
    try:
        logger.info(f"Received TDP event from device: {event.device_id}")
        
        # 处理TDP事件，生成IoT时序数据
        iot_records = await tdp_processor.process_tdp_event(event)
        
        if not iot_records:
            logger.warning(f"No IoT records generated from device: {event.device_id}")
            return {
                "status": "success",
                "message": "No data to process",
                "records_created": 0
            }
        
        # 异步保存数据（不阻塞响应）
        background_tasks.add_task(
            _save_iot_records_batch,
            iot_records
        )
        
        # 检查是否有告警
        alert_count = 0
        for record in iot_records:
            if record.alert_triggered:
                alert_count += 1
                # 异步处理告警
                background_tasks.add_task(
                    _process_alert,
                    record
                )
        
        logger.success(
            f"Processed TDP event: {len(iot_records)} records, {alert_count} alerts"
        )
        
        return {
            "status": "success",
            "message": "TDP data processed successfully",
            "records_created": len(iot_records),
            "alerts_triggered": alert_count,
            "device_id": str(event.device_id),
            "timestamp": event.timestamp.iso_timestamp if event.timestamp else None
        }
        
    except Exception as e:
        logger.error(f"Error processing TDP data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process TDP data: {str(e)}"
        )


@router.post("/batch/upload", response_model=dict, summary="批量上传IoT数据")
async def upload_batch_data(
    records: List[IOTTimeseriesCreate],
    background_tasks: BackgroundTasks,
):
    """
    批量上传IoT时序数据（适用于离线数据补传）
    
    ## 功能
    - 批量接收IoT数据
    - 数据验证
    - 异步批量写入
    
    ## 参数
    - **records**: IoT时序数据列表
    
    ## 返回
    - 处理状态和接收的记录数量
    """
    try:
        if not records:
            raise HTTPException(status_code=400, detail="No records provided")
        
        if len(records) > 1000:
            raise HTTPException(
                status_code=400,
                detail="Batch size too large (max 1000 records)"
            )
        
        logger.info(f"Received batch upload: {len(records)} records")
        
        # 转换为完整模型
        iot_records = [
            IOTTimeseries(**record.model_dump())
            for record in records
        ]
        
        # 异步保存
        background_tasks.add_task(
            _save_iot_records_batch,
            iot_records
        )
        
        return {
            "status": "success",
            "message": "Batch data queued for processing",
            "records_received": len(records)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing batch data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process batch data: {str(e)}"
        )


@router.get("/query", response_model=List[IOTTimeseries], summary="查询IoT数据")
async def query_iot_data(
    tenant_id: UUID = Query(..., description="租户ID"),
    device_id: Optional[UUID] = Query(None, description="设备ID"),
    resident_id: Optional[UUID] = Query(None, description="住户ID"),
    location_id: Optional[UUID] = Query(None, description="位置ID"),
    start_time: Optional[datetime] = Query(None, description="开始时间"),
    end_time: Optional[datetime] = Query(None, description="结束时间"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数量限制"),
):
    """
    查询IoT时序数据
    
    ## 功能
    - 按租户、设备、住户、位置查询
    - 时间范围筛选
    - 分页限制
    
    ## 参数
    - **tenant_id**: 租户ID（必需）
    - **device_id**: 设备ID（可选）
    - **resident_id**: 住户ID（可选）
    - **location_id**: 位置ID（可选）
    - **start_time**: 开始时间（可选，默认24小时前）
    - **end_time**: 结束时间（可选，默认当前时间）
    - **limit**: 返回数量（1-1000，默认100）
    
    ## 返回
    - IoT时序数据列表（按时间倒序）
    """
    try:
        # 设置默认时间范围（最近24小时）
        if end_time is None:
            end_time = datetime.now()
        if start_time is None:
            start_time = end_time - timedelta(hours=24)
        
        logger.info(
            f"Querying IoT data: tenant={tenant_id}, device={device_id}, "
            f"resident={resident_id}, time_range={start_time} to {end_time}"
        )
        
        # 构建查询条件
        def filter_func(record: dict) -> bool:
            # 租户ID必须匹配
            if str(record.get("tenant_id")) != str(tenant_id):
                return False
            
            # 设备ID筛选
            if device_id and str(record.get("device_id")) != str(device_id):
                return False
            
            # 住户ID筛选
            if resident_id and str(record.get("resident_id")) != str(resident_id):
                return False
            
            # 位置ID筛选
            if location_id and str(record.get("location_id")) != str(location_id):
                return False
            
            # 时间范围筛选
            timestamp_str = record.get("timestamp")
            if timestamp_str:
                try:
                    record_time = datetime.fromisoformat(timestamp_str)
                    if not (start_time <= record_time <= end_time):
                        return False
                except (ValueError, TypeError):
                    return False
            
            return True
        
        # 查询数据
        records = await iot_storage.find_all(filter_func)
        
        # 按时间倒序排序
        records.sort(
            key=lambda x: datetime.fromisoformat(x.get("timestamp", "1970-01-01")),
            reverse=True
        )
        
        # 限制返回数量
        records = records[:limit]
        
        logger.info(f"Found {len(records)} IoT records")
        
        return records
        
    except Exception as e:
        logger.error(f"Error querying IoT data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query IoT data: {str(e)}"
        )


@router.get("/latest/{device_id}", response_model=Optional[IOTTimeseries], summary="获取设备最新数据")
async def get_latest_data(
    device_id: UUID,
    tenant_id: UUID = Query(..., description="租户ID"),
):
    """
    获取指定设备的最新一条数据
    
    ## 参数
    - **device_id**: 设备ID
    - **tenant_id**: 租户ID
    
    ## 返回
    - 最新的IoT时序数据，如果没有则返回null
    """
    try:
        logger.info(f"Getting latest data for device: {device_id}")
        
        # 查询该设备的所有数据
        records = await iot_storage.find_all(
            lambda r: (
                str(r.get("device_id")) == str(device_id) and
                str(r.get("tenant_id")) == str(tenant_id)
            )
        )
        
        if not records:
            return None
        
        # 找到最新的记录
        latest = max(
            records,
            key=lambda x: datetime.fromisoformat(x.get("timestamp", "1970-01-01"))
        )
        
        return latest
        
    except Exception as e:
        logger.error(f"Error getting latest data: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get latest data: {str(e)}"
        )


@router.get("/statistics", response_model=dict, summary="获取数据统计信息")
async def get_statistics(
    tenant_id: UUID = Query(..., description="租户ID"),
    hours: int = Query(24, ge=1, le=168, description="统计时间范围（小时）"),
):
    """
    获取IoT数据统计信息
    
    ## 参数
    - **tenant_id**: 租户ID
    - **hours**: 统计时间范围（1-168小时，默认24小时）
    
    ## 返回
    - 数据统计信息（总记录数、设备数、告警数等）
    """
    try:
        start_time = datetime.now() - timedelta(hours=hours)
        
        # 查询时间范围内的数据
        records = await iot_storage.find_all(
            lambda r: (
                str(r.get("tenant_id")) == str(tenant_id) and
                datetime.fromisoformat(r.get("timestamp", "1970-01-01")) >= start_time
            )
        )
        
        # 统计设备数
        device_ids = set(str(r.get("device_id")) for r in records if r.get("device_id"))
        
        # 统计告警数
        alert_count = sum(1 for r in records if r.get("alert_triggered"))
        
        # 统计住户数
        resident_ids = set(str(r.get("resident_id")) for r in records if r.get("resident_id"))
        
        return {
            "tenant_id": str(tenant_id),
            "time_range_hours": hours,
            "total_records": len(records),
            "device_count": len(device_ids),
            "resident_count": len(resident_ids),
            "alert_count": alert_count,
            "start_time": start_time.isoformat(),
            "end_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.delete("/cleanup", response_model=dict, summary="清理历史数据")
async def cleanup_old_data(
    tenant_id: UUID = Query(..., description="租户ID"),
    days: int = Query(30, ge=7, le=365, description="保留最近N天的数据"),
    background_tasks: BackgroundTasks = None,
):
    """
    清理历史IoT数据（保留指定天数的数据）
    
    ## 参数
    - **tenant_id**: 租户ID
    - **days**: 保留天数（7-365天）
    
    ## 返回
    - 清理状态
    """
    try:
        cutoff_time = datetime.now() - timedelta(days=days)
        
        logger.info(f"Cleaning up data older than {cutoff_time} for tenant {tenant_id}")
        
        # 异步执行清理
        if background_tasks:
            background_tasks.add_task(
                _cleanup_old_records,
                tenant_id,
                cutoff_time
            )
        
        return {
            "status": "success",
            "message": f"Cleanup task scheduled for data older than {days} days",
            "cutoff_time": cutoff_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error scheduling cleanup: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to schedule cleanup: {str(e)}"
        )


# ==================== 后台任务函数 ====================

async def _save_iot_records_batch(records: List[IOTTimeseries]):
    """批量保存IoT记录（后台任务）"""
    try:
        for record in records:
            await iot_storage.create(record)
        logger.success(f"Saved {len(records)} IoT records")
    except Exception as e:
        logger.error(f"Error saving IoT records batch: {e}")


async def _process_alert(record: IOTTimeseries):
    """处理告警（后台任务）"""
    try:
        if record.alert_type and record.alert_level:
            await alert_engine.process_alert(
                tenant_id=record.tenant_id,
                alert_type=record.alert_type,
                alert_level=record.alert_level,
                resident_id=record.resident_id,
                device_id=record.device_id,
                location_id=record.location_id,
                alert_data={
                    "timestamp": record.timestamp,
                    "snomed_codes": record.snomed_codes,
                    "danger_level": record.danger_level,
                    "raw_data": record.raw_record
                }
            )
            logger.info(f"Processed alert: {record.alert_type} - {record.alert_level}")
    except Exception as e:
        logger.error(f"Error processing alert: {e}")


async def _cleanup_old_records(tenant_id: UUID, cutoff_time: datetime):
    """清理旧记录（后台任务）"""
    try:
        all_records = await iot_storage.find_all(
            lambda r: str(r.get("tenant_id")) == str(tenant_id)
        )
        
        deleted_count = 0
        for record in all_records:
            try:
                timestamp = datetime.fromisoformat(record.get("timestamp", "1970-01-01"))
                if timestamp < cutoff_time:
                    record_id = record.get("id")
                    if record_id:
                        await iot_storage.delete(UUID(record_id))
                        deleted_count += 1
            except (ValueError, TypeError):
                continue
        
        logger.success(f"Cleaned up {deleted_count} old IoT records for tenant {tenant_id}")
    except Exception as e:
        logger.error(f"Error cleaning up old records: {e}")
