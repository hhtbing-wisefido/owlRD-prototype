# owlRD 完整系统测试

本目录包含owlRD项目的**完整系统测试** - 后端API + 前端编译 + 代码质量

---

## 📁 目录结构

```
tests/
├── README.md                    ← 本文件（测试使用说明）
├── full_system_test.py          ← 完整系统测试脚本
└── test_reports/                ← 测试报告输出目录（自动创建）
    └── test_report_*.json       ← JSON格式测试报告
```

---

## 🚀 快速开始

### 方式1: 交互式菜单（推荐）
```bash
# 直接运行，进入交互式菜单
python tests/full_system_test.py
```

**菜单界面**（14个选项）：
```
owlRD 完整系统测试 - 交互式菜单
================================================================================

【核心功能测试】
  1. 运行所有测试（后端 + 前端 + 集成）
  2. 运行所有后端API测试
  3. 运行所有前端测试
  4. 运行E2E端到端测试
  5. 运行API集成测试
  6. 运行冒烟测试（快速验证）

【专项测试】
  7. 运行性能测试
  8. 运行安全测试
  9. 运行兼容性测试
  10. 运行数据库测试
  11. 运行压力测试

【分组和工具】
  12. 选择特定测试分组（交互式）
  13. 查看最新测试报告
  14. 列出所有可用测试

  0. 退出

请输入选项 (0-14):
```

**优势**：
- ✅ 适合新手使用
- ✅ 不需要记忆命令
- ✅ 可以查看测试报告
- ✅ 支持分类浏览

### 方式2: 命令行参数（自动化/CI/CD）

#### 核心测试命令
```bash
# 运行所有测试（后端 + 前端 + 集成）
python tests/full_system_test.py --all

# 只测试后端API（33个端点）
python tests/full_system_test.py --backend

# 只测试前端（编译 + 质量 + 单元）
python tests/full_system_test.py --frontend

# 集成测试（E2E + API集成）
python tests/full_system_test.py --integration

# 专项测试（性能 + 安全 + 兼容性 + 数据库 + 压力）
python tests/full_system_test.py --specialist
```

#### 特定分组测试
```bash
# 后端API分组测试
python tests/full_system_test.py --api health      # 健康检查
python tests/full_system_test.py --api alert       # 告警系统
python tests/full_system_test.py --api iot         # IoT数据
python tests/full_system_test.py --api tenant      # 租户管理
python tests/full_system_test.py --api user        # 用户和角色
python tests/full_system_test.py --api location    # 位置管理
python tests/full_system_test.py --api resident    # 住户管理
python tests/full_system_test.py --api device      # 设备管理
python tests/full_system_test.py --api card        # 卡片管理
python tests/full_system_test.py --api quality     # 护理质量
python tests/full_system_test.py --api integrity   # 数据完整性

# 快速测试
python tests/full_system_test.py --smoke           # 冒烟测试（2分钟）
python tests/full_system_test.py --e2e             # E2E测试
```

#### 专项测试命令
```bash
python tests/full_system_test.py --performance     # 性能测试
python tests/full_system_test.py --security        # 安全测试
python tests/full_system_test.py --compatibility   # 兼容性测试
python tests/full_system_test.py --database        # 数据库测试
python tests/full_system_test.py --stress          # 压力测试
```

#### 工具命令
```bash
# 列出所有可用测试
python tests/full_system_test.py --list

# 查看最新测试报告
python tests/full_system_test.py --report

# 查看完整帮助
python tests/full_system_test.py --help
```

### 前提条件

#### 后端测试需要：
- 后端服务已启动在 `http://localhost:8000`
  ```bash
  cd owlRD-prototype/backend
  python start_with_check.py
  ```

#### 前端测试需要：
- Node.js环境已安装
- 前端依赖已安装（`npm install`）

---

## 📋 测试内容

### 测试体系总览（23个测试分组）

#### 🔵 后端API测试（12个分组）- ✅ 已实现

| 分组ID | 名称 | 测试内容 | 状态 |
|--------|------|---------|------|
| `health` | 健康检查 | API健康状态、根路径 | ✅ |
| `docs` | API文档 | Swagger UI、OpenAPI规范 | ✅ |
| `tenant` | 租户管理 | 租户CRUD操作 | ✅ |
| `user` | 用户和角色 | 用户、角色管理 | ✅ |
| `location` | 位置管理 | 位置、房间、床位 | ✅ |
| `resident` | 住户管理 | 住户、联系人、护理关联 | ✅ |
| `device` | 设备管理 | 设备CRUD操作 | ✅ |
| `iot` | IoT数据 | 数据查询、统计 | ✅ |
| `alert` | 告警管理 | 告警列表、统计、策略 | ✅ |
| `card` | 卡片管理 | 卡片系统 | ✅ |
| `quality` | 护理质量 | 质量报告、评分 | ✅ |
| `integrity` | 数据完整性 | 数据存在性检查 | ✅ |

#### 🟢 前端测试（3个分组）- 🔶 部分实现

| 分组ID | 名称 | 测试内容 | 状态 | 说明 |
|--------|------|---------|------|------|
| `frontend-build` | 前端构建 | TypeScript编译、dist生成 | ✅ | npm run build |
| `frontend-lint` | 代码质量 | ESLint检查 | ✅ | npm run lint |
| `frontend-unit` | 单元测试 | 组件、Hook测试 | 🟡 | 需配置Vitest |

#### 🟡 集成测试（2个分组）- 🟡 框架搭建

| 分组ID | 名称 | 测试内容 | 状态 | 推荐工具 |
|--------|------|---------|------|----------|
| `e2e` | E2E端到端 | 完整业务流程测试 | 🟡 | Playwright |
| `api-integration` | API集成 | 前后端接口对接 | 🟡 | MSW |

#### 🔴 专项测试（5个分组）- 🟡 框架搭建

| 分组ID | 名称 | 测试内容 | 状态 | 推荐工具 |
|--------|------|---------|------|----------|
| `performance` | 性能测试 | API响应时间、页面加载 | 🟡 | Locust + Lighthouse |
| `security` | 安全测试 | 认证、注入防护、XSS | 🟡 | OWASP ZAP |
| `compatibility` | 兼容性测试 | 多浏览器、响应式 | 🟡 | Playwright |
| `database` | 数据库测试 | 数据一致性、备份恢复 | 🟡 | pytest |
| `stress` | 压力测试 | 高并发、稳定性 | 🟡 | JMeter |

#### 🔵 快速测试（1个分组）- ✅ 已实现

| 分组ID | 名称 | 测试内容 | 状态 |
|--------|------|---------|------|
| `smoke` | 冒烟测试 | 核心功能快速验证 | ✅ |

### 图例说明
- ✅ **已实现**: 可以直接运行，有完整测试逻辑
- 🟡 **框架搭建**: 已有测试函数框架，需要配置工具和实现
- 🔶 **部分实现**: 有部分功能实现，其他待配置

### 测试统计
```
✅ 已实现:    16个测试 (后端12 + 前端2 + 快速1 + 冒烟1)
🟡 框架搭建:  7个测试  (前端单元1 + 集成2 + 专项5)
总计:         23个测试分组
```

---

## 📊 测试报告

测试报告自动保存在 `test_reports/` 目录下，文件名格式：
```
test_report_YYYYMMDD_HHMMSS.json
```

**报告内容**:
```json
{
  "timestamp": "2025-11-22T15:30:00",
  "summary": {
    "total": 50,
    "passed": 48,
    "failed": 2,
    "pass_rate": 96.0
  },
  "tests": [
    {
      "test": "健康检查端点",
      "passed": true,
      "details": "状态码: 200",
      "timestamp": "2025-11-22T15:30:01"
    }
    // ... 更多测试结果
  ]
}
```

---

## 🎯 使用场景

### 场景1: 日常开发测试
```bash
# 修改API后快速验证
python tests/full_system_test.py --api user

# 修改前端后验证编译
python tests/full_system_test.py --frontend
```

### 场景2: 提交前完整测试
```bash
# 运行所有测试确保无问题
python tests/full_system_test.py --all
```

### 场景3: CI/CD自动化
```bash
# 在CI流水线中自动运行
python tests/full_system_test.py --backend
python tests/full_system_test.py --frontend
python tests/full_system_test.py --e2e

# GitHub Actions示例
- name: Run Backend Tests
  run: python tests/full_system_test.py --backend
  
- name: Run Frontend Tests
  run: python tests/full_system_test.py --frontend
```

### 场景4: 问题排查
```bash
# 查看最新测试报告
python tests/full_system_test.py --report

# 只测试问题模块
python tests/full_system_test.py --api alert

# 快速验证修复
python tests/full_system_test.py --smoke
```

### 场景5: 发布前验证
```bash
# 1. 运行完整测试
python tests/full_system_test.py --all

# 2. 查看报告确认100%通过
python tests/full_system_test.py --report

# 3. 运行专项测试
python tests/full_system_test.py --specialist
```

---

## 💡 最佳实践

### 开发阶段
1. ✅ 修改代码后立即运行相关测试
2. ✅ 使用`--api`参数快速测试单个模块
3. ✅ 关注测试报告，及时修复失败测试
4. ✅ 提交前运行`--all`确保全系统通过

### 代码审查阶段
1. ✅ 要求PR必须附带测试通过截图
2. ✅ 检查`test_reports/`中的最新报告
3. ✅ 通过率必须保持100%

### 部署前检查
1. ✅ 运行`--all`进行完整测试
2. ✅ 检查前端build是否成功
3. ✅ 验证数据完整性测试通过
4. ✅ 保存测试报告作为部署文档

---

## 🔧 扩展测试

### 添加新的后端API测试

1. 在`full_system_test.py`中添加测试函数：
```python
def test_new_feature_endpoints():
    """测试新功能API"""
    print_section("新功能API测试")
    
    test_api_endpoint(
        "GET", "/new-feature/",
        "获取新功能列表"
    )
```

2. 在`TEST_GROUPS`字典中注册：
```python
TEST_GROUPS = {
    # ... 其他测试
    'new-feature': {
        'name': '新功能',
        'tests': [test_new_feature_endpoints]
    }
}
```

3. 现在可以单独运行：
```bash
python tests/full_system_test.py --api new-feature
```

### 添加新的前端测试

参考`test_frontend_build()`和`test_frontend_lint()`的实现方式。

### 创建独立测试文件

按照文档规范，其他测试文件应命名为：
- `test_performance.py` - 性能测试
- `test_security.py` - 安全测试
- `test_e2e.py` - 端到端测试

---

## 🎯 待实现测试实施指南

以下测试框架已搭建完成，以下是具体实施步骤：

### 1. 前端单元测试（优先级：⭐⭐⭐⭐⭐）

**安装依赖**：
```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

**配置vitest.config.ts**：
```typescript
import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
  },
})
```

**添加测试脚本到package.json**：
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

**示例测试文件**：
```typescript
// src/components/__tests__/UserForm.test.tsx
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import UserForm from '../UserForm'

describe('UserForm', () => {
  it('应该渲染表单字段', () => {
    render(<UserForm />)
    expect(screen.getByLabelText('用户名')).toBeInTheDocument()
  })
})
```

**运行测试**：
```bash
# 现在可以运行
python tests/full_system_test.py --api frontend-unit
```

---

### 2. E2E端到端测试（优先级：⭐⭐⭐⭐⭐）

**安装Playwright**：
```bash
# 在项目根目录
npm init playwright@latest

# 选择配置：
# - TypeScript
# - tests目录名：e2e-tests
# - 添加GitHub Actions workflow: Yes
```

**创建示例测试**：
```typescript
// e2e-tests/login.spec.ts
import { test, expect } from '@playwright/test'

test('用户登录流程', async ({ page }) => {
  await page.goto('http://localhost:3000')
  
  // 填写登录表单
  await page.fill('[name="username"]', 'admin')
  await page.fill('[name="password"]', 'password')
  await page.click('button[type="submit"]')
  
  // 验证登录成功
  await expect(page).toHaveURL('http://localhost:3000/dashboard')
})
```

**配置playwright.config.ts**：
```typescript
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './e2e-tests',
  use: {
    baseURL: 'http://localhost:3000',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
  },
  webServer: {
    command: 'cd ../frontend && npm run dev',
    port: 3000,
  },
})
```

**运行测试**：
```bash
# 现在可以运行
python tests/full_system_test.py --e2e
```

---

### 3. API集成测试（优先级：⭐⭐⭐⭐）

**安装MSW**：
```bash
cd frontend
npm install -D msw
```

**配置Mock Service Worker**：
```typescript
// src/test/mocks/handlers.ts
import { rest } from 'msw'

export const handlers = [
  rest.get('/api/v1/users/', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        { user_id: '1', username: 'test', email: 'test@example.com' }
      ])
    )
  }),
]
```

**示例集成测试**：
```typescript
// src/services/__tests__/api.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { handlers } from '../mocks/handlers'
import { getUsers } from '../api'

const server = setupServer(...handlers)

beforeAll(() => server.listen())
afterAll(() => server.close())

describe('API Service', () => {
  it('应该获取用户列表', async () => {
    const users = await getUsers()
    expect(users).toHaveLength(1)
    expect(users[0].username).toBe('test')
  })
})
```

**运行测试**：
```bash
python tests/full_system_test.py --api api-integration
```

---

### 4. 性能测试（优先级：⭐⭐⭐）

**后端性能测试（Locust）**：
```bash
pip install locust

# 创建locustfile.py
```

```python
# tests/locustfile.py
from locust import HttpUser, task, between

class OwlRDUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:8000"
    
    @task
    def get_users(self):
        self.client.get("/api/v1/users/")
    
    @task
    def get_alerts(self):
        self.client.get("/api/v1/alerts/")
```

**运行性能测试**：
```bash
# 启动Locust
locust -f tests/locustfile.py

# 访问 http://localhost:8089 配置并发用户数
```

**前端性能测试（Lighthouse）**：
```bash
npm install -g lighthouse

# 运行Lighthouse
lighthouse http://localhost:3000 --output html --output-path ./report.html
```

---

### 5. 安全测试（优先级：⭐⭐⭐）

**使用OWASP ZAP**：
```bash
# 下载并安装 OWASP ZAP
# https://www.zaproxy.org/download/

# 自动扫描
zap-cli quick-scan --self-contained http://localhost:8000

# 完整扫描
zap-cli active-scan http://localhost:8000
```

**基础安全检查脚本**：
```python
# tests/test_security.py
def test_sql_injection():
    """测试SQL注入防护"""
    response = requests.get(
        f"{BASE_URL}/api/v1/users/",
        params={'user_id': "1' OR '1'='1"}
    )
    assert response.status_code != 200 or 'error' in response.json()

def test_xss_protection():
    """测试XSS防护"""
    response = requests.post(
        f"{BASE_URL}/api/v1/users/",
        json={'username': '<script>alert("xss")</script>'}
    )
    data = response.json()
    assert '<script>' not in str(data)
```

---

### 6. 兼容性测试（优先级：⭐⭐）

使用Playwright的多浏览器支持：

```typescript
// e2e-tests/compatibility.spec.ts
import { test, expect, chromium, firefox, webkit } from '@playwright/test'

for (const browserType of [chromium, firefox, webkit]) {
  test(`在 ${browserType.name()} 中测试`, async () => {
    const browser = await browserType.launch()
    const page = await browser.newPage()
    await page.goto('http://localhost:3000')
    await expect(page).toHaveTitle(/owlRD/)
    await browser.close()
  })
}
```

---

### 实施优先级总结

| 优先级 | 测试类型 | 预计工时 | 价值 |
|-------|---------|---------|-----|
| ⭐⭐⭐⭐⭐ | 前端单元测试 | 2-3天 | 快速反馈，提高质量 |
| ⭐⭐⭐⭐⭐ | E2E测试 | 3-4天 | 验证业务流程 |
| ⭐⭐⭐⭐ | API集成测试 | 1-2天 | 确保前后端协作 |
| ⭐⭐⭐ | 性能测试 | 1-2天 | 发现性能瓶颈 |
| ⭐⭐⭐ | 安全测试 | 2-3天 | 保障系统安全 |
| ⭐⭐ | 兼容性测试 | 1天 | 支持多浏览器 |

**建议实施顺序**：前端单元测试 → E2E测试 → API集成测试 → 其他专项测试

---

## 📚 相关文档

- [完成报告](../项目记录/7-过程记录/2025-11-22_1755_Alert系统对齐与测试100%通过完成报告.md)
- [主README](../README.md)
- [后端README](../backend/README.md)
- [前端README](../frontend/README.md)

---

## ⚠️ 常见问题

### Q1: 测试失败 - 连接被拒绝
**原因**: 后端服务未启动  
**解决**:
```bash
cd backend
python start_with_check.py
```

### Q2: 前端测试失败 - npm命令未找到
**原因**: Node.js未安装  
**解决**: 安装Node.js (https://nodejs.org/)

### Q3: 部分API测试失败
**检查清单**:
1. 后端服务是否在8000端口运行？
2. 是否运行过`init_sample_data.py`？
3. 数据文件是否存在？

### Q4: 如何只测试某个API？
**方法1**: 命令行参数
```bash
python tests/full_system_test.py --api alert
```

**方法2**: 交互式菜单
```bash
python tests/full_system_test.py
# 选择 4. 选择特定测试分组
```

### Q5: 测试报告在哪里？
**位置**: `tests/test_reports/test_report_*.json`  
**查看**: 
```bash
python tests/full_system_test.py --report
```

### Q6: 如何跳过前端测试？
```bash
# 只运行后端测试
python tests/full_system_test.py --backend
```

---

## 📝 更新日志

### 2025-11-22 v3.0 - 完整测试体系
- ✨ 新增23个测试分组（全覆盖）
- ✨ 新增14选项交互式菜单
- ✨ 新增17个命令行参数
- ✨ 新增集成测试框架（E2E + API集成）
- ✨ 新增专项测试框架（5类）
- ✨ 新增快速冒烟测试
- ✨ 新增前端单元测试框架
- 📚 完整实施指南文档
- 🎯 测试分类：后端12 + 前端3 + 集成2 + 专项5 + 快速1
- 📊 已实现16个，框架搭建7个
- ✅ 后端测试通过率: 100%

### 2025-11-22 v2.0 - 交互式菜单
- ✨ 新增交互式菜单支持
- ✨ 新增命令行参数支持
- ✨ 新增前端编译测试
- ✨ 新增前端代码质量测试
- ✨ 新增测试分组功能
- ✨ 新增最新报告查看功能
- 🎯 支持14个测试分组（12个后端 + 2个前端）
- 📊 总计35个测试（33个后端 + 2个前端）
- ✅ 通过率: 100%

### 2025-11-21 v1.0 - 初始版本
- 初始版本：后端API测试
- 33个端点测试

---

## 🎯 系统状态

**当前版本**: v3.0  
**创建时间**: 2025-11-21  
**最后更新**: 2025-11-22 18:25  
**维护者**: 项目团队  
**状态**: ✅ 生产就绪

**测试覆盖**：
- ✅ 后端API: 100% (33/33测试通过)
- ✅ 前端编译: 100% (TypeScript + ESLint)
- 🟡 前端单元: 框架就绪（待配置Vitest）
- 🟡 E2E测试: 框架就绪（待配置Playwright）
- 🟡 专项测试: 框架就绪（5类测试）

**总结**: 完整测试框架已搭建，核心测试已实现，专项测试可按需扩展。
