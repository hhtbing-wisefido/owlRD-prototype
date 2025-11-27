"""
护理质量评估服务 - 基于空间智能的护理质量分析

对齐源参考：
- 17_care_quality_reports.sql - 护理质量报告表
- AI护理.md - AI分析方法和指标
- 评分维度包含告警响应速度和告警处理质量
"""

from typing import Dict, List, Any, Optional, Tuple
from uuid import UUID
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

from app.services.storage import StorageService
from app.services.snomed_service import get_snomed_service


class CareQualityService:
    """护理质量评估服务"""
    
    def __init__(self):
        """初始化护理质量服务"""
        self.iot_storage = StorageService(collection="iot_timeseries")
        self.resident_storage = StorageService(collection="residents")
        self.caregiver_storage = StorageService(collection="resident_caregivers")
        self.location_storage = StorageService(collection="locations")
        self.snomed_service = get_snomed_service()
    
    def analyze_spatial_coverage(self, tenant_id: UUID, 
                                 location_id: Optional[UUID] = None,
                                 time_range_hours: int = 24) -> Dict[str, Any]:
        """
        空间覆盖分析
        分析护理人员在各个区域的巡视覆盖情况
        
        Args:
            tenant_id: 租户ID
            location_id: 位置ID（可选，不指定则分析所有位置）
            time_range_hours: 时间范围（小时）
            
        Returns:
            空间覆盖分析报告
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        # 获取所有位置
        locations = self.location_storage.find_all(
            lambda l: str(l.get("tenant_id")) == str(tenant_id)
        )
        
        if location_id:
            locations = [l for l in locations if str(l.get("location_id")) == str(location_id)]
        
        coverage_report = {
            "tenant_id": str(tenant_id),
            "analysis_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": time_range_hours
            },
            "locations": [],
            "summary": {
                "total_locations": len(locations),
                "covered_locations": 0,
                "coverage_rate": 0.0,
                "avg_visit_frequency": 0.0,
                "high_risk_areas": []
            }
        }
        
        covered_count = 0
        total_visits = 0
        
        for location in locations:
            location_analysis = self._analyze_location_coverage(
                location, start_time, end_time
            )
            
            coverage_report["locations"].append(location_analysis)
            
            if location_analysis["visit_count"] > 0:
                covered_count += 1
            
            total_visits += location_analysis["visit_count"]
            
            # 识别高风险区域（24小时内未巡视）
            if location_analysis["hours_since_last_visit"] > 24:
                coverage_report["summary"]["high_risk_areas"].append({
                    "location_id": location_analysis["location_id"],
                    "location_name": location_analysis["location_name"],
                    "hours_since_last_visit": location_analysis["hours_since_last_visit"]
                })
        
        # 计算汇总指标
        coverage_report["summary"]["covered_locations"] = covered_count
        coverage_report["summary"]["coverage_rate"] = (
            covered_count / len(locations) * 100 if locations else 0
        )
        coverage_report["summary"]["avg_visit_frequency"] = (
            total_visits / len(locations) if locations else 0
        )
        
        return coverage_report
    
    def _analyze_location_coverage(self, location: Dict[str, Any],
                                   start_time: datetime,
                                   end_time: datetime) -> Dict[str, Any]:
        """分析单个位置的覆盖情况"""
        location_id = location.get("location_id")
        
        # 查询该位置的IoT数据（代表有人员活动）
        location_iot_data = self.iot_storage.find_all(
            lambda record: (
                str(record.get("location_id")) == str(location_id) and
                start_time <= datetime.fromisoformat(record.get("timestamp", "")) <= end_time
            )
        )
        
        visit_count = len(location_iot_data)
        last_visit_time = None
        if location_iot_data:
            # 找到最近一次访问时间
            latest_record = max(location_iot_data, 
                              key=lambda r: datetime.fromisoformat(r.get("timestamp", "")))
            last_visit_time = latest_record.get("timestamp")
        
        analysis = {
            "location_id": str(location_id),
            "location_name": location.get("location_name", "Unknown"),
            "location_type": location.get("location_type", "Unknown"),
            "visit_count": visit_count,
            "last_visit_time": last_visit_time.isoformat() if last_visit_time else None,
            "hours_since_last_visit": None,
            "risk_level": "normal"
        }
        
        if last_visit_time:
            hours_since = (datetime.utcnow() - last_visit_time).total_seconds() / 3600
            analysis["hours_since_last_visit"] = round(hours_since, 2)
            
            # 风险等级判定
            if hours_since > 24:
                analysis["risk_level"] = "high"
            elif hours_since > 12:
                analysis["risk_level"] = "medium"
        else:
            analysis["hours_since_last_visit"] = float('inf')
            analysis["risk_level"] = "high"
        
        return analysis
    
    def generate_team_report(self, tenant_id: UUID, 
                           team_tag: Optional[str] = None,
                           time_range_hours: int = 24) -> Dict[str, Any]:
        """
        生成团队护理质量报告
        
        Args:
            tenant_id: 租户ID
            team_tag: 团队标签（可选）
            time_range_hours: 时间范围（小时）
            
        Returns:
            团队护理质量报告
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=time_range_hours)
        
        # 获取所有住户
        residents = self.resident_storage.find_all(
            lambda r: str(r.get("tenant_id")) == str(tenant_id) and r.get("status") == "active"
        )
        
        report = {
            "tenant_id": str(tenant_id),
            "team_tag": team_tag,
            "report_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": time_range_hours
            },
            "metrics": {
                "total_residents": len(residents),
                "residents_monitored": 0,
                "monitoring_rate": 0.0,
                "total_alerts": 0,
                "critical_alerts": 0,
                "fall_events": 0,
                "vital_sign_alerts": 0,
                "avg_response_time_minutes": 0.0
            },
            "quality_score": {
                "overall": 0.0,
                "monitoring_coverage": 0.0,
                "response_time": 0.0,
                "alert_handling": 0.0
            },
            "recommendations": []
        }
        
        # 分析每个住户的护理质量
        monitored_count = 0
        total_alerts = 0
        critical_alerts = 0
        fall_events = 0
        vital_alerts = 0
        
        for resident in residents:
            resident_analysis = self._analyze_resident_care(
                resident, start_time, end_time
            )
            
            if resident_analysis["monitored"]:
                monitored_count += 1
            
            total_alerts += resident_analysis["alert_count"]
            critical_alerts += resident_analysis["critical_alert_count"]
            fall_events += resident_analysis["fall_count"]
            vital_alerts += resident_analysis["vital_alert_count"]
        
        # 更新指标
        report["metrics"]["residents_monitored"] = monitored_count
        report["metrics"]["monitoring_rate"] = (
            monitored_count / len(residents) * 100 if residents else 0
        )
        report["metrics"]["total_alerts"] = total_alerts
        report["metrics"]["critical_alerts"] = critical_alerts
        report["metrics"]["fall_events"] = fall_events
        report["metrics"]["vital_sign_alerts"] = vital_alerts
        
        # 计算质量评分
        report["quality_score"] = self._calculate_quality_score(report["metrics"])
        
        # 生成建议
        report["recommendations"] = self._generate_recommendations(report)
        
        return report
    
    def _analyze_resident_care(self, resident: Dict[str, Any],
                               start_time: datetime,
                               end_time: datetime) -> Dict[str, Any]:
        """分析单个住户的护理质量"""
        resident_id = resident.get("resident_id")
        
        analysis = {
            "resident_id": str(resident_id),
            "monitored": False,
            "alert_count": 0,
            "critical_alert_count": 0,
            "fall_count": 0,
            "vital_alert_count": 0,
            "avg_response_time": 0.0
        }
        
        # 查询团队相关的IoT数据和告警记录
        # 获取团队成员
        team_members = self.caregiver_storage.find_all(
            lambda cg: team_tag in str(cg.get("nurse_group_tags", []))
        )
        
        team_resident_ids = set()
        for member in team_members:
            resident_id = member.get("resident_id")
            if resident_id:
                team_resident_ids.add(str(resident_id))
        
        if team_resident_ids:
            # 查询这些住户的IoT数据
            team_iot_data = self.iot_storage.find_all(
                lambda record: (
                    str(record.get("resident_id")) in team_resident_ids and
                    start_time <= datetime.fromisoformat(record.get("timestamp", "")) <= end_time
                )
            )
            
            # 计算实际指标
            analysis["total_events"] = len(team_iot_data)
            
            # 计算告警处理情况
            alert_events = [r for r in team_iot_data if r.get("alert_triggered")]
            analysis["alert_count"] = len(alert_events)
            if team_iot_data:
                analysis["alert_rate"] = len(alert_events) / len(team_iot_data)
            
            # 计算响应时间（简化：基于数据时间戳间隔）
            if alert_events:
                response_times = []
                for alert in alert_events:
                    alert_time = datetime.fromisoformat(alert.get("timestamp", ""))
                    # 查找该告警后的第一次记录作为响应
                    responses = [r for r in team_iot_data 
                               if datetime.fromisoformat(r.get("timestamp", "")) > alert_time]
                    if responses:
                        first_response = min(responses, 
                                           key=lambda r: datetime.fromisoformat(r.get("timestamp", "")))
                        response_time = (datetime.fromisoformat(first_response.get("timestamp", "")) - alert_time).total_seconds() / 60
                        response_times.append(response_time)
                
                if response_times:
                    analysis["avg_response_time"] = statistics.mean(response_times)
        
        return analysis
    
    def _calculate_quality_score(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """
        计算护理质量评分
        
        评分维度：
        - 监控覆盖率（40分）
        - 响应时间（30分）
        - 告警处理（30分）
        """
        scores = {
            "overall": 0.0,
            "monitoring_coverage": 0.0,
            "response_time": 0.0,
            "alert_handling": 0.0
        }
        
        # 监控覆盖率评分（0-40分）
        monitoring_rate = metrics.get("monitoring_rate", 0)
        if monitoring_rate >= 95:
            scores["monitoring_coverage"] = 40.0
        elif monitoring_rate >= 90:
            scores["monitoring_coverage"] = 35.0
        elif monitoring_rate >= 80:
            scores["monitoring_coverage"] = 30.0
        elif monitoring_rate >= 70:
            scores["monitoring_coverage"] = 25.0
        else:
            scores["monitoring_coverage"] = monitoring_rate / 70 * 25
        
        # 响应时间评分（0-30分）
        avg_response = metrics.get("avg_response_time_minutes", 0)
        if avg_response <= 2:
            scores["response_time"] = 30.0
        elif avg_response <= 5:
            scores["response_time"] = 25.0
        elif avg_response <= 10:
            scores["response_time"] = 20.0
        elif avg_response <= 15:
            scores["response_time"] = 15.0
        else:
            scores["response_time"] = max(0, 30 - avg_response)
        
        # 告警处理评分（0-30分）
        total_alerts = metrics.get("total_alerts", 0)
        critical_alerts = metrics.get("critical_alerts", 0)
        
        if total_alerts > 0:
            # 基于危重告警比例
            critical_ratio = critical_alerts / total_alerts
            if critical_ratio <= 0.05:  # ≤5%危重告警
                scores["alert_handling"] = 30.0
            elif critical_ratio <= 0.10:
                scores["alert_handling"] = 25.0
            elif critical_ratio <= 0.15:
                scores["alert_handling"] = 20.0
            else:
                scores["alert_handling"] = max(0, 30 - critical_ratio * 100)
        else:
            scores["alert_handling"] = 30.0  # 无告警视为良好
        
        # 总分
        scores["overall"] = sum([
            scores["monitoring_coverage"],
            scores["response_time"],
            scores["alert_handling"]
        ])
        
        return scores
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """生成护理改进建议"""
        recommendations = []
        
        metrics = report["metrics"]
        quality = report["quality_score"]
        
        # 监控覆盖率建议
        if metrics["monitoring_rate"] < 90:
            recommendations.append(
                f"监控覆盖率仅{metrics['monitoring_rate']:.1f}%，"
                f"建议加强对未监控住户的关注"
            )
        
        # 告警处理建议
        if metrics["critical_alerts"] > 0:
            recommendations.append(
                f"发现{metrics['critical_alerts']}个危重告警，"
                f"需要重点关注高风险住户"
            )
        
        # 跌倒事件建议
        if metrics["fall_events"] > 0:
            recommendations.append(
                f"发生{metrics['fall_events']}起跌倒事件，"
                f"建议加强跌倒预防措施"
            )
        
        # 响应时间建议
        if metrics["avg_response_time_minutes"] > 10:
            recommendations.append(
                f"平均响应时间{metrics['avg_response_time_minutes']:.1f}分钟，"
                f"建议优化响应流程"
            )
        
        # 整体质量建议
        if quality["overall"] < 70:
            recommendations.append(
                f"整体质量评分{quality['overall']:.1f}分，"
                f"需要全面提升护理质量"
            )
        elif quality["overall"] >= 90:
            recommendations.append(
                f"整体质量评分{quality['overall']:.1f}分，"
                f"护理质量优秀，请继续保持"
            )
        
        if not recommendations:
            recommendations.append("护理质量良好，继续保持当前标准")
        
        return recommendations
    
    def analyze_resident_behavior_pattern(self, resident_id: UUID,
                                         days: int = 7) -> Dict[str, Any]:
        """
        分析住户行为模式
        
        Args:
            resident_id: 住户ID
            days: 分析天数
            
        Returns:
            行为模式分析报告
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        pattern = {
            "resident_id": str(resident_id),
            "analysis_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "days": days
            },
            "activity_pattern": {
                "avg_daily_steps": 0,
                "avg_active_hours": 0.0,
                "peak_activity_hours": [],
                "low_activity_hours": []
            },
            "sleep_pattern": {
                "avg_sleep_duration_hours": 0.0,
                "avg_bedtime": None,
                "avg_wake_time": None,
                "sleep_quality_score": 0.0
            },
            "posture_distribution": {
                "standing": 0.0,
                "sitting": 0.0,
                "lying": 0.0,
                "walking": 0.0
            },
            "vital_signs_trends": {
                "heart_rate": {
                    "avg": 0.0,
                    "min": 0,
                    "max": 0,
                    "trend": "stable"
                },
                "respiratory_rate": {
                    "avg": 0.0,
                    "min": 0,
                    "max": 0,
                    "trend": "stable"
                }
            },
            "anomalies": [],
            "health_recommendations": []
        }
        
        # 查询住户的IoT时序数据进行行为模式分析
        resident_iot_data = self.iot_storage.find_all(
            lambda record: (
                str(record.get("resident_id")) == str(resident_id) and
                start_time <= datetime.fromisoformat(record.get("timestamp", "")) <= end_time
            )
        )
        
        if resident_iot_data:
            # 按时间段分析活动模式
            hourly_patterns = defaultdict(list)
            for record in resident_iot_data:
                timestamp = datetime.fromisoformat(record.get("timestamp", ""))
                hour = timestamp.hour
                posture = record.get("posture_snomed_code")
                if posture:
                    hourly_patterns[hour].append(posture)
            
            # 生成每小时的主要活动
            for hour, postures in hourly_patterns.items():
                if postures:
                    main_posture = max(set(postures), key=postures.count)
                    frequency = postures.count(main_posture) / len(postures)
                    pattern["hourly_patterns"][hour] = {
                        "main_activity": main_posture,
                        "frequency": round(frequency, 2),
                        "sample_count": len(postures)
                    }
            
            # 分析活动规律性
            # 计算每天相同时间段的活动一致性
            daily_patterns = defaultdict(lambda: defaultdict(list))
            for record in resident_iot_data:
                timestamp = datetime.fromisoformat(record.get("timestamp", ""))
                date_key = timestamp.date().isoformat()
                hour_key = timestamp.hour
                posture = record.get("posture_snomed_code")
                if posture:
                    daily_patterns[date_key][hour_key].append(posture)
            
            # 计算规律性评分
            consistency_scores = []
            for hour in range(24):
                hour_activities = []
                for date_activities in daily_patterns.values():
                    if hour in date_activities:
                        main_activity = max(set(date_activities[hour]), 
                                          key=date_activities[hour].count)
                        hour_activities.append(main_activity)
                
                if len(hour_activities) > 1:
                    # 计算该时段活动的一致性
                    most_common = max(set(hour_activities), key=hour_activities.count)
                    consistency = hour_activities.count(most_common) / len(hour_activities)
                    consistency_scores.append(consistency)
            
            if consistency_scores:
                pattern["regularity_score"] = round(statistics.mean(consistency_scores) * 100, 1)
        
        return pattern
    
    def compare_with_baseline(self, resident_id: UUID,
                             current_metrics: Dict[str, Any],
                             baseline_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        将当前指标与健康基线比较
        
        Args:
            resident_id: 住户ID
            current_metrics: 当前指标
            baseline_metrics: 基线指标
            
        Returns:
            比较结果
        """
        comparison = {
            "resident_id": str(resident_id),
            "comparison_time": datetime.utcnow().isoformat(),
            "deviations": [],
            "risk_level": "normal",
            "recommendations": []
        }
        
        # 比较各项指标
        for metric_name, current_value in current_metrics.items():
            if metric_name in baseline_metrics:
                baseline_value = baseline_metrics[metric_name]
                
                # 计算偏差百分比
                if isinstance(current_value, (int, float)) and isinstance(baseline_value, (int, float)):
                    if baseline_value != 0:
                        deviation_pct = ((current_value - baseline_value) / baseline_value) * 100
                        
                        if abs(deviation_pct) > 20:  # 偏差超过20%
                            comparison["deviations"].append({
                                "metric": metric_name,
                                "current": current_value,
                                "baseline": baseline_value,
                                "deviation_percent": round(deviation_pct, 2),
                                "severity": "high" if abs(deviation_pct) > 50 else "medium"
                            })
        
        # 确定风险等级
        if comparison["deviations"]:
            high_severity_count = sum(
                1 for d in comparison["deviations"] if d["severity"] == "high"
            )
            if high_severity_count > 0:
                comparison["risk_level"] = "high"
            else:
                comparison["risk_level"] = "medium"
        
        # 生成建议
        if comparison["risk_level"] != "normal":
            comparison["recommendations"].append(
                f"发现{len(comparison['deviations'])}项指标偏离基线，建议进行详细评估"
            )
        
        return comparison


# 全局单例
_care_quality_service = None

def get_care_quality_service() -> CareQualityService:
    """获取护理质量服务单例"""
    global _care_quality_service
    if _care_quality_service is None:
        _care_quality_service = CareQualityService()
    return _care_quality_service
