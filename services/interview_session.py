from fastapi import WebSocket
import asyncio
import uuid
from collections import deque
from typing import Deque, Optional, Dict
from utils.util import base64_to_image
from datetime import datetime

from services.audio_processor import AudioProcessor


class InterviewSession:
    def __init__(self, session_id: str, loop: asyncio.AbstractEventLoop):
        self.session_id: str = session_id
        self.last_active_time = datetime.now()
        print(f"[{self.session_id}] Creating new interview session.")

        # 1. 独立的资源
        self.video_buffer: Deque[tuple] = deque(maxlen=500)  # 每个会话独有的视频缓冲
        self.audio_results_queue: asyncio.Queue = asyncio.Queue()
        # 将 loop 传递给 AudioProcessor
        self.audio_processor: AudioProcessor = AudioProcessor(
            output_queue=self.audio_results_queue, loop=loop
        )

        # 2. 状态和任务管理
        self.integrator_task: Optional[asyncio.Task] = None
        self.is_active: bool = True

        # 3. WebSocket连接的引用（可选，但对于双向通信很有用）
        self.audio_websocket: Optional[WebSocket] = None
        self.video_websocket: Optional[WebSocket] = None

    async def start_integrator(self):
        """启动该会话的整合器任务"""
        if not self.integrator_task:
            self.integrator_task = asyncio.create_task(self._integrator_logic())
            print(f"[{self.session_id}] Integrator task started.")

    async def _integrator_logic(self):
        """
        整合器逻辑，现在是类的一个方法，操作的是类的属性。
        1. 从音频队列中获取音频结果
        2. 从视频缓冲区中查找视频帧
        3. 打包数据，调用LLM(留给wjq实现)
        4. 结果处理（尚未分锅）
        """
        # todo @wjq 在别的地方实现一个ai接口类 调用模型的逻辑写在类里 这里只负责将拿到的语音转写文字和图像整合
        while self.is_active:
            try:
                sentence = await self.audio_results_queue.get()
                print(f"[{self.session_id}] 获取到音频转写的句子: {sentence}")
                self.audio_results_queue.task_done()
                timestamp, base64_img = self.video_buffer.pop()
                img = base64_to_image(base64_img)
                
            except asyncio.CancelledError:
                break
        print(f"[{self.session_id}] Integrator logic stopped.")

    async def cleanup(self):
        """清理该会话的所有资源"""
        self.is_active = False

        if self.integrator_task:
            self.integrator_task.cancel()
            try:
                await self.integrator_task
            except asyncio.CancelledError:
                pass

        if self.audio_processor:
            self.audio_processor.stop()

        # 清空缓冲区和队列
        self.video_buffer.clear()
        while not self.audio_results_queue.empty():
            self.audio_results_queue.get_nowait()

        print(f"[{self.session_id}] Session resources cleaned up.")
