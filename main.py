from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import logging
import os
import sys
from routers import interview, ai_processing
from services.websocket_manager import WebSocketManager
from utils.logger import setup_logger
import uuid

# 设置编码（解决Windows系统上的Unicode问题）
if sys.platform.startswith("win"):
    os.environ["PYTHONIOENCODING"] = "utf-8"

# 设置日志
setup_logger()
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="AI面试系统后端",
    description="基于FastAPI的AI面试系统，支持实时视频流处理和AI分析",
    version="1.0.0",
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应设置允许的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

websocket_manager = WebSocketManager()

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="example"), name="static")

# 路由注册
app.include_router(interview.router, prefix="/api/interview", tags=["面试管理"])
app.include_router(ai_processing.router, prefix="/api/ai", tags=["AI处理"])


@app.get("/")
async def root():
    return {"message": "AI面试系统后端API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务运行正常"}


@app.get("/example", response_class=HTMLResponse)
async def get_example_page():
    """
    访问示例测试页面
    """
    try:
        with open("example/example.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>示例页面未找到</h1>", status_code=404)


@app.get("/demo", response_class=HTMLResponse)
async def get_demo_page():
    """
    访问演示测试页面（与example相同）
    """
    try:
        with open("example/example.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content, status_code=200)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>演示页面未找到</h1>", status_code=404)


@app.post("/interviews/start")
async def start_interview():
    """
    客户端调用此接口开始一个新的面试，并获取session_id。
    """
    try:
        session_id = str(uuid.uuid4())
        await websocket_manager.create_session(session_id)
        logger.info(f"新的面试会话创建成功: session_id={session_id}")
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"创建面试会话失败: {e}")
        return {"error": "创建面试会话失败"}


@app.websocket("/ws/video/{session_id}")
async def websocket_video_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket视频流接收接口
    接受"timestamp:base64_frame"
    """
    logger.info(f"新的视频流连接: session_id={session_id}")

    try:
        await websocket_manager.connect_video(websocket, session_id)

        while True:
            data = await websocket.receive_text()
            if ":" in data:
                time_stamp, frame_data = data.split(":", 1)
                logger.debug(f"接收到视频数据: {len(data)} bytes")
                websocket_manager.feed_frame(session_id, frame_data, time_stamp)
            else:
                logger.warning(f"无效的视频数据格式: session_id={session_id}")

    except WebSocketDisconnect:
        logger.info(f"视频WebSocket连接断开: session_id={session_id}")
    except Exception as e:
        logger.error(f"视频WebSocket处理错误: {e}")
    finally:
        try:
            websocket_manager.disconnect_video(session_id)
            session = websocket_manager.get_session(session_id)
            if session and not session.audio_websocket:
                await websocket_manager.cleanup_session(session_id)
                logger.info(f"会话清理完成: session_id={session_id}")
        except Exception as e:
            logger.error(f"清理视频会话时出错: {e}")


@app.websocket("/ws/audio/{session_id}")
async def websocket_audio_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket音频流接收接口
    """
    logger.info(f"新的音频流连接: session_id={session_id}")

    try:
        await websocket_manager.connect_audio(websocket, session_id)

        while True:
            data = await websocket.receive_bytes()
            logger.debug(f"接收到音频数据: {len(data)} bytes")
            websocket_manager.feed_audio(session_id, data)

    except WebSocketDisconnect:
        logger.info(f"音频WebSocket连接断开: session_id={session_id}")
    except Exception as e:
        logger.error(f"音频WebSocket处理错误: {e}")
    finally:
        try:
            websocket_manager.disconnect_audio(session_id)
            session = websocket_manager.get_session(session_id)
            if session and not session.video_websocket:
                await websocket_manager.cleanup_session(session_id)
                logger.info(f"会话清理完成: session_id={session_id}")
        except Exception as e:
            logger.error(f"清理音频会话时出错: {e}")


if __name__ == "__main__":
    logger.info("启动AI面试系统后端服务")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
