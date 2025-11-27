"""
WebSocket实时数据推送
支持告警、设备状态、IoT数据的实时更新
"""

from typing import List, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger
import json
import asyncio
from datetime import datetime

router = APIRouter()


class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket):
        """接受新连接"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """断开连接"""
        self.active_connections.remove(websocket)
        # 清理订阅
        for topic in list(self.subscriptions.keys()):
            if websocket in self.subscriptions[topic]:
                self.subscriptions[topic].remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        await websocket.send_json(message)
    
    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
    
    async def broadcast_to_topic(self, topic: str, message: dict):
        """向特定主题订阅者广播"""
        if topic in self.subscriptions:
            for connection in self.subscriptions[topic]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to topic {topic}: {e}")
    
    def subscribe(self, topic: str, websocket: WebSocket):
        """订阅主题"""
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        if websocket not in self.subscriptions[topic]:
            self.subscriptions[topic].append(websocket)
        logger.info(f"WebSocket subscribed to topic: {topic}")
    
    def unsubscribe(self, topic: str, websocket: WebSocket):
        """取消订阅"""
        if topic in self.subscriptions and websocket in self.subscriptions[topic]:
            self.subscriptions[topic].remove(websocket)
        logger.info(f"WebSocket unsubscribed from topic: {topic}")


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket主端点
    
    **消息格式**：
    ```json
    {
        "type": "subscribe|unsubscribe|ping",
        "topic": "alerts|devices|iot_data|residents",
        "filters": {"tenant_id": "xxx"}
    }
    ```
    
    **推送格式**：
    ```json
    {
        "type": "alert|device_status|iot_data|resident_update",
        "data": {...},
        "timestamp": "2025-11-21T11:38:00Z"
    }
    ```
    """
    await manager.connect(websocket)
    
    try:
        # 发送连接成功消息
        await manager.send_personal_message({
            "type": "connected",
            "message": "WebSocket连接成功",
            "timestamp": datetime.now().isoformat()
        }, websocket)
        
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            message_type = message.get("type")
            
            if message_type == "ping":
                # 心跳响应
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
            
            elif message_type == "subscribe":
                # 订阅主题
                topic = message.get("topic")
                if topic:
                    manager.subscribe(topic, websocket)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "topic": topic,
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
            
            elif message_type == "unsubscribe":
                # 取消订阅
                topic = message.get("topic")
                if topic:
                    manager.unsubscribe(topic, websocket)
                    await manager.send_personal_message({
                        "type": "unsubscribed",
                        "topic": topic,
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
            
            else:
                # 未知消息类型
                await manager.send_personal_message({
                    "type": "error",
                    "message": f"Unknown message type: {message_type}",
                    "timestamp": datetime.now().isoformat()
                }, websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# 辅助函数：推送告警
async def push_alert(alert_data: dict):
    """推送新告警到所有订阅者"""
    message = {
        "type": "alert",
        "data": alert_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_topic("alerts", message)


# 辅助函数：推送设备状态更新
async def push_device_status(device_data: dict):
    """推送设备状态更新"""
    message = {
        "type": "device_status",
        "data": device_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_topic("devices", message)


# 辅助函数：推送IoT数据
async def push_iot_data(iot_data: dict):
    """推送IoT实时数据"""
    message = {
        "type": "iot_data",
        "data": iot_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_topic("iot_data", message)


# 辅助函数：推送住户状态更新
async def push_resident_update(resident_data: dict):
    """推送住户状态更新"""
    message = {
        "type": "resident_update",
        "data": resident_data,
        "timestamp": datetime.now().isoformat()
    }
    await manager.broadcast_to_topic("residents", message)
