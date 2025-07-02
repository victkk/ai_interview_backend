from fastapi import WebSocket
from typing import Dict, List, Optional
import asyncio
import logging
import json
from datetime import datetime
import uuid
from models.schemas import VideoStreamData, WebSocketMessage
from services.video_processor import VideoProcessor
from services.ai_service import AIService

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""

    def __init__(self):
        # 存储活跃的WebSocket连接
        self.active_connections: Dict[str, WebSocket] = {}
        # 存储会话信息
        self.sessions: Dict[str, Dict] = {}
        # 视频处理器
        self.video_processor = VideoProcessor()
        # AI服务
        self.ai_service = AIService()

    async def connect(self, websocket: WebSocket, session_id: str):
        """
        建立WebSocket连接

        Args:
            websocket: WebSocket连接对象
            session_id: 会话ID
        """
        await websocket.accept()
        self.active_connections[session_id] = websocket

        # 初始化会话信息
        self.sessions[session_id] = {
            "start_time": datetime.now(),
            "status": "connected",
            "video_chunks": [],
            "processed_data": [],
        }

        logger.info(f"WebSocket连接已建立: session_id={session_id}")

        # 发送连接确认消息
        await self.send_message(
            session_id,
            {
                "type": "connection_established",
                "session_id": session_id,
                "message": "连接已建立，可以开始传输视频流",
            },
        )

    async def disconnect(self, session_id: str):
        """
        断开WebSocket连接

        Args:
            session_id: 会话ID
        """
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        if session_id in self.sessions:
            # 更新会话状态
            self.sessions[session_id]["status"] = "disconnected"
            self.sessions[session_id]["end_time"] = datetime.now()

        logger.info(f"WebSocket连接已断开: session_id={session_id}")

    async def send_message(self, session_id: str, message: dict):
        """
        向指定会话发送消息

        Args:
            session_id: 会话ID
            message: 要发送的消息
        """
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

    async def broadcast_message(
        self, message: dict, exclude_session: Optional[str] = None
    ):
        """
        广播消息到所有连接

        Args:
            message: 要广播的消息
            exclude_session: 要排除的会话ID
        """
        disconnected_sessions = []

        for session_id, websocket in self.active_connections.items():
            if exclude_session and session_id == exclude_session:
                continue

            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"广播消息失败 {session_id}: {e}")
                disconnected_sessions.append(session_id)

        # 清理断开的连接
        for session_id in disconnected_sessions:
            await self.disconnect(session_id)

    async def handle_video_data(self, session_id: str, video_data: bytes):
        """
        处理接收到的视频数据

        Args:
            session_id: 会话ID
            video_data: 视频数据字节
        """
        try:
            logger.debug(
                f"处理视频数据: session_id={session_id}, size={len(video_data)}"
            )

            # 存储视频数据块
            if session_id in self.sessions:
                self.sessions[session_id]["video_chunks"].append(
                    {
                        "timestamp": datetime.now(),
                        "size": len(video_data),
                        "data": video_data,
                    }
                )

            # 创建视频流数据对象
            stream_data = VideoStreamData(
                session_id=session_id, data_size=len(video_data)
            )

            # 异步处理视频数据
            asyncio.create_task(self._process_video_async(session_id, video_data))

            # 发送处理状态更新
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
        """
        异步处理视频数据

        Args:
            session_id: 会话ID
            video_data: 视频数据字节
        """
        try:
            # 提取音频
            audio_data = await self.video_processor.extract_audio(video_data)

            if audio_data:
                # 调用AI服务处理音频
                transcription = await self.ai_service.transcribe_audio(
                    audio_data, session_id
                )

                # 存储处理结果
                if session_id in self.sessions:
                    self.sessions[session_id]["processed_data"].append(
                        {
                            "type": "transcription",
                            "result": transcription,
                            "timestamp": datetime.now(),
                        }
                    )

                # 发送转录结果
                await self.send_message(
                    session_id,
                    {
                        "type": "transcription_result",
                        "session_id": session_id,
                        "transcription": transcription,
                        "timestamp": datetime.now().isoformat(),
                    },
                )

            # 视频分析（可选）
            video_analysis = await self.ai_service.analyze_video(video_data, session_id)

            if video_analysis:
                # 存储视频分析结果
                if session_id in self.sessions:
                    self.sessions[session_id]["processed_data"].append(
                        {
                            "type": "video_analysis",
                            "result": video_analysis,
                            "timestamp": datetime.now(),
                        }
                    )

                # 发送视频分析结果
                await self.send_message(
                    session_id,
                    {
                        "type": "video_analysis_result",
                        "session_id": session_id,
                        "analysis": video_analysis,
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
        """
        获取会话信息

        Args:
            session_id: 会话ID

        Returns:
            会话信息字典
        """
        return self.sessions.get(session_id)

    def get_active_sessions(self) -> List[str]:
        """
        获取所有活跃会话ID

        Returns:
            活跃会话ID列表
        """
        return list(self.active_connections.keys())

    async def cleanup_session(self, session_id: str):
        """
        清理会话数据

        Args:
            session_id: 会话ID
        """
        if session_id in self.sessions:
            # 清理视频数据块以释放内存
            if "video_chunks" in self.sessions[session_id]:
                self.sessions[session_id]["video_chunks"].clear()

            logger.info(f"会话数据已清理: session_id={session_id}")
