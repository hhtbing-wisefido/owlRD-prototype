"""
配置版本历史管理API端点
对应 config_versions 表 (15_config_versions.sql)
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query

from app.models.config import ConfigVersion, ConfigVersionCreate, ConfigVersionUpdate
from app.services.storage import StorageService

router = APIRouter()
config_storage = StorageService[ConfigVersion]("config_versions")


@router.get("", response_model=List[ConfigVersion])
async def list_config_versions(
    tenant_id: UUID = Query(..., description="租户ID"),
    config_type: Optional[str] = Query(None, description="配置类型过滤"),
    entity_id: Optional[UUID] = Query(None, description="实体ID过滤"),
    limit: int = Query(100, ge=1, le=1000)
):
    """
    获取配置版本历史列表
    
    支持按配置类型和实体ID过滤
    """
    def filter_fn(cv):
        if str(cv.get("tenant_id")) != str(tenant_id):
            return False
        if config_type and cv.get("config_type") != config_type:
            return False
        if entity_id and str(cv.get("entity_id")) != str(entity_id):
            return False
        return True
    
    versions = config_storage.find_all(filter_fn)
    # 按生效时间倒序排列
    versions_sorted = sorted(versions, key=lambda x: x.get("valid_from", ""), reverse=True)
    return versions_sorted[:limit]


@router.get("/{version_id}", response_model=ConfigVersion)
async def get_config_version(version_id: UUID):
    """
    获取单个配置版本详情
    """
    version = config_storage.find_by_id("version_id", version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Config version not found")
    return version


@router.get("/current/{config_type}/{entity_id}", response_model=Optional[ConfigVersion])
async def get_current_config(
    config_type: str,
    entity_id: UUID,
    tenant_id: UUID = Query(..., description="租户ID"),
    as_of_time: Optional[datetime] = Query(None, description="回放到指定时间点")
):
    """
    获取当前生效的配置版本（支持历史回放）
    
    - **config_type**: 配置类型
    - **entity_id**: 实体ID
    - **as_of_time**: 可选，回放到指定时间点（用于历史数据分析）
    
    **使用场景**：
    - 查询某个房间当前的布局配置
    - 查询某个设备在某个历史时间点的技术配置
    - 分析某个时间点的告警策略配置
    """
    def filter_fn(cv):
        if str(cv.get("tenant_id")) != str(tenant_id):
            return False
        if cv.get("config_type") != config_type:
            return False
        if str(cv.get("entity_id")) != str(entity_id):
            return False
        
        # 时间区间过滤
        valid_from_str = cv.get("valid_from")
        valid_to_str = cv.get("valid_to")
        
        if not valid_from_str:
            return False
        
        valid_from = datetime.fromisoformat(valid_from_str.replace('Z', '+00:00'))
        valid_to = datetime.fromisoformat(valid_to_str.replace('Z', '+00:00')) if valid_to_str else None
        
        target_time = as_of_time or datetime.utcnow()
        
        # valid_from <= target_time < valid_to (or valid_to is NULL)
        if valid_from > target_time:
            return False
        if valid_to and valid_to <= target_time:
            return False
        
        return True
    
    versions = config_storage.find_all(filter_fn)
    
    if not versions:
        return None
    
    # 返回最新的生效版本
    versions_sorted = sorted(versions, key=lambda x: x.get("valid_from", ""), reverse=True)
    return versions_sorted[0]


@router.post("", response_model=ConfigVersion, status_code=201)
async def create_config_version(version_data: ConfigVersionCreate):
    """
    创建新的配置版本
    
    **注意**：
    - 创建新版本时，应将同一entity_id的旧版本的valid_to设置为新版本的valid_from
    - 确保任一时间点只有一个生效版本
    
    **配置类型**：
    - room_layout: 房间布局配置
    - device_config: 设备技术配置
    - cloud_alert_policy: 云端告警策略
    - iot_monitor_alert: IoT设备报警配置
    - device_installation: 设备安装/绑定
    """
    from app.models.base import generate_uuid
    version_dict = version_data.model_dump()
    version_dict["version_id"] = str(generate_uuid())
    version_dict["created_at"] = datetime.now().isoformat()
    version_dict["updated_at"] = datetime.now().isoformat()
    
    # 如果valid_from未指定，使用当前时间
    if not version_dict.get("valid_from"):
        version_dict["valid_from"] = datetime.now().isoformat()
    
    # 自动失效同一entity的旧版本
    def find_old_versions(cv):
        return (
            str(cv.get("tenant_id")) == str(version_data.tenant_id) and
            cv.get("config_type") == version_data.config_type and
            str(cv.get("entity_id")) == str(version_data.entity_id) and
            cv.get("valid_to") is None  # 当前仍生效的版本
        )
    
    old_versions = config_storage.find_all(find_old_versions)
    for old_version in old_versions:
        config_storage.update(
            "version_id",
            old_version["version_id"],
            {
                "valid_to": version_dict["valid_from"],
                "updated_at": datetime.now().isoformat()
            }
        )
    
    config_storage.create(version_dict)
    return version_dict


@router.put("/{version_id}", response_model=ConfigVersion)
async def update_config_version(version_id: UUID, version_data: ConfigVersionUpdate):
    """
    更新配置版本
    
    通常用于：
    - 手动设置valid_to（失效某个版本）
    - 更新config_data（修正配置内容）
    """
    existing_version = config_storage.find_by_id("version_id", version_id)
    if not existing_version:
        raise HTTPException(status_code=404, detail="Config version not found")
    
    update_data = version_data.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now().isoformat()
    
    updated = config_storage.update("version_id", version_id, update_data)
    return updated


@router.delete("/{version_id}", status_code=204)
async def delete_config_version(version_id: UUID):
    """
    删除配置版本
    
    **警告**：删除配置版本可能导致历史数据无法回放
    """
    version = config_storage.find_by_id("version_id", version_id)
    if not version:
        raise HTTPException(status_code=404, detail="Config version not found")
    
    config_storage.delete("version_id", version_id)
    return None


@router.get("/history/{config_type}/{entity_id}", response_model=List[ConfigVersion])
async def get_config_history(
    config_type: str,
    entity_id: UUID,
    tenant_id: UUID = Query(..., description="租户ID"),
    limit: int = Query(50, ge=1, le=500)
):
    """
    获取某个实体的完整配置历史
    
    **使用场景**：
    - 查看房间布局的所有历史版本
    - 追踪设备配置的变更记录
    - 审计告警策略的修改历史
    """
    def filter_fn(cv):
        return (
            str(cv.get("tenant_id")) == str(tenant_id) and
            cv.get("config_type") == config_type and
            str(cv.get("entity_id")) == str(entity_id)
        )
    
    versions = config_storage.find_all(filter_fn)
    versions_sorted = sorted(versions, key=lambda x: x.get("valid_from", ""), reverse=True)
    return versions_sorted[:limit]
