"""
FastAPI主应用入口
owlRD智慧养老IoT监测系统
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import sys

from app.config import settings
from app.api.v1 import (
    tenants,
    users,
    residents,
    devices,
    alerts,
    cards,
    care_quality,
    realtime,
)

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
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["Tenants"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(residents.router, prefix="/api/v1/residents", tags=["Residents"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(cards.router, prefix="/api/v1/cards", tags=["Cards"])
app.include_router(care_quality.router, prefix="/api/v1/care-quality", tags=["Care Quality"])
app.include_router(realtime.router, prefix="/api/v1/realtime", tags=["Realtime"])


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


# 启动事件
@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Data directory: {settings.data_dir}")
    # 初始化数据存储
    from app.services.storage import init_storage
    await init_storage()
    logger.success("Application started successfully")


# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application")
    # 清理资源
    logger.success("Application shutdown complete")


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
