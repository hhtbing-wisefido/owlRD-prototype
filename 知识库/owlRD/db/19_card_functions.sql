-- 卡片自动生成函数和触发器
-- 用途：根据卡片创建规则自动生成和维护卡片
-- 参考：docs/20_Card_Creation_Rules_Final.md

-- ============================================================================
-- 辅助函数：计算卡片地址
-- ============================================================================

-- 计算 ActiveBed 卡片地址
CREATE OR REPLACE FUNCTION calculate_activebed_address(
    p_location_tag VARCHAR(255),
    p_location_name VARCHAR(255),
    p_bed_name VARCHAR(50)
) RETURNS VARCHAR(255) AS $$
BEGIN
    IF p_location_tag IS NOT NULL THEN
        RETURN p_location_tag || '-' || p_location_name || '-' || p_bed_name;
    ELSE
        RETURN p_location_name || '-' || p_bed_name;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- 计算 Location 卡片地址
CREATE OR REPLACE FUNCTION calculate_location_address(
    p_location_tag VARCHAR(255),
    p_location_name VARCHAR(255)
) RETURNS VARCHAR(255) AS $$
BEGIN
    IF p_location_tag IS NOT NULL THEN
        RETURN p_location_tag || '-' || p_location_name;
    ELSE
        RETURN p_location_name;
    END IF;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ============================================================================
-- 辅助函数：判断是否为 ActiveBed
-- ============================================================================

CREATE OR REPLACE FUNCTION is_activebed(
    p_bed_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    v_resident_id UUID;
    v_bound_device_count INTEGER;
BEGIN
    SELECT b.resident_id, b.bound_device_count
    INTO v_resident_id, v_bound_device_count
    FROM beds b
    WHERE b.bed_id = p_bed_id;
    
    -- ActiveBed 条件：
    -- 1. 有住户
    -- 2. 有激活监护的监控设备（bound_device_count > 0）
    -- 3. 床位激活（is_active = TRUE，由 bound_device_count > 0 自动计算）
    RETURN v_resident_id IS NOT NULL 
       AND v_bound_device_count > 0;
END;
$$ LANGUAGE plpgsql STABLE;

-- ============================================================================
-- 核心函数：为指定 location 重新生成所有卡片
-- ============================================================================

CREATE OR REPLACE FUNCTION regenerate_cards_for_location(
    p_location_id UUID
) RETURNS void AS $$
DECLARE
    v_tenant_id UUID;
    v_location_tag VARCHAR(255);
    v_location_name VARCHAR(255);
    v_location_type VARCHAR(20);
    v_is_public_space BOOLEAN;
    v_is_multi_person_room BOOLEAN;
    v_primary_resident_id UUID;
    v_activebed_count INTEGER;
    v_bed_record RECORD;
    v_card_id UUID;
    v_card_name VARCHAR(255);
    v_card_address VARCHAR(255);
    v_resident_count INTEGER;
    v_device_record RECORD;
BEGIN
    -- 获取 location 信息
    SELECT l.tenant_id, l.location_tag, l.location_name, l.location_type, l.is_public_space, l.is_multi_person_room, l.primary_resident_id
    INTO v_tenant_id, v_location_tag, v_location_name, v_location_type, v_is_public_space, v_is_multi_person_room, v_primary_resident_id
    FROM locations l
    WHERE l.location_id = p_location_id;
    
    IF v_tenant_id IS NULL THEN
        RAISE EXCEPTION 'Location not found: %', p_location_id;
    END IF;
    
    -- 开始事务：删除该 location 下的所有旧卡片
    DELETE FROM cards
    WHERE tenant_id = v_tenant_id
      AND (location_id = p_location_id OR bed_id IN (
          SELECT bed_id FROM beds WHERE location_id = p_location_id
      ));
    
    -- 统计该 location 下的 ActiveBed 数量
    SELECT COUNT(*)
    INTO v_activebed_count
    FROM beds b
    WHERE b.location_id = p_location_id
      AND is_activebed(b.bed_id);
    
    -- ========================================================================
    -- 场景 A：门牌下只有 1 个 ActiveBed
    -- ========================================================================
    IF v_activebed_count = 1 THEN
        -- 找到唯一的 ActiveBed
        SELECT b.bed_id, b.bed_name, b.resident_id, r.last_name
        INTO v_bed_record
        FROM beds b
        JOIN residents r ON b.resident_id = r.resident_id
        WHERE b.location_id = p_location_id
          AND is_activebed(b.bed_id)
        LIMIT 1;
        
        -- 计算卡片名称和地址
        v_card_name := v_bed_record.last_name;
        v_card_address := calculate_activebed_address(
            v_location_tag, 
            v_location_name, 
            v_bed_record.bed_name
        );
        
        -- 创建 ActiveBed 卡片
        INSERT INTO cards (
            tenant_id, card_type, bed_id, location_id,
            card_name, card_address, resident_id
        ) VALUES (
            v_tenant_id, 'ActiveBed', v_bed_record.bed_id, p_location_id,
            v_card_name, v_card_address, v_bed_record.resident_id
        ) RETURNING card_id INTO v_card_id;
        
        -- 绑定设备：该 ActiveBed 绑定的设备（direct）
        INSERT INTO card_devices (tenant_id, card_id, device_id, binding_type)
        SELECT 
            v_tenant_id, v_card_id, d.device_id, 'direct'
        FROM devices d
        WHERE d.bound_bed_id = v_bed_record.bed_id
          AND d.monitoring_enabled = TRUE
          AND d.installed = TRUE;
        
        -- 绑定设备：该 location 下未绑床的设备（indirect）
        INSERT INTO card_devices (tenant_id, card_id, device_id, binding_type)
        SELECT 
            v_tenant_id, v_card_id, d.device_id, 'indirect'
        FROM devices d
        WHERE d.location_id = p_location_id
          AND d.bound_bed_id IS NULL
          AND d.monitoring_enabled = TRUE
          AND d.installed = TRUE;
    
    -- ========================================================================
    -- 场景 B：门牌下有多个 ActiveBed（≥2）
    -- ========================================================================
    ELSIF v_activebed_count >= 2 THEN
        -- 为每个 ActiveBed 创建卡片
        FOR v_bed_record IN
            SELECT b.bed_id, b.bed_name, b.resident_id, r.last_name
            FROM beds b
            JOIN residents r ON b.resident_id = r.resident_id
            WHERE b.location_id = p_location_id
              AND is_activebed(b.bed_id)
        LOOP
            -- 计算卡片名称和地址
            v_card_name := v_bed_record.last_name;
            v_card_address := calculate_activebed_address(
                v_location_tag, 
                v_location_name, 
                v_bed_record.bed_name
            );
            
            -- 创建 ActiveBed 卡片
            INSERT INTO cards (
                tenant_id, card_type, bed_id, location_id,
                card_name, card_address, resident_id
            ) VALUES (
                v_tenant_id, 'ActiveBed', v_bed_record.bed_id, p_location_id,
                v_card_name, v_card_address, v_bed_record.resident_id
            ) RETURNING card_id INTO v_card_id;
            
            -- 绑定设备：该床位的设备（direct）
            INSERT INTO card_devices (tenant_id, card_id, device_id, binding_type)
            SELECT 
                v_tenant_id, v_card_id, d.device_id, 'direct'
            FROM devices d
            WHERE d.bound_bed_id = v_bed_record.bed_id
              AND d.monitoring_enabled = TRUE
              AND d.installed = TRUE;
        END LOOP;
        
        -- 检查是否有未绑床的设备
        IF EXISTS (
            SELECT 1
            FROM devices d
            WHERE d.location_id = p_location_id
              AND d.bound_bed_id IS NULL
              AND d.monitoring_enabled = TRUE
              AND d.installed = TRUE
        ) THEN
            -- 计算 Location 卡片名称（按优先级）
            IF v_is_public_space = TRUE THEN
                -- 优先级1：Institutional 公共空间，显示 location_name
                v_card_name := v_location_name;
            ELSIF v_is_multi_person_room = TRUE THEN
                -- 优先级2：Institutional 多人房间，显示 location_name
                v_card_name := v_location_name;
            ELSIF v_location_type = 'HomeCare' AND v_primary_resident_id IS NOT NULL THEN
                -- 优先级3：HomeCare 场景，直接使用 primary_resident_id 对应的住户的 LastName
                SELECT r.last_name
                INTO v_card_name
                FROM residents r
                WHERE r.resident_id = v_primary_resident_id
                  AND r.status = 'active';
                
                -- 如果找不到住户，使用 location_name 作为后备
                IF v_card_name IS NULL THEN
                    v_card_name := v_location_name;
                END IF;
            ELSIF v_is_multi_person_room = FALSE THEN
                -- 优先级4：Institutional 单人房间/夫妻套房（is_multi_person_room = FALSE）
                -- 必须设置 primary_resident_id（绑定用户时，必须处理该值不为空）
                IF v_primary_resident_id IS NOT NULL THEN
                    -- 使用第一位入住者的 LastName
                    SELECT r.last_name
                    INTO v_card_name
                    FROM residents r
                    WHERE r.resident_id = v_primary_resident_id
                      AND r.status = 'active';
                    
                    -- 如果找不到住户，使用 location_name 作为后备
                    IF v_card_name IS NULL THEN
                        v_card_name := v_location_name;
                    END IF;
                ELSE
                    -- 如果没有设置 primary_resident_id（不应该发生，但作为后备处理）
                    -- 使用 location_name 作为后备
                    v_card_name := v_location_name;
                END IF;
            ELSE
                -- 其他情况（不应该到达这里），使用 location_name 作为后备
                v_card_name := v_location_name;
            END IF;
            
            -- 计算 Location 卡片地址
            v_card_address := calculate_location_address(
                v_location_tag, 
                v_location_name
            );
            
            -- 创建 Location 卡片
            INSERT INTO cards (
                tenant_id, card_type, location_id,
                card_name, card_address
            ) VALUES (
                v_tenant_id, 'Location', p_location_id,
                v_card_name, v_card_address
            ) RETURNING card_id INTO v_card_id;
            
            -- 绑定设备：该 location 下未绑床的设备（indirect）
            INSERT INTO card_devices (tenant_id, card_id, device_id, binding_type)
            SELECT 
                v_tenant_id, v_card_id, d.device_id, 'indirect'
            FROM devices d
            WHERE d.location_id = p_location_id
              AND d.bound_bed_id IS NULL
              AND d.monitoring_enabled = TRUE
              AND d.installed = TRUE;
            
            -- 绑定住户：该 location 下所有绑定到 ActiveBed 的住户
            INSERT INTO card_residents (tenant_id, card_id, resident_id)
            SELECT DISTINCT
                v_tenant_id, v_card_id, b.resident_id
            FROM beds b
            WHERE b.location_id = p_location_id
              AND is_activebed(b.bed_id)
              AND b.resident_id IS NOT NULL;
        END IF;
    
    -- ========================================================================
    -- 场景 C：门牌下无 ActiveBed
    -- ========================================================================
    ELSE
        -- 检查是否有未绑床的设备
        IF EXISTS (
            SELECT 1
            FROM devices d
            WHERE d.location_id = p_location_id
              AND d.bound_bed_id IS NULL
              AND d.monitoring_enabled = TRUE
              AND d.installed = TRUE
        ) THEN
            -- 计算 Location 卡片名称（按优先级）
            IF v_is_public_space = TRUE THEN
                -- 优先级1：Institutional 公共空间，显示 location_name
                v_card_name := v_location_name;
            ELSIF v_is_multi_person_room = TRUE THEN
                -- 优先级2：Institutional 多人房间，显示 location_name
                v_card_name := v_location_name;
            ELSIF v_location_type = 'HomeCare' AND v_primary_resident_id IS NOT NULL THEN
                -- 优先级3：HomeCare 场景，直接使用 primary_resident_id 对应的住户的 LastName
                SELECT r.last_name
                INTO v_card_name
                FROM residents r
                WHERE r.resident_id = v_primary_resident_id
                  AND r.status = 'active';
                
                -- 如果找不到住户，使用 location_name 作为后备
                IF v_card_name IS NULL THEN
                    v_card_name := v_location_name;
                END IF;
            ELSIF v_is_multi_person_room = FALSE THEN
                -- 优先级4：Institutional 单人房间/夫妻套房（is_multi_person_room = FALSE）
                -- 必须设置 primary_resident_id（绑定用户时，必须处理该值不为空）
                IF v_primary_resident_id IS NOT NULL THEN
                    -- 使用第一位入住者的 LastName
                    SELECT r.last_name
                    INTO v_card_name
                    FROM residents r
                    WHERE r.resident_id = v_primary_resident_id
                      AND r.status = 'active';
                    
                    -- 如果找不到住户，使用 location_name 作为后备
                    IF v_card_name IS NULL THEN
                        v_card_name := v_location_name;
                    END IF;
                ELSE
                    -- 如果没有设置 primary_resident_id（不应该发生，但作为后备处理）
                    -- 使用 location_name 作为后备
                    v_card_name := v_location_name;
                END IF;
            ELSE
                -- 其他情况（不应该到达这里），使用 location_name 作为后备
                v_card_name := v_location_name;
            END IF;
            
            -- 计算 Location 卡片地址
            v_card_address := calculate_location_address(
                v_location_tag, 
                v_location_name
            );
            
            -- 创建 Location 卡片
            INSERT INTO cards (
                tenant_id, card_type, location_id,
                card_name, card_address
            ) VALUES (
                v_tenant_id, 'Location', p_location_id,
                v_card_name, v_card_address
            ) RETURNING card_id INTO v_card_id;
            
            -- 绑定设备：该 location 下未绑床的设备（indirect）
            INSERT INTO card_devices (tenant_id, card_id, device_id, binding_type)
            SELECT 
                v_tenant_id, v_card_id, d.device_id, 'indirect'
            FROM devices d
            WHERE d.location_id = p_location_id
              AND d.bound_bed_id IS NULL
              AND d.monitoring_enabled = TRUE
              AND d.installed = TRUE;
        END IF;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 核心函数：为所有 location 重新生成所有卡片
-- ============================================================================

CREATE OR REPLACE FUNCTION regenerate_all_cards() RETURNS void AS $$
DECLARE
    v_location_record RECORD;
BEGIN
    -- 遍历所有 location，为每个 location 重新生成卡片
    FOR v_location_record IN
        SELECT DISTINCT location_id
        FROM locations
        WHERE is_active = TRUE
    LOOP
        PERFORM regenerate_cards_for_location(v_location_record.location_id);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- 维护策略说明
-- ============================================================================
-- 
-- 卡片维护采用应用层维护策略：
--   1. SQL 表只存储生成的卡片记录（cards、card_devices、card_residents）
--   2. 应用层在业务逻辑中调用 regenerate_cards_for_location() 函数
--   3. 不在数据库层面使用触发器自动维护
-- 
-- 优点：
--   - 逻辑清晰，易于调试和维护
--   - 避免触发器带来的性能问题和调试困难
--   - 应用层可以更好地控制更新时机和错误处理
-- 
-- 应用层调用时机：
--   1. 住户入住/出院时（beds.resident_id 变化）
--   2. 设备安装/移除时（devices.bound_bed_id 或 devices.location_id 变化）
--   3. 设备监护状态变化时（devices.monitoring_enabled 变化）
--   4. 地址信息变化时（locations.location_name 或 location_tag 变化）
-- 
-- 示例代码（应用层）：
--   -- 当住户入住时
--   UPDATE beds SET resident_id = ... WHERE bed_id = ...;
--   SELECT regenerate_cards_for_location(location_id, actor_id, 'Staff');
-- 
--   -- 当设备绑定变化时
--   UPDATE devices SET bound_bed_id = ... WHERE device_id = ...;
--   SELECT regenerate_cards_for_location(location_id, actor_id, 'Staff');
--

-- ============================================================================
-- 注释
-- ============================================================================

COMMENT ON FUNCTION regenerate_cards_for_location IS '为指定 location 重新生成所有卡片（根据卡片创建规则）。由应用层调用，不在数据库层面使用触发器。';
COMMENT ON FUNCTION regenerate_all_cards IS '为所有 location 重新生成所有卡片。用于初始化或批量更新。';
COMMENT ON FUNCTION is_activebed IS '判断指定床位是否为 ActiveBed（有住户且有激活监护的设备）';
COMMENT ON FUNCTION calculate_activebed_address IS '计算 ActiveBed 卡片地址';
COMMENT ON FUNCTION calculate_location_address IS '计算 Location 卡片地址';

