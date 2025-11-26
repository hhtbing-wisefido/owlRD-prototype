# 人员矩阵TDP Tag字段SNOMED CT编码标准

## 概述

本文档基于人员矩阵(Person Matrix)数据结构，为老人监测系统提供标准化的SNOMED CT编码规范。重点关注`posture`、`motion_state`和`health_score`三个Tag字段的编码标准，确保与医疗健康信息系统的互操作性。

---

## 人员矩阵核心字段映射

### TDP Tag字段结构
```protobuf
message Tag {
  string category = 1;    // 分类标识
  string code = 2;        // SNOMED CT编码
  string display = 3;     // 可读描述(可选)
}
```

### 核心监测字段
- **posture**: 姿态状态 → `Tag {category: "Posture", code: "SNOMED_CODE"}`
- **motion_state**: 运动状态 → `Tag {category: "MotionState", code: "SNOMED_CODE"}`  
- **health_score**: 健康评分 → `Tag {category: "HealthCondition", code: "SNOMED_CODE"}`

---

## 一、姿态编码 (Posture Category)

### 1.1 基础体位姿态

| SNOMED CT编码 | TDP Tag Code | 中文描述 | 英文描述 | 应用场景 |
|---------------|-------------|---------|---------|---------|
| 102538003 | STANDING | 站立 | Standing position | 日常活动监测、转移评估 |
| 102491009 | SITTING | 坐位 | Sitting position | 静态活动、椅子转移 |
| 40199007 | LYING_SUPINE | 仰卧 | Supine body position | 床位监测、睡眠分析 |
| 102535000 | LYING_SIDE | 侧卧 | Lying on side | 睡眠姿态、压疮预防 |
| 1240000 | LYING_PRONE | 俯卧 | Prone body position | 特殊体位监测 |
| 33586001 | KNEELING | 跪姿 | Kneeling | 特殊动作识别 |
| 26527006 | RECUMBENT | 半卧 | Recumbent position | 康复训练、休息状态 |

### 1.2 异常姿态

| SNOMED CT编码 | TDP Tag Code | 中文描述 | 英文描述 | 监测意义 |
|---------------|-------------|---------|---------|---------|
| 43029002 | ABNORMAL_POSTURE | 异常姿势 | Abnormal posture | **跌倒风险、疾病征象** |
| 8652009 | OPISTHOTONUS | 角弓反张 | Opisthotonus | 神经系统异常 |
| 271594007 | BRADYKINETIC_POSTURE | 运动迟缓性姿态 | Bradykinetic posture | 帕金森病特征 |

### 1.3 特定环境姿态

| SNOMED CT编码 | TDP Tag Code | 中文描述 | 英文描述 | 应用场景 |
|---------------|-------------|---------|---------|---------|
| 364830008 | POSTURAL_FINDING | 姿态发现 | Finding of body posture | 综合姿态评估 |
| 10904000 | ORTHOSTATIC | 直立体位 | Orthostatic position | 直立性低血压监测 |

---

## 二、运动状态编码 (MotionState Category)

### 2.1 基础运动状态

| SNOMED CT编码 | TDP Tag Code | 中文描述 | 英文描述 | 状态定义 |
|---------------|-------------|---------|---------|---------|
| 129006008 | WALKING | 行走中 | Walking | 正常步行状态 |
| 415568008 | MOVING | 移动中 | Moving | 一般性移动活动 |
| 263821009 | STATIC | 静止 | Static | 无明显位移 |
| 414549008 | STANDING_UP | 起立中 | Standing up | 转移动作进行中 |
| 300845008 | SITTING_DOWN | 坐下中 | Sitting down | 转移动作进行中 |

### 2.2 异常运动状态

| SNOMED CT编码 | TDP Tag Code | 中文描述 | 英文描述 | 临床意义 |
|---------------|-------------|---------|---------|---------|
| 22325002 | ABNORMAL_GAIT | 异常步态 | Abnormal gait | **疾病进展指标** |
| 249911004 | SHUFFLING_GAIT | 拖曳步态 | Shuffling gait | 帕金森病典型步态 |
| 16973004 | ATAXIC_GAIT | 共济失调步态 | Ataxic gait | 脑血管疾病指征 |
| 22160007 | FESTINATING_GAIT | 慌张步态 | Festinating gait | 帕金森病进展期 |
| 397776000 | FREEZING_GAIT | 步态冻结 | Freezing of gait | 帕金森病严重症状 |
| 102557002 | DIFFICULTY_WALKING | 行走困难 | Difficulty walking | 功能障碍评估 |

### 2.3 特定运动模式

| SNOMED CT编码 | TDP Tag Code | 中文描述 | 英文描述 | 监测价值 |
|---------------|-------------|---------|---------|---------|
| 1055001 | BRADYKINESIA | 运动迟缓 | Bradykinesia | 帕金森病核心症状 |
| 105723007 | CATATONIC | 紧张性运动 | Catatonic behavior | 精神状态异常 |
| 278273003 | MOVEMENT_DIFFICULTY | 运动困难 | Difficulty moving | 整体功能评估 |

---

## 三、健康状况编码 (HealthCondition Category)

### 3.1 核心疾病状态

| SNOMED CT编码 | TDP Tag Code | 中文描述 | 英文描述 | 监测级别 |
|---------------|-------------|---------|---------|---------|
| 49049000 | PARKINSONS_DISEASE | 帕金森病 | Parkinson's disease | 🔴 **重点监测** |
| 230690007 | CEREBROVASCULAR_ACCIDENT | 脑血管意外 | Cerebrovascular accident | 🔴 **重点监测** |
| 22298006 | MYOCARDIAL_INFARCTION | 心肌梗死 | Myocardial infarction | 🔴 **重点监测** |
| 422504002 | ISCHEMIC_STROKE | 缺血性脑卒中 | Ischemic stroke | 🔴 **重点监测** |
| 195189003 | HEMORRHAGIC_STROKE | 出血性脑卒中 | Hemorrhagic stroke | 🔴 **重点监测** |

### 3.2 关键症状与发现

| SNOMED CT编码 | TDP Tag Code | 中文描述 | 英文描述 | 预警价值 |
|---------------|-------------|---------|---------|---------|
| 161898004 | FALL_EVENT | 跌倒事件 | Fall | 🔴 **紧急事件** |
| 129839007 | FALL_RISK | 跌倒风险 | At risk for falls | 🟡 **风险预警** |
| 26079004 | TREMOR | 震颤 | Tremor | 🟡 **症状监测** |
| 29857009 | CHEST_PAIN | 胸痛 | Chest pain | 🟡 **症状监测** |
| 7006003 | RIGIDITY | 肌肉僵硬 | Rigidity | 🟡 **症状监测** |

### 3.3 功能状态评估

| SNOMED CT编码 | TDP Tag Code | 中文描述 | 英文描述 | 评估维度 |
|---------------|-------------|---------|---------|---------|
| 50582007 | HEMIPLEGIA | 偏瘫 | Hemiplegia | 运动功能障碍 |
| 37340000 | APHASIA | 失语 | Aphasia | 认知功能障碍 |
| 194828000 | ANGINA_PECTORIS | 心绞痛 | Angina pectoris | 心脏功能状态 |
| 233823007 | SILENT_MI | 无症状心梗 | Silent myocardial infarction | 隐匿性疾病 |

---

## 四、TDP协议集成示例

### 4.1 完整Person Matrix结构示例

```c
typedef struct {
    uint64_t id;                    // TDP producer_id(48位) + tracking_id(16位)
    uint16_t tracking_id;           // 传感器本地跟踪ID
    
    // 空间位置信息
    int16_t pos_x, pos_y, pos_z;    // 三维坐标(cm)
    int16_t vel_x, vel_y, vel_z;    // 三维速度(cm/秒)
    uint8_t height;                 // 身高(cm)
    
    // 时间戳信息
    uint64_t start_time_ts;         // 开始静止时间
    uint64_t last_update_ts;        // 最后更新时间
    uint64_t last_movement_ts;      // 上次移动时间
    uint64_t last_posture_change_ts; // 上次姿态变化时间
    
    // TDP Tag字段 - 使用SNOMED CT编码
    Tag posture;                    // 姿态状态
    Tag motion_state;               // 运动状态  
    Tag health_score;               // 健康状况
    
    // 系统字段
    int confidence;                 // 跟踪置信度(0-100)
    uint8_t reserved_tag;           // 云端标签ID
    float reserved_value;           // 关联数值
    uint32_t local_tags;            // 本地决策位掩码
} PersonMatrix;
```

### 4.2 典型监测场景Tag配置

**场景1：帕金森病患者步态监测**
```c
PersonMatrix patient = {
    .posture = {
        .category = "Posture",
        .code = "102538003",        // STANDING
        .display = "Standing position"
    },
    .motion_state = {
        .category = "MotionState", 
        .code = "249911004",        // SHUFFLING_GAIT
        .display = "Shuffling gait"
    },
    .health_score = {
        .category = "HealthCondition",
        .code = "49049000",         // PARKINSONS_DISEASE
        .display = "Parkinson's disease"
    }
};
```

**场景2：跌倒风险预警**
```c
PersonMatrix elderly = {
    .posture = {
        .category = "Posture",
        .code = "43029002",         // ABNORMAL_POSTURE
        .display = "Abnormal posture"
    },
    .motion_state = {
        .category = "MotionState",
        .code = "22325002",         // ABNORMAL_GAIT
        .display = "Abnormal gait"
    },
    .health_score = {
        .category = "HealthCondition",
        .code = "129839007",        // FALL_RISK
        .display = "At risk for falls"
    }
};
```

**场景3：急性心梗预警**
```c
PersonMatrix cardiac_patient = {
    .posture = {
        .category = "Posture",
        .code = "102491009",        // SITTING
        .display = "Sitting position"
    },
    .motion_state = {
        .category = "MotionState",
        .code = "263821009",        // STATIC
        .display = "Static"
    },
    .health_score = {
        .category = "HealthCondition",
        .code = "29857009",         // CHEST_PAIN
        .display = "Chest pain"
    }
};
```

---

## 五、实施建议

### 5.1 优先级分级

**🔴 紧急级别 (Emergency)**
- 跌倒事件 (161898004)
- 心肌梗死 (22298006) 
- 脑血管意外 (230690007)

**🟡 警告级别 (Warning)**
- 异常步态 (22325002)
- 跌倒风险 (129839007)
- 胸痛症状 (29857009)

**🟢 监测级别 (Monitoring)**
- 基础姿态变化
- 正常运动状态
- 日常功能评估

### 5.2 系统集成要点

1. **编码标准化**
   - 严格使用SNOMED CT国际标准编码
   - 建立本地编码映射表
   - 定期同步最新版本

2. **数据一致性**
   - posture、motion_state、health_score三字段协调一致
   - 时间戳字段与Tag状态同步更新
   - 置信度与编码准确性关联

3. **互操作性**
   - 支持HL7 FHIR资源映射
   - 兼容电子病历系统
   - 满足医疗数据交换标准

### 5.3 质量控制

1. **编码验证**
   - 实时验证SNOMED CT编码有效性
   - 检查category与code的一致性
   - 监控编码使用频率和准确性

2. **临床验证**
   - 定期与医疗专家验证编码适用性
   - 收集临床反馈优化编码选择
   - 建立异常情况处理机制

---

## 六、附录：快速查询表

### 常用姿态编码速查
```
STANDING (102538003) → 站立
SITTING (102491009) → 坐位  
LYING_SUPINE (40199007) → 仰卧
ABNORMAL_POSTURE (43029002) → 异常姿势
```

### 常用运动状态编码速查
```
WALKING (129006008) → 行走
STATIC (263821009) → 静止
ABNORMAL_GAIT (22325002) → 异常步态
SHUFFLING_GAIT (249911004) → 拖曳步态
```

### 常用健康状况编码速查
```
PARKINSONS_DISEASE (49049000) → 帕金森病
CEREBROVASCULAR_ACCIDENT (230690007) → 脑卒中
MYOCARDIAL_INFARCTION (22298006) → 心肌梗死
FALL_EVENT (161898004) → 跌倒事件
```

---

*版本：1.0*  
*最后更新：2025年9月*  
*兼容：SNOMED CT 2024国际版、TDPv2协议*