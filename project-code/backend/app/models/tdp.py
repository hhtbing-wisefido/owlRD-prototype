"""
TDPv2协议数据模型
基于 TDPv2-0916.md 定义
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import Field

from app.models.base import BaseModel


# ============================================================================
# Enums (枚举类型)
# ============================================================================

class DangerLevel(str, Enum):
    """危险等级（TDPv2协议定义）"""
    EMERGENCY = "L1"       # 紧急（HR<44或>116持续60s，RR<5或>27持续60s）
    ALERT = "L2"           # 警报（HR 45-54或96-115持续300s，RR 8-9或24-26持续300s）
    CRITICAL = "L3"        # 严重
    WARNING = "L5"         # 警告
    DEBUG = "L8"           # 调试
    CANCEL = "L9"          # 取消


class DatagramMode(str, Enum):
    """数据报文模式"""
    LITE = "LITE"           # 轻量级模式
    EXTEND = "EXTEND"       # 扩展模式


# ============================================================================
# Basic Models (基础模型)
# ============================================================================

class Timestamp(BaseModel):
    """时间戳（Protobuf格式）"""
    seconds: int = Field(..., description="Unix时间戳（秒）")
    nanos: int = Field(default=0, description="纳秒部分")


class CodeableConcept(BaseModel):
    """编码概念（SNOMED CT / LOINC）"""
    system: str = Field(..., description="编码系统（如http://snomed.info/sct）")
    code: str = Field(..., description="编码值")
    display: Optional[str] = Field(None, description="显示名称")


class Tag(BaseModel):
    """标签"""
    category: str = Field(..., description="标签类别")
    code: str = Field(..., description="标签代码")
    value: Optional[str] = Field(None, description="标签值")
    codeable_concept: Optional[CodeableConcept] = Field(None, description="编码概念")


class SleepPeriod(BaseModel):
    """睡眠周期"""
    start: Timestamp = Field(..., description="开始时间")
    end: Optional[Timestamp] = Field(None, description="结束时间")
    sleep_state: Optional[CodeableConcept] = Field(None, description="睡眠状态（Awake/Light/Deep）")


# ============================================================================
# Person Matrix (人员矩阵)
# ============================================================================

class PersonMatrix(BaseModel):
    """人员矩阵（核心数据结构）"""
    
    # 空间位置（雷达坐标系，厘米）
    pos_x: int = Field(..., description="X坐标（厘米）")
    pos_y: int = Field(..., description="Y坐标（厘米）")
    pos_z: int = Field(..., description="Z坐标（厘米）")
    
    # 速度信息（厘米/秒）
    vel_x: Optional[int] = Field(None, description="X方向速度（cm/s）")
    vel_y: Optional[int] = Field(None, description="Y方向速度（cm/s）")
    vel_z: Optional[int] = Field(None, description="Z方向速度（cm/s）")
    
    # 姿态状态（SNOMED CT编码）
    posture: Optional[CodeableConcept] = Field(None, description="姿态（Standing/Sitting/Lying等）")
    
    # 运动状态（SNOMED CT编码）
    motion_state: Optional[CodeableConcept] = Field(None, description="运动状态（Walking/Static/AbnormalGait等）")
    
    # 健康状况（SNOMED CT编码）
    health_score: Optional[CodeableConcept] = Field(None, description="健康状况（如Parkinsons/Fall等）")
    
    # 生命体征
    heart_rate: Optional[int] = Field(None, description="心率（bpm）")
    respiratory_rate: Optional[int] = Field(None, description="呼吸率（次/分钟）")
    
    # 睡眠状态
    sleep_state: Optional[CodeableConcept] = Field(None, description="睡眠状态（Awake/Light/Deep）")
    sleep_period: Optional[SleepPeriod] = Field(None, description="睡眠周期")
    
    # 其他
    tracking_id: Optional[int] = Field(None, description="跟踪ID（0-7）")
    confidence: Optional[int] = Field(None, ge=0, le=100, description="置信度（0-100）")
    tags: Optional[List[Tag]] = Field(None, description="标签列表")


# ============================================================================
# Object Matrix (物体矩阵)
# ============================================================================

class ObjectMatrix(BaseModel):
    """物体矩阵（床、轮椅、沙发等）"""
    
    object_type: str = Field(..., description="物体类型：Bed/Wheelchair/Sofa/DangerZone")
    object_id: Optional[str] = Field(None, description="物体ID")
    
    # 空间位置
    pos_x: int = Field(..., description="X坐标（厘米）")
    pos_y: int = Field(..., description="Y坐标（厘米）")
    pos_z: int = Field(..., description="Z坐标（厘米）")
    
    # 尺寸
    width: Optional[int] = Field(None, description="宽度（厘米）")
    height: Optional[int] = Field(None, description="高度（厘米）")
    depth: Optional[int] = Field(None, description="深度（厘米）")
    
    # 属性
    is_occupied: Optional[bool] = Field(None, description="是否有人占用")
    tags: Optional[List[Tag]] = Field(None, description="标签列表")


# ============================================================================
# Event Header (事件头)
# ============================================================================

class LiteEventHeader(BaseModel):
    """轻量级事件头"""
    
    device_id: str = Field(..., description="设备ID")
    timestamp: Timestamp = Field(..., description="时间戳")
    danger_level: Optional[DangerLevel] = Field(None, description="危险等级")
    event_type: Optional[str] = Field(None, description="事件类型")


class ExtendEventHeader(BaseModel):
    """扩展事件头"""
    
    device_id: str = Field(..., description="设备ID")
    timestamp: Timestamp = Field(..., description="时间戳")
    danger_level: Optional[DangerLevel] = Field(None, description="危险等级")
    event_type: Optional[str] = Field(None, description="事件类型")
    
    # 扩展信息
    tenant_id: Optional[str] = Field(None, description="租户ID")
    location_id: Optional[str] = Field(None, description="位置ID")
    room_id: Optional[str] = Field(None, description="房间ID")
    bed_id: Optional[str] = Field(None, description="床位ID")
    resident_id: Optional[str] = Field(None, description="住户ID")


# ============================================================================
# TDP Event (TDP数据报文)
# ============================================================================

class TDPEvent(BaseModel):
    """TDP事件数据报文"""
    
    mode: DatagramMode = Field(..., description="数据报文模式：LITE/EXTEND")
    header: LiteEventHeader | ExtendEventHeader = Field(..., description="事件头")
    
    # 数据内容
    person_matrices: Optional[List[PersonMatrix]] = Field(None, description="人员矩阵列表")
    object_matrices: Optional[List[ObjectMatrix]] = Field(None, description="物体矩阵列表")
    
    # 原始数据（可选）
    raw_data: Optional[bytes] = Field(None, description="原始Protobuf数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "mode": "EXTEND",
                "header": {
                    "device_id": "Radar01",
                    "timestamp": {"seconds": 1732089600, "nanos": 0},
                    "danger_level": "L1",
                    "event_type": "ABNORMAL_HEART_RATE",
                    "tenant_id": "550e8400-e29b-41d4-a716-446655440000",
                    "location_id": "550e8400-e29b-41d4-a716-446655440010",
                    "resident_id": "550e8400-e29b-41d4-a716-446655440020"
                },
                "person_matrices": [
                    {
                        "pos_x": 150,
                        "pos_y": 200,
                        "pos_z": 100,
                        "vel_x": 0,
                        "vel_y": 0,
                        "vel_z": 0,
                        "posture": {
                            "system": "http://snomed.info/sct",
                            "code": "102538003",
                            "display": "Lying position"
                        },
                        "heart_rate": 72,
                        "respiratory_rate": 16,
                        "tracking_id": 0,
                        "confidence": 95
                    }
                ],
                "object_matrices": [
                    {
                        "object_type": "Bed",
                        "object_id": "BedA",
                        "pos_x": 150,
                        "pos_y": 200,
                        "pos_z": 50,
                        "width": 200,
                        "height": 80,
                        "depth": 100,
                        "is_occupied": True
                    }
                ]
            }
        }
