# AI 护理数据整理设计文档

## 概述

本文档描述如何依据 AI 护理的设想，进行初步数据整理，为下一步规则引擎或 AI 模型训练准备数据。

## 设计目标

1. **数据标准化**：统一不同来源的数据格式
2. **特征提取**：从原始数据中提取有用特征
3. **数据聚合**：按时间窗口聚合数据，支持趋势分析
4. **标签生成**：为监督学习准备标签数据

## 数据模型设计

### 1. 住户健康画像数据模型

```sql
-- 住户每日健康指标表
CREATE TABLE resident_daily_health_metrics (
    metric_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    resident_id UUID NOT NULL REFERENCES residents(resident_id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    
    -- 睡眠质量指标
    total_bed_time_seconds INTEGER,  -- 总卧床时长（秒）
    night_awakening_count INTEGER,  -- 夜间离床次数
    sleep_start_time TIME,  -- 入睡时间
    sleep_end_time TIME,  -- 觉醒时间
    sleep_duration_minutes INTEGER,  -- 睡眠时长（分钟）
    
    -- 日间活动能力指标
    daytime_out_of_bed_duration_seconds INTEGER,  -- 日间离床总时长
    room_movement_distance_cm INTEGER,  -- 房间内移动距离（cm）
    posture_change_count INTEGER,  -- 坐/站切换频次
    
    -- 生活规律性指标
    wake_up_time_variance_minutes INTEGER,  -- 起床时间方差（分钟）
    meal_activity_pattern_score DECIMAL(5,2),  -- 三餐活动模式得分 (0-100)
    toilet_frequency INTEGER,  -- 如厕频率
    
    -- 跌倒风险指标
    abnormal_movement_count INTEGER,  -- 异常移动次数
    gait_instability_score DECIMAL(5,2),  -- 步态不稳得分 (0-100)
    
    -- 社交意愿指标
    door_approach_count INTEGER,  -- 主动走到门口次数
    common_area_visit_count INTEGER,  -- 公共区访问次数
    
    -- 综合评分
    health_score DECIMAL(5,2),  -- 综合健康评分 (0-100)
    mobility_level INTEGER CHECK (mobility_level >= 0 AND mobility_level <= 5),
    
    metadata JSONB,  -- 扩展指标和原始数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id, resident_id, metric_date)
);

CREATE INDEX idx_health_metrics_date ON resident_daily_health_metrics(tenant_id, metric_date DESC);
CREATE INDEX idx_health_metrics_resident ON resident_daily_health_metrics(tenant_id, resident_id, metric_date DESC);
```

### 2. 住户健康基线表

```sql
-- 住户健康基线（动态更新）
CREATE TABLE resident_health_baselines (
    baseline_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    resident_id UUID NOT NULL REFERENCES residents(resident_id) ON DELETE CASCADE,
    baseline_type VARCHAR(50) NOT NULL,  -- daily, weekly, monthly, weekday, weekend
    window_start_date DATE NOT NULL,
    window_end_date DATE NOT NULL,
    
    -- 基线指标（均值 ± 标准差）
    avg_sleep_duration_minutes DECIMAL(10,2),
    std_sleep_duration_minutes DECIMAL(10,2),
    avg_wake_up_time TIME,
    std_wake_up_time_minutes INTEGER,
    avg_daily_activity_minutes DECIMAL(10,2),
    std_daily_activity_minutes DECIMAL(10,2),
    avg_movement_distance_cm DECIMAL(10,2),
    std_movement_distance_cm DECIMAL(10,2),
    
    -- 正常范围
    normal_sleep_duration_range JSONB,  -- {"min": 360, "max": 540}
    normal_activity_range JSONB,
    
    -- 计算参数
    baseline_period_days INTEGER,  -- 基线计算周期（天）
    sample_count INTEGER,  -- 用于计算的样本数
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id, resident_id, baseline_type, window_start_date)
);

CREATE INDEX idx_baselines_resident ON resident_health_baselines(tenant_id, resident_id, baseline_type);
CREATE INDEX idx_baselines_date ON resident_health_baselines(window_end_date DESC);
```

### 3. 护理事件与健康状态关联表

```sql
-- 护理-健康关联分析表
CREATE TABLE care_health_correlation (
    correlation_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    resident_id UUID NOT NULL REFERENCES residents(resident_id) ON DELETE CASCADE,
    nurse_group_id UUID REFERENCES nurse_groups(group_id) ON DELETE SET NULL,
    analysis_date DATE NOT NULL,
    
    -- 护理质量指标
    effective_care_sessions INTEGER,  -- 有效护理次数（距离≤1.2m，≥5分钟）
    total_care_duration_seconds INTEGER,
    avg_care_distance_cm DECIMAL(10,2),
    
    -- 护理后健康响应
    care_response_window_hours INTEGER DEFAULT 1,  -- 护理后响应观察窗口（小时）
    post_care_stable_in_bed BOOLEAN,  -- 护理后是否安稳卧床
    post_care_meal_activity BOOLEAN,  -- 护理后是否有进餐活动
    post_care_heart_rate_change INTEGER,  -- 护理后心率变化
    
    -- 健康状态变化
    health_status_before VARCHAR(50),  -- normal, declining, critical
    health_status_after VARCHAR(50),
    health_change_score DECIMAL(5,2),  -- 健康变化得分
    
    -- 关联分析结果
    correlation_type VARCHAR(50),  -- positive, negative, neutral
    correlation_strength DECIMAL(5,2),  -- 关联强度 (0-1)
    insight_text TEXT,  -- 自动生成的洞察文本
    
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(tenant_id, resident_id, analysis_date)
);

CREATE INDEX idx_correlation_resident ON care_health_correlation(tenant_id, resident_id, analysis_date DESC);
CREATE INDEX idx_correlation_group ON care_health_correlation(tenant_id, nurse_group_id, analysis_date DESC);
```

### 4. 风险预警标签表

```sql
-- 风险预警标签（用于 AI 训练）
CREATE TABLE risk_warning_labels (
    label_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(tenant_id) ON DELETE CASCADE,
    resident_id UUID NOT NULL REFERENCES residents(resident_id) ON DELETE CASCADE,
    event_id UUID REFERENCES care_events(event_id) ON DELETE SET NULL,
    
    -- 标签信息
    label_type VARCHAR(50) NOT NULL,  -- fall_risk, activity_decline, sleep_disorder, etc.
    label_source VARCHAR(50),  -- manual, device, ai_prediction
    label_value VARCHAR(50),  -- confirmed, false_alarm, unknown
    confidence DECIMAL(5,2),  -- 标签置信度 (0-100)
    
    -- 关联数据
    data_window_start TIMESTAMP WITH TIME ZONE,
    data_window_end TIMESTAMP WITH TIME ZONE,
    feature_vector JSONB,  -- 提取的特征向量
    
    -- 人工验证
    verified_by UUID REFERENCES users(user_id) ON DELETE SET NULL,
    verified_at TIMESTAMP WITH TIME ZONE,
    verification_note TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_labels_resident ON risk_warning_labels(tenant_id, resident_id, label_type);
    INDEX idx_labels_event ON risk_warning_labels(event_id);
    INDEX idx_labels_verified ON risk_warning_labels(verified_at IS NOT NULL);
);
```

## 数据提取与特征工程

### 1. 睡眠质量指标提取

```python
def extract_sleep_metrics(resident_id: str, date: date) -> Dict:
    """提取睡眠质量指标"""
    
    # 获取该日期的雷达轨迹数据
    trajectories = get_radar_trajectories(resident_id, date)
    
    # 获取压力板数据
    pressure_events = get_pressure_plate_events(resident_id, date)
    
    # 识别卧床时段（00:00-05:00 长时间床上停留）
    bed_periods = identify_bed_periods(trajectories, pressure_events)
    
    # 计算指标
    total_bed_time = sum(
        (period.end - period.start).total_seconds()
        for period in bed_periods
    )
    
    # 识别离床事件
    out_of_bed_events = identify_out_of_bed_events(trajectories, bed_periods)
    night_awakening_count = len([
        e for e in out_of_bed_events
        if e.time.hour >= 0 and e.time.hour < 5
    ])
    
    # 计算入睡/觉醒时间
    sleep_start, sleep_end = calculate_sleep_times(bed_periods)
    
    return {
        "total_bed_time_seconds": int(total_bed_time),
        "night_awakening_count": night_awakening_count,
        "sleep_start_time": sleep_start,
        "sleep_end_time": sleep_end,
        "sleep_duration_minutes": int((sleep_end - sleep_start).total_seconds() / 60)
    }
```

### 2. 活动能力指标提取

```python
def extract_activity_metrics(resident_id: str, date: date) -> Dict:
    """提取日间活动能力指标"""
    
    trajectories = get_radar_trajectories(resident_id, date)
    
    # 日间时段（06:00-22:00）
    daytime_trajectories = [
        t for t in trajectories
        if 6 <= t.timestamp.hour < 22
    ]
    
    # 计算离床总时长
    out_of_bed_duration = calculate_out_of_bed_duration(daytime_trajectories)
    
    # 计算移动距离
    total_distance = 0
    for i in range(1, len(daytime_trajectories)):
        prev = daytime_trajectories[i-1]
        curr = daytime_trajectories[i]
        distance = calculate_distance(
            prev.room_pos_x, prev.room_pos_y,
            curr.room_pos_x, curr.room_pos_y
        )
        total_distance += distance
    
    # 计算姿态切换次数
    posture_changes = count_posture_changes(daytime_trajectories)
    
    return {
        "daytime_out_of_bed_duration_seconds": int(out_of_bed_duration),
        "room_movement_distance_cm": int(total_distance),
        "posture_change_count": posture_changes
    }
```

### 3. 健康基线计算

```python
def calculate_health_baseline(
    resident_id: str,
    baseline_type: str = "weekly",
    window_days: int = 7
) -> Dict:
    """计算健康基线"""
    
    end_date = date.today()
    start_date = end_date - timedelta(days=window_days)
    
    # 获取历史数据
    daily_metrics = get_daily_health_metrics(resident_id, start_date, end_date)
    
    if len(daily_metrics) < 3:  # 至少需要3天数据
        return None
    
    # 分离工作日和周末（如果需要）
    if baseline_type == "weekday":
        daily_metrics = [m for m in daily_metrics if m.date.weekday() < 5]
    elif baseline_type == "weekend":
        daily_metrics = [m for m in daily_metrics if m.date.weekday() >= 5]
    
    # 计算均值和标准差
    sleep_durations = [m.sleep_duration_minutes for m in daily_metrics if m.sleep_duration_minutes]
    activity_minutes = [m.daytime_out_of_bed_duration_seconds / 60 for m in daily_metrics]
    
    avg_sleep = np.mean(sleep_durations) if sleep_durations else None
    std_sleep = np.std(sleep_durations) if sleep_durations else None
    
    avg_activity = np.mean(activity_minutes) if activity_minutes else None
    std_activity = np.std(activity_minutes) if activity_minutes else None
    
    # 计算正常范围（均值 ± 2标准差）
    normal_sleep_range = {
        "min": max(0, avg_sleep - 2 * std_sleep),
        "max": avg_sleep + 2 * std_sleep
    } if avg_sleep and std_sleep else None
    
    return {
        "avg_sleep_duration_minutes": avg_sleep,
        "std_sleep_duration_minutes": std_sleep,
        "avg_daily_activity_minutes": avg_activity,
        "std_daily_activity_minutes": std_activity,
        "normal_sleep_duration_range": normal_sleep_range,
        "baseline_period_days": window_days,
        "sample_count": len(daily_metrics)
    }
```

### 4. 护理-健康关联分析

```python
def analyze_care_health_correlation(
    resident_id: str,
    date: date
) -> Dict:
    """分析护理质量与健康状态的关联"""
    
    # 获取护理事件
    care_sessions = get_care_sessions(resident_id, date)
    effective_sessions = [
        s for s in care_sessions
        if s.avg_distance <= 120 and s.duration >= 300  # ≤1.2m, ≥5分钟
    ]
    
    # 获取护理后健康响应
    care_response_window = timedelta(hours=1)
    
    post_care_responses = []
    for session in care_sessions:
        response_window_start = session.end_time
        response_window_end = session.end_time + care_response_window
        
        # 检查护理后是否安稳卧床
        trajectories_after = get_trajectories_in_window(
            resident_id, response_window_start, response_window_end
        )
        stable_in_bed = check_stable_in_bed(trajectories_after)
        
        # 检查是否有进餐活动
        meal_activity = check_meal_activity(trajectories_after)
        
        post_care_responses.append({
            "session_id": session.id,
            "stable_in_bed": stable_in_bed,
            "meal_activity": meal_activity
        })
    
    # 获取健康状态变化
    health_metrics_before = get_daily_health_metrics(resident_id, date - timedelta(days=1))
    health_metrics_after = get_daily_health_metrics(resident_id, date)
    
    health_change = compare_health_metrics(
        health_metrics_before, health_metrics_after
    )
    
    # 计算关联强度
    correlation_strength = calculate_correlation_strength(
        effective_sessions, post_care_responses, health_change
    )
    
    # 生成洞察
    insight = generate_insight(
        effective_sessions, post_care_responses, health_change
    )
    
    return {
        "effective_care_sessions": len(effective_sessions),
        "total_care_duration_seconds": sum(s.duration for s in care_sessions),
        "post_care_stable_in_bed": sum(r["stable_in_bed"] for r in post_care_responses) / len(post_care_responses) if post_care_responses else 0,
        "health_change_score": health_change["score"],
        "correlation_strength": correlation_strength,
        "insight_text": insight
    }
```

### 5. 特征向量构建（用于 AI 训练）

```python
def build_feature_vector(
    resident_id: str,
    timestamp: datetime,
    window_hours: int = 24
) -> Dict:
    """构建用于 AI 模型的特征向量"""
    
    window_start = timestamp - timedelta(hours=window_hours)
    window_end = timestamp
    
    # 1. 轨迹特征
    trajectories = get_trajectories_in_window(resident_id, window_start, window_end)
    trajectory_features = {
        "avg_velocity": np.mean([t.velocity for t in trajectories]),
        "max_velocity": np.max([t.velocity for t in trajectories]),
        "velocity_variance": np.var([t.velocity for t in trajectories]),
        "movement_distance": calculate_total_distance(trajectories),
        "static_duration_ratio": calculate_static_ratio(trajectories)
    }
    
    # 2. 生命体征特征
    vital_signs = get_vital_signs_in_window(resident_id, window_start, window_end)
    vital_features = {
        "avg_heart_rate": np.mean([v.heart_rate for v in vital_signs]),
        "heart_rate_variance": np.var([v.heart_rate for v in vital_signs]),
        "avg_respiratory_rate": np.mean([v.respiratory_rate for v in vital_signs]),
        "abnormal_vital_count": count_abnormal_vitals(vital_signs)
    }
    
    # 3. 行为模式特征
    behavior_features = {
        "out_of_bed_count": count_out_of_bed_events(resident_id, window_start, window_end),
        "posture_change_frequency": calculate_posture_change_frequency(trajectories),
        "time_in_danger_zone_ratio": calculate_danger_zone_ratio(trajectories)
    }
    
    # 4. 历史基线对比特征
    baseline = get_current_baseline(resident_id)
    baseline_features = {
        "sleep_deviation": calculate_deviation_from_baseline(
            get_sleep_duration(resident_id, window_start.date()),
            baseline["avg_sleep_duration_minutes"],
            baseline["std_sleep_duration_minutes"]
        ),
        "activity_deviation": calculate_deviation_from_baseline(
            get_activity_duration(resident_id, window_start.date()),
            baseline["avg_daily_activity_minutes"],
            baseline["std_daily_activity_minutes"]
        )
    }
    
    # 组合所有特征
    feature_vector = {
        **trajectory_features,
        **vital_features,
        **behavior_features,
        **baseline_features,
        "timestamp": timestamp.isoformat(),
        "resident_id": resident_id
    }
    
    return feature_vector
```

## 批处理任务

### 每日数据聚合任务

```python
@celery.task
def daily_health_metrics_aggregation(date: date = None):
    """每日健康指标聚合任务"""
    if date is None:
        date = date.today() - timedelta(days=1)  # 处理前一天的数据
    
    # 获取所有活跃住户
    residents = get_active_residents()
    
    for resident in residents:
        try:
            # 提取睡眠指标
            sleep_metrics = extract_sleep_metrics(resident.id, date)
            
            # 提取活动指标
            activity_metrics = extract_activity_metrics(resident.id, date)
            
            # 计算综合健康评分
            health_score = calculate_health_score(sleep_metrics, activity_metrics)
            
            # 保存到数据库
            save_daily_health_metrics(resident.id, date, {
                **sleep_metrics,
                **activity_metrics,
                "health_score": health_score
            })
            
        except Exception as e:
            logger.error(f"Failed to aggregate metrics for resident {resident.id}: {e}")
```

### 基线更新任务

```python
@celery.task
def update_health_baselines():
    """更新健康基线任务（每周执行）"""
    residents = get_active_residents()
    
    for resident in residents:
        # 计算周基线
        weekly_baseline = calculate_health_baseline(
            resident.id, baseline_type="weekly", window_days=7
        )
        if weekly_baseline:
            save_health_baseline(resident.id, "weekly", weekly_baseline)
        
        # 计算月基线
        monthly_baseline = calculate_health_baseline(
            resident.id, baseline_type="monthly", window_days=30
        )
        if monthly_baseline:
            save_health_baseline(resident.id, "monthly", monthly_baseline)
```

## 参考文档

- [AI护理.md](../AI护理.md) - AI 护理功能清单和数据需求
- [FHIR与SNOMED_CT代码.md](../FHIR与SNOMED_CT代码.md) - 医疗编码标准

