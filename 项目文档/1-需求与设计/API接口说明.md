# owlRD API接口文档

**版本**: v1.0  
**基础URL**: `http://localhost:8000/api/v1`  
**认证方式**: JWT Bearer Token

---

## 目录

1. [认证接口](#认证接口)
2. [核心业务接口](#核心业务接口)
3. [权限说明](#权限说明)
4. [错误码](#错误�?

---

## 认证接口

### 1. 用户登录
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "user_id": "uuid",
    "username": "admin",
    "role": "Admin",
    "tenant_id": "uuid"
  }
}
```

### 2. 用户注册
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "newuser",
  "password": "password123",
  "email": "user@example.com",
  "role": "Nurse",
  "tenant_id": "uuid"
}
```

---

## 核心业务接口

### 卡片管理 (Cards)

#### GET /api/v1/cards
获取卡片列表（带权限过滤�?
**权限**: 所有已认证用户  
**过滤**: 根据用户alert_scope自动过滤

**参数**:
- `tenant_id` (required): 租户ID
- `limit` (optional, default=100): 返回数量
- `is_active` (optional): 是否激�?- `is_public_space` (optional): 是否公共空间

**响应**: 200 OK
```json
[
  {
    "card_id": "uuid",
    "tenant_id": "uuid",
    "card_address": "E203-A",
    "resident_id": "uuid",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### GET /api/v1/cards/{card_id}
获取单个卡片详情（带权限检查）

**权限**: 必须有权查看该卡�?
#### POST /api/v1/cards
创建卡片

**权限**: canCreateCard (Admin/Director/NurseManager)

---

### 用户管理 (Users)

#### GET /api/v1/users
获取用户列表

**权限**: Admin/Director  
**参数**: `tenant_id`, `limit`

#### POST /api/v1/users
创建用户

**权限**: Admin/Director

#### PUT /api/v1/users/{user_id}
更新用户

**权限**: Admin/Director或自�?
#### DELETE /api/v1/users/{user_id}
删除用户

**权限**: 仅Admin

---

### 设备管理 (Devices)

#### GET /api/v1/devices
获取设备列表

**权限**: Admin/Director/NurseManager  
**参数**: `tenant_id`, `device_type`, `status`

#### POST /api/v1/devices
创建设备

**权限**: Admin/Director/NurseManager

#### PUT /api/v1/devices/{device_id}/status
更新设备状�?
**权限**: Admin/Director/NurseManager

---

### 位置管理 (Locations)

#### GET /api/v1/locations
获取位置列表

**参数**: `tenant_id`, `location_type`

#### POST /api/v1/locations
创建位置

**权限**: Admin/Director

#### DELETE /api/v1/locations/{location_id}
删除位置

**权限**: 仅Admin

---

### 住户管理 (Residents)

#### GET /api/v1/residents
获取住户列表

**参数**: `tenant_id`

#### POST /api/v1/residents
创建住户

**权限**: Admin/Director/NurseManager

#### GET /api/v1/residents/{resident_id}
获取住户详情

#### PUT /api/v1/residents/{resident_id}
更新住户信息

**权限**: Admin/Director/NurseManager

---

### 告警管理 (Alerts)

#### GET /api/v1/alerts
获取告警列表

**参数**: 
- `tenant_id`
- `status`: pending/acknowledged/resolved
- `alert_level`: L1/L2/L3

**响应**:
```json
[
  {
    "alert_id": "uuid",
    "alert_type": "Fall",
    "alert_level": "L1",
    "resident_id": "uuid",
    "location_id": "uuid",
    "status": "pending",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

#### POST /api/v1/alerts/{alert_id}/acknowledge
确认告警

#### POST /api/v1/alerts/{alert_id}/resolve
解决告警

---

### 告警策略 (Alert Policies)

#### GET /api/v1/alert-policies
获取告警策略列表

**权限**: Admin/Director

#### POST /api/v1/alert-policies
创建告警策略

**权限**: Admin/Director

#### PUT /api/v1/alert-policies/{policy_id}
更新告警策略

**权限**: Admin/Director

#### DELETE /api/v1/alert-policies/{policy_id}
删除告警策略

**权限**: 仅Admin

#### POST /api/v1/alert-policies/initialize/{tenant_id}
初始化租户告警策�?
**权限**: Admin

---

## 权限说明

### 角色权限矩阵

| 角色 | 查看 | 创建 | 编辑 | 删除 | 权限配置 |
|------|------|------|------|------|----------|
| Admin | �?| �?| �?| �?| �?|
| Director | �?| �?| �?| �?| �?|
| NurseManager | �?| �?| �?| �?| �?|
| Nurse | �?| �?| �?| �?| �?|
| Caregiver | �?| �?| �?| �?| �?|

### Alert Scope数据范围

| Scope | 描述 | 适用角色 |
|-------|------|----------|
| ALL | 租户下所有数�?| Admin, Director |
| LOCATION | 匹配location_tag的数�?| NurseManager |
| ASSIGNED_ONLY | 仅分配给自己的住�?| Nurse, Caregiver |

### 认证头格�?
所有需要认证的API请求必须包含:
```http
Authorization: Bearer <access_token>
```

---

## 错误�?
### HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未认�?|
| 403 | 权限不足 |
| 404 | 资源不存�?|
| 500 | 服务器错�?|

### 错误响应格式

```json
{
  "detail": "错误描述信息",
  "status_code": 403,
  "error_type": "PermissionDenied"
}
```

### 常见错误

**401 Unauthorized**:
```json
{
  "detail": "未提供认证令�?,
  "status_code": 401
}
```

**403 Forbidden**:
```json
{
  "detail": "无权访问其他租户的数�?,
  "status_code": 403
}
```

**404 Not Found**:
```json
{
  "detail": "Card not found",
  "status_code": 404
}
```

---

## 完整API端点列表

### 认证 (Auth)
- POST /api/v1/auth/login
- POST /api/v1/auth/register

### 卡片 (Cards)
- GET /api/v1/cards
- GET /api/v1/cards/{card_id}
- POST /api/v1/cards
- PUT /api/v1/cards/{card_id}
- DELETE /api/v1/cards/{card_id}

### 用户 (Users)
- GET /api/v1/users
- GET /api/v1/users/{user_id}
- POST /api/v1/users
- PUT /api/v1/users/{user_id}
- DELETE /api/v1/users/{user_id}

### 设备 (Devices)
- GET /api/v1/devices
- GET /api/v1/devices/{device_id}
- POST /api/v1/devices
- PUT /api/v1/devices/{device_id}
- PUT /api/v1/devices/{device_id}/status
- DELETE /api/v1/devices/{device_id}

### 位置 (Locations)
- GET /api/v1/locations
- GET /api/v1/locations/{location_id}
- POST /api/v1/locations
- PUT /api/v1/locations/{location_id}
- DELETE /api/v1/locations/{location_id}

### 住户 (Residents)
- GET /api/v1/residents
- GET /api/v1/residents/{resident_id}
- POST /api/v1/residents
- PUT /api/v1/residents/{resident_id}
- DELETE /api/v1/residents/{resident_id}

### 告警 (Alerts)
- GET /api/v1/alerts
- GET /api/v1/alerts/{alert_id}
- POST /api/v1/alerts/{alert_id}/acknowledge
- POST /api/v1/alerts/{alert_id}/resolve
- GET /api/v1/alerts/statistics

### 告警策略 (Alert Policies)
- GET /api/v1/alert-policies
- GET /api/v1/alert-policies/{policy_id}
- POST /api/v1/alert-policies
- PUT /api/v1/alert-policies/{policy_id}
- DELETE /api/v1/alert-policies/{policy_id}
- POST /api/v1/alert-policies/initialize/{tenant_id}

### 角色 (Roles)
- GET /api/v1/roles
- GET /api/v1/roles/{role_id}
- POST /api/v1/roles
- PUT /api/v1/roles/{role_id}
- DELETE /api/v1/roles/{role_id}

### IoT数据 (IoT Data)
- GET /api/v1/iot-data
- GET /api/v1/iot-data/{data_id}
- POST /api/v1/iot-data

### 配置版本 (Config Versions)
- GET /api/v1/config-versions
- GET /api/v1/config-versions/{version_id}
- POST /api/v1/config-versions

### 映射关系 (Mappings)
- GET /api/v1/mappings
- POST /api/v1/mappings
- DELETE /api/v1/mappings/{mapping_id}

### 实时数据 (Realtime)
- GET /api/v1/realtime/status
- GET /api/v1/realtime/monitor

### WebSocket
- WS /api/v1/ws/{client_id}

---

## 使用示例

### Python示例

```python
import requests

# 1. 登录获取token
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={"username": "admin", "password": "password123"}
)
token = response.json()["access_token"]

# 2. 使用token访问API
headers = {"Authorization": f"Bearer {token}"}
cards = requests.get(
    "http://localhost:8000/api/v1/cards",
    headers=headers,
    params={"tenant_id": "uuid"}
)
print(cards.json())
```

### JavaScript示例

```javascript
// 1. 登录
const login = async () => {
  const response = await fetch('http://localhost:8000/api/v1/auth/login', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({username: 'admin', password: 'password123'})
  });
  const data = await response.json();
  return data.access_token;
};

// 2. 获取卡片
const getCards = async (token) => {
  const response = await fetch(
    'http://localhost:8000/api/v1/cards?tenant_id=uuid',
    {headers: {'Authorization': `Bearer ${token}`}}
  );
  return await response.json();
};
```

---

**文档版本**: v1.0  
**最后更�?*: 2024-11-24  
**维护团队**: owlRD开发团�?