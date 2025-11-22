-- 核心扩展：UUID 生成 + 加密 + TimescaleDB

-- UUID / 加密相关函数（gen_random_uuid, pgp_sym_encrypt 等）
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- 时序数据库扩展（如未安装，可注释掉本行）
-- CREATE EXTENSION IF NOT EXISTS timescaledb;


