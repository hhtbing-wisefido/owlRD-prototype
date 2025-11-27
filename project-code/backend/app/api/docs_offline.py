"""
完全离线的API文档 - 不依赖任何外部CDN
使用FastAPI内置的Swagger UI
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.openapi.docs import get_swagger_ui_html
from app.config import settings

router = APIRouter()


@router.get("/docs-offline", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui_offline(request: Request):
    """
    完全离线的Swagger UI文档
    不依赖任何外部CDN，所有资源都从FastAPI内置包加载
    """
    return get_swagger_ui_html(
        openapi_url="/api/openapi.json",
        title=f"{settings.app_name} - API文档（离线版）",
        swagger_favicon_url="/static/favicon.ico",  # 可选：自定义图标
    )


@router.get("/docs-simple", response_class=HTMLResponse, include_in_schema=False)
async def simple_api_docs():
    """
    极简API文档 - 纯HTML，零依赖
    显示所有API端点列表
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>owlRD API - 简易文档</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            h1 { color: #2c3e50; }
            .endpoint {
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }
            .method {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 3px;
                color: white;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background: #61affe; }
            .post { background: #49cc90; }
            .put { background: #fca130; }
            .delete { background: #f93e3e; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <h1>🦉 owlRD API 文档</h1>
        <p>完全离线版本，不依赖任何CDN</p>
        
        <h2>📋 核心端点</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/</code>
            <p>系统健康检查</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/health</code>
            <p>详细健康检查</p>
        </div>
        
        <h2>👥 住户管理</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/v1/residents</code>
            <p>获取住户列表 - 参数: tenant_id</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/v1/residents/{resident_id}</code>
            <p>获取单个住户详情</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/v1/residents</code>
            <p>创建新住户</p>
        </div>
        
        <h2>🔔 告警管理</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/v1/alerts</code>
            <p>获取告警列表 - 参数: tenant_id, level, status</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/v1/alerts/statistics/summary</code>
            <p>获取告警统计摘要</p>
        </div>
        
        <h2>📡 设备管理</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/v1/devices</code>
            <p>获取设备列表 - 参数: tenant_id, device_type</p>
        </div>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/v1/devices/{device_id}</code>
            <p>获取设备详情</p>
        </div>
        
        <h2>📊 IoT数据</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/v1/iot-data/latest</code>
            <p>获取最新IoT数据 - 参数: resident_id</p>
        </div>
        
        <h2>📖 完整文档</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/openapi.json</code>
            <p>OpenAPI规范（JSON格式）- 可导入Postman、Insomnia等工具</p>
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background: #fff3cd; border-radius: 5px;">
            <strong>💡 提示：</strong>
            <ul>
                <li>所有API都需要 <code>tenant_id</code> 参数</li>
                <li>默认租户ID: <code>10000000-0000-0000-0000-000000000001</code></li>
                <li>完整的API规范请访问: <a href="/api/openapi.json">/api/openapi.json</a></li>
                <li>可视化文档（需要网络）: <a href="/docs-cn">/docs-cn</a></li>
            </ul>
        </div>
    </body>
    </html>
    """
