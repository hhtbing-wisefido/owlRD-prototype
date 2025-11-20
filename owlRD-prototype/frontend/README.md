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

### ✅ 已完成
- **仪表板** - 实时数据概览、WebSocket实时更新、设备状态分布、24小时告警趋势图
- **住户管理** - 住户列表、状态展示
- **设备管理** - IoT设备列表、在线状态监控
- **告警中心** - 告警统计、多级告警列表
- **护理质量** - 护理质量评分、响应时间趋势、时间分布、班次效率对比、改进建议

### 🎨 技术亮点
- ✅ React Query数据获取和缓存
- ✅ WebSocket实时数据推送
- ✅ Recharts数据可视化（折线图、饼图、柱状图）
- ✅ TailwindCSS响应式布局
- ✅ Lucide图标系统
- ✅ TypeScript类型安全

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
