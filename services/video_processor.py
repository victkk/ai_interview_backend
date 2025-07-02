import asyncio
import logging
import tempfile
import os
from typing import Optional, Tuple
import ffmpeg
import numpy as np
from datetime import datetime

logger = logging.getLogger(__name__)


class VideoProcessor:
    """视频处理器类"""

    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        logger.info(f"视频处理器初始化，临时目录: {self.temp_dir}")

    async def extract_audio(
        self, video_data: bytes, output_format: str = "wav", sample_rate: int = 16000
    ) -> Optional[bytes]:
        """
        从视频数据中提取音频

        Args:
            video_data: 视频数据字节
            output_format: 输出音频格式 (wav, mp3, etc.)
            sample_rate: 采样率

        Returns:
            音频数据字节，如果提取失败则返回None
        """
        try:
            # 创建临时文件
            input_path = os.path.join(
                self.temp_dir, f"input_{datetime.now().timestamp()}.webm"
            )
            output_path = os.path.join(
                self.temp_dir, f"output_{datetime.now().timestamp()}.{output_format}"
            )

            # 写入视频数据到临时文件
            with open(input_path, "wb") as f:
                f.write(video_data)

            # 使用ffmpeg提取音频
            (
                ffmpeg.input(input_path)
                .output(
                    output_path,
                    acodec="pcm_s16le" if output_format == "wav" else "mp3",
                    ar=sample_rate,
                    ac=1,
                )  # 单声道
                .overwrite_output()
                .run(quiet=True)
            )

            # 读取提取的音频数据
            with open(output_path, "rb") as f:
                audio_data = f.read()

            # 清理临时文件
            os.remove(input_path)
            os.remove(output_path)

            logger.debug(f"音频提取成功，大小: {len(audio_data)} bytes")
            return audio_data

        except Exception as e:
            logger.error(f"音频提取失败: {e}")
            # 清理可能存在的临时文件
            for path in [input_path, output_path]:
                if "path" in locals() and os.path.exists(path):
                    os.remove(path)
            return None

    async def extract_video_frames(
        self, video_data: bytes, interval: float = 1.0, max_frames: int = 10
    ) -> list:
        """
        从视频中提取关键帧

        Args:
            video_data: 视频数据字节
            interval: 提取帧的时间间隔（秒）
            max_frames: 最大提取帧数

        Returns:
            帧数据列表
        """
        try:
            frames = []
            input_path = os.path.join(
                self.temp_dir, f"input_{datetime.now().timestamp()}.webm"
            )

            # 写入视频数据
            with open(input_path, "wb") as f:
                f.write(video_data)

            # 获取视频信息
            probe = ffmpeg.probe(input_path)
            video_stream = next(
                (
                    stream
                    for stream in probe["streams"]
                    if stream["codec_type"] == "video"
                ),
                None,
            )

            if not video_stream:
                logger.warning("未找到视频流")
                return frames

            duration = float(video_stream.get("duration", 0))

            # 计算提取帧的时间点
            frame_times = []
            current_time = 0
            while current_time < duration and len(frame_times) < max_frames:
                frame_times.append(current_time)
                current_time += interval

            # 提取每一帧
            for i, time_point in enumerate(frame_times):
                frame_path = os.path.join(
                    self.temp_dir, f"frame_{i}_{datetime.now().timestamp()}.jpg"
                )

                (
                    ffmpeg.input(input_path, ss=time_point)
                    .output(frame_path, vframes=1, format="image2", vcodec="mjpeg")
                    .overwrite_output()
                    .run(quiet=True)
                )

                # 读取帧数据
                if os.path.exists(frame_path):
                    with open(frame_path, "rb") as f:
                        frame_data = f.read()

                    frames.append(
                        {
                            "timestamp": time_point,
                            "data": frame_data,
                            "size": len(frame_data),
                        }
                    )

                    os.remove(frame_path)

            # 清理输入文件
            os.remove(input_path)

            logger.debug(f"成功提取 {len(frames)} 帧")
            return frames

        except Exception as e:
            logger.error(f"视频帧提取失败: {e}")
            return []

    async def get_video_info(self, video_data: bytes) -> dict:
        """
        获取视频信息

        Args:
            video_data: 视频数据字节

        Returns:
            视频信息字典
        """
        try:
            input_path = os.path.join(
                self.temp_dir, f"input_{datetime.now().timestamp()}.webm"
            )

            # 写入视频数据
            with open(input_path, "wb") as f:
                f.write(video_data)

            # 获取视频信息
            probe = ffmpeg.probe(input_path)

            video_info = {
                "format": probe.get("format", {}).get("format_name", "unknown"),
                "duration": float(probe.get("format", {}).get("duration", 0)),
                "size": int(probe.get("format", {}).get("size", 0)),
                "streams": [],
            }

            # 获取流信息
            for stream in probe.get("streams", []):
                stream_info = {
                    "type": stream.get("codec_type", "unknown"),
                    "codec": stream.get("codec_name", "unknown"),
                }

                if stream.get("codec_type") == "video":
                    stream_info.update(
                        {
                            "width": stream.get("width", 0),
                            "height": stream.get("height", 0),
                            "fps": eval(stream.get("r_frame_rate", "0/1")),
                        }
                    )
                elif stream.get("codec_type") == "audio":
                    stream_info.update(
                        {
                            "sample_rate": stream.get("sample_rate", 0),
                            "channels": stream.get("channels", 0),
                        }
                    )

                video_info["streams"].append(stream_info)

            # 清理临时文件
            os.remove(input_path)

            return video_info

        except Exception as e:
            logger.error(f"获取视频信息失败: {e}")
            return {}

    async def convert_video_format(
        self, video_data: bytes, target_format: str = "mp4"
    ) -> Optional[bytes]:
        """
        转换视频格式

        Args:
            video_data: 输入视频数据
            target_format: 目标格式

        Returns:
            转换后的视频数据
        """
        try:
            input_path = os.path.join(
                self.temp_dir, f"input_{datetime.now().timestamp()}.webm"
            )
            output_path = os.path.join(
                self.temp_dir, f"output_{datetime.now().timestamp()}.{target_format}"
            )

            # 写入输入数据
            with open(input_path, "wb") as f:
                f.write(video_data)

            # 转换格式
            (
                ffmpeg.input(input_path)
                .output(output_path, vcodec="libx264", acodec="aac")
                .overwrite_output()
                .run(quiet=True)
            )

            # 读取转换后的数据
            with open(output_path, "rb") as f:
                converted_data = f.read()

            # 清理临时文件
            os.remove(input_path)
            os.remove(output_path)

            logger.debug(f"视频格式转换成功: {len(converted_data)} bytes")
            return converted_data

        except Exception as e:
            logger.error(f"视频格式转换失败: {e}")
            return None

    def cleanup(self):
        """清理临时文件和资源"""
        try:
            import shutil

            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
            logger.info("视频处理器资源清理完成")
        except Exception as e:
            logger.error(f"清理视频处理器资源失败: {e}")

    def __del__(self):
        """析构函数，确保资源清理"""
        self.cleanup()
