---
title: "Naming Convention"
description: "文件命名规范"
trigger: always
---

# 🏷�?文件命名规范

**规则类型**: 通用规则 �? 
**强制级别**: 🟡 强烈建议  
**适用场景**: 所有文件命�? 
**版本**: v1.0.0  

---

## 📋 目录

- [核心原则](#核心原则)
- [文档类型命名规范](#文档类型命名规范)
- [代码文件命名规范](#代码文件命名规范)
- [配置文件命名规范](#配置文件命名规范)
- [禁止的命名模式](#禁止的命名模�?
- [命名检查清单](#命名检查清�?
- [语言特定规范](#语言特定规范)
- [命名示例库](#命名示例�?

---

## 🎯 核心原则

### 五大命名原则

#### 1. 📖 **描述�?* (Descriptive)
```
�?好名�?
- user_authentication_service.py    # 清楚地说明用�?
- database_migration_script.sql     # 知道这是什�?
- customer_order_report.md          # 一目了�?

�?坏名�?
- file1.py                          # 完全不知道是什�?
- temp.md                           # 太模�?
- new.txt                           # 没有信息
```

**原则**: 文件名应该清楚说明文件的内容和用�?

#### 2. �?**简洁�?* (Concise)
```
�?好名�?
- user_auth.py                      # 简洁明�?
- db_config.json                    # 适度缩写
- api_routes.ts                     # 简短清�?

⚠️ 可接�?
- user_authentication.py            # 稍长但清�?

�?太长:
- this_is_a_very_long_file_name_that_describes_everything_in_detail.py
```

**原则**: 在描述清楚的前提下，尽量简�?

#### 3. 🎨 **一致�?* (Consistent)
```
�?一致的风格:
project/
├── user_service.py                 # snake_case
├── order_service.py                # snake_case
├── product_service.py              # snake_case
└── payment_service.py              # snake_case

�?不一�?
project/
├── user_service.py                 # snake_case
├── OrderService.py                 # PascalCase
├── product-service.py              # kebab-case
└── paymentService.py               # camelCase
```

**原则**: 同一项目中使用统一的命名风�?

#### 4. 🚫 **可读�?* (Readable)
```
�?易读:
- user_profile_settings.md
- api_response_handler.py
- database_connection_pool.ts

�?难读:
- usrprflsttngs.md                  # 过度缩写
- apirsphndlr.py                    # 无法理解
- dbcnpol.ts                        # 太简�?
```

**原则**: 避免过度缩写，保持可读�?

#### 5. 🌐 **可移植�?* (Portable)
```
�?安全的名�?
- user_data.json
- config_settings.yaml
- api_endpoints.md

�?可能有问�?
- 用户数据.json                    # 中文（某些系统可能不支持�?
- file name.txt                     # 空格（需要转义）
- data@2025.csv                     # 特殊字符（某些系统限制）
```

**原则**: 代码和配置文件使用英文和安全字符，文档可以使用中�?

---

## 📝 文档类型命名规范

### 规范类文�?(Specification Documents)

**格式**: `[主题]规范.md`

**用�?*: 定义规则、标准、流�?

**示例**:
```
�?正确:
- 文件操作规范.md
- API设计规范.md
- 代码审查规范.md
- 数据库命名规�?md
- Git提交规范.md

�?错误:
- 规范.md                          # 太模�?
- 文件规范文档.md                  # 啰嗦
- file_operations_spec.md          # 应该统一中文或英�?
```

### 说明类文�?(Description Documents)

**格式**: `[主题]说明.md`

**用�?*: 解释功能、使用方法、配�?

**示例**:
```
�?正确:
- API接口说明.md
- 部署流程说明.md
- 配置项说�?md
- 功能模块说明.md
- 数据库结构说�?md

�?错误:
- 说明.md                          # 太模�?
- 文档说明.md                      # 什么文档？
- API_description.md               # 应该统一中文或英�?
```

### 指南类文�?(Guide Documents)

**格式**: `[主题]指南.md`

**用�?*: 详细的操作指导、最佳实�?

**示例**:
```
�?正确:
- 新手入门指南.md
- 部署指南.md
- 开发指�?md
- 故障排除指南.md
- 安全配置指南.md

�?错误:
- 指南.md                          # 太模�?
- 使用手册.md                      # 应该�?指南"
- development_guide.md             # 应该统一风格
```

### 记录类文�?(Record Documents)

**格式**: `YYYY-MM-DD_[描述].md`

**用�?*: 时间相关的记录、日�?

**示例**:
```
�?正确:
- 2025-11-26_功能开发记�?md
- 2025-11-26_问题修复记录.md
- 2025-11-26_会议纪要.md
- 2025-11-26_版本发布记录.md

�?错误:
- 20251126_记录.md                # 日期格式错误
- 2025_11_26_record.md            # 分隔符不统一
- 记录_2025-11-26.md              # 日期应该在前
- 2025-11-26.md                   # 缺少描述
```

### 报告类文�?(Report Documents)

**格式**: `YYYY-MM-DD_[主题]报告.md`

**用�?*: 分析报告、测试报告、统计报�?

**示例**:
```
�?正确:
- 2025-11-26_测试报告.md
- 2025-11-26_性能分析报告.md
- 2025-11-26_用户调研报告.md
- 2025-11-26_完成度报�?md

�?错误:
- 测试报告.md                     # 缺少日期
- 2025-11-26_report.md            # 应该用中�?
- report_20251126.md              # 格式不符
```

### 总结类文�?(Summary Documents)

**格式**: `[主题]总结.md` �?`YYYY-MM-DD_[主题]总结.md`

**用�?*: 项目总结、阶段总结

**示例**:
```
�?正确:
- 2025-11-26_开发阶段总结.md
- Q4项目总结.md
- 年度工作总结.md
- Sprint12总结.md

�?错误:
- 总结.md                         # 太模�?
- summary.md                      # 应该用中�?
```

---

## 💻 代码文件命名规范

### Python 文件

**风格**: `snake_case`

**规范**:
```python
�?推荐:
user_service.py              # 服务�?
user_model.py                # 数据模型
user_schema.py               # 数据Schema
user_controller.py           # 控制�?
user_utils.py                # 工具函数
test_user_service.py         # 测试文件

�?避免:
UserService.py               # 不要用PascalCase
user-service.py              # 不要用kebab-case
userservice.py               # 不要省略下划�?
us.py                        # 不要过度缩写
```

**特殊文件**:
```python
�?标准名称:
__init__.py                  # 包初始化
__main__.py                  # 主入�?
setup.py                     # 安装脚本
conftest.py                  # pytest配置
```

### TypeScript / JavaScript 文件

**组件**: `PascalCase.tsx / .jsx`
```typescript
�?推荐:
UserProfile.tsx              # React组件
Button.tsx                   # UI组件
LoginForm.tsx                # 表单组件

�?避免:
userProfile.tsx              # 组件应该用PascalCase
user-profile.tsx             # 组件应该用PascalCase
```

**工具/服务**: `camelCase.ts / .js`
```typescript
�?推荐:
userService.ts               # 服务
apiClient.ts                 # API客户�?
authHelper.ts                # 辅助函数
dateUtils.ts                 # 工具函数

�?避免:
UserService.ts               # 非组件不要用PascalCase
user_service.ts              # JS/TS不用snake_case
```

**类型定义**: 可以�?`PascalCase` �?`camelCase`
```typescript
�?推荐:
User.types.ts                # 类型定义
user.types.ts                # 也可�?
types.ts                     # 综合类型文件

�?避免:
userTypes.ts                 # 建议�?.types 后缀
```

**测试文件**:
```typescript
�?推荐:
UserService.test.ts          # 测试文件
UserService.spec.ts          # 规范测试
Button.test.tsx              # 组件测试

�?避免:
test_UserService.ts          # 不要用Python风格
UserService_test.ts          # 后缀应该�?.test
```

### Java 文件

**风格**: `PascalCase.java`

```java
�?推荐:
UserService.java             # 服务�?
UserRepository.java          # 仓库�?
UserController.java          # 控制�?
User.java                    # 实体�?

�?避免:
userService.java             # 类名应该大写开�?
user_service.java            # 不要用snake_case
```

### CSS / SCSS 文件

**风格**: `kebab-case` �?`camelCase`

```css
�?推荐:
user-profile.css             # kebab-case
user-profile.module.css      # CSS模块
button.scss                  # SCSS文件
_variables.scss              # 部分文件（下划线开头）

⚠️ 可接�?
userProfile.css              # camelCase也可�?

�?避免:
UserProfile.css              # 不要用PascalCase
user_profile.css             # 不要用snake_case
```

---

## ⚙️ 配置文件命名规范

### 标准配置文件

**不要修改标准名称**:
```
�?标准名称:
package.json                 # Node.js包配�?
requirements.txt             # Python依赖
Cargo.toml                   # Rust配置
pom.xml                      # Maven配置
build.gradle                 # Gradle配置
tsconfig.json                # TypeScript配置
.eslintrc.js                 # ESLint配置
.prettierrc                  # Prettier配置
.gitignore                   # Git忽略
.env                         # 环境变量
docker-compose.yml           # Docker Compose

�?不要�?
package-config.json          # 标准�?package.json
python-requirements.txt      # 标准�?requirements.txt
```

### 自定义配置文�?

**推荐格式**: `[project].[env].config.[ext]`

```
�?推荐:
app.config.json              # 应用配置
database.config.js           # 数据库配�?
app.dev.config.json          # 开发环境配�?
app.prod.config.json         # 生产环境配置
logging.config.yaml          # 日志配置

�?避免:
config.json                  # 太模�?
my_config.json               # 太随�?
app-configuration.json       # 太长
```

---

## 🚫 禁止的命名模�?

### 1. �?模糊名称

**禁止**:
```
�?极度模糊:
- file.md
- document.txt
- data.json
- config.yaml
- script.py
- test.ts
- new.md
- untitled.txt

�?稍微模糊:
- 说明.md                    # 什么的说明�?
- 文档.md                    # 什么文档？
- 配置.json                  # 什么配置？
- 脚本.py                    # 什么脚本？
```

**正确**:
```
�?清晰具体:
- 用户认证功能说明.md
- API接口文档.md
- 数据库配�?json
- 数据库初始化脚本.py
```

### 2. �?临时/测试名称

**禁止在正式文件中使用**:
```
�?禁止:
- temp.md
- temporary.py
- test.js
- test123.ts
- new.md
- new_file.py
- untitled.txt
- copy.md
- backup.sql
- old.csv
- draft.md                   # 除非在drafts/目录

�?如果真的是临�?
- 放在临时目录
- 添加�?.gitignore
- 及时清理删除
```

### 3. �?版本号后缀

**禁止**:
```
�?禁止:
- document_v1.md
- document_v2.md
- document_final.md
- document_final_final.md
- user_service_old.py
- user_service_new.py
- api_backup.ts

�?使用Git管理版本:
- document.md                # Git会记录历�?
- user_service.py            # Git会管理版�?
- api.ts                     # Git是版本控制工�?
```

### 4. �?特殊字符

**代码和配置文件中禁止**:
```
�?禁止:
- user@service.py            # @ 符号
- data#2025.json             # # 符号
- file name.txt              # 空格
- config(prod).yaml          # 括号
- script&tool.sh             # & 符号

�?使用安全字符:
- user_service.py
- data_2025.json
- file_name.txt
- config.prod.yaml
- script_tool.sh
```

**文档文件可以使用中文**:
```
�?允许（文档）:
- 用户服务说明.md
- 2025年数据报�?md
- 功能列表.md

⚠️ 谨慎（代码）:
- 避免在代码文件名中使用中�?
```

### 5. �?数字开�?

**避免**:
```
�?避免:
- 1_user_service.py
- 2_order_service.py
- 3_product_service.py

⚠️ 例外（文档目录编号）:
- 1-归档/                    # 目录可以
- 2-源参考对�?              # 目录可以
```

**正确**:
```
�?推荐:
- user_service_v1.py         # 版本号在�?
- test_01_user.py            # 测试序号
- chapter_01.md              # 章节编号
```

### 6. �?过长的名�?

**避免**:
```
�?太长�?50字符�?
- this_is_a_very_long_file_name_that_tries_to_describe_everything_in_detail.py
- user_authentication_and_authorization_service_with_jwt_token_validation.ts

�?合理长度�?0-40字符�?
- user_auth_service.py
- jwt_validation_service.ts
```

---

## �?命名检查清�?

### 创建新文件前检�?

- [ ] 📝 文件名是否清晰描述内容？
- [ ] �?文件名是否足够简洁（< 50字符）？
- [ ] 🎨 文件名风格是否与项目一致？
- [ ] 🚫 是否避免了禁止的命名模式�?
- [ ] 🔤 代码文件是否使用了英文？
- [ ] 📅 记录/报告类是否包含日期？
- [ ] 🏷�?文档是否使用了正确的类型后缀（规�?说明/指南）？

### 重命名文件时检�?

- [ ] 🔍 是否搜索了文件引用？
- [ ] 📝 是否更新了文档中的链接？
- [ ] 💻 是否更新了代码中的import�?
- [ ] 📋 是否更新了README索引�?
- [ ] ⚠️ 是否通知了团队成员？

---

## 🌐 语言特定规范

### Python

```python
# 模块/�?
user_service.py              # snake_case
auth_middleware.py
database_utils.py

# �?(文件�?
class UserService:           # PascalCase
class AuthMiddleware:
class DatabaseUtils:

# 常量文件
CONSTANTS.py                 # 全大�?
CONFIG.py
```

### TypeScript / JavaScript

```typescript
// 组件
UserProfile.tsx              // PascalCase
LoginForm.tsx
Button.tsx

// 服务/工具
userService.ts               // camelCase
apiClient.ts
utils.ts

// 类型
User.types.ts                // PascalCase.types.ts
api.types.ts                 // camelCase.types.ts

// 测试
UserProfile.test.tsx         // 组件�?test.tsx
userService.spec.ts          // 文件�?spec.ts
```

### Java

```java
// 类文件（与类名一致）
UserService.java             // PascalCase
OrderRepository.java
ProductController.java

// 接口
IUserService.java            // I前缀（可选）
UserService.java             // 或不用前缀
```

### CSS / SCSS

```css
/* 样式文件 */
user-profile.css             /* kebab-case */
button.scss
_variables.scss              /* 部分文件�?_ 前缀 */

/* CSS模块 */
UserProfile.module.css       /* 组件�?module.css */
Button.module.scss
```

---

## 📚 命名示例�?

### 文档文件示例

#### 规范�?
```
�?优秀:
- 代码审查规范.md
- API设计规范.md
- Git提交规范.md
- 数据库命名规�?md
- 文档编写规范.md
```

#### 说明�?
```
�?优秀:
- 项目部署说明.md
- API接口说明.md
- 配置项说�?md
- 数据库Schema说明.md
- 开发环境搭建说�?md
```

#### 指南�?
```
�?优秀:
- 新手入门指南.md
- 故障排除指南.md
- 性能优化指南.md
- 安全配置指南.md
- 测试编写指南.md
```

#### 记录�?
```
�?优秀:
- 2025-11-26_Sprint12总结.md
- 2025-11-26_技术调研记�?md
- 2025-11-26_问题修复记录.md
- 2025-11-26_会议纪要.md
```

### 代码文件示例

#### Python后端
```
�?优秀:
models/
├── user.py
├── order.py
└── product.py

services/
├── user_service.py
├── order_service.py
└── email_service.py

utils/
├── date_utils.py
├── string_utils.py
└── validation_utils.py

tests/
├── test_user_service.py
├── test_order_service.py
└── conftest.py
```

#### TypeScript前端
```
�?优秀:
components/
├── UserProfile.tsx
├── LoginForm.tsx
└── Button.tsx

services/
├── userService.ts
├── apiClient.ts
└── authService.ts

utils/
├── dateUtils.ts
├── stringUtils.ts
└── validators.ts

types/
├── User.types.ts
├── Order.types.ts
└── common.types.ts

tests/
├── UserProfile.test.tsx
├── userService.spec.ts
└── setupTests.ts
```

---

## 🔄 命名演进指南

### 项目初期

**简单直�?*:
```
user.py
order.py
product.py
```

### 项目成长

**添加分类前缀**:
```
user_model.py
user_service.py
user_controller.py
```

### 项目成熟

**按模块组�?*:
```
modules/
├── user/
�?  ├── model.py
�?  ├── service.py
�?  └── controller.py
├── order/
�?  ├── model.py
�?  ├── service.py
�?  └── controller.py
```

---

## 💡 命名技�?

### 技�?: 使用领域术语

```
�?好的领域术语:
- invoice_generator.py       # 发票生成�?
- payment_processor.py       # 支付处理�?
- order_validator.py         # 订单验证�?

�?通用名称:
- generator.py               # 太模�?
- processor.py               # 太模�?
- validator.py               # 太模�?
```

### 技�?: 动词 + 名词

```
�?清晰的动�?
- create_user.py
- fetch_orders.py
- validate_input.py
- send_email.py
- generate_report.py
```

### 技�?: 名词 + 类型

```
�?明确类型:
- user_controller.py
- order_service.py
- product_repository.py
- email_template.html
- api_schema.json
```

---

**规则维护**: AI开发规范系�? 
**最后更�?*: 2025-11-26  
**规则版本**: v1.0.0  
**适用项目**: 所有软件开发项�? 

---

## 🔗 相关规则

- 📄 [01-file-operations.md](01-file-operations.md) - 文件操作强制规则
- 📁 [02-directory-management.md](02-directory-management.md) - 目录管理规范
- ⚙️ [project-config.md](project-config.md) - 项目配置
