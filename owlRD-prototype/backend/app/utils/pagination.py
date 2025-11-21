"""
分页工具
提供数据分页功能
"""

from typing import List, TypeVar, Generic, Callable, Any
from pydantic import BaseModel, Field
from math import ceil

T = TypeVar('T')


class PaginationParams(BaseModel):
    """分页参数"""
    page: int = Field(default=1, ge=1, description="页码（从1开始）")
    page_size: int = Field(default=20, ge=1, le=100, description="每页数量")
    sort_by: str = Field(default="created_at", description="排序字段")
    sort_order: str = Field(default="desc", description="排序方向：asc/desc")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T] = Field(..., description="当前页数据")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")


def paginate(
    items: List[Any],
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "created_at",
    sort_order: str = "desc"
) -> dict:
    """
    对数据进行分页处理
    
    Args:
        items: 原始数据列表
        page: 页码（从1开始）
        page_size: 每页数量
        sort_by: 排序字段
        sort_order: 排序方向（asc/desc）
    
    Returns:
        分页后的数据和元信息
    """
    # 计算总数
    total = len(items)
    
    # 排序
    if sort_by and items:
        reverse = sort_order.lower() == "desc"
        try:
            items_sorted = sorted(
                items,
                key=lambda x: x.get(sort_by, ""),
                reverse=reverse
            )
        except:
            items_sorted = items
    else:
        items_sorted = items
    
    # 计算分页
    total_pages = ceil(total / page_size) if total > 0 else 1
    
    # 确保页码有效
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    
    # 计算起始和结束索引
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # 获取当前页数据
    page_items = items_sorted[start_index:end_index]
    
    return {
        "items": page_items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }


def create_paginated_response(
    items: List[Any],
    params: PaginationParams
) -> dict:
    """
    创建分页响应（使用PaginationParams）
    
    Args:
        items: 原始数据列表
        params: 分页参数
    
    Returns:
        分页响应
    """
    return paginate(
        items=items,
        page=params.page,
        page_size=params.page_size,
        sort_by=params.sort_by,
        sort_order=params.sort_order
    )


def apply_filters(
    items: List[dict],
    filters: dict
) -> List[dict]:
    """
    应用过滤条件
    
    Args:
        items: 原始数据列表
        filters: 过滤条件字典 {"field": "value"}
    
    Returns:
        过滤后的数据列表
    """
    if not filters:
        return items
    
    filtered_items = items
    
    for field, value in filters.items():
        if value is not None:
            filtered_items = [
                item for item in filtered_items
                if str(item.get(field, "")).lower() == str(value).lower()
            ]
    
    return filtered_items


def search_items(
    items: List[dict],
    search_query: str,
    search_fields: List[str]
) -> List[dict]:
    """
    搜索数据
    
    Args:
        items: 原始数据列表
        search_query: 搜索关键词
        search_fields: 搜索字段列表
    
    Returns:
        匹配的数据列表
    """
    if not search_query:
        return items
    
    search_query_lower = search_query.lower()
    
    def item_matches(item: dict) -> bool:
        """检查项目是否匹配搜索条件"""
        for field in search_fields:
            field_value = str(item.get(field, "")).lower()
            if search_query_lower in field_value:
                return True
        return False
    
    return [item for item in items if item_matches(item)]
