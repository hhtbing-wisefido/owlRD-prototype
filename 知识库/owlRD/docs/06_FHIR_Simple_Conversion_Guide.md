# FHIR/SNOMED CT 简化转换指南

## 设计思路（前言）

为了让IT人员能够直接使用，不需要深入研究FHIR和SNOMED CT标准，我们提供：

1. **固定格式模板**：IT人员只需要替换值
2. **映射表**：TDP Tag → FHIR资源类型 → SNOMED CT编码（直接查表）
3. **简单转换函数**：输入TDP数据，输出FHIR JSON（自动填充）


先记住三条“用哪个表”的规则：

1. **呼吸 / 心率（生命体征）**
   - 内部：`heart_rate`、`resp_rate` 等数值 + 时间/房间/设备
   - 事件/告警：用“生理指标编码（Physiological）”里的 SNOMED（Tachycardia / Bradycardia / Tachypnea 等）+ vue_radar 阈值（L1/L2）

2. **运动 / 姿态实时监控**
   - 内部：按 `Posture` / `MotionState` 存内部枚举或 SNOMED（站立/坐位/仰卧/行走/静止等）
   - 需要统计/分析时，直接按这些状态过滤即可

3. **姿态报警 / 跌倒告警（安全告警）**
   - 事件/告警：用“安全告警编码（Safety）”里的 SNOMED  
     - 已跌倒：`161898004 | Fall`（紧急事件）  
     - 异常姿势 / 跌倒风险：`43029002 | Abnormal posture`

记法：**“内部只看数值 + SNOMED，LOINC 只在对外 FHIR 接口时才出现”**。

---

## 一、快速映射表（查表即用）

### 1.0 生命体征阈值表（来自 vue_radar 项目）

#### 心率（Heart Rate）阈值

| 级别 | 范围（次/分钟） | TDP DangerLevel | FHIR Flag状态 | 说明 |
|------|----------------|----------------|--------------|------|
| **Normal** | [55 - 95] | - | - | 正常范围，无需告警 |
| **L2 (警告)** | [45 - 54]<br>[96 - 115] | ALERT (2) | active | 中度关注，需要观察 |
| **L1 (危险)** | [0 - 44]<br>[116 - ∞] | EMERGENCY (1) | active | 高度警示，需要临床干预 |

**持续时长要求**：
- L1：持续 ≥ 1 分钟 → 触发 EMERGENCY 
- L2：持续 ≥ 5 分钟 → 触发 ALERT

#### 呼吸频率（Respiratory Rate, RR）阈值

| 级别 | 范围（次/分钟） | TDP DangerLevel | FHIR Flag状态 | 说明 |
|------|----------------|----------------|--------------|------|
| **Normal** | [10 - 23] | - | - | 正常范围，无需告警 |
| **L2 (警告)** | [8 - 9]<br>[24 - 26] | ALERT (2) | active | 中度关注，需要观察 |
| **L1 (危险)** | [0 - 7]<br>[27 - ∞] | EMERGENCY (1) | active | 高度警示，需要临床干预 |

**持续时长要求**：
- L1：持续 ≥ 1 分钟 → 触发 EMERGENCY
- L2：持续 ≥ 5 分钟 → 触发 ALERT

**使用示例**：
```python
# IT人员只需要这样判断：
heart_rate = 120  # 从设备获取
if heart_rate >= 116:  # L1范围
    danger_level = "EMERGENCY"  # L1
elif heart_rate >= 96 or heart_rate <= 54:  # L2范围
    danger_level = "ALERT"  # L2
else:
    danger_level = None  # Normal，无需告警
```

### 1.1 TDP Tag Category 总览

> 说明：本小节仅用于 **内部语义分层**，方便 IT 知道“这条数据属于哪一类”。  
> 具体的 SNOMED 列在 1.2 表中，LOINC 只在后面的 FHIR/HL7 接口章节中出现。

| TDP Tag Category   | 内部主要用途              |
|--------------------|---------------------------|
| **Physiological**  | 生命体征（心率 Heart Rate, HR、呼吸频率 Respiratory Rate, RR 等），按数值 + 阈值判断 L1/L2 |
| **Behavioral**     | 行为观测（如离床/上床/床上坐起等床相关事件）       |
| **Posture**        | 姿态观测（站立/坐位/卧位/床上坐姿等）             |
| **MotionState**    | 运动状态（行走/静止/异常步态等）                 |
| **SleepState**     | 睡眠状态（清醒/浅睡眠/深睡眠等）                 |
| **Safety**         | 安全告警（跌倒、异常姿势、长时间滞留等事件）       |
| **HealthCondition**| 健康风险（超2H未翻身、2H无体动等长时间无活动事件）  |
| **DeviceError**    | 设备故障状态 + 告警                           |

### 1.2 常用SNOMED CT编码速查表

#### 姿态编码（Posture） 56903-8 (姿态)

| 中文名称 | SNOMED CT编码 | 使用场景 |
|---------|--------------|---------|
| 站立 | 383370001 | 日常活动 |
| 坐位 | 402120000 | 休息状态 |
| 仰卧 | 109030009 | 睡眠监测 | 
| 侧卧 | 102536004 (左) / 102538003 (右) | 睡眠姿态 |
| 异常姿势 | 43029002 | 跌倒风险 |

**注意**：上床/离床/床上坐起属于**行为事件**，请参考"行为观测编码（Behavioral）"部分。


#### 运动状态编码（MotionState）  68461-1 (运动)

| 中文名称 | SNOMED CT编码 | 使用场景 |
|---------|--------------|---------|
| 行走 | 129006008 | 正常步行 |
| 静止 | 263821009 | 无移动 |
| 异常步态 | 22325002 | 疾病预警 |
| 拖曳步态 | 249911004 | 帕金森 |
| 跌倒 | 161898004 | 紧急事件 |

#### 生理指标编码（Physiological）

**基础生命体征测量项目**

| 中文名称 | TDP Tag Code | SNOMED CT编码 | 使用场景 |
|---------|-------------|--------------|---------|
| 心率（Heart Rate, HR） | HeartRate | 364075005 | 心率测量项目（基础观测值） |
| 呼吸频率（Respiratory Rate, RR） | RespiratoryRate | 86290005 | 呼吸频率测量项目（基础观测值） |

**基于 vue_radar 项目的阈值定义（异常状态）**

| 中文名称 | TDP Tag Code | SNOMED CT编码 | 阈值范围 | 使用场景 |
|---------|-------------|--------------|---------|---------|
| 心动过速 | Tachycardia | 271636001 | 心率 ≥ 116 (L1) | 严重心动过速，需要临床干预 |
| 心动过速（中度） | Tachycardia.Moderate | 271636001 | 心率 96-115 (L2) | 中度心动过速，需要观察 |
| 心动过缓 | Bradycardia | 342400002 | 心率 ≤ 44 (L1) | 严重心动过缓，需要临床干预 |
| 心动过缓（中度） | Bradycardia.Moderate | 342400002 | 心率 45-54 (L2) | 中度心动过缓，需要观察 |
| 呼吸急促 | Tachypnea | 30128008 | 呼吸频率 ≥ 27 (L1) | 严重呼吸急促，需要临床干预 |
| 呼吸急促（中度） | Tachypnea.Moderate | 30128008 | 呼吸频率 24-26 (L2) | 中度呼吸急促，需要观察 |
| 呼吸缓慢 | Bradypnea | 248546003 | 呼吸频率 ≤ 7 (L1) | 严重呼吸缓慢，需要临床干预 |
| 呼吸缓慢（中度） | Bradypnea.Moderate | 248546003 | 呼吸频率 8-9 (L2) | 中度呼吸缓慢，需要观察 |
| 呼吸暂停 | Apnea.Confirmed | 28436001 | 呼吸频率 < 5 持续10秒 | 确诊呼吸暂停 |

**注意**：阈值判断需要结合持续时长：
- L1：持续 ≥ 1 分钟 → EMERGENCY
- L2：持续 ≥ 5 分钟 → ALERT

#### 安全告警编码（Safety）
-特点：事件型告警，不依赖数值阈值

| 中文名称 | TDP Tag Code | SNOMED CT编码 | 使用场景 |
|---------|-------------|--------------|---------|
| 跌倒 | Fall | 161898004 | 紧急告警 |
| 疑似跌倒 | Fall.Suspected | 129839007 | 风险预警 |
| 在地面 | OnFloor | 161898004 | 坐地检测 |
| 身体抽畜 | ABM | 248540003 | Abnormal body movements | 床上 |
| 长时间滞留 | ProlongedStay | 77605003 | 卫生间ProlongedStay |
| 24H无人 | 24h INA | 373147003 | 整个房间 24-hour Inactivity |

#### 行为观测编码（Behavioral）
-特点：床相关行为事件（Radar/SleepPad 通用）
-说明：这些是 **IoT 设备上报的行为事件**，不是静态姿态。姿态编码（Posture）仅用于静态身体位置（如站立、坐位、卧位）。

| 中文名称 | TDP Tag Code | SNOMED CT编码 | 使用场景 |
|---------|-------------|--------------|---------|
| 离床 | LeftBed | 248570008 | 离开床位（从卧床状态转为非卧床状态） |
| 上床 | EnterBed | 248569007 | 进入床位（从非卧床状态转为卧床状态） |
| 床上坐起 | Bed.SitUp | 40199007 | 床上坐起（从卧位转为坐位） |

#### 睡眠状态编码（SleepState）
-特点：睡眠状态观测（Radar/SleepPad 通用）
-说明：用于描述睡眠质量监测中的睡眠状态，区别于行为事件（Behavioral）和姿态（Posture）。

| 中文名称 | TDP Tag Code | SNOMED CT编码 | 使用场景 |
|---------|-------------|--------------|---------|
| 清醒 | Awake | 248220002 | 清醒状态（Awake） |
| 浅睡眠 | LightSleep | 248232005 | 浅睡眠（非快速眼动睡眠 N1 + N2） |
| 深睡眠 | DeepSleep | 248233000 | 深睡眠（非快速眼动睡眠 N3） |

#### 健康风险编码（HealthCondition）
-特点：长时间无活动/无体动事件（用于压疮预防和异常检测）

| 中文名称 | TDP Tag Code | SNOMED CT编码 | 持续时间阈值 | 使用场景 |
|---------|-------------|--------------|------------|---------|
| 超2H未翻身 | NoTurning.2H | 248527007 | 120分钟 | 防床褥/压疮预防（超过2小时未翻身） |
| 2H无体动 | NoBodyMovement.2H | 260413007 | 120分钟 | 异常检测（人体睡觉时会有体动，完全无动作可能异常） |



#### 设备故障编码（DeviceError）282095001

| 中文名称   | TDP Tag Code       | SNOMED CT编码 | 使用场景       |
|-----------|--------------------|--------------|---------------|
| 设备故障   | DeviceError        | 282095001    | 通用设备故障   |
| 传感器断线 | SensorDisconnected | 282095001    | 传感器连接中断 |
| 通信故障   | CommunicationError | 282095001    | 设备通信失败   |
| 电源故障   | PowerFailure       | 282095001    | 设备断电       |
| 校准失败   | CalibrationFailed  | 282095001    | 设备校准失败   |
| 数据异常   | DataAnomaly        | 282095001    | 数据异常       |

**注意**：设备故障通常使用通用的SNOMED CT编码 `282095001` (Device malfunction)，具体故障类型在`display`字段中描述。

#### 常见环境（Environment / Location）类的 SNOMED CT 代码清单

家庭/住宅类环境（Home Environment）常用 SNOMED 代码
环境	SNOMED Code	描述
家 / 家庭环境	314767009	Home environment
卧室	257667001	Bedroom
客厅（Living room）	257669003	Living room
浴室 / 卫生间（Bathroom）	77605003	Bathroom
厕所（Toilet room）	257914005	Toilet
厨房（Kitchen）	257670002	Kitchen
餐厅（Dining room）	257671003	Dining room
走廊（Corridor / Hallway）	257915006	Corridor
玄关 / 门厅（Entrance hall）	257916007	Entrance hall
楼梯（Stairway）	257917003	Stairway
洗衣房（Laundry room）	257663009	Laundry room
车库（Garage）	257664003	Garage
院子（Yard）	257673000	Yard
床边（Bedside）	257880003	At bedside（医疗也可用）

医疗类环境（Hospital / Clinical Environment）
环境	SNOMED Code	描述
医院 (Hospital)	22232009	Hospital
病房 (Ward)	309900005	Hospital ward
病房区（Inpatient unit）	309915005	Inpatient unit
急诊科（Emergency department）	113858008	Emergency department
ICU（Intensive care unit）	309904001	ICU
观察室（Observation room）	309912008	Observation room
诊室（Consulting room）	309898003	Consulting room
候诊区（Waiting room）	309898003	Waiting room

养老院 / 护理环境（Long-term care）
环境	SNOMED Code	描述
养老院 (Nursing home)	225368008	Nursing home
长期护理机构（Long term care facility）	42665001	Long-term care facility
护理房间（Care home room）	257667001	可重复使用 Bedroom
生活区（Lounge / Communal area）	257669003	Living/Lounge
活动区（Activity room）	257918008	Activity area


户外 / 公共环境
环境	SNOMED Code	描述
室外（Outdoor）」	260787004	Outdoor environment
公园（Park）	257672007	Park
街道（Street）	257914005	Street
商店（Store/Shop）	27250006	Shop
建筑物（Building）	257914005	Building（泛用）

场景	SNOMED Code	说明
床上（In bed）	248569007	用于上床状态
不在床上（Not in bed）	248570008	用于离床状态
床边（At bedside）	257880003	床附近活动区域
浴室（Bathroom）	77605003	卫生间滞留事件
厕所（Toilet room）	257914005	更精确
走廊（Corridor）	257915006	跌倒检测常用
客厅（Living room）	257669003	日常活动区域
卧室（Bedroom）	257667001	夜间状况监测
厨房（Kitchen）	257670002	烟雾/活动监测


---

## 三、FHIR/HL7 对外接口（使用 LOINC）

### 3.1 LOINC vs SNOMED：谁管什么？

- **LOINC 解决“这一列是什么项目？”**  
  - 例如：`8867-4` = Heart rate（这是“心率”这个测量项目）  
  - 在 FHIR 里一般放在 `Observation.code`，表示“测的是什么”。

- **SNOMED 解决“这个值说明了什么临床含义？”**  
  - 例如：`271636001` = Tachycardia（心动过速，这个结果的医学意义）  
  - 在 FHIR 里放在 `Observation.valueCodeableConcept` / `interpretation`、`Flag.code` 等，表示“结果是什么状态/事件”。

**简化规则（对外接口）**：  
- `Observation.code` 一律用 LOINC 表示“测量项目”；  
- 需要表达结论/状态/告警时，再用 SNOMED（如 Tachycardia、Fall 等）。

### 3.2 对外 FHIR 接口中 LOINC 的使用位置

对外提供 FHIR/HL7 接口时，**仅在以下场景使用 LOINC**（内部一律不用）：

- **生命体征 Observation**：  
  - 呼吸频率（Respiratory Rate, RR）：`Observation.code = 9279-1 (Respiratory rate)`  
  - 心率（Heart Rate, HR）：`Observation.code = 8867-4 (Heart rate)`  
- **姿态 / 运动 Observation**：  
  - 姿态：`Observation.code = 56903-8 (Body position)`  
  - 运动：`Observation.code = 68461-1 (Physical activity)`  

其他事件 / 告警（跌倒、心动过速、长时间无活动等）只需用 SNOMED（Safety / Physiological / HealthCondition），不需要额外的 LOINC。

---

## 二、固定格式模板（直接替换值）

### 2.1 生命体征观测模板（呼吸频率/心率）

```json
{
  "resourceType": "Observation",
  "status": "final",
  "category": [{
    "coding": [{
      "system": "http://terminology.hl7.org/CodeSystem/observation-category",
      "code": "vital-signs",
      "display": "Vital Signs"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "{{LOINC_CODE}}",
      "display": "{{LOINC_DISPLAY}}"
    }]
  },
  "subject": {
    "reference": "Patient/{{RESIDENT_UUID}}",
    "identifier": {
      "system": "http://wisefido.io/anonymous",
      "value": "{{ANONYMOUS_NAME}}"
    }
  },
  "effectiveDateTime": "{{TIMESTAMP}}",
  "valueQuantity": {
    "value": {{VALUE}},
    "unit": "{{UNIT}}",
    "system": "http://unitsofmeasure.org",
    "code": "{{UNIT_CODE}}"
  },
  "device": {
    "reference": "Device/{{DEVICE_UUID}}"
  }
}
```

**替换说明**：
- `{{LOINC_CODE}}`: 呼吸频率（Respiratory Rate, RR）用 `9279-1`，心率（Heart Rate, HR）用 `8867-4`
- `{{LOINC_DISPLAY}}`: 呼吸频率用 `Respiratory rate`，心率用 `Heart rate`
- `{{RESIDENT_UUID}}`: 住户UUID
- `{{ANONYMOUS_NAME}}`: 匿名代称（如"钟表匠"）
- `{{TIMESTAMP}}`: ISO 8601格式时间戳（如 `2025-01-15T10:30:00Z`）
- `{{VALUE}}`: 数值（如 `16`）
- `{{UNIT}}`: 单位（如 `/min`）
- `{{UNIT_CODE}}`: 单位代码（如 `/min`）
- `{{DEVICE_UUID}}`: 设备UUID

### 2.2 姿态观测模板

```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "56903-8",
      "display": "Body position"
    }]
  },
  "subject": {
    "reference": "Patient/{{RESIDENT_UUID}}",
    "identifier": {
      "system": "http://wisefido.io/anonymous",
      "value": "{{ANONYMOUS_NAME}}"
    }
  },
  "effectiveDateTime": "{{TIMESTAMP}}",
  "valueCodeableConcept": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "{{SNOMED_CODE}}",
      "display": "{{SNOMED_DISPLAY}}"
    }]
  },
  "device": {
    "reference": "Device/{{DEVICE_UUID}}"
  }
}
```

**替换说明**：
- `{{SNOMED_CODE}}`: 从映射表查（如 `383370001` 表示站立）
- `{{SNOMED_DISPLAY}}`: 从映射表查（如 `Standing position`）

### 2.3 运动状态观测模板

```json
{
  "resourceType": "Observation",
  "status": "final",
  "code": {
    "coding": [{
      "system": "http://loinc.org",
      "code": "68461-1",
      "display": "Motion state"
    }]
  },
  "subject": {
    "reference": "Patient/{{RESIDENT_UUID}}",
    "identifier": {
      "system": "http://wisefido.io/anonymous",
      "value": "{{ANONYMOUS_NAME}}"
    }
  },
  "effectiveDateTime": "{{TIMESTAMP}}",
  "valueCodeableConcept": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "{{SNOMED_CODE}}",
      "display": "{{SNOMED_DISPLAY}}"
    }]
  },
  "device": {
    "reference": "Device/{{DEVICE_UUID}}"
  }
}
```

### 2.4 安全告警模板（Flag）

```json
{
  "resourceType": "Flag",
  "status": "active",
  "category": [{
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "840539006",
      "display": "Safety alert"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "{{SNOMED_CODE}}",
      "display": "{{SNOMED_DISPLAY}}"
    }]
  },
  "subject": {
    "reference": "Patient/{{RESIDENT_UUID}}",
    "identifier": {
      "system": "http://wisefido.io/anonymous",
      "value": "{{ANONYMOUS_NAME}}"
    }
  },
  "period": {
    "start": "{{TIMESTAMP}}"
  },
  "author": {
    "reference": "Device/{{DEVICE_UUID}}",
    "display": "{{DEVICE_NAME}}"
  }
}
```

### 2.5 设备故障模板（DeviceMetric + Flag）

设备故障需要两个FHIR资源：
1. **DeviceMetric**：记录设备状态
2. **Flag**：告警标志

#### DeviceMetric模板

```json
{
  "resourceType": "DeviceMetric",
  "status": "{{STATUS}}",
  "type": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "462226007",
      "display": "Radar sensor"
    }]
  },
  "unit": {
    "coding": [{
      "system": "http://unitsofmeasure.org",
      "code": "1",
      "display": "Status"
    }]
  },
  "device": {
    "reference": "Device/{{DEVICE_UUID}}"
  },
  "calibration": [{
    "type": "offset",
    "state": "{{CALIBRATION_STATE}}",
    "time": "{{TIMESTAMP}}"
  }],
  "note": [{
    "text": "{{ERROR_DESCRIPTION}}"
  }]
}
```

**替换说明**：
- `{{STATUS}}`: `active`（正常）或 `off`（故障）
- `{{CALIBRATION_STATE}}`: `calibrated`（已校准）或 `not-calibrated`（未校准）
- `{{ERROR_DESCRIPTION}}`: 故障描述（如"传感器断线"）

#### Flag模板（设备故障告警）

```json
{
  "resourceType": "Flag",
  "status": "active",
  "category": [{
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "840539006",
      "display": "Safety alert"
    }]
  }],
  "code": {
    "coding": [{
      "system": "http://snomed.info/sct",
      "code": "282095001",
      "display": "{{ERROR_TYPE}}"
    }],
    "text": "{{ERROR_DESCRIPTION}}"
  },
  "subject": {
    "reference": "Device/{{DEVICE_UUID}}",
    "display": "{{DEVICE_NAME}}"
  },
  "period": {
    "start": "{{TIMESTAMP}}"
  },
  "author": {
    "reference": "Device/{{DEVICE_UUID}}",
    "display": "{{DEVICE_NAME}}"
  }
}
```

**替换说明**：
- `{{ERROR_TYPE}}`: 故障类型（如"Device malfunction"、"Sensor disconnected"）
- `{{ERROR_DESCRIPTION}}`: 详细故障描述
- `{{DEVICE_NAME}}`: 设备名称（如"Radar Sensor 001"）

---

## 三、简单转换函数（Python示例）

### 3.1 生命体征阈值判断函数

```python
# 心率阈值判断（来自 vue_radar 项目）
def get_heart_rate_danger_level(heart_rate: int, duration_seconds: int = 0) -> str:
    """
    根据心率值判断危险等级
    
    Args:
        heart_rate: 心率值（次/分钟）
        duration_seconds: 持续时长（秒），用于判断是否需要告警
    
    Returns:
        "EMERGENCY" (L1), "ALERT" (L2), "CRITICAL" (L3), 或 None (Normal)
    """
    if heart_rate is None or heart_rate <= 0:
        return None
    
    # L1: [0-44] 或 [116-∞]，持续≥1分钟
    if (heart_rate <= 44 or heart_rate >= 116):
        if duration_seconds >= 60:  # 持续1分钟
            return "EMERGENCY"  # L1
        else:
            return "CRITICAL"  # L3（未达到持续时长）
    
    # L2: [45-54] 或 [96-115]，持续≥5分钟
    if ((heart_rate >= 45 and heart_rate <= 54) or 
        (heart_rate >= 96 and heart_rate <= 115)):
        if duration_seconds >= 300:  # 持续5分钟
            return "ALERT"  # L2
        else:
            return "CRITICAL"  # L3（未达到持续时长）
    
    # Normal: [55-95]
    return None

# 呼吸频率阈值判断（来自 vue_radar 项目）
def get_respiratory_rate_danger_level(respiratory_rate: int, duration_seconds: int = 0) -> str:
    """
    根据呼吸频率值判断危险等级（Respiratory Rate, RR）
    
    Args:
        respiratory_rate: 呼吸频率值（次/分钟）
        duration_seconds: 持续时长（秒），用于判断是否需要告警
    
    Returns:
        "EMERGENCY" (L1), "ALERT" (L2), "CRITICAL" (L3), 或 None (Normal)
    """
    if respiratory_rate is None or respiratory_rate <= 0:
        return None
    
    # L1: [0-7] 或 [27-∞]，持续≥1分钟
    if (respiratory_rate <= 7 or respiratory_rate >= 27):
        if duration_seconds >= 60:  # 持续1分钟
            return "EMERGENCY"  # L1
        else:
            return "CRITICAL"  # L3（未达到持续时长）
    
    # L2: [8-9] 或 [24-26]，持续≥5分钟
    if ((respiratory_rate >= 8 and respiratory_rate <= 9) or 
        (respiratory_rate >= 24 and respiratory_rate <= 26)):
        if duration_seconds >= 300:  # 持续5分钟
            return "ALERT"  # L2
        else:
            return "CRITICAL"  # L3（未达到持续时长）
    
    # Normal: [10-23]
    return None
```

### 3.2 通用转换函数

```python
# 映射表配置（IT人员只需要维护这个表）
MAPPING_TABLE = {
    # 生命体征（基础测量项目）
    "RespiratoryRate": {
        "loinc_code": "9279-1",
        "loinc_display": "Respiratory rate",
        "snomed_code": "86290005",
        "snomed_display": "Respiratory rate",
        "unit": "/min",
        "unit_code": "/min"
    },
    "HeartRate": {
        "loinc_code": "8867-4",
        "loinc_display": "Heart rate",
        "snomed_code": "364075005",
        "snomed_display": "Heart rate",
        "unit": "/min",
        "unit_code": "/min"
    },
    "respiratory_rate": {
        "loinc_code": "9279-1",
        "loinc_display": "Respiratory rate",
        "snomed_code": "86290005",
        "snomed_display": "Respiratory rate",
        "unit": "/min",
        "unit_code": "/min"
    },
    "heart_rate": {
        "loinc_code": "8867-4",
        "loinc_display": "Heart rate",
        "snomed_code": "364075005",
        "snomed_display": "Heart rate",
        "unit": "/min",
        "unit_code": "/min"
    },
    # 姿态
    "posture_standing": {
        "snomed_code": "383370001",
        "snomed_display": "Standing position"
    },
    "posture_sitting": {
        "snomed_code": "402120000",
        "snomed_display": "Sitting position"
    },
    "posture_lying": {
        "snomed_code": "109030009",
        "snomed_display": "Lying position"
    },
    # 运动状态
    "motion_walking": {
        "snomed_code": "129006008",
        "snomed_display": "Walking"
    },
    "motion_static": {
        "snomed_code": "263821009",
        "snomed_display": "Static"
    },
    "motion_fall": {
        "snomed_code": "161898004",
        "snomed_display": "Fall"
    },
    # 睡眠状态
    "sleep_awake": {
        "snomed_code": "248220002",
        "snomed_display": "Awake"
    },
    "sleep_light": {
        "snomed_code": "248232005",
        "snomed_display": "Light sleep"
    },
    "sleep_deep": {
        "snomed_code": "248233000",
        "snomed_display": "Deep sleep"
    },
    # 设备故障
    "device_error": {
        "snomed_code": "282095001",
        "snomed_display": "Device malfunction"
    },
    "sensor_disconnected": {
        "snomed_code": "282095001",
        "snomed_display": "Sensor disconnected"
    },
    "communication_error": {
        "snomed_code": "282095001",
        "snomed_display": "Communication error"
    },
    "power_failure": {
        "snomed_code": "282095001",
        "snomed_display": "Power failure"
    }
}

def convert_to_fhir_observation(
    observation_type: str,  # "respiratory_rate", "heart_rate", "posture_standing", etc.
    resident_uuid: str,
    anonymous_name: str,
    device_uuid: str,
    timestamp: str,
    value: float = None,  # 仅用于生命体征
    snomed_code: str = None,  # 仅用于姿态/运动状态（如果映射表中没有）
    snomed_display: str = None
) -> dict:
    """
    简单转换函数：IT人员只需要调用这个函数，传入参数即可
    
    Args:
        observation_type: 观测类型（从MAPPING_TABLE中查找）
        resident_uuid: 住户UUID
        anonymous_name: 匿名代称（如"钟表匠"）
        device_uuid: 设备UUID
        timestamp: ISO 8601时间戳
        value: 数值（仅用于生命体征）
        snomed_code: SNOMED CT编码（可选，如果映射表中有则不需要）
        snomed_display: SNOMED CT显示名称（可选）
    
    Returns:
        FHIR Observation JSON
    """
    mapping = MAPPING_TABLE.get(observation_type)
    if not mapping:
        raise ValueError(f"Unknown observation type: {observation_type}")
    
    # 判断是生命体征还是姿态/运动状态
    if "loinc_code" in mapping:
        # 生命体征
        return {
            "resourceType": "Observation",
            "status": "final",
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                    "code": "vital-signs",
                    "display": "Vital Signs"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": mapping["loinc_code"],
                    "display": mapping["loinc_display"]
                }]
            },
            "subject": {
                "reference": f"Patient/{resident_uuid}",
                "identifier": {
                    "system": "http://wisefido.io/anonymous",
                    "value": anonymous_name
                }
            },
            "effectiveDateTime": timestamp,
            "valueQuantity": {
                "value": value,
                "unit": mapping["unit"],
                "system": "http://unitsofmeasure.org",
                "code": mapping["unit_code"]
            },
            "device": {
                "reference": f"Device/{device_uuid}"
            }
        }
    else:
        # 姿态/运动状态
        return {
            "resourceType": "Observation",
            "status": "final",
            "code": {
                "coding": [{
                    "system": "http://loinc.org",
                    "code": "56903-8" if "posture" in observation_type else "68461-1",
                    "display": "Body position" if "posture" in observation_type else "Motion state"
                }]
            },
            "subject": {
                "reference": f"Patient/{resident_uuid}",
                "identifier": {
                    "system": "http://wisefido.io/anonymous",
                    "value": anonymous_name
                }
            },
            "effectiveDateTime": timestamp,
            "valueCodeableConcept": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": snomed_code or mapping["snomed_code"],
                    "display": snomed_display or mapping["snomed_display"]
                }]
            },
            "device": {
                "reference": f"Device/{device_uuid}"
            }
        }

def convert_to_fhir_flag(
    alert_type: str,  # "fall", "fall_suspected", etc.
    resident_uuid: str,
    anonymous_name: str,
    device_uuid: str,
    device_name: str,
    timestamp: str,
    snomed_code: str = None,
    snomed_display: str = None
) -> dict:
    """
    转换安全告警为FHIR Flag
    
    Args:
        alert_type: 告警类型（从MAPPING_TABLE中查找）
        resident_uuid: 住户UUID
        anonymous_name: 匿名代称
        device_uuid: 设备UUID
        device_name: 设备名称
        timestamp: ISO 8601时间戳
        snomed_code: SNOMED CT编码（可选）
        snomed_display: SNOMED CT显示名称（可选）
    
    Returns:
        FHIR Flag JSON
    """
    mapping = MAPPING_TABLE.get(alert_type)
    if not mapping:
        # 如果没有映射，使用传入的编码
        if not snomed_code:
            raise ValueError(f"Unknown alert type: {alert_type} and no snomed_code provided")
    
    return {
        "resourceType": "Flag",
        "status": "active",
        "category": [{
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "840539006",
                "display": "Safety alert"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": snomed_code or mapping.get("snomed_code"),
                "display": snomed_display or mapping.get("snomed_display")
            }]
        },
        "subject": {
            "reference": f"Patient/{resident_uuid}",
            "identifier": {
                "system": "http://wisefido.io/anonymous",
                "value": anonymous_name
            }
        },
        "period": {
            "start": timestamp
        },
        "author": {
            "reference": f"Device/{device_uuid}",
            "display": device_name
        }
    }

def convert_to_fhir_device_error(
    error_type: str,  # "device_error", "sensor_disconnected", "communication_error", etc.
    device_uuid: str,
    device_name: str,
    timestamp: str,
    error_description: str,
    calibration_state: str = "not-calibrated"
) -> tuple:
    """
    转换设备故障为FHIR DeviceMetric和Flag
    
    Args:
        error_type: 故障类型（从MAPPING_TABLE中查找）
        device_uuid: 设备UUID
        device_name: 设备名称
        timestamp: ISO 8601时间戳
        error_description: 故障描述
        calibration_state: 校准状态（"calibrated"或"not-calibrated"）
    
    Returns:
        (DeviceMetric JSON, Flag JSON) 元组
    """
    mapping = MAPPING_TABLE.get(error_type)
    if not mapping:
        raise ValueError(f"Unknown error type: {error_type}")
    
    # DeviceMetric资源
    device_metric = {
        "resourceType": "DeviceMetric",
        "status": "off",  # 故障时状态为off
        "type": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "462226007",
                "display": "Radar sensor"
            }]
        },
        "unit": {
            "coding": [{
                "system": "http://unitsofmeasure.org",
                "code": "1",
                "display": "Status"
            }]
        },
        "device": {
            "reference": f"Device/{device_uuid}"
        },
        "calibration": [{
            "type": "offset",
            "state": calibration_state,
            "time": timestamp
        }],
        "note": [{
            "text": error_description
        }]
    }
    
    # Flag资源（告警）
    device_flag = {
        "resourceType": "Flag",
        "status": "active",
        "category": [{
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": "840539006",
                "display": "Safety alert"
            }]
        }],
        "code": {
            "coding": [{
                "system": "http://snomed.info/sct",
                "code": mapping.get("snomed_code", "282095001"),
                "display": mapping.get("snomed_display", "Device malfunction")
            }],
            "text": error_description
        },
        "subject": {
            "reference": f"Device/{device_uuid}",
            "display": device_name
        },
        "period": {
            "start": timestamp
        },
        "author": {
            "reference": f"Device/{device_uuid}",
            "display": device_name
        }
    }
    
    return device_metric, device_flag
```

### 3.3 使用示例

```python
# 示例1：转换呼吸频率（带危险等级判断，Respiratory Rate, RR）
respiratory_rate = 16  # 从设备获取
duration = 120  # 持续时长（秒）

# 先判断危险等级
danger_level = get_respiratory_rate_danger_level(respiratory_rate, duration)

# 转换为FHIR Observation
fhir_obs = convert_to_fhir_observation(
    observation_type="respiratory_rate",
    resident_uuid="123e4567-e89b-12d3-a456-426614174000",
    anonymous_name="钟表匠",
    device_uuid="device-001",
    timestamp="2025-01-15T10:30:00Z",
    value=respiratory_rate
)

# 如果有危险等级，创建Flag告警
if danger_level:
    fhir_flag = convert_to_fhir_flag(
        alert_type="respiratory_rate_alert",
        resident_uuid="123e4567-e89b-12d3-a456-426614174000",
        anonymous_name="钟表匠",
        device_uuid="device-001",
        device_name="Radar Sensor 001",
        timestamp="2025-01-15T10:30:00Z",
        snomed_code="30128008" if respiratory_rate >= 27 else "248546003"  # Tachypnea 或 Bradypnea
    )

# 示例2：转换姿态
fhir_obs = convert_to_fhir_observation(
    observation_type="posture_standing",
    resident_uuid="123e4567-e89b-12d3-a456-426614174000",
    anonymous_name="钟表匠",
    device_uuid="device-001",
    timestamp="2025-01-15T10:30:00Z"
)

# 示例3：转换跌倒告警
fhir_flag = convert_to_fhir_flag(
    alert_type="motion_fall",
    resident_uuid="123e4567-e89b-12d3-a456-426614174000",
    anonymous_name="钟表匠",
    device_uuid="device-001",
    device_name="Radar Sensor 001",
    timestamp="2025-01-15T10:35:00Z"
)

# 示例4：转换设备故障
device_metric, device_flag = convert_to_fhir_device_error(
    error_type="sensor_disconnected",
    device_uuid="device-001",
    device_name="Radar Sensor 001",
    timestamp="2025-01-15T10:40:00Z",
    error_description="传感器连接中断，无法获取数据"
)
```

---

## 四、完整映射表（Excel/CSV格式）

为了方便IT人员维护，提供Excel格式的完整映射表：

| TDP Tag Category | TDP Tag Code | 中文名称 | FHIR资源类型 | LOINC Code | SNOMED CT Code | SNOMED CT Display | 单位 | 单位代码 |
|-----------------|-------------|---------|-------------|-----------|---------------|------------------|------|---------|
| Physiological | RespiratoryRate | 呼吸频率（Respiratory Rate, RR） | Observation | 9279-1 | 86290005 | Respiratory rate | /min | /min |
| Physiological | HeartRate | 心率（Heart Rate, HR） | Observation | 8867-4 | 364075005 | Heart rate | /min | /min |
| Physiological | respiratory_rate | 呼吸频率（Respiratory Rate, RR） | Observation | 9279-1 | 86290005 | Respiratory rate | /min | /min |
| Physiological | heart_rate | 心率（Heart Rate, HR） | Observation | 8867-4 | 364075005 | Heart rate | /min | /min |
| Physiological | Tachycardia | 心动过速 | Observation | 8867-4 | 271636001 | Tachycardia | /min | /min |
| Physiological | Bradycardia | 心动过缓 | Observation | 8867-4 | 342400002 | Bradycardia | /min | /min |
| SleepState | Awake | 清醒 | Observation | - | 248220002 | Awake | - | - |
| SleepState | LightSleep | 浅睡眠 | Observation | - | 248232005 | Light sleep | - | - |
| SleepState | DeepSleep | 深睡眠 | Observation | - | 248233000 | Deep sleep | - | - |
| Posture | STANDING | 站立 | Observation | 56903-8 | 383370001 | Standing position | - | - |
| Posture | SITTING | 坐位 | Observation | 56903-8 | 402120000 | Sitting position | - | - |
| Posture | LYING | 仰卧 | Observation | 56903-8 | 109030009 | Lying position | - | - |
| MotionState | WALKING | 行走 | Observation | 68461-1 | 129006008 | Walking | - | - |
| MotionState | STATIC | 静止 | Observation | 68461-1 | 263821009 | Static | - | - |
| MotionState | ABNORMAL_GAIT | 异常步态 | Observation | 68461-1 | 22325002 | Abnormal gait | - | - |
| Safety | Fall | 跌倒 | Flag | - | 161898004 | Fall | - | - |
| Safety | Fall.Suspected | 疑似跌倒 | Flag | - | 129839007 | At risk for falls | - | - |
| DeviceError | DeviceError | 设备故障 | DeviceMetric + Flag | - | 282095001 | Device malfunction | - | - |
| DeviceError | SensorDisconnected | 传感器断线 | DeviceMetric + Flag | - | 282095001 | Sensor disconnected | - | - |
| DeviceError | CommunicationError | 通信故障 | DeviceMetric + Flag | - | 282095001 | Communication error | - | - |
| DeviceError | PowerFailure | 电源故障 | DeviceMetric + Flag | - | 282095001 | Power failure | - | - |

---

## 五、实施步骤

### Phase 1: 建立映射表（1周）
1. 将完整映射表导入数据库或配置文件
2. 创建转换函数库
3. 编写单元测试

### Phase 2: 集成到数据流（1周）
1. 在数据接收层调用转换函数
2. 验证转换后的FHIR资源
3. 存储到FHIR资源库

### Phase 3: 扩展和维护（持续）
1. 新增设备类型时，更新映射表
2. 新增观测类型时，添加到映射表
3. IT人员只需要维护映射表，不需要理解FHIR细节

---

## 六、最佳实践

1. **使用映射表**：所有编码都从映射表查找，不要硬编码
2. **固定模板**：使用提供的模板，只替换变量值
3. **统一函数**：使用转换函数，不要手动构建JSON
4. **验证数据**：转换后验证FHIR资源格式
5. **文档更新**：新增映射时，同步更新映射表文档

---

## 参考文档

- [person_matrix_snomed_tags.md](../person_matrix_snomed_tags.md) - TDP Tag编码规范（包含高级编码如帕金森、中风、心梗等）

