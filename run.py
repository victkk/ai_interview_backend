#!/usr/bin/env python3
"""
AI面试系统启动脚本
"""
import os
import sys
import subprocess


def check_dependencies():
    """检查依赖是否安装"""
    try:
        import fastapi
        import uvicorn
        import websockets

        print("✓ 依赖检查通过")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False


def start_server():
    """启动服务器"""
    if not check_dependencies():
        sys.exit(1)

    print("🚀 启动AI面试系统后端...")
    print("📝 API文档: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws/video-stream/{session_id}")
    print("⚡ 使用 Ctrl+C 停止服务")

    try:
        # 使用uvicorn启动
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
                "--log-level",
                "info",
            ]
        )
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")


if __name__ == "__main__":
    start_server()
