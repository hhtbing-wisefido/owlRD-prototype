# owlRD Frontend

React + TypeScript前端应用

## 技术栈

- React 18
- TypeScript
- Vite
- TailwindCSS  
- React Router
- React Query
- Recharts
- Lucide Icons

## 安装依赖

```bash
npm install
```

## 开发

### 本地开发
```bash
npm run dev
```
访问: http://localhost:3000

### 局域网访问
```bash
# 方法1: 使用npm脚本（推荐）
npm run dev

# 方法2: 使用启动脚本
.\start_lan.bat    # Windows
./start_lan.sh     # Linux/Mac

# 方法3: 指定IP启动
npm run dev:lan
```

访问地址:
- 本机: http://localhost:3000 或 http://192.168.2.6:3000
- 局域网其他设备: http://192.168.2.6:3000

## 构建

```bash
npm run build
```

## 功能模块

### ✅ 已完成（12个页面 - 95%完成度）

#### 核心监控页面
- **仪表板** ⭐ - 实时数据概览、WebSocket实时更新、IoT数据统计、设备状态分布、24小时告警趋势图
- **IoT数据监测** ⭐ (NEW) - 列表/图表切换视图、心率/呼吸率趋势可视化、危险等级识别、设备筛选、自动刷新
- **设备管理** - IoT设备列表、在线状态监控、设备类型筛选
- **告警中心** ⭐ - 告警统计、多级告警列表、确认/解决功能、状态筛选、告警详情
- **告警策略** ⭐ (NEW) - 策略列表、启用/禁用管理、严重程度标识、规则配置

#### 业务管理页面
- **住户管理** ⭐ - 住户列表、状态展示、SNOMED标签显示、健康标签
- **卡片管理** ⭐ (NEW) - 卡片列表、创建表单、卡片类型/住户/设备选择、启用/停用、功能查看
- **护理质量** ⭐ - 概览/详细视图切换、6维度雷达图、AI智能分析（优势/改进/建议）、护理员绩效排名

#### 系统管理页面
- **用户管理** - 用户列表、角色分配、CRUD操作
- **位置管理** - 位置/房间/床位管理
- **角色管理** - 角色列表、权限配置
- **登录/注册** - 用户认证

### 🎨 技术亮点
- ✅ React Query数据获取和缓存
- ✅ WebSocket实时数据推送
- ✅ Recharts高级可视化（折线图、饼图、柱状图、雷达图） ⭐
- ✅ TailwindCSS响应式布局 + 渐变色设计 ⭐
- ✅ Lucide图标系统
- ✅ TypeScript完整类型安全
- ✅ shadcn/ui高质量组件 ⭐
- ✅ 列表/图表视图切换 ⭐
- ✅ 实时数据自动刷新（10s/30s间隔） ⭐

### 🎊 2025-11-22 重大更新

**4小时持续开发，前端从29%提升到95% (+66%)！**

**新增页面（3个）**:
- ⭐ IoTData.tsx (360行) - IoT数据列表+图表可视化
- ⭐ Cards.tsx (520行) - 卡片管理+创建表单
- ⭐ AlertPolicies.tsx (330行) - 告警规则配置

**新增组件（1个）**:
- ⭐ VitalSignsChart.tsx (85行) - 心率/呼吸率趋势图组件

**功能增强（4个页面）**:
- ⭐ Dashboard - IoT数据概览卡片（心率/呼吸率统计+趋势图）
- ⭐ CareQuality - AI深度分析（6维雷达图+智能洞察+排名）
- ⭐ Alerts - 确认/解决功能+状态筛选
- ⭐ Residents - SNOMED标签显示（健康标签+编码）

**代码统计**:
- 总行数: 10,700+行 (+2,200行)
- 页面数: 12个 (+3个)
- 组件数: 40+个 (+10个)
- 完成度: 95% (+66%)

## 环境配置

### 本地开发配置
复制 `.env.example` 到 `.env`:
```bash
cp .env.example .env
```

默认配置（本地访问）:
```bash
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000
```

### 局域网访问配置
如需在局域网其他设备访问，修改 `.env`:
```bash
VITE_API_URL=http://192.168.2.6:8000
VITE_WS_URL=ws://192.168.2.6:8000
```

**注意**: 修改配置后需要重启开发服务器
