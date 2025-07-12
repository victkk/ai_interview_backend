from fastapi import WebSocket
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime
from models.schemas import VideoStreamData
from services.ai_service import AIService
from services.interview_session import InterviewSession


logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储会话信息
        self.sessions: Dict[str, InterviewSession] = {}

    async def create_session(self, session_id: str):
        # 在这里获取当前正在运行的事件循环
        loop = asyncio.get_running_loop()
        # 将获取到的 loop 传给 InterviewSession 的构造函数
        self.sessions[session_id] = InterviewSession(session_id, loop)
        await self.sessions[session_id].start_integrator()
        logger.info(f"started new session:{session_id}")

    async def connect_audio(self, websocket: WebSocket, session_id: str):
        if session_id not in self.sessions.keys():
            raise ValueError(f"session_id:{session_id} not found")
        await websocket.accept()
        self.sessions[session_id].audio_websocket = websocket
        logger.info(f"audio websocket connected: session_id={session_id}")
        return True

    def disconnect_audio(self, session_id: str):
        if session_id not in self.sessions.keys():
            raise ValueError(f"session_id:{session_id} not found")
        self.sessions[session_id].audio_websocket = None
        logger.info(f"audio websocket disconnected: session_id={session_id}")
        return True

    def disconnect_video(self, session_id: str):
        if session_id not in self.sessions.keys():
            raise ValueError(f"session_id:{session_id} not found")
        self.sessions[session_id].video_websocket = None
        logger.info(f"video websocket disconnected: session_id={session_id}")
        return True

    async def connect_video(self, websocket: WebSocket, session_id: str):
        if session_id not in self.sessions.keys():
            raise ValueError(f"session_id:{session_id} not found")
        await websocket.accept()
        self.sessions[session_id].video_websocket = websocket
        logger.info(f"video websocket connected: session_id={session_id}")
        return True

    def feed_audio(self, session_id: str, audio_data: bytes):
        if session_id not in self.sessions.keys():
            raise ValueError(f"session_id:{session_id} not found")
        self.sessions[session_id].audio_processor.feed_audio(audio_data)
        return True

    def feed_frame(self, session_id: str, frame_data: str, timestamp: str):
        if session_id not in self.sessions.keys():
            raise ValueError(f"session_id:{session_id} not found")
        self.sessions[session_id].video_buffer.append((float(timestamp), frame_data))
        return True

    @DeprecationWarning
    async def send_message(self, session_id: str, message: dict):
        if session_id in self.sessions.keys():
            try:
                websocket = self.sessions[session_id].video_websocket
                if websocket:
                    await websocket.send_json(message)
                    logger.debug(
                        f"消息已发送到 {session_id}: {message.get('type', 'unknown')}"
                    )
            except Exception as e:
                logger.error(f"发送消息失败 {session_id}: {e}")

    @DeprecationWarning
    async def broadcast_message(
        self, message: dict, exclude_session: Optional[str] = None
    ):
        disconnected_sessions = []
        sessions_to_iterate = list(self.sessions.items())
        for session_id, session in sessions_to_iterate:
            if exclude_session and session_id == exclude_session:
                continue
            try:
                if session.video_websocket:
                    await session.video_websocket.send_json(message)
                else:
                    raise ConnectionError("Video websocket is not connected.")
            except Exception as e:
                logger.error(f"广播消息失败 {session_id}: {e}")
                disconnected_sessions.append(session_id)

        for session_id in disconnected_sessions:
            if session_id in self.sessions:
                await self.cleanup_session(session_id)

    @DeprecationWarning
    async def handle_video_data(self, session_id: str, video_data: bytes):
        try:
            logger.debug(
                f"处理视频数据: session_id={session_id}, size={len(video_data)}"
            )
            if session_id in self.sessions:
                self.sessions[session_id]["video_chunks"].append(
                    {
                        "timestamp": datetime.now(),
                        "size": len(video_data),
                        "data": video_data,
                    }
                )
            _ = VideoStreamData(session_id=session_id, data_size=len(video_data))
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

    @DeprecationWarning
    async def _process_video_async(self, session_id: str, video_data: bytes):
        """异步处理视频数据（仅保留视频分析功能）"""
        try:
            # 这里假设有一个ai_service实例
            # video_analysis = await self.ai_service.analyze_video(video_data, session_id)
            # if video_analysis:
            #     await self.send_message(
            #         session_id,
            #         {
            #             "type": "video_analysis_result",
            #             "session_id": session_id,
            #             "analysis": (
            #                 video_analysis.model_dump()
            #                 if hasattr(video_analysis, "model_dump")
            #                 else video_analysis
            #             ),
            #             "timestamp": datetime.now().isoformat(),
            #         },
            #     )
            pass
        except Exception as e:
            logger.error(f"异步视频处理失败: {e}")
            await self.send_message(
                session_id,
                {"type": "processing_error", "message": f"视频处理失败: {str(e)}"},
            )

    def get_session(self, session_id: str) -> Optional[InterviewSession]:
        return self.sessions.get(session_id)

    async def cleanup_session(self, session_id: str):
        if session_id in self.sessions:
            await self.sessions[session_id].cleanup()
            del self.sessions[session_id]
            logger.info(f"会话数据已清理: session_id={session_id}")
