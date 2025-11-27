#!/usr/bin/env python3
"""
带端口检查的uvicorn启动脚本
使用方法: python start_with_check.py
"""

import sys
import subprocess
import re
from loguru import logger

# 配置
HOST = "0.0.0.0"
PORT = 8000
APP_NAME = "owlRD Backend"

def get_port_processes(port: int) -> list:
    """获取占用指定端口的进程信息"""
    try:
        result = subprocess.run(
            f'netstat -ano | findstr ":{port}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        processes = []
        pids_seen = set()
        
        for line in result.stdout.strip().split('\n'):
            if line.strip() and 'LISTENING' in line:
                # 提取PID
                match = re.search(r'\s+(\d+)\s*$', line)
                if match:
                    pid = match.group(1)
                    if pid in pids_seen:
                        continue
                    pids_seen.add(pid)
                    
                    # 验证进程是否真的存在
                    try:
                        proc_check = subprocess.run(
                            f'tasklist /FI "PID eq {pid}" /NH',
                            shell=True,
                            capture_output=True,
                            text=True
                        )
                        
                        if proc_check.returncode == 0 and proc_check.stdout.strip():
                            # 进程存在，获取进程名
                            lines = proc_check.stdout.strip().split('\n')
                            for proc_line in lines:
                                if pid in proc_line and not '没有运行的任务' in proc_line:
                                    parts = proc_line.split()
                                    if len(parts) >= 1:
                                        proc_name = parts[0]
                                        processes.append({'pid': pid, 'name': proc_name})
                                        break
                            else:
                                # 如果没有找到有效的进程名，跳过这个PID
                                continue
                        else:
                            # 进程不存在，跳过
                            continue
                    except:
                        # 如果检查失败，跳过这个PID
                        continue
        
        return processes
    except Exception:
        return []


def kill_processes(pids: list) -> bool:
    """终止指定的进程"""
    success = True
    for pid in pids:
        try:
            subprocess.run(f'taskkill /PID {pid} /F', shell=True, check=True)
            logger.info(f"✅ 成功终止进程 PID: {pid}")
        except subprocess.CalledProcessError:
            logger.error(f"❌ 无法终止进程 PID: {pid}")
            success = False
    return success


def check_port_available(port: int) -> bool:
    """检查端口是否被占用，如果被占用则提供交互式清理"""
    processes = get_port_processes(port)
    
    if not processes:
        return True
    
    logger.warning(f"⚠️  端口 {port} 被以下进程占用:")
    for proc in processes:
        logger.warning(f"  - PID: {proc['pid']} | 进程: {proc['name']}")
    
    print()
    while True:
        response = input(f"是否终止这些进程以启动新的服务? (Y/N): ").strip().upper()
        if response in ['Y', 'YES']:
            pids = [proc['pid'] for proc in processes]
            if kill_processes(pids):
                logger.success("✅ 所有占用进程已清理")
                return True
            else:
                logger.error("❌ 部分进程清理失败")
                return False
        elif response in ['N', 'NO']:
            logger.info("❌ 用户选择不清理进程，服务无法启动")
            return False
        else:
            print("请输入 Y 或 N")


def main():
    """主函数"""
    print("========================================")
    print(f"  {APP_NAME} 启动脚本")
    print(f"  端口: {PORT}")
    print("========================================")
    print()
    
    # 检查端口是否被占用，提供交互式清理
    if not check_port_available(PORT):
        sys.exit(1)
    
    logger.info(f"✅ 端口 {PORT} 可用，启动服务...")
    print()
    print(f"正在启动 {APP_NAME}...")
    print(f"访问地址: http://localhost:{PORT}")
    print(f"API文档: http://localhost:{PORT}/docs")
    print()
    print("按 Ctrl+C 停止服务")
    print("========================================")
    print()
    
    # 启动uvicorn
    try:
        subprocess.run([
            "uvicorn", 
            "app.main:app", 
            "--host", HOST,
            "--port", str(PORT),
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        logger.info("服务已停止")
    except subprocess.CalledProcessError as e:
        logger.error(f"启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
