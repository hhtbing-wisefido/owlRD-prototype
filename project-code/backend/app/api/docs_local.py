"""
使用本地Swagger UI静态文件的文档路由
完全离线，不依赖任何CDN
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.config import settings

router = APIRouter()


@router.get("/docs-local", response_class=HTMLResponse, include_in_schema=False)
async def local_swagger_ui():
    """使用本地Swagger UI文件的API文档"""
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>{settings.app_name} - API文档 (本地版)</title>
        <link rel="stylesheet" type="text/css" href="/static/swagger-ui/swagger-ui.css">
        <link rel="icon" type="image/png" href="/static/swagger-ui/favicon-32x32.png" sizes="32x32">
        <link rel="icon" type="image/png" href="/static/swagger-ui/favicon-16x16.png" sizes="16x16">
        <style>
            html {{
                box-sizing: border-box;
                overflow: -moz-scrollbars-vertical;
                overflow-y: scroll;
            }}
            *, *:before, *:after {{
                box-sizing: inherit;
            }}
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        
        <script src="/static/swagger-ui/swagger-ui-bundle.js" charset="UTF-8"></script>
        <script src="/static/swagger-ui/swagger-ui-standalone-preset.js" charset="UTF-8"></script>
        <script>
            window.onload = function() {{
                const ui = SwaggerUIBundle({{
                    url: "/api/openapi.json",
                    dom_id: '#swagger-ui',
                    deepLinking: true,
                    presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                    ],
                    plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                    ],
                    layout: "StandaloneLayout",
                    syntaxHighlight: {{
                        activate: true,
                        theme: "monokai"
                    }}
                }});
                
                window.ui = ui;
            }};
        </script>
    </body>
    </html>
    """


@router.get("/redoc-local", response_class=HTMLResponse, include_in_schema=False)
async def local_redoc():
    """使用本地ReDoc文件的API文档"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>{settings.app_name} - API文档 (ReDoc本地版)</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                margin: 0;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        <redoc spec-url='/api/openapi.json'></redoc>
        <script src="/static/swagger-ui/redoc.standalone.js"></script>
    </body>
    </html>
    """
