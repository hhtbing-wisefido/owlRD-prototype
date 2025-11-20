"""
应用配置模块
基于Pydantic Settings的环境变量管理
"""

from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """应用配置"""
    
    # Application
    app_name: str = Field(default="owlRD Prototype", env="APP_NAME")
    app_version: str = Field(default="0.1.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        env="CORS_ORIGINS"
    )
    
    # Data Storage
    data_dir: str = Field(default="./app/data", env="DATA_DIR")
    backup_dir: str = Field(default="./backups", env="BACKUP_DIR")
    max_timeseries_days: int = Field(default=30, env="MAX_TIMESERIES_DAYS")
    
    # Encryption (PHI Data)
    encryption_key: str = Field(default="", env="ENCRYPTION_KEY")
    
    # Cache
    cache_ttl_seconds: int = Field(default=300, env="CACHE_TTL_SECONDS")
    max_cache_size: int = Field(default=1000, env="MAX_CACHE_SIZE")
    
    # TDP Protocol
    tdp_buffer_size: int = Field(default=8192, env="TDP_BUFFER_SIZE")
    tdp_compression_enabled: bool = Field(default=True, env="TDP_COMPRESSION_ENABLED")
    
    # Alert System
    alert_confirmation_timeout_l5: int = Field(default=30, env="ALERT_CONFIRMATION_TIMEOUT_L5")
    alert_secondary_timeout_l5: int = Field(default=150, env="ALERT_SECONDARY_TIMEOUT_L5")
    alert_server_override_timeout: int = Field(default=50, env="ALERT_SERVER_OVERRIDE_TIMEOUT")
    
    # Care Quality
    effective_care_radius_meters: float = Field(default=1.2, env="EFFECTIVE_CARE_RADIUS_METERS")
    care_coverage_threshold: float = Field(default=0.7, env="CARE_COVERAGE_THRESHOLD")
    
    # Anonymous Names
    anonymous_names_profession: int = Field(default=50, env="ANONYMOUS_NAMES_PROFESSION")
    anonymous_names_character: int = Field(default=50, env="ANONYMOUS_NAMES_CHARACTER")
    anonymous_names_animal: int = Field(default=100, env="ANONYMOUS_NAMES_ANIMAL")
    anonymous_names_item: int = Field(default=100, env="ANONYMOUS_NAMES_ITEM")
    
    # Session
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# 全局配置实例
settings = Settings()
