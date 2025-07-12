from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import logging
from routers import interview, ai_processing
from services.websocket_manager import WebSocketManager
from utils.logger import setup_logger

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

# WebSocket连接管理器（只用于视频）
websocket_manager = WebSocketManager()

# 路由注册
app.include_router(interview.router, prefix="/api/interview", tags=["面试管理"])
app.include_router(ai_processing.router, prefix="/api/ai", tags=["AI处理"])


@app.get("/")
async def root():
    return {"message": "AI面试系统后端API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "服务运行正常"}


@app.websocket("/ws/video-stream/{session_id}")
async def websocket_video_stream(websocket: WebSocket, session_id: str):
    """
    WebSocket视频流接收接口
    """
    await websocket_manager.connect(websocket, session_id)
    logger.info(f"新的视频流连接: session_id={session_id}")

    try:
        while True:
            data = await websocket.receive_bytes()
            logger.debug(f"接收到视频数据: {len(data)} bytes")
            await websocket_manager.handle_video_data(session_id, data)

    except WebSocketDisconnect:
        logger.info(f"WebSocket连接断开: session_id={session_id}")
        await websocket_manager.disconnect(session_id)

    except Exception as e:
        logger.error(f"WebSocket处理错误: {e}")
        await websocket_manager.disconnect(session_id)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
