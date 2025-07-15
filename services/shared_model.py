# shared_model.py
import asyncio
from RealtimeSTT import AudioToTextRecorder

class SharedRecorder:
    _recorder = None
    _lock = asyncio.Lock()  # 锁保护调用

    @classmethod
    async def _ensure_recorder(cls):
        if cls._recorder is None:
            cls._recorder = AudioToTextRecorder(
                spinner=False,
                use_microphone=False,
                model="large",         # 或 small、medium，根据显存
                language="zh",
                silero_sensitivity=0.4,
                webrtc_sensitivity=2,
                post_speech_silence_duration=0.7,
                min_length_of_recording=0,
                min_gap_between_recordings=0,
                enable_realtime_transcription=False
            )

    @classmethod
    async def transcribe(cls) -> str:
        await cls._ensure_recorder()
        async with cls._lock:
            return cls._recorder.text()

    @classmethod
    def feed_audio(cls, chunk: bytes):
        if cls._recorder:
            cls._recorder.feed_audio(chunk)

    @classmethod
    def stop(cls):
        if cls._recorder:
            cls._recorder.stop()
