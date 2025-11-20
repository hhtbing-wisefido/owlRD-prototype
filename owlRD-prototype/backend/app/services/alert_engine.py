"""
告警引擎服务
多级报警处理、路由和发送
"""

from typing import Dict, List, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime

from app.models.alert import CloudAlertPolicy, AlertLevel, DangerLevel
from app.services.storage import StorageService


class AlertEngine:
    """告警引擎"""
    
    def __init__(self):
        """初始化告警引擎"""
        self.policy_storage = StorageService(collection="cloud_alert_policies")
        self.alert_history: List[Dict[str, Any]] = []
    
    def process_alert(self, alert: Dict[str, Any], tenant_id: UUID) -> Dict[str, Any]:
        """
        处理告警
        
        Args:
            alert: 告警数据
            tenant_id: 租户ID
            
        Returns:
            处理结果
        """
        # 获取租户的告警策略
        policy = self.policy_storage.find_by_id("tenant_id", tenant_id)
        
        # 确定告警级别
        danger_level = alert.get("danger_level", "L2")
        alert_type = alert.get("type", "Unknown")
        
        # 确定告警路由
        recipients = self._determine_recipients(alert, policy)
        
        # 确定发送通道
        channels = self._determine_channels(danger_level, policy)
        
        # 创建告警记录
        alert_record = {
            "alert_id": str(uuid4()),
            "tenant_id": str(tenant_id),
            "alert_type": alert_type,
            "danger_level": danger_level,
            "timestamp": datetime.utcnow().isoformat(),
            "data": alert,
            "recipients": recipients,
            "channels": channels,
            "status": "pending"
        }
        
        # 保存告警历史
        self.alert_history.append(alert_record)
        
        # 发送告警
        self._send_alert(alert_record)
        
        return alert_record
    
    def _determine_recipients(self, alert: Dict[str, Any], policy: Optional[Dict]) -> List[str]:
        """确定告警接收者"""
        recipients = []
        
        if not policy:
            # 无策略时，返回默认管理员
            return ["admin@example.com"]
        
        # 根据告警接收范围确定接收者
        alert_scope = policy.get("alert_scope", "NURSE_ONLY")
        alert_user_ids = policy.get("alert_user_ids", [])
        alert_tags = policy.get("alert_tags", [])
        
        # 从alert_user_ids获取用户
        if alert_user_ids:
            recipients.extend([f"user_{uid}" for uid in alert_user_ids])
        
        # 从alert_tags获取标签组用户
        if alert_tags:
            for tag in alert_tags:
                recipients.append(f"group_{tag}")
        
        # 根据接收范围扩展接收者
        if alert_scope == "FAMILY":
            # 添加家属联系人
            resident_id = alert.get("resident_id")
            if resident_id:
                recipients.append(f"family_{resident_id}")
        elif alert_scope == "ALL":
            # 添加所有相关人员
            recipients.append("all_staff")
            resident_id = alert.get("resident_id")
            if resident_id:
                recipients.append(f"family_{resident_id}")
        
        return recipients if recipients else ["admin@example.com"]
    
    def _determine_channels(self, danger_level: str, policy: Optional[Dict]) -> List[str]:
        """确定发送通道"""
        if danger_level == "L1":
            return ["WEB", "APP", "PHONE", "EMAIL"]
        else:
            return ["WEB", "APP"]
    
    def _send_alert(self, alert_record: Dict[str, Any]) -> None:
        """
        发送告警
        
        实现多通道告警发送逻辑：
        - WEB: 网页推送（WebSocket）
        - APP: 移动应用推送
        - PHONE: 电话呼叫
        - EMAIL: 邮件通知
        """
        channels = alert_record.get("channels", [])
        recipients = alert_record.get("recipients", [])
        alert_level = alert_record.get("alert_level", "INFO")
        alert_type = alert_record.get("alert_type", "GENERAL")
        message = alert_record.get("message", "")
        tenant_id = alert_record.get("tenant_id")
        
        # 记录发送日志
        print(f"[AlertEngine] Sending alert via {channels} to {recipients}")
        print(f"[AlertEngine] Level: {alert_level}, Type: {alert_type}, Message: {message}")
        
        # 实际发送实现
        for channel in channels:
            try:
                if channel == "WEB":
                    self._send_websocket(tenant_id, alert_type, alert_level, alert_record)
                elif channel == "APP":
                    self._send_push_notification(recipients, alert_level, message)
                elif channel == "PHONE":
                    self._make_phone_call(recipients, alert_level, message)
                elif channel == "EMAIL":
                    self._send_email(recipients, alert_level, message)
                else:
                    print(f"[AlertEngine] Unknown channel: {channel}")
            except Exception as e:
                print(f"[AlertEngine] Error sending via {channel}: {e}")
    
    def _send_websocket(self, tenant_id: str, alert_type: str, alert_level: str, alert_data: Dict[str, Any]) -> None:
        """
        通过WebSocket发送告警
        
        Args:
            tenant_id: 租户ID
            alert_type: 告警类型
            alert_level: 告警级别
            alert_data: 告警数据
        """
        try:
            # 导入realtime模块并调用push_alert
            import asyncio
            from app.api.v1 import realtime
            
            # 创建异步任务推送告警
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                realtime.push_alert(tenant_id, alert_type, alert_level, alert_data)
            )
            loop.close()
            
            print(f"[AlertEngine] WebSocket alert sent to tenant {tenant_id}")
        except Exception as e:
            print(f"[AlertEngine] WebSocket send error: {e}")
    
    def _send_push_notification(self, recipients: List[str], alert_level: str, message: str) -> None:
        """
        发送移动应用推送通知
        
        Args:
            recipients: 接收者列表
            alert_level: 告警级别
            message: 告警消息
            
        Note:
            实际实现需要集成FCM（Firebase Cloud Messaging）或APNs（Apple Push Notification service）
        """
        print(f"[AlertEngine] APP Push: {alert_level} to {recipients}")
        print(f"[AlertEngine] Message: {message}")
        # 实际实现示例：
        # from firebase_admin import messaging
        # notification = messaging.Notification(title=f"Alert - {alert_level}", body=message)
        # messaging.send(notification, tokens=recipients)
    
    def _make_phone_call(self, recipients: List[str], alert_level: str, message: str) -> None:
        """
        拨打电话告警
        
        Args:
            recipients: 接收者电话号码列表
            alert_level: 告警级别
            message: 告警消息
            
        Note:
            实际实现需要集成Twilio或类似的电话服务
        """
        print(f"[AlertEngine] Phone Call: {alert_level} to {recipients}")
        print(f"[AlertEngine] Message: {message}")
        # 实际实现示例：
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # for phone in recipients:
        #     call = client.calls.create(to=phone, from_=from_phone, twiml=f"<Response><Say>{message}</Say></Response>")
    
    def _send_email(self, recipients: List[str], alert_level: str, message: str) -> None:
        """
        发送邮件告警
        
        Args:
            recipients: 接收者邮箱列表
            alert_level: 告警级别
            message: 告警消息
            
        Note:
            实际实现需要配置SMTP服务器
        """
        print(f"[AlertEngine] Email: {alert_level} to {recipients}")
        print(f"[AlertEngine] Message: {message}")
        # 实际实现示例：
        # import smtplib
        # from email.mime.text import MIMEText
        # msg = MIMEText(message)
        # msg['Subject'] = f'Alert - {alert_level}'
        # msg['From'] = from_email
        # msg['To'] = ', '.join(recipients)
        # with smtplib.SMTP(smtp_server, smtp_port) as server:
        #     server.send_message(msg)


def get_alert_engine() -> AlertEngine:
    """获取告警引擎单例"""
    return AlertEngine()
