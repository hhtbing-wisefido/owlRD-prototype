"""
下载Swagger UI静态文件到本地
使用国内镜像加速下载
"""

import os
import urllib.request
import zipfile
from pathlib import Path

# Swagger UI版本
SWAGGER_VERSION = "5.10.3"

# 下载地址（使用GitHub镜像）
DOWNLOAD_URL = f"https://github.com/swagger-api/swagger-ui/archive/refs/tags/v{SWAGGER_VERSION}.zip"

# 目标目录
STATIC_DIR = Path(__file__).parent / "app" / "static" / "swagger-ui"

def download_swagger_ui():
    """下载并解压Swagger UI"""
    
    print(f"🦉 开始下载Swagger UI v{SWAGGER_VERSION}...")
    print(f"📦 下载地址: {DOWNLOAD_URL}")
    
    # 创建目录
    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    
    # 下载文件
    zip_path = STATIC_DIR.parent / "swagger-ui.zip"
    
    try:
        print("⏬ 正在下载...")
        urllib.request.urlretrieve(DOWNLOAD_URL, zip_path)
        print(f"✅ 下载完成: {zip_path}")
        
        # 解压文件
        print("📂 正在解压...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # 只提取dist目录中的文件
            for file in zip_ref.namelist():
                if 'dist/' in file and not file.endswith('/'):
                    # 提取到目标目录
                    filename = file.split('dist/')[-1]
                    target = STATIC_DIR / filename
                    
                    # 创建子目录
                    target.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 写入文件
                    with zip_ref.open(file) as source, open(target, 'wb') as dest:
                        dest.write(source.read())
        
        print(f"✅ 解压完成: {STATIC_DIR}")
        
        # 删除zip文件
        zip_path.unlink()
        print("🧹 清理临时文件...")
        
        # 检查必要文件
        required_files = [
            'swagger-ui.css',
            'swagger-ui-bundle.js',
            'swagger-ui-standalone-preset.js',
        ]
        
        missing = []
        for file in required_files:
            if not (STATIC_DIR / file).exists():
                missing.append(file)
        
        if missing:
            print(f"⚠️  警告: 缺少文件 {missing}")
            return False
        
        print("🎉 Swagger UI本地部署成功！")
        print(f"📁 文件位置: {STATIC_DIR}")
        print(f"📝 重启服务器后访问: http://localhost:8000/docs-local")
        
        return True
        
    except Exception as e:
        print(f"❌ 下载失败: {e}")
        print("\n💡 手动下载方法:")
        print(f"1. 访问: https://github.com/swagger-api/swagger-ui/releases/tag/v{SWAGGER_VERSION}")
        print(f"2. 下载 swagger-ui-{SWAGGER_VERSION}.zip")
        print(f"3. 解压dist目录到: {STATIC_DIR}")
        return False

if __name__ == "__main__":
    download_swagger_ui()
