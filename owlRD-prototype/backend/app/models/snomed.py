"""
SNOMED CT编码数据模型
基于 person_matrix_snomed_tags.md 定义
完整的姿态、运动状态、健康状况SNOMED CT编码
"""

from enum import Enum
from pydantic import Field
from app.models.base import BaseModel


# ============================================================================
# Basic SNOMED Code Model
# ============================================================================

class SNOMEDCode(BaseModel):
    """SNOMED CT编码基础模型"""
    code: str = Field(..., description="SNOMED CT编码")
    display: str = Field(..., description="显示名称")
    system: str = Field(default="http://snomed.info/sct", description="编码系统")


# ============================================================================
# Posture Codes (姿态编码)
# ============================================================================

class PostureCode(str, Enum):
    """姿态SNOMED CT编码（基于person_matrix_snomed_tags.md）"""
    
    # 基础体位姿态
    STANDING = "383370001"            # Standing position (站立位)
    SITTING = "402120000"             # Sitting position (坐位)
    LYING = "102538003"               # Lying position (卧位)
    LYING_SUPINE = "40199007"         # Supine body position (仰卧位)
    LYING_PRONE = "1240000"           # Prone body position (俯卧位)
    LYING_LEFT = "102536008"          # Left lateral decubitus position (左侧卧位)
    LYING_RIGHT = "102535007"         # Right lateral decubitus position (右侧卧位)
    
    # 异常姿态
    FALLING = "1912002"               # Fall (跌倒)
    FALL_RISK = "129839007"           # At risk for falls (有跌倒风险)
    ON_FLOOR = "248227000"            # On floor (在地面上)
    
    # 特定环境姿态
    IN_BED = "248569007"              # In bed (在床上)
    NOT_IN_BED = "248570008"          # Not in bed (不在床上)
    BED_SITTING = "40199007"          # Bed sitting position (床上坐姿)
    IN_CHAIR = "248547000"            # Sitting in chair (坐在椅子上)
    IN_WHEELCHAIR = "248546009"       # Sitting in wheelchair (坐在轮椅上)


# ============================================================================
# Motion State Codes (运动状态编码)
# ============================================================================

class MotionStateCode(str, Enum):
    """运动状态SNOMED CT编码"""
    
    # 基础运动状态
    WALKING = "129006008"             # Walking (行走)
    MOVING = "415568008"              # Moving (移动中)
    STATIC = "263821009"              # Static (静止)
    RUNNING = "418060005"             # Running (跑步)
    
    # 异常运动状态
    ABNORMAL_GAIT = "22325002"        # Abnormal gait (异常步态)
    SHUFFLING_GAIT = "22286001"       # Shuffling gait (曳行步态)
    FESTINATING_GAIT = "16973004"     # Festinating gait (慌张步态，帕金森症状)
    LIMPING = "16973004"              # Limping (跛行)
    
    # 特定运动模式
    TREMOR = "26079004"               # Tremor (震颤)
    BRADYKINESIA = "271587009"        # Bradykinesia (运动迟缓)
    HYPERKINESIA = "271589007"        # Hyperkinesia (运动过度)
    RESTLESSNESS = "247379004"        # Restlessness (躁动不安)


# ============================================================================
# Health Condition Codes (健康状况编码)
# ============================================================================

class HealthConditionCode(str, Enum):
    """健康状况SNOMED CT编码"""
    
    # 核心疾病状态
    PARKINSONS_DISEASE = "49049000"   # Parkinson's disease (帕金森病)
    DEMENTIA = "52448006"             # Dementia (痴呆)
    ALZHEIMERS = "26929004"           # Alzheimer's disease (阿尔茨海默病)
    STROKE = "230690007"              # Cerebrovascular accident (脑卒中)
    
    # 关键症状与发现
    FALL_EVENT = "161898004"          # Fall (跌倒事件)
    FALL_RISK = "129839007"           # At risk for falls (跌倒风险)
    CONFUSION = "40917007"            # Confusion (意识混乱)
    DISORIENTATION = "62476001"       # Disorientation (定向障碍)
    AGITATION = "24199005"            # Agitation (躁动)
    
    # 功能状态评估
    MOBILITY_IMPAIRED = "22325002"    # Impaired mobility (活动能力受损)
    SELF_CARE_DEFICIT = "225528002"   # Self-care deficit (自理能力缺陷)
    WEAKNESS = "13791008"             # Weakness (虚弱)
    FATIGUE = "84229001"              # Fatigue (疲劳)


# ============================================================================
# Sleep State Codes (睡眠状态编码)
# ============================================================================

class SleepStateCode(str, Enum):
    """睡眠状态SNOMED CT编码"""
    
    AWAKE = "248220002"               # Awake (清醒)
    LIGHT_SLEEP = "248232005"         # Light sleep (浅睡眠)
    DEEP_SLEEP = "248233000"          # Deep sleep (深睡眠)
    REM_SLEEP = "62106007"            # REM sleep (快速眼动睡眠)


# ============================================================================
# Vital Signs Codes (生命体征编码)
# ============================================================================

class VitalSignsCode(str, Enum):
    """生命体征SNOMED CT编码"""
    
    HEART_RATE = "364075005"          # Heart rate (心率)
    RESPIRATORY_RATE = "86290005"     # Respiratory rate (呼吸率)
    BLOOD_PRESSURE = "75367002"       # Blood pressure (血压)
    BODY_TEMPERATURE = "386725007"    # Body temperature (体温)
    OXYGEN_SATURATION = "431314004"   # Oxygen saturation (血氧饱和度)


# ============================================================================
# Abnormal Vital Signs Codes (异常生命体征编码)
# ============================================================================

class AbnormalVitalSignsCode(str, Enum):
    """异常生命体征SNOMED CT编码"""
    
    # 心率异常
    TACHYCARDIA = "3424008"           # Tachycardia (心动过速，HR>100)
    BRADYCARDIA = "48867003"          # Bradycardia (心动过缓，HR<60)
    
    # 呼吸异常
    TACHYPNEA = "271823003"           # Tachypnea (呼吸急促，RR>20)
    BRADYPNEA = "48867003"            # Bradypnea (呼吸缓慢，RR<12)
    APNEA = "1023001"                 # Apnea (呼吸暂停)
    DYSPNEA = "267036007"             # Dyspnea (呼吸困难)
    
    # 体温异常
    HYPERTHERMIA = "386661006"        # Hyperthermia (高热)
    HYPOTHERMIA = "38692000"          # Hypothermia (低温)
    
    # 血压异常
    HYPERTENSION = "38341003"         # Hypertension (高血压)
    HYPOTENSION = "45007003"          # Hypotension (低血压)


# ============================================================================
# Safety Event Codes (安全事件编码)
# ============================================================================

class SafetyEventCode(str, Enum):
    """安全事件SNOMED CT编码"""
    
    FALL = "161898004"                # Fall (跌倒)
    SUSPECTED_FALL = "129839007"      # At risk for falls (疑似跌倒)
    PROLONGED_STAY = "271889006"      # Prolonged stay (长时间滞留)
    WANDERING = "419223000"           # Wandering (游走)
    ELOPEMENT = "713491005"           # Elopement (走失)
    NO_ACTIVITY = "373930000"         # No activity (无活动)


# ============================================================================
# Helper Functions
# ============================================================================

def get_snomed_display(code: str) -> str:
    """根据SNOMED CT编码获取显示名称"""
    code_map = {
        # Posture
        "383370001": "Standing position",
        "402120000": "Sitting position",
        "102538003": "Lying position",
        "40199007": "Supine body position",
        
        # Motion State
        "129006008": "Walking",
        "415568008": "Moving",
        "263821009": "Static",
        "22325002": "Abnormal gait",
        
        # Health Condition
        "49049000": "Parkinson's disease",
        "161898004": "Fall",
        "129839007": "At risk for falls",
        
        # Sleep State
        "248220002": "Awake",
        "248232005": "Light sleep",
        "248233000": "Deep sleep",
        
        # Vital Signs
        "364075005": "Heart rate",
        "86290005": "Respiratory rate",
    }
    return code_map.get(code, "Unknown")


def create_snomed_code(code: str, display: str = None) -> SNOMEDCode:
    """创建SNOMED CT编码对象"""
    if display is None:
        display = get_snomed_display(code)
    return SNOMEDCode(code=code, display=display)
