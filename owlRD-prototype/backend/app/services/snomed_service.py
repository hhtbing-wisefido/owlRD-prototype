"""
SNOMED CT编码服务
提供SNOMED CT编码的查询、验证和转换功能
"""

from typing import Optional, Dict, List
from app.models.snomed import (
    SNOMEDCode,
    PostureCode, MotionStateCode, HealthConditionCode,
    SleepStateCode, VitalSignsCode, AbnormalVitalSignsCode, SafetyEventCode,
    get_snomed_display, create_snomed_code
)


class SnomedService:
    """SNOMED CT编码服务"""
    
    def __init__(self):
        """初始化SNOMED服务"""
        self._init_code_mappings()
    
    def _init_code_mappings(self) -> None:
        """初始化编码映射"""
        # 姿态编码映射
        self.posture_codes: Dict[str, str] = {
            PostureCode.STANDING: "Standing position",
            PostureCode.SITTING: "Sitting position",
            PostureCode.LYING: "Lying position",
            PostureCode.LYING_SUPINE: "Supine body position",
            PostureCode.LYING_PRONE: "Prone body position",
            PostureCode.LYING_LEFT: "Left lateral decubitus position",
            PostureCode.LYING_RIGHT: "Right lateral decubitus position",
            PostureCode.FALLING: "Fall",
            PostureCode.FALL_RISK: "At risk for falls",
            PostureCode.ON_FLOOR: "On floor",
            PostureCode.IN_BED: "In bed",
            PostureCode.NOT_IN_BED: "Not in bed",
            PostureCode.BED_SITTING: "Bed sitting position",
            PostureCode.IN_CHAIR: "Sitting in chair",
            PostureCode.IN_WHEELCHAIR: "Sitting in wheelchair",
        }
        
        # 运动状态编码映射
        self.motion_codes: Dict[str, str] = {
            MotionStateCode.WALKING: "Walking",
            MotionStateCode.MOVING: "Moving",
            MotionStateCode.STATIC: "Static",
            MotionStateCode.RUNNING: "Running",
            MotionStateCode.ABNORMAL_GAIT: "Abnormal gait",
            MotionStateCode.SHUFFLING_GAIT: "Shuffling gait",
            MotionStateCode.FESTINATING_GAIT: "Festinating gait",
            MotionStateCode.LIMPING: "Limping",
            MotionStateCode.TREMOR: "Tremor",
            MotionStateCode.BRADYKINESIA: "Bradykinesia",
            MotionStateCode.HYPERKINESIA: "Hyperkinesia",
            MotionStateCode.RESTLESSNESS: "Restlessness",
        }
        
        # 健康状况编码映射
        self.health_codes: Dict[str, str] = {
            HealthConditionCode.PARKINSONS_DISEASE: "Parkinson's disease",
            HealthConditionCode.DEMENTIA: "Dementia",
            HealthConditionCode.ALZHEIMERS: "Alzheimer's disease",
            HealthConditionCode.STROKE: "Cerebrovascular accident",
            HealthConditionCode.FALL_EVENT: "Fall",
            HealthConditionCode.FALL_RISK: "At risk for falls",
            HealthConditionCode.CONFUSION: "Confusion",
            HealthConditionCode.DISORIENTATION: "Disorientation",
            HealthConditionCode.AGITATION: "Agitation",
            HealthConditionCode.MOBILITY_IMPAIRED: "Impaired mobility",
            HealthConditionCode.SELF_CARE_DEFICIT: "Self-care deficit",
            HealthConditionCode.WEAKNESS: "Weakness",
            HealthConditionCode.FATIGUE: "Fatigue",
        }
        
        # 睡眠状态编码映射
        self.sleep_codes: Dict[str, str] = {
            SleepStateCode.AWAKE: "Awake",
            SleepStateCode.LIGHT_SLEEP: "Light sleep",
            SleepStateCode.DEEP_SLEEP: "Deep sleep",
            SleepStateCode.REM_SLEEP: "REM sleep",
        }
        
        # 生命体征编码映射
        self.vital_codes: Dict[str, str] = {
            VitalSignsCode.HEART_RATE: "Heart rate",
            VitalSignsCode.RESPIRATORY_RATE: "Respiratory rate",
            VitalSignsCode.BLOOD_PRESSURE: "Blood pressure",
            VitalSignsCode.BODY_TEMPERATURE: "Body temperature",
            VitalSignsCode.OXYGEN_SATURATION: "Oxygen saturation",
        }
        
        # 异常生命体征编码映射
        self.abnormal_vital_codes: Dict[str, str] = {
            AbnormalVitalSignsCode.TACHYCARDIA: "Tachycardia",
            AbnormalVitalSignsCode.BRADYCARDIA: "Bradycardia",
            AbnormalVitalSignsCode.TACHYPNEA: "Tachypnea",
            AbnormalVitalSignsCode.BRADYPNEA: "Bradypnea",
            AbnormalVitalSignsCode.APNEA: "Apnea",
            AbnormalVitalSignsCode.DYSPNEA: "Dyspnea",
            AbnormalVitalSignsCode.HYPERTHERMIA: "Hyperthermia",
            AbnormalVitalSignsCode.HYPOTHERMIA: "Hypothermia",
            AbnormalVitalSignsCode.HYPERTENSION: "Hypertension",
            AbnormalVitalSignsCode.HYPOTENSION: "Hypotension",
        }
        
        # 安全事件编码映射
        self.safety_codes: Dict[str, str] = {
            SafetyEventCode.FALL: "Fall",
            SafetyEventCode.SUSPECTED_FALL: "At risk for falls",
            SafetyEventCode.PROLONGED_STAY: "Prolonged stay",
            SafetyEventCode.WANDERING: "Wandering",
            SafetyEventCode.ELOPEMENT: "Elopement",
            SafetyEventCode.NO_ACTIVITY: "No activity",
        }
        
        # 合并所有编码
        self.all_codes = {
            **self.posture_codes,
            **self.motion_codes,
            **self.health_codes,
            **self.sleep_codes,
            **self.vital_codes,
            **self.abnormal_vital_codes,
            **self.safety_codes
        }
    
    def get_display_name(self, code: str) -> str:
        """
        获取SNOMED CT编码的显示名称
        
        Args:
            code: SNOMED CT编码
            
        Returns:
            显示名称，如果编码不存在返回"Unknown"
        """
        return self.all_codes.get(code, "Unknown")
    
    def validate_code(self, code: str) -> bool:
        """
        验证SNOMED CT编码是否有效
        
        Args:
            code: SNOMED CT编码
            
        Returns:
            是否有效
        """
        return code in self.all_codes
    
    def create_code(self, code: str, display: Optional[str] = None) -> SNOMEDCode:
        """
        创建SNOMED CT编码对象
        
        Args:
            code: SNOMED CT编码
            display: 显示名称（可选，如果不提供则自动查找）
            
        Returns:
            SNOMED CT编码对象
        """
        if display is None:
            display = self.get_display_name(code)
        return SNOMEDCode(code=code, display=display)
    
    def get_codes_by_category(self, category: str) -> Dict[str, str]:
        """
        根据类别获取编码
        
        Args:
            category: 类别（posture/motion/health/sleep/vital/abnormal_vital/safety）
            
        Returns:
            编码字典
        """
        category_map = {
            "posture": self.posture_codes,
            "motion": self.motion_codes,
            "health": self.health_codes,
            "sleep": self.sleep_codes,
            "vital": self.vital_codes,
            "abnormal_vital": self.abnormal_vital_codes,
            "safety": self.safety_codes,
        }
        return category_map.get(category, {})
    
    def search_codes(self, query: str) -> List[SNOMEDCode]:
        """
        搜索SNOMED CT编码
        
        Args:
            query: 搜索关键词
            
        Returns:
            匹配的编码列表
        """
        query_lower = query.lower()
        results = []
        
        for code, display in self.all_codes.items():
            if query_lower in display.lower() or query_lower in code:
                results.append(SNOMEDCode(code=code, display=display))
        
        return results
    
    def get_posture_from_raw(self, raw_posture: int) -> Optional[SNOMEDCode]:
        """
        从原始姿态值获取SNOMED CT编码
        
        Args:
            raw_posture: 原始姿态值（0-11）
            
        Returns:
            SNOMED CT编码对象，如果原始值无效返回None
        """
        # 基于16_mapping_tables.sql的映射
        raw_to_snomed = {
            0: None,  # 初始化
            1: PostureCode.WALKING,
            2: PostureCode.FALL_RISK,
            3: PostureCode.SITTING,
            4: PostureCode.STANDING,
            5: PostureCode.FALLING,
            6: PostureCode.LYING,
            7: PostureCode.FALL_RISK,  # 疑似坐地
            8: PostureCode.FALLING,    # 确认坐地
            9: PostureCode.LYING,      # 普通床上坐起
            10: PostureCode.FALL_RISK, # 疑似床上坐起
            11: PostureCode.FALLING,   # 确认床上坐起
        }
        
        snomed_code = raw_to_snomed.get(raw_posture)
        if snomed_code is None:
            return None
        
        return self.create_code(snomed_code)
    
    def assess_vital_signs(self, heart_rate: Optional[int] = None, 
                          respiratory_rate: Optional[int] = None) -> Dict[str, any]:
        """
        评估生命体征并返回SNOMED CT编码
        
        Args:
            heart_rate: 心率（bpm）
            respiratory_rate: 呼吸率（次/分钟）
            
        Returns:
            评估结果字典，包含危险等级和SNOMED编码
        """
        result = {
            "danger_level": None,
            "abnormalities": []
        }
        
        # 心率评估（基于TDPv2-0916.md）
        if heart_rate is not None:
            if heart_rate < 44 or heart_rate > 116:
                result["danger_level"] = "L1"  # EMERGENCY
                if heart_rate < 44:
                    result["abnormalities"].append(
                        self.create_code(AbnormalVitalSignsCode.BRADYCARDIA)
                    )
                else:
                    result["abnormalities"].append(
                        self.create_code(AbnormalVitalSignsCode.TACHYCARDIA)
                    )
            elif 45 <= heart_rate <= 54 or 96 <= heart_rate <= 115:
                result["danger_level"] = "L2"  # ALERT
        
        # 呼吸率评估
        if respiratory_rate is not None:
            if respiratory_rate < 5:
                result["danger_level"] = "L1"  # EMERGENCY
                result["abnormalities"].append(
                    self.create_code(AbnormalVitalSignsCode.APNEA)
                )
            elif respiratory_rate > 27:
                result["danger_level"] = "L1"  # EMERGENCY
                result["abnormalities"].append(
                    self.create_code(AbnormalVitalSignsCode.TACHYPNEA)
                )
            elif 8 <= respiratory_rate <= 9 or 24 <= respiratory_rate <= 26:
                if result["danger_level"] != "L1":
                    result["danger_level"] = "L2"  # ALERT
        
        return result


# 全局单例
_snomed_service = None

def get_snomed_service() -> SnomedService:
    """获取SNOMED服务单例"""
    global _snomed_service
    if _snomed_service is None:
        _snomed_service = SnomedService()
    return _snomed_service
