"""
FastAPI主应用入口
owlRD智慧养老IoT监测系统
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
import sys
from pathlib import Path

from app.config import settings
from app.api.v1 import (
    auth, tenants, users, roles, residents, locations,
    resident_phi, resident_contacts, resident_caregivers, devices,
    iot_data, alerts, alert_policies,
    cards, card_functions,
    care_quality,
    config_versions, mappings,
    export_api, websocket
)
from app.api import docs, docs_offline, docs_local

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level=settings.log_level,
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="30 days",
    level="INFO",
)

# 创建FastAPI应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    # owlRD 智慧养老IoT监测系统API
    
    ## 核心功能
    - 🚨 实时跌倒检测与多级报警
    - 💓 非接触式生命体征监测（心率/呼吸率）
    - 🏥 护理质量评估与团队绩效分析
    - 🏷️ SNOMED CT医疗编码标准
    - 📡 TDPv2 IoT数据协议
    - 🔐 HIPAA合规的完全匿名化
    
    ## 文档
    - **API文档**: /docs
    - **ReDoc**: /redoc
    - **源项目**: https://github.com/sady37/owlRD
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json",
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（本地Swagger UI）
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"Static files mounted at /static from {static_dir}")


# 健康检查
@app.get("/", tags=["Health"])
async def root():
    """根路径 - 系统健康检查"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "message": "owlRD Backend API is running",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """详细健康检查"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug,
        "components": {
            "api": "operational",
            "storage": "operational",
            "cache": "operational",
        },
    }


# 注册API路由
# 认证相关（无需前缀）
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

# 用户和权限
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(roles.router, prefix="/api/v1/roles", tags=["Roles"])
app.include_router(locations.router, prefix="/api/v1/locations", tags=["Locations"])
app.include_router(residents.router, prefix="/api/v1/residents", tags=["Residents"])
app.include_router(resident_phi.router, prefix="/api/v1", tags=["Resident PHI"])
app.include_router(resident_contacts.router, prefix="/api/v1", tags=["Resident Contacts"])
app.include_router(resident_caregivers.router, prefix="/api/v1", tags=["Resident Caregivers"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(alert_policies.router, prefix="/api/v1/alert_policies", tags=["Alert Policies"])
app.include_router(config_versions.router, prefix="/api/v1/config_versions", tags=["Config Versions"])
app.include_router(mappings.router, prefix="/api/v1/mappings", tags=["Mappings"])
app.include_router(cards.router, prefix="/api/v1/cards", tags=["Cards"])
app.include_router(card_functions.router, prefix="/api/v1/card_functions", tags=["Card Functions"])
app.include_router(care_quality.router, prefix="/api/v1/care-quality", tags=["Care Quality"])
app.include_router(export_api.router, prefix="/api/v1/export", tags=["Export"])
app.include_router(websocket.router, prefix="/api/v1/realtime", tags=["Realtime WebSocket"])
app.include_router(iot_data.router, prefix="/api/v1/iot-data", tags=["IoT Data"])
# 自定义文档页面（使用国内CDN）
app.include_router(docs.router)
# 离线文档页面（完全不依赖外部CDN）
app.include_router(docs_offline.router)
# 本地文档页面（使用本地Swagger UI文件）
app.include_router(docs_local.router)


# 注册错误处理器
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler,
    api_error_handler,
    APIError
)

app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(APIError, api_error_handler)
app.add_exception_handler(Exception, general_exception_handler)


# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Data directory: {settings.data_dir}")
    # 初始化存储目录
    from app.services.storage import init_storage
    init_storage()
    logger.success("Application started successfully")


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")
    # 清理资源
    logger.success("Application shutdown complete")


def get_port_processes(port: int) -> list:
    """获取占用指定端口的进程信息"""
    import subprocess
    import re
    try:
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        processes = []
        for line in result.stdout.strip().split('\n'):
            if line.strip() and 'LISTENING' in line:
                # 提取PID
                match = re.search(r'\s+(\d+)\s*$', line)
                if match:
                    pid = match.group(1)
                    try:
                        # 获取进程名称
                        proc_result = subprocess.run(
                            f'tasklist /FI "PID eq {pid}" /FO CSV /NH',
                            shell=True,
                            capture_output=True,
                            text=True
                        )
                        if proc_result.stdout.strip():
                            proc_name = proc_result.stdout.strip().split(',')[0].strip('"')
                            processes.append({'pid': pid, 'name': proc_name})
                    except:
                        processes.append({'pid': pid, 'name': 'Unknown'})
        
        return processes
    except Exception:
        return []


def kill_processes(pids: list) -> bool:
    """终止指定的进程"""
    import subprocess
    success = True
    for pid in pids:
        try:
            subprocess.run(f'taskkill /PID {pid} /F', shell=True, check=True)
            logger.info(f"✅ 成功终止进程 PID: {pid}")
        except subprocess.CalledProcessError:
            logger.error(f"❌ 无法终止进程 PID: {pid}")
            success = False
    return success


def check_port_available(port: int) -> bool:
    """检查端口是否被占用，如果被占用则提供交互式清理"""
    processes = get_port_processes(port)
    
    if not processes:
        return True
    
    logger.warning(f"⚠️  端口 {port} 被以下进程占用:")
    for proc in processes:
        logger.warning(f"  - PID: {proc['pid']} | 进程: {proc['name']}")
    
    print()
    while True:
        response = input(f"是否终止这些进程以启动新的服务? (Y/N): ").strip().upper()
        if response in ['Y', 'YES']:
            pids = [proc['pid'] for proc in processes]
            if kill_processes(pids):
                logger.success("✅ 所有占用进程已清理")
                return True
            else:
                logger.error("❌ 部分进程清理失败")
                return False
        elif response in ['N', 'NO']:
            logger.info("❌ 用户选择不清理进程，服务无法启动")
            return False
        else:
            print("请输入 Y 或 N")


if __name__ == "__main__":
    import uvicorn
    import sys
    
    # 检查端口是否被占用，提供交互式清理
    if not check_port_available(settings.port):
        sys.exit(1)
    
    logger.info(f"✅ 端口 {settings.port} 可用，启动服务...")
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
