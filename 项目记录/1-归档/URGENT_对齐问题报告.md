# 🚨 紧急：数据对齐问题报告

**生成时间**: 2025-11-21  
**问题等级**: CRITICAL  
**影响范围**: init_sample_data.py �?Model 定义严重不一�?
---

## 问题1: IoT时序数据字段完全不匹�?
### 源参�?(12_iot_timeseries.sql)
```sql
-- 必需字段
tenant_id, device_id, timestamp
tracking_id, radar_pos_x, radar_pos_y, radar_pos_z
heart_rate, respiratory_rate
raw_original, raw_format
location_id, room_id
```

### 实际Model (iot_data.py - IOTTimeseries)
```python
�?完全对齐源SQL，字段齐全：
- tracking_id, radar_pos_x/y/z
- heart_rate, respiratory_rate  
- raw_original, raw_format, raw_compression
- posture_snomed_code, event_type
- sleep_state_snomed_code
- location_id, room_id
```

### init_sample_data.py 实际生成的数�?```python
�?严重不匹配：
{
    "id": str(uuid4()),  # �?应该是BIGSERIAL自增，不是UUID
    "tenant_id": SAMPLE_TENANT_ID,  # �?    "device_id": SAMPLE_DEVICE_ID,  # �?    "resident_id": SAMPLE_RESIDENT_ID,  # �?Model没有此字段！
    "bed_id": SAMPLE_BED_ID,  # �?重复，应该只在location_id/room_id
    "location_id": SAMPLE_LOCATION_ID,  # �?    "timestamp": timestamp.isoformat(),  # �?    "heart_rate": random.randint(60, 80),  # �?    "respiration_rate": random.randint(12, 18),  # �?字段名错误！应该是respiratory_rate
    "motion_intensity": round(random.uniform(0.1, 0.5), 2),  # �?Model没有此字段！
    "presence": True,  # �?Model没有此字段！
    "in_bed": True,  # �?Model没有此字段！
    "alert_triggered": False,  # �?不应在iot_timeseries�?    "data_source": "TDP",  # �?Model没有此字段！
    "created_at": timestamp.isoformat()  # �?}
```

### 缺失的必需字段
```python
�?以下字段是Model必需的，但init_sample_data.py没有生成�?- tracking_id (必需，默认值可以是0或NULL)
- radar_pos_x (必需)
- radar_pos_y (必需)
- radar_pos_z (必需)
- raw_original (必需，bytes类型)
- raw_format (必需，如"json")
```

---

## 问题2: 检查清单标�?00%，但实际未对�?
**检查清�?*: 
```
| 12 | 12_iot_timeseries.sql | �?| �?| �?| �?| 🔵 | �?| **100%** |
```

**实际情况**:
- �?后端Model：对齐正�?(iot_data.py)
- �?后端API：存�?(iot_data.py)
- �?**示例数据：严重不一�?* (init_sample_data.py)

**结论**: 检查清单的"示例数据 �?�?*错误标记**�?
---

## 根本原因分析

### 为什么会出现不一致？

1. **Model是正确的**：iot_data.py严格按照SQL定义
2. **init_sample_data.py是旧代码**：可能是早期版本，未更新
3. **没有自动化验�?*：缺少脚本验证示例数据是否符合Model

### 为什么检查清单标�?00%�?
可能�?*只检查了文件存在**，没有检�?*字段对齐�?*�?
---

## 修复方案

### 立即修复 init_sample_data.py

```python
# 正确的IoT数据生成
async def init_iot_data():
    """初始化IoT数据 - 严格对齐 12_iot_timeseries.sql"""
    print("\n📊 Creating sample IoT data...")
    storage = StorageService("iot_timeseries")
    
    now = datetime.now()
    
    for i in range(24):
        timestamp = now - timedelta(hours=i)
        
        # 模拟原始数据
        raw_data = {
            "device_type": "Radar",
            "timestamp": timestamp.isoformat(),
            "tracking": {"id": 0, "x": 150, "y": 200, "z": 100},
            "vitals": {"hr": random.randint(60, 80), "rr": random.randint(12, 18)}
        }
        
        iot_data = {
            # 设备索引
            "tenant_id": SAMPLE_TENANT_ID,
            "device_id": SAMPLE_DEVICE_ID,
            
            # 时间�?            "timestamp": timestamp.isoformat(),
            
            # TDP分类
            "tdp_tag_category": "Physiological",
            
            # 轨迹数据（必需�?            "tracking_id": 0,  # 0-7，NULL表示无人
            "radar_pos_x": 150,  # 厘米
            "radar_pos_y": 200,
            "radar_pos_z": 100,
            
            # 姿态（可选）
            "posture_snomed_code": "102538003",  # Lying position
            "posture_display": "Lying position",
            
            # 生命体征
            "heart_rate": random.randint(60, 80),
            "respiratory_rate": random.randint(12, 18),  # �?正确字段�?            
            # 睡眠状�?            "sleep_state_snomed_code": "248233000",  # Deep sleep
            "sleep_state_display": "Deep sleep",
            
            # 位置信息
            "location_id": SAMPLE_LOCATION_ID,
            "room_id": SAMPLE_ROOM_ID,
            
            # 置信�?            "confidence": 95,
            
            # 原始记录（必需�?            "raw_original": json.dumps(raw_data).encode('utf-8'),  # �?bytes类型
            "raw_format": "json",  # �?必需
            "raw_compression": None,
            
            # 元数�?            "metadata": {},
            
            "created_at": timestamp.isoformat()
        }
        
        storage.create(iot_data)
```

---

## 建议的自动化验证

### 创建验证脚本 `validate_sample_data.py`

```python
"""验证示例数据是否符合Model定义"""

from app.models.iot_data import IOTTimeseriesCreate
from init_sample_data import init_iot_data

def validate_iot_data():
    # 1. 读取生成的数�?    storage = StorageService("iot_timeseries")
    samples = storage.load_all()
    
    # 2. 用Pydantic Model验证
    for sample in samples:
        try:
            IOTTimeseriesCreate(**sample)
            print(f"�?Valid: {sample['id']}")
        except Exception as e:
            print(f"�?Invalid: {sample['id']}, Error: {e}")
```

---

## 下一步行�?
1. �?**立即修复** init_sample_data.py �?init_iot_data() 函数
2. �?**检查其他表**的示例数据是否对�?3. �?**更新检查清�?*：标记真实的对齐状�?4. �?**创建验证脚本**：防止未来再次不一�?5. �?**重新初始化数�?*：用正确的脚本生�?
---

**优先�?*: P0 - 必须立即修复  
**估计时间**: 30分钟  
**风险**: 如不修复，系统无法正常演示IoT功能
