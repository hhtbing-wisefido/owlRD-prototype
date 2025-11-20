# WEB演示实现方案

**创建时间**: 2025-11-20 19:55  
**目的**: 通过Web界面完整演示所有功能和业务流程

---

## 🎯 演示目标

### 需要演示的核心功能

1. **租户和用户管理**
   - 多租户隔离
   - 用户角色权限

2. **住户管理**
   - 住户信息（匿名化）
   - 床位绑定
   - 护理人员分配

3. **设备和IoT数据**
   - 设备监控
   - 实时数据采集
   - 历史数据查询

4. **告警系统**
   - 多级告警(L1/L2/L3/L5)
   - 实时告警推送
   - 告警处理流程

5. **护理质量评估**
   - 监控覆盖率
   - 质量评分
   - 趋势分析

6. **实时WebSocket**
   - 实时数据推送
   - 告警通知
   - 状态更新

---

## ✅ 当前已有基础

### 前端页面 (5个)
- ✅ Dashboard - 总览
- ✅ Residents - 住户管理
- ✅ Devices - 设备管理
- ✅ Alerts - 告警中心
- ✅ CareQuality - 护理质量

### 后端API (37个端点)
- ✅ 完整的CRUD操作
- ✅ WebSocket实时推送
- ✅ 数据统计和分析

### 示例数据
- ✅ init_sample_data.py 脚本
- ✅ 基础演示数据已初始化

---

## 🚀 实现步骤

### Phase 1: 增强示例数据 (30分钟)

#### 1.1 创建丰富的演示场景

**目标**: 让数据更真实、更有故事性

**实现**:
```python
# scripts/init_demo_data.py

# 场景1: 正常监控
- 3个住户正常活动
- 设备正常上报数据
- 护理质量良好

# 场景2: 告警触发
- 1个住户触发跌倒告警
- 生命体征异常告警
- 离床告警

# 场景3: 护理质量问题
- 某房间长时间未巡视
- 监控覆盖率下降
- 异常事件增多
```

#### 1.2 添加时间序列数据

**目标**: 展示趋势和变化

```python
# 生成过去7天的IoT数据
for day in range(7):
    # 心率、呼吸率数据
    # 姿态变化数据
    # 位置轨迹数据
```

#### 1.3 创建演示账户

```python
# 不同角色的演示账户
admin_user = {
    "username": "demo_admin",
    "role": "ADMIN",
    "features": "all"
}

nurse_user = {
    "username": "demo_nurse",
    "role": "NURSE",
    "features": "limited"
}
```

---

### Phase 2: 添加演示模式功能 (1小时)

#### 2.1 创建演示控制面板

**新增组件**: `frontend/src/components/DemoControl.tsx`

```typescript
功能:
- 📊 演示场景切换
- ⏯️ 暂停/播放自动演示
- 🔄 重置演示数据
- 📝 演示流程说明
```

#### 2.2 实现场景切换

```typescript
// 场景列表
const demoScenarios = [
  {
    id: 'normal',
    name: '正常运营',
    description: '展示日常监控和数据采集'
  },
  {
    id: 'alert',
    name: '告警处理',
    description: '演示告警触发和处理流程'
  },
  {
    id: 'quality',
    name: '护理质量评估',
    description: '展示质量分析和报告'
  }
];
```

#### 2.3 添加自动演示功能

```typescript
// 自动播放演示
const autoDemo = {
  step1: '显示Dashboard总览',
  step2: '切换到住户管理',
  step3: '触发告警事件',
  step4: '展示实时数据',
  step5: '生成质量报告'
};
```

---

### Phase 3: 创建演示向导 (1小时)

#### 3.1 新增演示向导页面

**新组件**: `frontend/src/pages/DemoGuide.tsx`

```typescript
功能:
- 📖 演示步骤说明
- 🎯 功能亮点标注
- ▶️ 一键执行演示
- 📹 演示进度追踪
```

#### 3.2 实现交互式教程

```typescript
const tutorialSteps = [
  {
    target: '.dashboard',
    content: '这是系统总览，显示关键指标',
    action: () => navigate('/dashboard')
  },
  {
    target: '.alerts',
    content: '查看实时告警',
    action: () => triggerDemoAlert()
  },
  // ... 更多步骤
];
```

---

### Phase 4: 增强前端交互 (1.5小时)

#### 4.1 添加实时数据模拟

**新建**: `frontend/src/utils/demoDataGenerator.ts`

```typescript
// 模拟实时数据生成
export function generateRealtimeData() {
  return {
    heartRate: randomInRange(60, 100),
    respirationRate: randomInRange(12, 20),
    posture: randomPosture(),
    timestamp: new Date().toISOString()
  };
}
```

#### 4.2 增强WebSocket演示

```typescript
// 模拟WebSocket事件
function simulateWebSocketEvents() {
  // 每5秒推送新数据
  setInterval(() => {
    const event = generateDemoEvent();
    handleWebSocketMessage(event);
  }, 5000);
}
```

#### 4.3 添加可视化效果

```typescript
// 数据变化动画
- 实时图表更新动画
- 告警闪烁效果
- 状态变化过渡
```

---

### Phase 5: 创建演示文档 (30分钟)

#### 5.1 演示脚本

**创建**: `项目记录/演示脚本.md`

```markdown
# 系统演示脚本

## 场景1: 日常监控 (2分钟)
1. 打开Dashboard
2. 查看住户状态
3. 查看设备运行情况
4. 展示实时数据更新

## 场景2: 告警处理 (3分钟)
1. 触发跌倒告警
2. 展示告警通知
3. 查看告警详情
4. 演示处理流程

## 场景3: 护理质量 (2分钟)
1. 查看质量报告
2. 展示覆盖率统计
3. 查看趋势分析
4. 显示改进建议
```

#### 5.2 功能演示清单

**创建**: `项目记录/演示功能清单.md`

```markdown
# 演示功能清单

## 数据管理
- [ ] 租户信息展示
- [ ] 用户管理
- [ ] 住户列表
- [ ] 设备列表

## 实时监控
- [ ] 实时数据采集
- [ ] WebSocket推送
- [ ] 状态更新

## 告警系统
- [ ] 告警触发
- [ ] 告警通知
- [ ] 告警历史

## 护理质量
- [ ] 质量评分
- [ ] 趋势分析
- [ ] 报告生成

## 数据可视化
- [ ] Dashboard仪表盘
- [ ] 实时图表
- [ ] 统计图表
```

---

## 📝 具体实现代码

### 1. 增强示例数据脚本

**文件**: `scripts/init_demo_data.py`

```python
"""
完整演示数据初始化脚本
包含多个演示场景的数据
"""

def create_demo_scenario_normal():
    """场景1: 正常运营"""
    # 3个住户，各有设备，数据正常
    pass

def create_demo_scenario_alerts():
    """场景2: 告警事件"""
    # 触发各种告警
    pass

def create_demo_scenario_quality():
    """场景3: 质量问题"""
    # 模拟质量下降场景
    pass
```

### 2. 演示控制组件

**文件**: `frontend/src/components/DemoControl.tsx`

```typescript
import React, { useState } from 'react';

export function DemoControl() {
  const [scenario, setScenario] = useState('normal');
  const [isPlaying, setIsPlaying] = useState(false);

  const scenarios = [
    { id: 'normal', name: '正常运营' },
    { id: 'alert', name: '告警处理' },
    { id: 'quality', name: '护理质量' }
  ];

  const switchScenario = (scenarioId: string) => {
    // 调用API切换场景
    fetch(`/api/v1/demo/scenario/${scenarioId}`, {
      method: 'POST'
    });
    setScenario(scenarioId);
  };

  return (
    <div className="demo-control">
      <h3>演示控制</h3>
      <div className="scenarios">
        {scenarios.map(s => (
          <button 
            key={s.id}
            onClick={() => switchScenario(s.id)}
            className={scenario === s.id ? 'active' : ''}
          >
            {s.name}
          </button>
        ))}
      </div>
      <button onClick={() => setIsPlaying(!isPlaying)}>
        {isPlaying ? '⏸️ 暂停' : '▶️ 播放'}
      </button>
    </div>
  );
}
```

### 3. 演示向导页面

**文件**: `frontend/src/pages/DemoGuide.tsx`

```typescript
import React, { useState } from 'react';

export default function DemoGuide() {
  const [currentStep, setCurrentStep] = useState(0);

  const steps = [
    {
      title: '欢迎使用owlRD演示系统',
      description: '这个向导将带你了解系统的核心功能',
      action: null
    },
    {
      title: 'Dashboard总览',
      description: '查看系统关键指标和实时状态',
      action: () => navigate('/dashboard')
    },
    {
      title: '住户管理',
      description: '了解如何管理住户信息',
      action: () => navigate('/residents')
    },
    {
      title: '告警系统',
      description: '体验实时告警和通知',
      action: () => {
        navigate('/alerts');
        triggerDemoAlert();
      }
    },
    {
      title: '护理质量',
      description: '查看质量评估报告',
      action: () => navigate('/care-quality')
    }
  ];

  const next = () => {
    if (currentStep < steps.length - 1) {
      const nextStep = steps[currentStep + 1];
      if (nextStep.action) {
        nextStep.action();
      }
      setCurrentStep(currentStep + 1);
    }
  };

  return (
    <div className="demo-guide">
      <div className="step-indicator">
        步骤 {currentStep + 1} / {steps.length}
      </div>
      <h2>{steps[currentStep].title}</h2>
      <p>{steps[currentStep].description}</p>
      <button onClick={next}>
        {currentStep < steps.length - 1 ? '下一步 →' : '完成'}
      </button>
    </div>
  );
}
```

---

## 🎬 演示流程设计

### 完整演示流程 (10分钟)

#### 第1分钟: 系统概览
1. 打开首页，显示欢迎界面
2. 展示系统架构图
3. 说明核心功能模块

#### 第2-3分钟: Dashboard
1. 展示关键指标卡片
2. 实时数据更新
3. WebSocket连接状态

#### 第4-5分钟: 住户和设备管理
1. 查看住户列表（匿名化）
2. 查看设备监控状态
3. 展示绑定关系

#### 第6-7分钟: 告警演示
1. 触发跌倒告警
2. 显示实时通知
3. 查看告警详情
4. 演示处理流程

#### 第8-9分钟: 护理质量
1. 展示质量评分
2. 查看趋势图表
3. 显示改进建议

#### 第10分钟: 总结
1. 回顾核心功能
2. 展示技术亮点
3. Q&A

---

## ⚡ 快速启动方案

### 方案A: 最小实现 (2小时)

**只需要做**:
1. ✅ 增强现有示例数据（添加更多场景）
2. ✅ 在Dashboard添加演示控制按钮
3. ✅ 编写演示脚本文档

**可以演示**:
- 所有页面和基础功能
- 手动切换场景
- 按脚本演示

---

### 方案B: 完整实现 (1天)

**需要做**:
1. ✅ 创建完整演示数据
2. ✅ 实现演示控制面板
3. ✅ 添加演示向导
4. ✅ 增强交互效果
5. ✅ 编写完整文档

**可以演示**:
- 自动化演示流程
- 场景一键切换
- 交互式教程
- 所有高级功能

---

## 📋 检查清单

### 演示前准备
- [ ] 后端服务启动正常
- [ ] 前端开发服务器运行
- [ ] 示例数据已初始化
- [ ] WebSocket连接正常
- [ ] 所有API端点可访问

### 演示内容
- [ ] Dashboard显示数据
- [ ] 住户列表加载
- [ ] 设备状态正常
- [ ] 告警可以触发
- [ ] 图表正常显示
- [ ] WebSocket实时更新

### 演示效果
- [ ] 页面加载流畅
- [ ] 数据更新及时
- [ ] 交互响应快速
- [ ] 视觉效果美观

---

## 🎯 下一步行动

### 立即可做 (方案A - 2小时)

1. **增强示例数据** (1小时)
   ```bash
   # 运行增强脚本
   python scripts/init_demo_data.py
   ```

2. **编写演示脚本** (30分钟)
   - 创建演示流程文档
   - 准备演示说明

3. **测试演示流程** (30分钟)
   - 启动服务
   - 按脚本演示
   - 记录问题

### 完整实现 (方案B - 1天)

按Phase 1-5顺序实施

---

**创建时间**: 2025-11-20 19:55  
**预估时间**: 方案A 2小时 / 方案B 1天  
**推荐**: 先实现方案A，满足基本演示需求
