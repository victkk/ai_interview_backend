from fastapi import WebSocket
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
from models.schemas import VideoStreamData
from services.ai_service import AIService

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储活跃的WebSocket连接
        self.active_connections: Dict[str, WebSocket] = {}
        # 存储会话信息
        self.sessions: Dict[str, Dict] = {}
        # AI服务（用于视频分析）
        self.ai_service = AIService()

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.sessions[session_id] = {
            "start_time": datetime.now(),
            "status": "connected",
            "video_chunks": [],
            "processed_data": [],
        }
        logger.info(f"WebSocket连接已建立: session_id={session_id}")
        await self.send_message(
            session_id,
            {
                "type": "connection_established",
                "session_id": session_id,
                "message": "连接已建立，可以开始传输视频流",
            },
        )

    async def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.sessions:
            self.sessions[session_id]["status"] = "disconnected"
            self.sessions[session_id]["end_time"] = datetime.now()
        logger.info(f"WebSocket连接已断开: session_id={session_id}")

    async def send_message(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_json(message)
                logger.debug(
                    f"消息已发送到 {session_id}: {message.get('type', 'unknown')}"
                )
            except Exception as e:
                logger.error(f"发送消息失败 {session_id}: {e}")
                await self.disconnect(session_id)

    async def broadcast_message(self, message: dict, exclude_session: Optional[str] = None):
        disconnected_sessions = []
        for session_id, websocket in self.active_connections.items():
            if exclude_session and session_id == exclude_session:
                continue
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败 {session_id}: {e}")
                disconnected_sessions.append(session_id)
        for session_id in disconnected_sessions:
            await self.disconnect(session_id)

    async def handle_video_data(self, session_id: str, video_data: bytes):
        try:
            logger.debug(f"处理视频数据: session_id={session_id}, size={len(video_data)}")
            if session_id in self.sessions:
                self.sessions[session_id]["video_chunks"].append(
                    {
                        "timestamp": datetime.now(),
                        "size": len(video_data),
                        "data": video_data,
                    }
                )
            _ = VideoStreamData(
                session_id=session_id, data_size=len(video_data)
            )
            asyncio.create_task(self._process_video_async(session_id, video_data))
            await self.send_message(
                session_id,
                {
                    "type": "video_data_received",
                    "session_id": session_id,
                    "data_size": len(video_data),
                    "timestamp": datetime.now().isoformat(),
                },
            )
        except Exception as e:
            logger.error(f"处理视频数据失败: {e}")
            await self.send_message(
                session_id, {"type": "error", "message": f"视频数据处理失败: {str(e)}"}
            )

    async def _process_video_async(self, session_id: str, video_data: bytes):
        """异步处理视频数据（仅保留视频分析功能）"""
        try:
            video_analysis = await self.ai_service.analyze_video(video_data, session_id)
            if video_analysis:
                await self.send_message(
                    session_id,
                    {
                        "type": "video_analysis_result",
                        "session_id": session_id,
                        "analysis": (
                            video_analysis.model_dump()
                            if hasattr(video_analysis, "model_dump")
                            else video_analysis
                        ),
                        "timestamp": datetime.now().isoformat(),
                    },
                )
        except Exception as e:
            logger.error(f"异步视频处理失败: {e}")
            await self.send_message(
                session_id,
                {"type": "processing_error", "message": f"视频处理失败: {str(e)}"},
            )

    def get_session_info(self, session_id: str) -> Optional[Dict]:
        return self.sessions.get(session_id)

    def get_active_sessions(self) -> List[str]:
        return list(self.active_connections.keys())

    async def cleanup_session(self, session_id: str):
        if session_id in self.sessions:
            if "video_chunks" in self.sessions[session_id]:
                self.sessions[session_id]["video_chunks"].clear()
            logger.info(f"会话数据已清理: session_id={session_id}")
