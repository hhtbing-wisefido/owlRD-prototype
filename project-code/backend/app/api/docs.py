"""
自定义API文档页面 - 使用国内CDN，解决局域网白屏问题
"""

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.config import settings

router = APIRouter()


@router.get("/docs-cn", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui():
    """使用国内CDN的Swagger UI"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{settings.app_name} - API文档</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <!-- 使用国内CDN镜像 -->
        <link rel="stylesheet" href="https://cdn.staticfile.org/swagger-ui/5.10.3/swagger-ui.css">
        <style>
            body {{ margin: 0; padding: 0; }}
        </style>
    </head>
    <body>
        <div id="swagger-ui"></div>
        <script src="https://cdn.staticfile.org/swagger-ui/5.10.3/swagger-ui-bundle.js"></script>
        <script src="https://cdn.staticfile.org/swagger-ui/5.10.3/swagger-ui-standalone-preset.js"></script>
        <script>
            window.onload = function() {{
                const ui = SwaggerUIBundle({{
                    url: '/api/openapi.json',
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
                        theme: "monokai"
                    }},
                    defaultModelsExpandDepth: -1
                }});
                window.ui = ui;
            }};
        </script>
    </body>
    </html>
    """


@router.get("/redoc-cn", response_class=HTMLResponse, include_in_schema=False)
async def custom_redoc():
    """使用国内CDN的ReDoc"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{settings.app_name} - API文档 (ReDoc)</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet">
        <style>
            body {{ margin: 0; padding: 0; }}
        </style>
    </head>
    <body>
        <redoc spec-url='/api/openapi.json'></redoc>
        <script src="https://cdn.staticfile.org/redoc/2.1.3/bundles/redoc.standalone.js"></script>
    </body>
    </html>
    """
