"""
TDP协议处理器
处理TDPv2协议数据报文，解析Person Matrix和Object Matrix
"""

from typing import Optional, Dict, List, Any
from datetime import datetime
from uuid import UUID

from app.models.tdp import (
    TDPEvent, PersonMatrix, ObjectMatrix,
    LiteEventHeader, ExtendEventHeader,
    CodeableConcept, Tag, Timestamp,
    DangerLevel, DatagramMode
)
from app.models.iot_data import IOTTimeseries, IOTTimeseriesCreate
from app.services.snomed_service import get_snomed_service


class TDPProcessor:
    """TDP协议处理器"""
    
    def __init__(self):
        """初始化TDP处理器"""
        self.snomed_service = get_snomed_service()
    
    def process_event(self, event: TDPEvent, tenant_id: UUID, device_id: UUID) -> Dict[str, Any]:
        """
        处理TDP事件数据报文
        
        Args:
            event: TDP事件
            tenant_id: 租户ID
            device_id: 设备ID
            
        Returns:
            处理结果
        """
        result = {
            "status": "success",
            "timestamp": datetime.utcnow(),
            "person_matrices": [],
            "object_matrices": [],
            "alerts": [],
            "iot_records": []
        }
        
        # 处理Person Matrix
        if event.person_matrices:
            for person_matrix in event.person_matrices:
                processed = self._process_person_matrix(person_matrix, event, tenant_id, device_id)
                result["person_matrices"].append(processed)
                
                # 生成IoT时序数据
                iot_record = self._create_iot_timeseries(person_matrix, event, tenant_id, device_id)
                result["iot_records"].append(iot_record)
                
                # 检查是否需要告警
                alerts = self._check_alerts(person_matrix)
                result["alerts"].extend(alerts)
        
        # 处理Object Matrix
        if event.object_matrices:
            for object_matrix in event.object_matrices:
                processed = self._process_object_matrix(object_matrix)
                result["object_matrices"].append(processed)
        
        return result
    
    def _process_person_matrix(self, person: PersonMatrix, event: TDPEvent, 
                               tenant_id: UUID, device_id: UUID) -> Dict[str, Any]:
        """
        处理人员矩阵数据
        
        Args:
            person: 人员矩阵
            event: TDP事件
            tenant_id: 租户ID
            device_id: 设备ID
            
        Returns:
            处理后的数据
        """
        result = {
            "tracking_id": person.tracking_id,
            "position": {
                "x": person.pos_x,
                "y": person.pos_y,
                "z": person.pos_z
            },
            "velocity": None,
            "posture": None,
            "motion_state": None,
            "health_score": None,
            "vital_signs": {},
            "sleep_state": None
        }
        
        # 速度信息
        if person.vel_x is not None:
            result["velocity"] = {
                "x": person.vel_x,
                "y": person.vel_y,
                "z": person.vel_z
            }
        
        # 姿态
        if person.posture:
            result["posture"] = {
                "code": person.posture.code,
                "display": person.posture.display
            }
        
        # 运动状态
        if person.motion_state:
            result["motion_state"] = {
                "code": person.motion_state.code,
                "display": person.motion_state.display
            }
        
        # 健康状况
        if person.health_score:
            result["health_score"] = {
                "code": person.health_score.code,
                "display": person.health_score.display
            }
        
        # 生命体征
        if person.heart_rate is not None:
            result["vital_signs"]["heart_rate"] = person.heart_rate
        if person.respiratory_rate is not None:
            result["vital_signs"]["respiratory_rate"] = person.respiratory_rate
        
        # 睡眠状态
        if person.sleep_state:
            result["sleep_state"] = {
                "code": person.sleep_state.code,
                "display": person.sleep_state.display
            }
        
        return result
    
    def _process_object_matrix(self, obj: ObjectMatrix) -> Dict[str, Any]:
        """
        处理物体矩阵数据
        
        Args:
            obj: 物体矩阵
            
        Returns:
            处理后的数据
        """
        result = {
            "object_type": obj.object_type,
            "object_id": obj.object_id,
            "position": {
                "x": obj.pos_x,
                "y": obj.pos_y,
                "z": obj.pos_z
            },
            "dimensions": None,
            "is_occupied": obj.is_occupied
        }
        
        if obj.width is not None:
            result["dimensions"] = {
                "width": obj.width,
                "height": obj.height,
                "depth": obj.depth
            }
        
        return result
    
    def _create_iot_timeseries(self, person: PersonMatrix, event: TDPEvent,
                              tenant_id: UUID, device_id: UUID) -> Dict[str, Any]:
        """
        从Person Matrix创建IoT时序数据记录
        
        Args:
            person: 人员矩阵
            event: TDP事件
            tenant_id: 租户ID
            device_id: 设备ID
            
        Returns:
            IoT时序数据字典
        """
        # 提取timestamp
        if isinstance(event.header, ExtendEventHeader):
            timestamp = datetime.fromtimestamp(event.header.timestamp.seconds)
        else:
            timestamp = datetime.fromtimestamp(event.header.timestamp.seconds)
        
        # 确定TDP Tag Category
        tdp_tag_category = self._determine_tag_category(person, event.header)
        
        # 创建IoT时序数据
        record = {
            "tenant_id": str(tenant_id),
            "device_id": str(device_id),
            "timestamp": timestamp.isoformat(),
            "tdp_tag_category": tdp_tag_category,
            "tracking_id": person.tracking_id,
            "radar_pos_x": person.pos_x,
            "radar_pos_y": person.pos_y,
            "radar_pos_z": person.pos_z,
            "posture_snomed_code": person.posture.code if person.posture else None,
            "posture_display": person.posture.display if person.posture else None,
            "event_type": event.header.event_type if hasattr(event.header, 'event_type') else None,
            "event_display": None,
            "area_id": None,
            "heart_rate": person.heart_rate,
            "respiratory_rate": person.respiratory_rate,
            "sleep_state_snomed_code": person.sleep_state.code if person.sleep_state else None,
            "sleep_state_display": person.sleep_state.display if person.sleep_state else None,
            "location_id": getattr(event.header, 'location_id', None),
            "room_id": getattr(event.header, 'room_id', None),
            "confidence": person.confidence,
            "remaining_time": None,
            "raw_original": event.raw_data if event.raw_data else b"",
            "raw_format": "binary",
            "raw_compression": None,
            "metadata": {}
        }
        
        return record
    
    def _determine_tag_category(self, person: PersonMatrix, header: Any) -> Optional[str]:
        """
        确定TDP Tag Category
        
        Args:
            person: 人员矩阵
            header: 事件头
            
        Returns:
            Tag类别
        """
        # 如果有生命体征数据，分类为Physiological
        if person.heart_rate is not None or person.respiratory_rate is not None:
            return "Physiological"
        
        # 如果有睡眠状态，分类为SleepState
        if person.sleep_state is not None:
            return "SleepState"
        
        # 如果有姿态，分类为Posture
        if person.posture is not None:
            return "Posture"
        
        # 如果有运动状态，分类为MotionState
        if person.motion_state is not None:
            return "MotionState"
        
        # 如果有事件类型且为安全事件
        if hasattr(header, 'event_type') and header.event_type:
            safety_events = ['FALL', 'FALL_SUSPECTED', 'PROLONGED_STAY', 'NO_ACTIVITY_24H']
            if header.event_type in safety_events:
                return "Safety"
        
        return None
    
    def _check_alerts(self, person: PersonMatrix) -> List[Dict[str, Any]]:
        """
        检查是否需要触发告警
        
        Args:
            person: 人员矩阵
            
        Returns:
            告警列表
        """
        alerts = []
        
        # 评估生命体征
        if person.heart_rate is not None or person.respiratory_rate is not None:
            assessment = self.snomed_service.assess_vital_signs(
                heart_rate=person.heart_rate,
                respiratory_rate=person.respiratory_rate
            )
            
            if assessment["danger_level"]:
                alerts.append({
                    "type": "vital_signs",
                    "danger_level": assessment["danger_level"],
                    "abnormalities": [
                        {"code": ab.code, "display": ab.display}
                        for ab in assessment["abnormalities"]
                    ],
                    "heart_rate": person.heart_rate,
                    "respiratory_rate": person.respiratory_rate
                })
        
        # 检查跌倒
        if person.posture and person.posture.code in ["1912002", "129839007"]:  # Fall or Fall Risk
            alerts.append({
                "type": "fall",
                "danger_level": "L1" if person.posture.code == "1912002" else "L2",
                "posture": {
                    "code": person.posture.code,
                    "display": person.posture.display
                }
            })
        
        return alerts
    
    def parse_protobuf(self, raw_data: bytes) -> Optional[TDPEvent]:
        """
        解析Protobuf格式的TDP数据
        
        Args:
            raw_data: 原始Protobuf数据
            
        Returns:
            TDP事件对象，解析失败返回None
            
        Note:
            需要先生成Protobuf类文件：
            protoc --python_out=. tdp.proto
        """
        try:
            # 尝试导入生成的Protobuf类
            # 如果未生成，将使用备用的JSON解析
            try:
                from app.proto import tdp_pb2
                
                # 解析Protobuf消息
                message = tdp_pb2.EventDatagram()
                message.ParseFromString(raw_data)
                
                # 转换为TDPEvent对象
                return self._convert_protobuf_to_tdp_event(message)
                
            except ImportError:
                # Protobuf类未生成，尝试将bytes当作JSON处理
                print("[TDPProcessor] Protobuf classes not found, attempting JSON fallback")
                try:
                    import json
                    json_data = json.loads(raw_data.decode('utf-8'))
                    return self.parse_json(json_data)
                except Exception as json_error:
                    print(f"[TDPProcessor] JSON fallback failed: {json_error}")
                    return None
                    
        except Exception as e:
            print(f"[TDPProcessor] Protobuf parsing error: {e}")
            return None
    
    def _convert_protobuf_to_tdp_event(self, proto_message) -> TDPEvent:
        """
        将Protobuf消息转换为TDPEvent对象
        
        Args:
            proto_message: Protobuf EventDatagram消息
            
        Returns:
            TDP事件对象
        """
        # 解析时间戳
        timestamp = TDPTimestamp(
            iso_timestamp=proto_message.timestamp.iso_timestamp,
            unix_timestamp=proto_message.timestamp.unix_timestamp
        )
        
        # 解析Person Matrix
        person_matrix = []
        for person in proto_message.person_matrix:
            person_entry = TDPPersonEntry(
                person_id=person.person_id,
                matrix_id=person.matrix_id,
                location_x=person.location_x,
                location_y=person.location_y,
                zone_index=person.zone_index,
                heart_rate=person.heart_rate if person.HasField('heart_rate') else None,
                respiration_rate=person.respiration_rate if person.HasField('respiration_rate') else None,
                motion_intensity=person.motion_intensity if person.HasField('motion_intensity') else None,
                presence_confidence=person.presence_confidence,
                posture=person.posture if person.HasField('posture') else None,
                fall_detected=person.fall_detected,
                metadata=dict(person.metadata) if person.metadata else {}
            )
            person_matrix.append(person_entry)
        
        # 解析Object Matrix
        object_matrix = []
        for obj in proto_message.object_matrix:
            object_entry = TDPObjectEntry(
                object_id=obj.object_id,
                matrix_id=obj.matrix_id,
                location_x=obj.location_x,
                location_y=obj.location_y,
                zone_index=obj.zone_index,
                object_type=obj.object_type,
                motion_detected=obj.motion_detected,
                metadata=dict(obj.metadata) if obj.metadata else {}
            )
            object_matrix.append(object_entry)
        
        # 创建TDPEvent对象
        tdp_event = TDPEvent(
            device_id=UUID(proto_message.device_id),
            tenant_id=UUID(proto_message.tenant_id),
            timestamp=timestamp,
            person_matrix=person_matrix,
            object_matrix=object_matrix,
            metadata=dict(proto_message.metadata) if proto_message.metadata else {}
        )
        
        return tdp_event


# 全局单例
_tdp_processor = None

def get_tdp_processor() -> TDPProcessor:
    """获取TDP处理器单例"""
    global _tdp_processor
    if _tdp_processor is None:
        _tdp_processor = TDPProcessor()
    return _tdp_processor
