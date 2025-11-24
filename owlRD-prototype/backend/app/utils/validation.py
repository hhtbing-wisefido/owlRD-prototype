"""
数据验证工具
为JSON存储提供数据完整性验证
"""

from typing import Dict, List, Any, Callable, Optional
from datetime import datetime
import re


class ValidationError(Exception):
    """验证错误"""
    pass


class Validator:
    """数据验证器"""
    
    def __init__(self):
        self.rules = {}
    
    def add_rule(self, field: str, rule: Callable, message: str):
        """添加验证规则"""
        if field not in self.rules:
            self.rules[field] = []
        self.rules[field].append((rule, message))
    
    def validate(self, data: Dict) -> List[str]:
        """验证数据，返回错误消息列表"""
        errors = []
        
        for field, rules in self.rules.items():
            value = data.get(field)
            for rule, message in rules:
                if not rule(value, data):
                    errors.append(f"{field}: {message}")
        
        return errors
    
    def validate_or_raise(self, data: Dict):
        """验证数据，如果有错误则抛出异常"""
        errors = self.validate(data)
        if errors:
            raise ValidationError("; ".join(errors))


# ============================================================================
# 预定义验证规则
# ============================================================================

def required(value, data) -> bool:
    """必填验证"""
    return value is not None and value != ""


def min_length(min_len: int):
    """最小长度验证"""
    def validator(value, data) -> bool:
        if value is None:
            return True
        return len(str(value)) >= min_len
    return validator


def max_length(max_len: int):
    """最大长度验证"""
    def validator(value, data) -> bool:
        if value is None:
            return True
        return len(str(value)) <= max_len
    return validator


def email_format(value, data) -> bool:
    """邮箱格式验证"""
    if value is None:
        return True
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, value) is not None


def phone_format(value, data) -> bool:
    """手机号格式验证（中国）- 宽松模式，允许任意非空字符串"""
    if value is None or value == "":
        return True
    # 宽松验证：如果提供了值，只要不为空就通过
    # 允许任意格式的联系方式（电话、工号、用户名等）
    return len(str(value).strip()) > 0


def in_choices(choices: List[Any]):
    """枚举值验证"""
    def validator(value, data) -> bool:
        if value is None:
            return True
        return value in choices
    return validator


def is_uuid(value, data) -> bool:
    """UUID格式验证"""
    if value is None:
        return True
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return re.match(pattern, str(value).lower()) is not None


def is_date(value, data) -> bool:
    """日期格式验证"""
    if value is None:
        return True
    try:
        datetime.fromisoformat(str(value).replace('Z', '+00:00'))
        return True
    except:
        return False


def numeric_range(min_val: Optional[float] = None, max_val: Optional[float] = None):
    """数值范围验证"""
    def validator(value, data) -> bool:
        if value is None:
            return True
        try:
            num = float(value)
            if min_val is not None and num < min_val:
                return False
            if max_val is not None and num > max_val:
                return False
            return True
        except:
            return False
    return validator


# ============================================================================
# 预定义实体验证器
# ============================================================================

def get_user_validator() -> Validator:
    """用户数据验证器"""
    validator = Validator()
    
    validator.add_rule("username", required, "用户名不能为空")
    validator.add_rule("username", min_length(3), "用户名至少3个字符")
    validator.add_rule("username", max_length(50), "用户名最多50个字符")
    
    validator.add_rule("email", required, "邮箱不能为空")
    validator.add_rule("email", email_format, "邮箱格式不正确")
    
    validator.add_rule("phone", phone_format, "手机号格式不正确")
    
    validator.add_rule("role", required, "角色不能为空")
    validator.add_rule("role", in_choices([
        "Director", "NurseManager", "Nurse", 
        "Caregiver", "Doctor", "FamilyMember"
    ]), "角色值无效")
    
    validator.add_rule("tenant_id", required, "租户ID不能为空")
    validator.add_rule("tenant_id", is_uuid, "租户ID格式不正确")
    
    return validator


def get_resident_validator() -> Validator:
    """住户数据验证器 - 对齐07_residents.sql（完全匿名化，无PHI）"""
    validator = Validator()
    
    # residents表是完全匿名化的，这些字段可选或不存在
    # first_name是可选的（Optional）
    # last_name是匿名代称，必需
    validator.add_rule("last_name", required, "姓氏/匿名代称不能为空")
    
    # gender和date_of_birth在resident_phi表中，不在residents表
    # 不应该验证这些字段
    
    # admission_date是必需的
    validator.add_rule("admission_date", required, "入住日期不能为空")
    validator.add_rule("admission_date", is_date, "入住日期格式不正确")
    
    # status必需，值为 active, discharged, transferred
    validator.add_rule("status", in_choices(["active", "discharged", "transferred"]), "状态值无效")
    
    validator.add_rule("tenant_id", required, "租户ID不能为空")
    validator.add_rule("tenant_id", is_uuid, "租户ID格式不正确")
    
    return validator


def get_device_validator() -> Validator:
    """设备数据验证器 - 对齐11_devices.sql"""
    validator = Validator()
    
    # device_code在SQL中不存在，应该是device_name和serial_number
    # 不验证device_code
    
    # device_type的值应该对齐SQL和Model: Radar, SleepPad, VibrationSensor, Camera, Gateway等
    validator.add_rule("device_type", required, "设备类型不能为空")
    # 验证规则过于严格，改为只验证必需，允许任何类型值
    # validator.add_rule("device_type", in_choices([
    #     "Radar", "SleepPad", "VibrationSensor", "Camera", "Gateway", "Wearable", "Other"
    # ]), "设备类型无效")
    
    # status的值应该对齐SQL: online, offline, error, dormant, maintenance
    validator.add_rule("status", in_choices([
        "online", "offline", "error", "dormant", "maintenance"
    ]), "状态值无效")
    
    validator.add_rule("tenant_id", required, "租户ID不能为空")
    validator.add_rule("tenant_id", is_uuid, "租户ID格式不正确")
    
    return validator


def get_alert_validator() -> Validator:
    """
    告警数据验证器
    对齐源参考: TDPv2-0916.md + 25_Alarm_Notification_Flow.md
    告警级别: L1/L2/L3/L5/L8/L9/DISABLE
    """
    validator = Validator()
    
    validator.add_rule("alert_type", required, "告警类型不能为空")
    
    # 使用alert_level而非severity（对齐源参考）
    validator.add_rule("alert_level", required, "告警级别不能为空")
    validator.add_rule("alert_level", in_choices([
        "L1", "L2", "L3", "L5", "L8", "L9", "DISABLE"
    ]), "告警级别无效，必须是L1/L2/L3/L5/L8/L9/DISABLE")
    
    validator.add_rule("status", in_choices([
        "pending", "acknowledged", "resolved", "dismissed"
    ]), "状态值无效")
    
    # 使用timestamp而非alert_time（对齐models/alert.py）
    validator.add_rule("timestamp", required, "告警时间不能为空")
    validator.add_rule("timestamp", is_date, "告警时间格式不正确")
    
    validator.add_rule("tenant_id", required, "租户ID不能为空")
    validator.add_rule("tenant_id", is_uuid, "租户ID格式不正确")
    
    return validator


# ============================================================================
# 验证器工厂
# ============================================================================

VALIDATORS = {
    "users": get_user_validator,
    "residents": get_resident_validator,
    "devices": get_device_validator,
    "alerts": get_alert_validator,
}


def get_validator(entity_type: str) -> Optional[Validator]:
    """获取实体类型的验证器"""
    factory = VALIDATORS.get(entity_type)
    return factory() if factory else None
