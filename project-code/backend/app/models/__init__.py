"""
数据模型模块
完整实现19个核心数据实体的Pydantic模型
"""

from app.models.base import BaseModel, TimestampMixin, UUIDMixin, generate_uuid
from app.models.tenant import Tenant, TenantCreate, TenantUpdate
from app.models.user import User, Role, UserCreate, UserUpdate, UserLogin, UserLoginResponse
from app.models.location import (
    Location, LocationCreate, LocationUpdate,
    Room, RoomCreate, RoomUpdate,
    Bed, BedCreate, BedUpdate
)
from app.models.resident import (
    Resident, ResidentCreate, ResidentUpdate,
    ResidentPHI, ResidentPHICreate, ResidentPHIUpdate,
    ResidentContact, ResidentContactCreate, ResidentContactUpdate,
    ResidentCaregiver, ResidentCaregiverCreate, ResidentCaregiverUpdate,
    AnonymousNamePool, AnonymousNamePoolCreate, AnonymousNamePoolUpdate,
)
from app.models.device import Device, DeviceCreate, DeviceUpdate
from app.models.iot_data import (
    IOTTimeseries, IOTTimeseriesCreate,
    IOTMonitorAlert, IOTMonitorAlertCreate, IOTMonitorAlertUpdate
)
from app.models.alert import (
    Alert, AlertCreate, AlertUpdate, AlertStatus,
    CloudAlertPolicy, CloudAlertPolicyCreate, CloudAlertPolicyUpdate,
    AlertLevel, AlertScope, DangerLevel
)
from app.models.card import (
    Card, CardCreate, CardUpdate,
    CardDevice, CardDeviceCreate,
    CardType, BindingType
)
from app.models.config import (
    ConfigVersion, ConfigVersionCreate, ConfigVersionUpdate,
    PostureMapping, PostureMappingCreate, PostureMappingUpdate,
    EventMapping, EventMappingCreate, EventMappingUpdate
)
from app.models.tdp import (
    TDPEvent, LiteEventHeader, ExtendEventHeader,
    PersonMatrix, ObjectMatrix,
    Tag, CodeableConcept, Timestamp, SleepPeriod,
    DangerLevel as TDPDangerLevel, DatagramMode
)
from app.models.snomed import (
    SNOMEDCode,
    PostureCode, MotionStateCode, HealthConditionCode,
    SleepStateCode, VitalSignsCode, AbnormalVitalSignsCode, SafetyEventCode,
    get_snomed_display, create_snomed_code
)

__all__ = [
    # Base
    "BaseModel",
    "TimestampMixin",
    "UUIDMixin",
    "generate_uuid",
    # Tenant
    "Tenant",
    "TenantCreate",
    "TenantUpdate",
    # User & Role
    "User",
    "UserCreate",
    "UserUpdate",
    "UserLogin",
    "UserLoginResponse",
    "Role",
    # Location, Room, Bed
    "Location",
    "LocationCreate",
    "LocationUpdate",
    "Room",
    "RoomCreate",
    "RoomUpdate",
    "Bed",
    "BedCreate",
    "BedUpdate",
    # Resident Series
    "Resident",
    "ResidentCreate",
    "ResidentUpdate",
    "ResidentPHI",
    "ResidentPHICreate",
    "ResidentPHIUpdate",
    "ResidentContact",
    "ResidentContactCreate",
    "ResidentContactUpdate",
    "ResidentCaregiver",
    "ResidentCaregiverCreate",
    "ResidentCaregiverUpdate",
    "AnonymousNamePool",
    "AnonymousNamePoolCreate",
    "AnonymousNamePoolUpdate",
    # Device
    "Device",
    "DeviceCreate",
    "DeviceUpdate",
    # IOT Data
    "IOTTimeseries",
    "IOTTimeseriesCreate",
    "IOTMonitorAlert",
    "IOTMonitorAlertCreate",
    "IOTMonitorAlertUpdate",
    # Alert
    "Alert",
    "AlertCreate",
    "AlertUpdate",
    "AlertStatus",
    "CloudAlertPolicy",
    "CloudAlertPolicyCreate",
    "CloudAlertPolicyUpdate",
    "AlertLevel",
    "AlertScope",
    "DangerLevel",
    # Card
    "Card",
    "CardCreate",
    "CardUpdate",
    "CardDevice",
    "CardDeviceCreate",
    "CardType",
    "BindingType",
    # Config
    "ConfigVersion",
    "ConfigVersionCreate",
    "ConfigVersionUpdate",
    "PostureMapping",
    "PostureMappingCreate",
    "PostureMappingUpdate",
    "EventMapping",
    "EventMappingCreate",
    "EventMappingUpdate",
    # TDP Protocol
    "TDPEvent",
    "LiteEventHeader",
    "ExtendEventHeader",
    "PersonMatrix",
    "ObjectMatrix",
    "Tag",
    "CodeableConcept",
    "Timestamp",
    "SleepPeriod",
    "TDPDangerLevel",
    "DatagramMode",
    # SNOMED CT
    "SNOMEDCode",
    "PostureCode",
    "MotionStateCode",
    "HealthConditionCode",
    "SleepStateCode",
    "VitalSignsCode",
    "AbnormalVitalSignsCode",
    "SafetyEventCode",
    "get_snomed_display",
    "create_snomed_code",
]
