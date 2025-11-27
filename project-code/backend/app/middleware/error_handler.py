"""
统一错误处理中间件
提供标准化的错误响应格式和详细的错误日志
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from loguru import logger
import traceback
from typing import Union


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    HTTP异常处理器
    """
    logger.warning(
        f"HTTP {exc.status_code}: {request.method} {request.url.path} - {exc.detail}"
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "path": str(request.url.path),
                "method": request.method
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    请求验证异常处理器
    """
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    logger.warning(
        f"Validation error: {request.method} {request.url.path} - {len(errors)} error(s)"
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "请求参数验证失败",
                "path": str(request.url.path),
                "method": request.method,
                "details": errors
            }
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    通用异常处理器
    捕获所有未处理的异常
    """
    # 记录详细的错误日志
    logger.error(
        f"Unhandled exception: {request.method} {request.url.path}\n"
        f"Exception: {type(exc).__name__}: {str(exc)}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )
    
    # 根据环境决定是否返回详细错误信息
    import os
    is_development = os.getenv("ENV", "development") == "development"
    
    error_detail = {
        "code": 500,
        "message": "服务器内部错误",
        "path": str(request.url.path),
        "method": request.method
    }
    
    if is_development:
        error_detail["debug"] = {
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback": traceback.format_exc().split("\n")
        }
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": error_detail}
    )


class APIError(Exception):
    """
    自定义API错误基类
    """
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Union[dict, None] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


class ResourceNotFoundError(APIError):
    """资源未找到错误"""
    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} not found: {identifier}",
            status_code=404,
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "identifier": identifier}
        )


class ValidationError(APIError):
    """验证错误"""
    def __init__(self, field: str, message: str):
        super().__init__(
            message=f"Validation failed for field '{field}': {message}",
            status_code=400,
            error_code="VALIDATION_ERROR",
            details={"field": field, "validation_message": message}
        )


class AuthorizationError(APIError):
    """授权错误"""
    def __init__(self, message: str = "Unauthorized access"):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class BusinessLogicError(APIError):
    """业务逻辑错误"""
    def __init__(self, message: str, details: Union[dict, None] = None):
        super().__init__(
            message=message,
            status_code=400,
            error_code="BUSINESS_LOGIC_ERROR",
            details=details
        )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    自定义API错误处理器
    """
    logger.warning(
        f"API Error: {request.method} {request.url.path} - "
        f"{exc.error_code}: {exc.message}"
    )
    
    error_content = {
        "error": {
            "code": exc.status_code,
            "error_code": exc.error_code,
            "message": exc.message,
            "path": str(request.url.path),
            "method": request.method
        }
    }
    
    if exc.details:
        error_content["error"]["details"] = exc.details
    
    return JSONResponse(
        status_code=exc.status_code,
        content=error_content
    )
