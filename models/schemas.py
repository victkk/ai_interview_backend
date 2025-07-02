from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class InterviewStatus(str, Enum):
    """面试状态枚举"""

    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ProcessingType(str, Enum):
    """处理类型枚举"""

    AUDIO_TO_TEXT = "audio_to_text"
    VIDEO_ANALYSIS = "video_analysis"
    EMOTION_DETECTION = "emotion_detection"


class InterviewSession(BaseModel):
    """面试会话模型"""

    session_id: str = Field(..., description="会话ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    status: InterviewStatus = Field(InterviewStatus.WAITING, description="面试状态")
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="额外元数据"
    )


class InterviewSessionCreate(BaseModel):
    """创建面试会话请求"""

    user_id: Optional[str] = Field(None, description="用户ID")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="额外元数据"
    )


class VideoStreamData(BaseModel):
    """视频流数据模型"""

    session_id: str = Field(..., description="会话ID")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")
    data_size: int = Field(..., description="数据大小")
    format: Optional[str] = Field("webm", description="视频格式")


class AudioProcessingRequest(BaseModel):
    """音频处理请求"""

    session_id: str = Field(..., description="会话ID")
    audio_data: Optional[str] = Field(None, description="音频数据（base64编码）")
    processing_type: ProcessingType = Field(
        ProcessingType.AUDIO_TO_TEXT, description="处理类型"
    )
    language: Optional[str] = Field("zh", description="语言代码")


class AudioProcessingResponse(BaseModel):
    """音频处理响应"""

    session_id: str = Field(..., description="会话ID")
    processing_type: ProcessingType = Field(..., description="处理类型")
    result: Dict[str, Any] = Field(..., description="处理结果")
    confidence: Optional[float] = Field(None, description="置信度")
    processing_time: Optional[float] = Field(None, description="处理时间（秒）")
    timestamp: datetime = Field(default_factory=datetime.now, description="处理时间戳")


class WhisperResponse(BaseModel):
    """Whisper模型响应"""

    text: str = Field(..., description="识别出的文本")
    language: str = Field(..., description="检测到的语言")
    segments: List[Dict[str, Any]] = Field(default_factory=list, description="分段信息")
    confidence: float = Field(..., description="整体置信度")


class VideoAnalysisResponse(BaseModel):
    """视频分析响应"""

    emotions: List[Dict[str, Any]] = Field(
        default_factory=list, description="情感分析结果"
    )
    gestures: List[Dict[str, Any]] = Field(
        default_factory=list, description="手势识别结果"
    )
    eye_contact: Optional[float] = Field(None, description="眼神接触度")
    posture_score: Optional[float] = Field(None, description="姿态评分")


class InterviewResult(BaseModel):
    """面试结果模型"""

    session_id: str = Field(..., description="会话ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    transcript: List[str] = Field(default_factory=list, description="对话转录")
    video_analysis: Optional[VideoAnalysisResponse] = Field(
        None, description="视频分析结果"
    )
    overall_score: Optional[float] = Field(None, description="总体评分")
    feedback: Optional[str] = Field(None, description="反馈意见")
    duration: Optional[float] = Field(None, description="面试时长（分钟）")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")


class WebSocketMessage(BaseModel):
    """WebSocket消息模型"""

    type: str = Field(..., description="消息类型")
    session_id: str = Field(..., description="会话ID")
    data: Dict[str, Any] = Field(default_factory=dict, description="消息数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class APIResponse(BaseModel):
    """通用API响应格式"""

    success: bool = Field(True, description="请求是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")
