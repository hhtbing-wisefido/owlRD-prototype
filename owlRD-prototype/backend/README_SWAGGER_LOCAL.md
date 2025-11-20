# 本地Swagger UI部署说明

## 📦 已完成的工作

本项目已配置完整的**本地Swagger UI**部署，完全不依赖外部CDN。

## 🎯 文档访问地址

项目提供4种API文档访问方式：

| 地址 | 特点 | 推荐场景 |
|------|------|---------|
| `/docs` | FastAPI默认，使用国外CDN | ❌ 局域网可能白屏 |
| `/docs-cn` | 使用国内CDN镜像 | ✅ 局域网开发（需联网） |
| `/docs-local` | **本地静态文件** | ✅✅ 完全离线，最稳定 |
| `/docs-simple` | 纯HTML极简版 | ✅ 应急备用 |

## 🚀 快速开始

### 1. 下载Swagger UI（首次使用）

如果 `app/static/swagger-ui/` 目录为空，运行：

```bash
cd backend
python download_swagger_ui.py
```

输出示例：
```
🦉 开始下载Swagger UI v5.10.3...
📦 下载地址: https://github.com/swagger-api/swagger-ui/...
⏬ 正在下载...
✅ 下载完成
📂 正在解压...
✅ 解压完成
🎉 Swagger UI本地部署成功！
```

### 2. 启动服务器

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 访问本地文档

**本机访问：**
```
http://localhost:8000/docs-local
```

**局域网访问：**
```
http://192.168.2.6:8000/docs-local
```

## 📂 文件结构

```
backend/
├── app/
│   ├── api/
│   │   ├── docs.py              # 国内CDN版文档
│   │   ├── docs_offline.py      # FastAPI内置文档
│   │   └── docs_local.py        # 本地静态文件文档
│   ├── static/
│   │   ├── .gitkeep
│   │   └── swagger-ui/          # Swagger UI静态文件（不提交到Git）
│   │       ├── swagger-ui.css
│   │       ├── swagger-ui-bundle.js
│   │       ├── swagger-ui-standalone-preset.js
│   │       └── ...
│   └── main.py                  # 挂载静态文件路由
├── download_swagger_ui.py       # 下载脚本
└── .gitignore                   # 排除大文件

## 🔧 技术细节

### 静态文件挂载

在 `app/main.py` 中：

```python
from fastapi.staticfiles import StaticFiles
from pathlib import Path

# 挂载静态文件目录
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
```

### 本地文档路由

在 `app/api/docs_local.py` 中：

```python
@router.get("/docs-local", response_class=HTMLResponse)
async def local_swagger_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="/static/swagger-ui/swagger-ui.css">
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="/static/swagger-ui/swagger-ui-bundle.js"></script>
        <script>
            SwaggerUIBundle({
                url: "/api/openapi.json",
                dom_id: '#swagger-ui',
            });
        </script>
    </body>
    </html>
    """
```

## ⚙️ Git配置

Swagger UI静态文件已添加到 `.gitignore`：

```gitignore
# Swagger UI静态文件（可本地下载，无需提交）
app/static/swagger-ui/*.js
app/static/swagger-ui/*.js.map
app/static/swagger-ui/*.css
app/static/swagger-ui/*.css.map
```

**原因**：这些文件超过10MB，不适合提交到Git。团队成员各自运行 `download_swagger_ui.py` 下载。

## 🆚 版本对比

### /docs（默认）
- ✅ FastAPI官方默认
- ❌ 使用国外CDN（cdn.jsdelivr.net）
- ❌ 局域网可能无法访问

### /docs-cn（国内CDN）
- ✅ 使用国内镜像（cdn.staticfile.org）
- ✅ 局域网可以访问
- ⚠️ 依赖外部CDN

### /docs-local（本地文件）✨
- ✅ 完全本地化，零外部依赖
- ✅ 断网也能使用
- ✅ 访问速度最快
- ✅ 适合生产环境

## 🔄 更新Swagger UI

如果需要更新到新版本：

1. 编辑 `download_swagger_ui.py`，修改版本号：
   ```python
   SWAGGER_VERSION = "5.11.0"  # 新版本
   ```

2. 删除旧文件：
   ```bash
   rm -rf app/static/swagger-ui
   ```

3. 重新下载：
   ```bash
   python download_swagger_ui.py
   ```

## 🐛 故障排查

### 问题1: /docs-local 显示404

**原因**：静态文件未下载

**解决**：
```bash
python download_swagger_ui.py
```

### 问题2: 页面白屏，无样式

**原因**：静态文件路径错误

**检查**：
```bash
ls app/static/swagger-ui/
# 应该看到 swagger-ui.css、swagger-ui-bundle.js 等文件
```

### 问题3: 下载失败

**原因**：GitHub访问受限

**解决**：手动下载
1. 访问：https://github.com/swagger-api/swagger-ui/releases
2. 下载对应版本的zip文件
3. 解压 `dist/` 目录到 `app/static/swagger-ui/`

## 📊 性能对比

| 指标 | 国外CDN | 国内CDN | 本地文件 |
|------|---------|---------|---------|
| 首次加载 | 3-10s | 1-2s | **<0.5s** |
| 断网可用 | ❌ | ❌ | ✅ |
| 局域网可用 | ❌ | ✅ | ✅ |
| 依赖外部 | ✅ | ✅ | ❌ |

## 🎉 总结

- ✅ 本地部署完成，完全离线可用
- ✅ 提供4种文档访问方式
- ✅ 适配各种网络环境
- ✅ 生产环境推荐使用 `/docs-local`

**推荐访问地址：**
```
http://192.168.2.6:8000/docs-local
```
