"""
实时数据WebSocket API
实时推送IoT数据、告警和系统事件
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Set, Dict
from uuid import UUID
import asyncio
import json
from loguru import logger
from datetime import datetime

router = APIRouter()

# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        # 按租户ID组织的连接池
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # 按设备ID订阅
        self.device_subscriptions: Dict[str, Set[WebSocket]] = {}
        # 按住户ID订阅
        self.resident_subscriptions: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, tenant_id: str):
        """接受新连接"""
        await websocket.accept()
        if tenant_id not in self.active_connections:
            self.active_connections[tenant_id] = set()
        self.active_connections[tenant_id].add(websocket)
        logger.info(f"WebSocket connected: tenant={tenant_id}, total={len(self.active_connections[tenant_id])}")
    
    def disconnect(self, websocket: WebSocket, tenant_id: str):
        """断开连接"""
        if tenant_id in self.active_connections:
            self.active_connections[tenant_id].discard(websocket)
            if not self.active_connections[tenant_id]:
                del self.active_connections[tenant_id]
        
        # 清理订阅
        for device_id in list(self.device_subscriptions.keys()):
            self.device_subscriptions[device_id].discard(websocket)
            if not self.device_subscriptions[device_id]:
                del self.device_subscriptions[device_id]
        
        for resident_id in list(self.resident_subscriptions.keys()):
            self.resident_subscriptions[resident_id].discard(websocket)
            if not self.resident_subscriptions[resident_id]:
                del self.resident_subscriptions[resident_id]
        
        logger.info(f"WebSocket disconnected: tenant={tenant_id}")
    
    def subscribe_device(self, websocket: WebSocket, device_id: str):
        """订阅设备数据"""
        if device_id not in self.device_subscriptions:
            self.device_subscriptions[device_id] = set()
        self.device_subscriptions[device_id].add(websocket)
        logger.info(f"Subscribed to device: {device_id}")
    
    def subscribe_resident(self, websocket: WebSocket, resident_id: str):
        """订阅住户数据"""
        if resident_id not in self.resident_subscriptions:
            self.resident_subscriptions[resident_id] = set()
        self.resident_subscriptions[resident_id].add(websocket)
        logger.info(f"Subscribed to resident: {resident_id}")
    
    def unsubscribe_device(self, websocket: WebSocket, device_id: str):
        """取消订阅设备数据"""
        if device_id in self.device_subscriptions:
            self.device_subscriptions[device_id].discard(websocket)
            if not self.device_subscriptions[device_id]:
                del self.device_subscriptions[device_id]
            logger.info(f"Unsubscribed from device: {device_id}")
    
    def unsubscribe_resident(self, websocket: WebSocket, resident_id: str):
        """取消订阅住户数据"""
        if resident_id in self.resident_subscriptions:
            self.resident_subscriptions[resident_id].discard(websocket)
            if not self.resident_subscriptions[resident_id]:
                del self.resident_subscriptions[resident_id]
            logger.info(f"Unsubscribed from resident: {resident_id}")
    
    async def broadcast_to_tenant(self, tenant_id: str, message: dict):
        """向租户的所有连接广播消息"""
        if tenant_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[tenant_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to connection: {e}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.active_connections[tenant_id].discard(connection)
    
    async def send_to_device_subscribers(self, device_id: str, message: dict):
        """向设备订阅者发送消息"""
        if device_id not in self.device_subscriptions:
            return
        
        disconnected = set()
        for connection in self.device_subscriptions[device_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to device subscriber: {e}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.device_subscriptions[device_id].discard(connection)
    
    async def send_to_resident_subscribers(self, resident_id: str, message: dict):
        """向住户订阅者发送消息"""
        if resident_id not in self.resident_subscriptions:
            return
        
        disconnected = set()
        for connection in self.resident_subscriptions[resident_id]:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error sending to resident subscriber: {e}")
                disconnected.add(connection)
        
        # 清理断开的连接
        for connection in disconnected:
            self.resident_subscriptions[resident_id].discard(connection)
    
    def get_stats(self) -> dict:
        """获取连接统计信息"""
        total_connections = sum(len(conns) for conns in self.active_connections.values())
        return {
            "total_connections": total_connections,
            "tenants": len(self.active_connections),
            "device_subscriptions": len(self.device_subscriptions),
            "resident_subscriptions": len(self.resident_subscriptions)
        }


# 全局连接管理器
manager = ConnectionManager()


@router.websocket("/ws/{tenant_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    tenant_id: str,
):
    """
    WebSocket实时数据推送
    
    ## 连接
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/api/v1/realtime/ws/{tenant_id}');
    ```
    
    ## 消息格式
    
    ### 客户端发送（订阅）
    ```json
    {
        "action": "subscribe",
        "type": "device",
        "id": "device_uuid"
    }
    ```
    
    ### 服务端推送（IoT数据）
    ```json
    {
        "type": "iot_data",
        "data": {...},
        "timestamp": "2025-11-20T15:30:00"
    }
    ```
    
    ### 服务端推送（告警）
    ```json
    {
        "type": "alert",
        "alert_type": "fall_detection",
        "alert_level": "critical",
        "data": {...}
    }
    ```
    """
    await manager.connect(websocket, tenant_id)
    
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "message": "WebSocket connection established",
            "tenant_id": tenant_id,
            "timestamp": datetime.now().isoformat()
        })
        
        # 启动心跳任务
        heartbeat_task = asyncio.create_task(_send_heartbeat(websocket))
        
        # 消息处理循环
        while True:
            # 接收客户端消息
            data = await websocket.receive_json()
            
            # 处理订阅请求
            if data.get("action") == "subscribe":
                sub_type = data.get("type")
                sub_id = data.get("id")
                
                if sub_type == "device" and sub_id:
                    manager.subscribe_device(websocket, sub_id)
                    await websocket.send_json({
                        "type": "subscribed",
                        "subscription_type": "device",
                        "id": sub_id
                    })
                
                elif sub_type == "resident" and sub_id:
                    manager.subscribe_resident(websocket, sub_id)
                    await websocket.send_json({
                        "type": "subscribed",
                        "subscription_type": "resident",
                        "id": sub_id
                    })
            
            # 处理取消订阅
            elif data.get("action") == "unsubscribe":
                unsub_type = data.get("type")
                unsub_id = data.get("id")
                
                if unsub_type == "device" and unsub_id:
                    manager.unsubscribe_device(websocket, unsub_id)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "subscription_type": "device",
                        "id": unsub_id
                    })
                
                elif unsub_type == "resident" and unsub_id:
                    manager.unsubscribe_resident(websocket, unsub_id)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "subscription_type": "resident",
                        "id": unsub_id
                    })
            
            # 处理ping
            elif data.get("action") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected normally: tenant={tenant_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        heartbeat_task.cancel()
        manager.disconnect(websocket, tenant_id)


@router.get("/stats", summary="获取WebSocket连接统计")
async def get_websocket_stats():
    """
    获取WebSocket连接统计信息
    
    ## 返回
    - 总连接数
    - 租户数量
    - 设备订阅数
    - 住户订阅数
    """
    return manager.get_stats()


# ==================== 辅助函数 ====================

async def _send_heartbeat(websocket: WebSocket, interval: int = 30):
    """发送心跳包"""
    try:
        while True:
            await asyncio.sleep(interval)
            await websocket.send_json({
                "type": "heartbeat",
                "timestamp": datetime.now().isoformat()
            })
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Heartbeat error: {e}")


# ==================== 公共接口（供其他模块调用）====================

async def push_iot_data(tenant_id: str, device_id: str, resident_id: str, data: dict):
    """推送IoT数据到WebSocket客户端"""
    message = {
        "type": "iot_data",
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    # 推送给租户
    await manager.broadcast_to_tenant(tenant_id, message)
    
    # 推送给设备订阅者
    await manager.send_to_device_subscribers(device_id, message)
    
    # 推送给住户订阅者
    if resident_id:
        await manager.send_to_resident_subscribers(resident_id, message)


async def push_alert(tenant_id: str, alert_type: str, alert_level: str, data: dict):
    """推送告警到WebSocket客户端"""
    message = {
        "type": "alert",
        "alert_type": alert_type,
        "alert_level": alert_level,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    await manager.broadcast_to_tenant(tenant_id, message)
