-- 房间表 (rooms)
-- 对应权限表中的 Room 定义：
-- 业务规则：
--   1) 每个 Location 创建时，应用层应自动生成一个 IsDefault = TRUE 的 Room
--      - RoomName = Location.location_name（默认房间名称等于位置名称，如 "E203"）
--      - 如果 RoomName 不为空且不是默认值，则使用自定义名称（如 "Bedroom"）
--   2) Bed 和 Device 总是绑定到 Room（绑定路径：Location → Room → Bed/Device）
--   3) 当客户细分房间时，Default Room 保持 Active，但不再接受新的 Bed/Device 绑定
--      （即一旦细分，就不能再将新的 Bed/Device 挂在 Default Room 上，由应用层控制）
--       细分前：可以暂时把所有 Bed/Device 都挂在 Default Room 上。
--       细分后（新建了 bedroom/bathroom 等具体房间）：
--       旧的 Bed/Device 绑定可以慢慢迁移走；
--   4) 当客户取消细分时，可以重新将所有 Bed/Device 挂回到 Default Room 上。

CREATE TABLE IF NOT EXISTS rooms (
    -- Primary / SaaS
    room_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,

    -- Structure
    location_id UUID NOT NULL REFERENCES locations(location_id) ON DELETE CASCADE,

    is_default  BOOLEAN      NOT NULL DEFAULT FALSE,
    room_name   VARCHAR(100) NOT NULL,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,

    -- 房间布局配置（可选，用于房间级独立布局）
    -- 如果使用统一楼层布局（locations.layout_config），此字段可为 NULL
    -- 如果使用房间级独立布局，此字段存储该房间的独立布局
    -- 布局 JSON 结构（vue_radar canvasData）：
    -- {
    --   "params": CanvasParams,   // 画布参数，包含 devices 列表等
    --   "objects": BaseObject[],  // 所有对象（Bed/Radar/Furniture/Wall...）
    --   "timestamp": "ISO8601"
    -- }
    -- 详见 vue_radar/src/stores/objects.ts 中 saveCanvas/loadCanvas 实现
    -- 注意：
    --   1) 统一楼层布局：layout_config 存储在 locations 表，此字段为 NULL
    --   2) 房间级布局：此字段存储房间独立布局，locations.layout_config 可为 NULL
    --   3) 坐标系统：楼层布局使用楼层坐标系，房间布局使用房间坐标系
    layout_config JSONB,

    -- 同一租户 + 地址下房间名唯一
    UNIQUE(tenant_id, location_id, room_name)
);

CREATE INDEX IF NOT EXISTS idx_rooms_tenant_id ON rooms(tenant_id);
CREATE INDEX IF NOT EXISTS idx_rooms_location_id ON rooms(tenant_id, location_id);
