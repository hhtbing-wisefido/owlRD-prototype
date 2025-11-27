"""
健康基线服务
为每个住户建立个性化健康基线，用于异常检测和趋势分析
"""

from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from app.services.storage import StorageService
from app.services.snomed_service import get_snomed_service


class BaselineService:
    """健康基线服务"""
    
    def __init__(self):
        """初始化健康基线服务"""
        self.iot_storage = StorageService(collection="iot_timeseries")
        self.resident_storage = StorageService(collection="residents")
        self.baseline_storage = StorageService(collection="health_baselines")
        self.snomed_service = get_snomed_service()
    
    def establish_baseline(self, resident_id: UUID, 
                          observation_days: int = 14) -> Dict[str, Any]:
        """
        为住户建立健康基线
        
        Args:
            resident_id: 住户ID
            observation_days: 观察天数（默认14天）
            
        Returns:
            健康基线数据
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=observation_days)
        
        # 查询住户信息
        resident = self.resident_storage.find_by_id("resident_id", resident_id)
        if not resident:
            raise ValueError(f"Resident {resident_id} not found")
        
        # 收集IoT时序数据
        iot_data = self.iot_storage.find_all(
            lambda record: (
                str(record.get("resident_id")) == str(resident_id) and
                start_time <= datetime.fromisoformat(record.get("timestamp", "")) <= end_time
            )
        )
        
        # 建立各项基线
        baseline = {
            "baseline_id": str(UUID.uuid4()),
            "resident_id": str(resident_id),
            "tenant_id": resident.get("tenant_id"),
            "observation_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "days": observation_days
            },
            "vital_signs_baseline": self._calculate_vital_signs_baseline(iot_data),
            "activity_baseline": self._calculate_activity_baseline(iot_data),
            "sleep_baseline": self._calculate_sleep_baseline(iot_data),
            "posture_baseline": self._calculate_posture_baseline(iot_data),
            "location_baseline": self._calculate_location_baseline(iot_data),
            "behavioral_patterns": self._identify_behavioral_patterns(iot_data),
            "anomaly_thresholds": self._calculate_anomaly_thresholds(iot_data),
            "confidence_score": 0.0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        # 计算置信度
        baseline["confidence_score"] = self._calculate_confidence_score(
            iot_data, observation_days
        )
        
        # 保存基线
        self.baseline_storage.create(baseline)
        
        return baseline
    
    def _calculate_vital_signs_baseline(self, iot_data: List[Dict]) -> Dict[str, Any]:
        """
        计算生命体征基线
        
        包括心率、呼吸率的平均值、标准差、正常范围
        """
        heart_rates = []
        respiratory_rates = []
        
        for record in iot_data:
            if record.get("heart_rate"):
                heart_rates.append(record["heart_rate"])
            if record.get("respiratory_rate"):
                respiratory_rates.append(record["respiratory_rate"])
        
        baseline = {
            "heart_rate": {
                "mean": statistics.mean(heart_rates) if heart_rates else 0,
                "std": statistics.stdev(heart_rates) if len(heart_rates) > 1 else 0,
                "min": min(heart_rates) if heart_rates else 0,
                "max": max(heart_rates) if heart_rates else 0,
                "normal_range": {
                    "lower": 0,
                    "upper": 0
                },
                "sample_count": len(heart_rates)
            },
            "respiratory_rate": {
                "mean": statistics.mean(respiratory_rates) if respiratory_rates else 0,
                "std": statistics.stdev(respiratory_rates) if len(respiratory_rates) > 1 else 0,
                "min": min(respiratory_rates) if respiratory_rates else 0,
                "max": max(respiratory_rates) if respiratory_rates else 0,
                "normal_range": {
                    "lower": 0,
                    "upper": 0
                },
                "sample_count": len(respiratory_rates)
            }
        }
        
        # 计算正常范围（均值 ± 2倍标准差）
        if heart_rates:
            mean_hr = baseline["heart_rate"]["mean"]
            std_hr = baseline["heart_rate"]["std"]
            baseline["heart_rate"]["normal_range"]["lower"] = max(40, mean_hr - 2 * std_hr)
            baseline["heart_rate"]["normal_range"]["upper"] = min(120, mean_hr + 2 * std_hr)
        
        if respiratory_rates:
            mean_rr = baseline["respiratory_rate"]["mean"]
            std_rr = baseline["respiratory_rate"]["std"]
            baseline["respiratory_rate"]["normal_range"]["lower"] = max(8, mean_rr - 2 * std_rr)
            baseline["respiratory_rate"]["normal_range"]["upper"] = min(30, mean_rr + 2 * std_rr)
        
        return baseline
    
    def _calculate_activity_baseline(self, iot_data: List[Dict]) -> Dict[str, Any]:
        """
        计算活动基线
        
        包括日常活动量、活跃时段、步数等
        """
        # 按日期分组统计活动
        daily_activities = defaultdict(list)
        
        for record in iot_data:
            timestamp = datetime.fromisoformat(record.get("timestamp", ""))
            date_key = timestamp.date().isoformat()
            
            # 统计活动类型
            if record.get("posture_snomed_code") == "249904006":  # Walking
                daily_activities[date_key].append("walking")
            elif record.get("posture_snomed_code") == "255324009":  # Moving
                daily_activities[date_key].append("moving")
        
        # 计算每日平均活动次数
        daily_counts = [len(acts) for acts in daily_activities.values()]
        
        baseline = {
            "avg_daily_activities": statistics.mean(daily_counts) if daily_counts else 0,
            "std_daily_activities": statistics.stdev(daily_counts) if len(daily_counts) > 1 else 0,
            "min_daily_activities": min(daily_counts) if daily_counts else 0,
            "max_daily_activities": max(daily_counts) if daily_counts else 0,
            "peak_activity_hours": self._identify_peak_hours(iot_data),
            "low_activity_hours": self._identify_low_hours(iot_data),
            "activity_pattern": "regular"  # regular, irregular, variable
        }
        
        return baseline
    
    def _calculate_sleep_baseline(self, iot_data: List[Dict]) -> Dict[str, Any]:
        """
        计算睡眠基线
        
        包括睡眠时长、入睡时间、起床时间、睡眠质量等
        """
        # 识别睡眠周期 - 分析连续的睡眠状态
        sleep_periods = []
        bedtimes = []
        wake_times = []
        
        # 按日期分组，分析每天的睡眠模式
        daily_sleep = defaultdict(list)
        for record in iot_data:
            timestamp = datetime.fromisoformat(record.get("timestamp", ""))
            date_key = timestamp.date().isoformat()
            sleep_state = record.get("sleep_state_snomed_code")
            
            if sleep_state:  # 有睡眠状态数据
                daily_sleep[date_key].append({
                    "timestamp": timestamp,
                    "sleep_state": sleep_state
                })
        
        # 分析每天的睡眠周期
        for date_key, records in daily_sleep.items():
            if not records:
                continue
                
            # 按时间排序
            records.sort(key=lambda x: x["timestamp"])
            
            # 查找入睡时间（第一个进入睡眠状态的时间）
            for record in records:
                if record["sleep_state"] in ["258158006", "60984000"]:  # Light sleep or Deep sleep
                    bedtimes.append(record["timestamp"].time())
                    break
            
            # 查找起床时间（最后一个离开睡眠状态的时间）
            for record in reversed(records):
                if record["sleep_state"] == "248218005":  # Awake
                    wake_times.append(record["timestamp"].time())
                    break
            
            # 计算睡眠时长
            sleep_start = None
            sleep_end = None
            for record in records:
                if sleep_start is None and record["sleep_state"] in ["258158006", "60984000"]:
                    sleep_start = record["timestamp"]
                if sleep_start and record["sleep_state"] == "248218005":
                    sleep_end = record["timestamp"]
            
            if sleep_start and sleep_end:
                duration = (sleep_end - sleep_start).total_seconds() / 3600
                sleep_periods.append(duration)
        
        # 计算平均值
        avg_bedtime_seconds = 0
        if bedtimes:
            bedtime_seconds = [t.hour * 3600 + t.minute * 60 + t.second for t in bedtimes]
            avg_bedtime_seconds = statistics.mean(bedtime_seconds)
            avg_bedtime_hour = int(avg_bedtime_seconds // 3600)
            avg_bedtime_minute = int((avg_bedtime_seconds % 3600) // 60)
            avg_bedtime_str = f"{avg_bedtime_hour:02d}:{avg_bedtime_minute:02d}:00"
        else:
            avg_bedtime_str = "22:30:00"
        
        avg_wake_time_seconds = 0
        if wake_times:
            wake_time_seconds = [t.hour * 3600 + t.minute * 60 + t.second for t in wake_times]
            avg_wake_time_seconds = statistics.mean(wake_time_seconds)
            avg_wake_hour = int(avg_wake_time_seconds // 3600)
            avg_wake_minute = int((avg_wake_time_seconds % 3600) // 60)
            avg_wake_time_str = f"{avg_wake_hour:02d}:{avg_wake_minute:02d}:00"
        else:
            avg_wake_time_str = "06:00:00"
        
        baseline = {
            "avg_sleep_duration_hours": statistics.mean(sleep_periods) if sleep_periods else 7.5,
            "std_sleep_duration": statistics.stdev(sleep_periods) if len(sleep_periods) > 1 else 0.5,
            "avg_bedtime": avg_bedtime_str,
            "std_bedtime_minutes": statistics.stdev([t.hour * 60 + t.minute for t in bedtimes]) if len(bedtimes) > 1 else 30,
            "avg_wake_time": avg_wake_time_str,
            "std_wake_time_minutes": statistics.stdev([t.hour * 60 + t.minute for t in wake_times]) if len(wake_times) > 1 else 30,
            "sleep_efficiency": self._calculate_sleep_efficiency(iot_data),
            "sleep_quality_score": self._calculate_sleep_quality_score(sleep_periods, iot_data),
            "night_awakenings_avg": self._calculate_night_awakenings(iot_data),
            "sleep_pattern": self._determine_sleep_pattern(bedtimes, wake_times)
        }
        
        return baseline
    
    def _calculate_posture_baseline(self, iot_data: List[Dict]) -> Dict[str, Any]:
        """
        计算姿态分布基线
        
        统计各种姿态的时间占比
        """
        posture_counts = defaultdict(int)
        total_records = len(iot_data)
        
        for record in iot_data:
            posture_code = record.get("posture_snomed_code")
            if posture_code:
                posture_counts[posture_code] += 1
        
        # 计算占比
        posture_distribution = {}
        for code, count in posture_counts.items():
            display = self.snomed_service.get_display_name(code)
            posture_distribution[display] = {
                "code": code,
                "count": count,
                "percentage": (count / total_records * 100) if total_records > 0 else 0
            }
        
        baseline = {
            "distribution": posture_distribution,
            "dominant_posture": max(posture_counts, key=posture_counts.get) if posture_counts else None,
            "posture_variety_score": len(posture_counts),
            "total_samples": total_records
        }
        
        return baseline
    
    def _calculate_location_baseline(self, iot_data: List[Dict]) -> Dict[str, Any]:
        """
        计算位置活动基线
        
        统计住户在各个位置的时间分布
        """
        location_time = defaultdict(int)
        
        for record in iot_data:
            location_id = record.get("location_id")
            if location_id:
                location_time[location_id] += 1
        
        total_records = len(iot_data)
        
        location_distribution = {}
        for loc_id, count in location_time.items():
            location_distribution[loc_id] = {
                "time_count": count,
                "percentage": (count / total_records * 100) if total_records > 0 else 0
            }
        
        baseline = {
            "primary_location": max(location_time, key=location_time.get) if location_time else None,
            "location_distribution": location_distribution,
            "location_variety": len(location_time),
            "mobility_score": len(location_time) / 10 * 100  # 简化计算
        }
        
        return baseline
    
    def _calculate_sleep_efficiency(self, iot_data: List[Dict]) -> float:
        """计算睡眠效率（实际睡眠时间/在床时间）"""
        total_in_bed_time = 0
        total_sleep_time = 0
        
        for record in iot_data:
            sleep_state = record.get("sleep_state_snomed_code")
            if sleep_state in ["258158006", "60984000"]:  # Light/Deep sleep
                total_sleep_time += 1
                total_in_bed_time += 1
            elif sleep_state == "248218005":  # Awake in bed
                total_in_bed_time += 1
        
        if total_in_bed_time == 0:
            return 0.85  # 默认值
        
        efficiency = total_sleep_time / total_in_bed_time
        return round(efficiency, 2)
    
    def _calculate_sleep_quality_score(self, sleep_periods: List[float], 
                                       iot_data: List[Dict]) -> float:
        """计算睡眠质量评分（0-100）"""
        if not sleep_periods:
            return 80.0  # 默认值
        
        # 因素1: 睡眠时长（40分）
        avg_duration = statistics.mean(sleep_periods)
        if 7 <= avg_duration <= 9:
            duration_score = 40
        elif 6 <= avg_duration < 7 or 9 < avg_duration <= 10:
            duration_score = 35
        elif 5 <= avg_duration < 6 or 10 < avg_duration <= 11:
            duration_score = 30
        else:
            duration_score = 20
        
        # 因素2: 睡眠一致性（30分）
        if len(sleep_periods) > 1:
            std_duration = statistics.stdev(sleep_periods)
            if std_duration < 0.5:
                consistency_score = 30
            elif std_duration < 1.0:
                consistency_score = 25
            elif std_duration < 1.5:
                consistency_score = 20
            else:
                consistency_score = 15
        else:
            consistency_score = 25
        
        # 因素3: 睡眠效率（30分）
        efficiency = self._calculate_sleep_efficiency(iot_data)
        efficiency_score = efficiency * 30
        
        total_score = duration_score + consistency_score + efficiency_score
        return round(total_score, 1)
    
    def _calculate_night_awakenings(self, iot_data: List[Dict]) -> float:
        """计算平均夜间觉醒次数"""
        daily_awakenings = defaultdict(int)
        
        for record in iot_data:
            timestamp = datetime.fromisoformat(record.get("timestamp", ""))
            # 夜间时段：22:00-06:00
            if timestamp.hour >= 22 or timestamp.hour < 6:
                sleep_state = record.get("sleep_state_snomed_code")
                if sleep_state == "248218005":  # Awake
                    date_key = timestamp.date().isoformat()
                    daily_awakenings[date_key] += 1
        
        if daily_awakenings:
            return statistics.mean(daily_awakenings.values())
        return 2.0  # 默认值
    
    def _determine_sleep_pattern(self, bedtimes: List, wake_times: List) -> str:
        """判断睡眠模式类型"""
        if not bedtimes or not wake_times:
            return "insufficient_data"
        
        # 计算入睡时间和起床时间的标准差
        bedtime_minutes = [t.hour * 60 + t.minute for t in bedtimes]
        waketime_minutes = [t.hour * 60 + t.minute for t in wake_times]
        
        if len(bedtime_minutes) > 1 and len(waketime_minutes) > 1:
            bedtime_std = statistics.stdev(bedtime_minutes)
            waketime_std = statistics.stdev(waketime_minutes)
            
            # 标准差小于30分钟为一致，30-60为可变，>60为不规律
            if bedtime_std < 30 and waketime_std < 30:
                return "consistent"
            elif bedtime_std < 60 and waketime_std < 60:
                return "variable"
            else:
                return "irregular"
        
        return "consistent"
    
    def _identify_behavioral_patterns(self, iot_data: List[Dict]) -> Dict[str, Any]:
        """
        识别行为模式
        
        包括规律性、习惯性活动、异常行为等
        """
        # 按时间段分析活动模式
        morning_activities = []  # 06:00-12:00
        afternoon_activities = []  # 12:00-18:00
        evening_activities = []  # 18:00-22:00
        night_activities = []  # 22:00-06:00
        
        for record in iot_data:
            timestamp = datetime.fromisoformat(record.get("timestamp", ""))
            hour = timestamp.hour
            posture = record.get("posture_snomed_code")
            
            if 6 <= hour < 12:
                morning_activities.append(posture)
            elif 12 <= hour < 18:
                afternoon_activities.append(posture)
            elif 18 <= hour < 22:
                evening_activities.append(posture)
            else:
                night_activities.append(posture)
        
        # 分析每个时段的主要活动
        def get_main_activity(activities):
            if not activities:
                return None
            counter = defaultdict(int)
            for activity in activities:
                if activity:
                    counter[activity] += 1
            if counter:
                return max(counter.items(), key=lambda x: x[1])[0]
            return None
        
        # 计算规律性评分
        # 基于活动时段的一致性
        time_segments = [morning_activities, afternoon_activities, 
                        evening_activities, night_activities]
        segment_consistency = []
        for segment in time_segments:
            if segment:
                main_activity = get_main_activity(segment)
                if main_activity:
                    consistency = segment.count(main_activity) / len(segment)
                    segment_consistency.append(consistency)
        
        regularity_score = 0.0
        if segment_consistency:
            regularity_score = statistics.mean(segment_consistency) * 100
        
        patterns = {
            "regularity_score": round(regularity_score, 1),
            "habit_activities": [],
            "time_based_patterns": {
                "morning_routine": {"main_activity": get_main_activity(morning_activities)},
                "afternoon_routine": {"main_activity": get_main_activity(afternoon_activities)},
                "evening_routine": {"main_activity": get_main_activity(evening_activities)},
                "night_routine": {"main_activity": get_main_activity(night_activities)}
            },
            "weekly_patterns": {},
            "identified_habits": self._identify_habits(iot_data)
        }
        
        return patterns
    
    def _identify_habits(self, iot_data: List[Dict]) -> List[str]:
        """识别习惯性行为"""
        habits = []
        
        # 分析是否有固定的活动模式
        hourly_activities = defaultdict(list)
        for record in iot_data:
            timestamp = datetime.fromisoformat(record.get("timestamp", ""))
            hour = timestamp.hour
            posture = record.get("posture_snomed_code")
            if posture:
                hourly_activities[hour].append(posture)
        
        # 查找高频率固定时间活动
        for hour, activities in hourly_activities.items():
            if len(activities) >= 5:  # 至少出现5次
                main_activity = max(set(activities), key=activities.count)
                frequency = activities.count(main_activity) / len(activities)
                if frequency >= 0.7:  # 70%以上的一致性
                    habit_desc = f"每天{hour:02d}:00左右 - {main_activity}"
                    habits.append(habit_desc)
        
        return habits
    
    def _calculate_anomaly_thresholds(self, iot_data: List[Dict]) -> Dict[str, Any]:
        """
        计算异常检测阈值
        
        为各项指标设定异常检测的阈值
        """
        thresholds = {
            "heart_rate": {
                "critical_low": 40,
                "warning_low": 50,
                "warning_high": 100,
                "critical_high": 120
            },
            "respiratory_rate": {
                "critical_low": 8,
                "warning_low": 10,
                "warning_high": 24,
                "critical_high": 30
            },
            "activity_level": {
                "no_activity_hours": 24,
                "low_activity_threshold": 0.3,
                "high_activity_threshold": 2.0
            },
            "sleep_quality": {
                "min_duration_hours": 4,
                "max_duration_hours": 12,
                "max_awakenings": 5
            },
            "location_change": {
                "prolonged_stay_hours": 24,
                "unusual_location_threshold": 0.05
            }
        }
        
        return thresholds
    
    def _identify_peak_hours(self, iot_data: List[Dict]) -> List[int]:
        """识别活动高峰时段（小时）"""
        hour_counts = defaultdict(int)
        
        for record in iot_data:
            timestamp = datetime.fromisoformat(record.get("timestamp", ""))
            hour_counts[timestamp.hour] += 1
        
        # 返回活动量前3的小时
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, _ in sorted_hours[:3]]
    
    def _identify_low_hours(self, iot_data: List[Dict]) -> List[int]:
        """识别活动低谷时段（小时）"""
        hour_counts = defaultdict(int)
        
        for record in iot_data:
            timestamp = datetime.fromisoformat(record.get("timestamp", ""))
            hour_counts[timestamp.hour] += 1
        
        # 返回活动量最少的3个小时
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1])
        return [hour for hour, _ in sorted_hours[:3]]
    
    def _calculate_confidence_score(self, iot_data: List[Dict], 
                                    observation_days: int) -> float:
        """
        计算基线置信度
        
        基于数据完整性、样本量、一致性等因素
        """
        if not iot_data:
            return 0.0
        
        # 数据完整性评分（40分）
        completeness_score = min(40, len(iot_data) / (observation_days * 100) * 40)
        
        # 观察时长评分（30分）
        duration_score = min(30, observation_days / 14 * 30)
        
        # 数据一致性评分（30分）
        # 基于数据间隔的一致性
        if len(iot_data) > 1:
            timestamps = [datetime.fromisoformat(r.get("timestamp", "")) for r in iot_data]
            timestamps.sort()
            intervals = [(timestamps[i+1] - timestamps[i]).total_seconds() 
                        for i in range(len(timestamps)-1)]
            if intervals:
                avg_interval = statistics.mean(intervals)
                std_interval = statistics.stdev(intervals) if len(intervals) > 1 else 0
                # 间隔越稳定，一致性越高
                consistency_ratio = 1 - min(std_interval / max(avg_interval, 1), 1)
                consistency_score = consistency_ratio * 30
            else:
                consistency_score = 20
        else:
            consistency_score = 20
        
        total_score = completeness_score + duration_score + consistency_score
        return round(total_score, 2)
    
    def detect_anomalies(self, resident_id: UUID, 
                        current_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        基于基线检测异常
        
        Args:
            resident_id: 住户ID
            current_data: 当前数据
            
        Returns:
            异常检测结果
        """
        # 获取住户基线
        baseline = self.baseline_storage.find_by_id("resident_id", resident_id)
        if not baseline:
            return {
                "status": "no_baseline",
                "message": "No baseline established for this resident"
            }
        
        anomalies = {
            "resident_id": str(resident_id),
            "detection_time": datetime.utcnow().isoformat(),
            "baseline_id": baseline.get("baseline_id"),
            "detected_anomalies": [],
            "overall_risk_level": "normal"
        }
        
        # 检测生命体征异常
        vital_anomalies = self._detect_vital_signs_anomalies(
            current_data, baseline.get("vital_signs_baseline", {})
        )
        anomalies["detected_anomalies"].extend(vital_anomalies)
        
        # 检测活动异常
        activity_anomalies = self._detect_activity_anomalies(
            current_data, baseline.get("activity_baseline", {})
        )
        anomalies["detected_anomalies"].extend(activity_anomalies)
        
        # 检测睡眠异常
        sleep_anomalies = self._detect_sleep_anomalies(
            current_data, baseline.get("sleep_baseline", {})
        )
        anomalies["detected_anomalies"].extend(sleep_anomalies)
        
        # 确定总体风险等级
        if anomalies["detected_anomalies"]:
            critical_count = sum(1 for a in anomalies["detected_anomalies"] 
                               if a.get("severity") == "critical")
            if critical_count > 0:
                anomalies["overall_risk_level"] = "critical"
            else:
                anomalies["overall_risk_level"] = "warning"
        
        return anomalies
    
    def _detect_vital_signs_anomalies(self, current: Dict, baseline: Dict) -> List[Dict]:
        """检测生命体征异常"""
        anomalies = []
        
        # 心率异常
        if "heart_rate" in current and "heart_rate" in baseline:
            hr = current["heart_rate"]
            hr_baseline = baseline["heart_rate"]
            normal_range = hr_baseline.get("normal_range", {})
            
            if hr < normal_range.get("lower", 0):
                anomalies.append({
                    "type": "vital_signs",
                    "metric": "heart_rate",
                    "value": hr,
                    "baseline_range": normal_range,
                    "deviation": "below_normal",
                    "severity": "critical" if hr < 40 else "warning"
                })
            elif hr > normal_range.get("upper", 999):
                anomalies.append({
                    "type": "vital_signs",
                    "metric": "heart_rate",
                    "value": hr,
                    "baseline_range": normal_range,
                    "deviation": "above_normal",
                    "severity": "critical" if hr > 120 else "warning"
                })
        
        # 呼吸率异常
        if "respiratory_rate" in current and "respiratory_rate" in baseline:
            rr = current["respiratory_rate"]
            rr_baseline = baseline["respiratory_rate"]
            normal_range = rr_baseline.get("normal_range", {})
            
            if rr < normal_range.get("lower", 0):
                anomalies.append({
                    "type": "vital_signs",
                    "metric": "respiratory_rate",
                    "value": rr,
                    "baseline_range": normal_range,
                    "deviation": "below_normal",
                    "severity": "critical" if rr < 8 else "warning"
                })
            elif rr > normal_range.get("upper", 999):
                anomalies.append({
                    "type": "vital_signs",
                    "metric": "respiratory_rate",
                    "value": rr,
                    "baseline_range": normal_range,
                    "deviation": "above_normal",
                    "severity": "critical" if rr > 30 else "warning"
                })
        
        return anomalies
    
    def _detect_activity_anomalies(self, current: Dict, baseline: Dict) -> List[Dict]:
        """检测活动异常"""
        anomalies = []
        
        if "activity_level" in current and "activity_baseline" in baseline:
            current_activity = current["activity_level"]
            baseline_activity = baseline["activity_baseline"]
            
            avg_activity = baseline_activity.get("avg_daily_activities", 0)
            std_activity = baseline_activity.get("std_daily_activities", 0)
            
            # 活动量过低
            if avg_activity > 0 and current_activity < avg_activity - 2 * std_activity:
                anomalies.append({
                    "type": "activity",
                    "metric": "daily_activity",
                    "value": current_activity,
                    "baseline_avg": avg_activity,
                    "deviation": "below_normal",
                    "severity": "warning"
                })
            
            # 活动量过高（可能异常兴奋或躁动）
            if avg_activity > 0 and current_activity > avg_activity + 3 * std_activity:
                anomalies.append({
                    "type": "activity",
                    "metric": "daily_activity",
                    "value": current_activity,
                    "baseline_avg": avg_activity,
                    "deviation": "above_normal",
                    "severity": "warning"
                })
        
        return anomalies
    
    def _detect_sleep_anomalies(self, current: Dict, baseline: Dict) -> List[Dict]:
        """检测睡眠异常"""
        anomalies = []
        
        if "sleep_duration" in current and "sleep_baseline" in baseline:
            current_duration = current["sleep_duration"]
            baseline_sleep = baseline["sleep_baseline"]
            
            avg_duration = baseline_sleep.get("avg_sleep_duration_hours", 7.5)
            std_duration = baseline_sleep.get("std_sleep_duration", 0.5)
            
            # 睡眠时长过短
            if current_duration < avg_duration - 2 * std_duration or current_duration < 4:
                anomalies.append({
                    "type": "sleep",
                    "metric": "sleep_duration",
                    "value": current_duration,
                    "baseline_avg": avg_duration,
                    "deviation": "below_normal",
                    "severity": "critical" if current_duration < 4 else "warning"
                })
            
            # 睡眠时长过长
            if current_duration > avg_duration + 2 * std_duration or current_duration > 12:
                anomalies.append({
                    "type": "sleep",
                    "metric": "sleep_duration",
                    "value": current_duration,
                    "baseline_avg": avg_duration,
                    "deviation": "above_normal",
                    "severity": "warning"
                })
        
        # 检测入睡时间异常
        if "bedtime" in current and "sleep_baseline" in baseline:
            baseline_bedtime = baseline["sleep_baseline"].get("avg_bedtime", "22:30:00")
            std_bedtime_minutes = baseline["sleep_baseline"].get("std_bedtime_minutes", 30)
            
            # 将时间转换为分钟进行比较
            current_time = datetime.strptime(current["bedtime"], "%H:%M:%S").time()
            baseline_time = datetime.strptime(baseline_bedtime, "%H:%M:%S").time()
            
            current_minutes = current_time.hour * 60 + current_time.minute
            baseline_minutes = baseline_time.hour * 60 + baseline_time.minute
            
            time_diff = abs(current_minutes - baseline_minutes)
            if time_diff > 2 * std_bedtime_minutes:
                anomalies.append({
                    "type": "sleep",
                    "metric": "bedtime",
                    "value": current["bedtime"],
                    "baseline_avg": baseline_bedtime,
                    "deviation": "irregular",
                    "severity": "info"
                })
        
        return anomalies
    
    def update_baseline(self, resident_id: UUID, 
                       new_observation_days: int = 7) -> Dict[str, Any]:
        """
        更新住户健康基线
        
        Args:
            resident_id: 住户ID
            new_observation_days: 新增观察天数
            
        Returns:
            更新后的基线
        """
        # 查找现有基线
        existing_baseline = self.baseline_storage.find_by_id("resident_id", resident_id)
        
        if not existing_baseline:
            # 如果不存在，建立新基线
            return self.establish_baseline(resident_id, new_observation_days)
        
        # 增量更新基线 - 合并旧数据和新数据
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=new_observation_days)
        
        # 获取新数据
        new_iot_data = self.iot_storage.find_all(
            lambda record: (
                str(record.get("resident_id")) == str(resident_id) and
                start_time <= datetime.fromisoformat(record.get("timestamp", "")) <= end_time
            )
        )
        
        if new_iot_data:
            # 重新计算整个基线（使用最近14天的数据）
            updated_baseline = self.establish_baseline(
                resident_id, 
                observation_days=14  # 保持14天观察窗口
            )
        else:
            # 没有新数据，返回现有基线
            updated_baseline = existing_baseline
        
        return updated_baseline
    
    def get_baseline(self, resident_id: UUID) -> Optional[Dict[str, Any]]:
        """
        获取住户健康基线
        
        Args:
            resident_id: 住户ID
            
        Returns:
            健康基线数据，如果不存在返回None
        """
        return self.baseline_storage.find_by_id("resident_id", resident_id)


# 全局单例
_baseline_service = None

def get_baseline_service() -> BaselineService:
    """获取健康基线服务单例"""
    global _baseline_service
    if _baseline_service is None:
        _baseline_service = BaselineService()
    return _baseline_service
