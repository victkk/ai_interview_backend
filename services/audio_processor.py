# audio_processor.py

import asyncio
import threading
from opencc import OpenCC
from RealtimeSTT import AudioToTextRecorder
import numpy as np
from scipy.signal import resample


class AudioProcessor:
    def __init__(self, output_queue: asyncio.Queue, loop: asyncio.AbstractEventLoop):
        self.output_queue = output_queue
        self.main_loop = loop  # 保存主线程的事件循环引用
        self.cc = OpenCC("t2s")
        self.is_running = True

        recorder_config = {
            "spinner": False,
            "use_microphone": False,
            "model": "large",
            "language": "zh",
            "silero_sensitivity": 0.4,
            "webrtc_sensitivity": 2,
            "post_speech_silence_duration": 0.7,
            "min_length_of_recording": 0,
            "min_gap_between_recordings": 0,
            "enable_realtime_transcription": False,  # 我们只关心最终结果
        }
        self.recorder = AudioToTextRecorder(**recorder_config)

        # 启动后台处理线程
        self.processing_thread = threading.Thread(target=self._process_text)
        self.processing_thread.daemon = True
        self.processing_thread.start()

    def _process_text(self):
        """这个函数在独立的线程中运行，专门处理最终文本"""
        while self.is_running:
            try:
                # recorder.text() 是一个阻塞操作，正好符合我们的需求
                full_sentence = self.recorder.text()
                if full_sentence:
                    simplified_sentence = self.cc.convert(full_sentence)
                    print(f"[AudioProcessor] Detected Sentence: {simplified_sentence}")

                    # 关键：使用保存的 self.main_loop，而不是 get_running_loop()
                    asyncio.run_coroutine_threadsafe(
                        self.output_queue.put(simplified_sentence),
                        self.main_loop,
                    )
            except Exception as e:
                print(f"Error in recorder text processing thread: {e}")
                break

    def feed_audio(self, chunk: bytes):
        """接收音频块并喂给recorder"""
        # 注意：这里的音频重采样逻辑需要根据客户端发送的数据格式来确定
        # 我这里直接假设客户端发送的就是16-bit PCM了
        # 有人写了重采样 没看懂 修
        # todo： @hyq
        self.recorder.feed_audio(chunk)

    def stop(self):
        """停止处理器"""
        self.is_running = False
        self.recorder.stop()
        if self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
