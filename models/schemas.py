from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
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

# ================================
# 面试官角色相关模型
# ================================

class InterviewerPersona(BaseModel):
    """面试官角色模型"""
    interviewer_name: str = Field(..., description="面试官姓名")
    personality_description: str = Field(..., description="角色性格描述")
    opening_statement: str = Field(..., description="开场白")
    questioning_style: str = Field(..., description="提问风格")
    interaction_style: str = Field(..., description="互动风格")

class InterviewerPersonaRequest(BaseModel):
    """生成面试官角色请求"""
    job_position: str = Field(..., description="面试岗位")
    key_focus_areas: List[str] = Field(..., description="考察重点")
    personality_style: str = Field(..., description="性格风格")
    interviewer_name: str = Field(..., description="面试官姓名")

# ================================
# 面试题库相关模型
# ================================

class InterviewQuestion(BaseModel):
    """面试题目模型"""
    question_text: str = Field(..., description="问题内容")
    question_type: str = Field(..., description="问题类型")
    primary_indicator: str = Field(..., description="主要考察能力指标")

class QuestionBankRequest(BaseModel):
    """生成题库请求"""
    job_position: str = Field(..., description="面试岗位")
    technical_field: str = Field(..., description="技术领域")
    core_competency_indicators: List[str] = Field(..., description="核心能力指标")

class QuestionBankResponse(BaseModel):
    """题库响应"""
    questions: List[InterviewQuestion] = Field(..., description="问题列表")
    total_count: int = Field(..., description="题目总数")

# ================================
# 动态追问相关模型
# ================================

class FollowUpRequest(BaseModel):
    """追问请求"""
    original_question: str = Field(..., description="原始问题")
    candidate_answer: str = Field(..., description="候选人回答")
    target_competency: str = Field(..., description="主要考察能力点")
    interviewer_persona: str = Field(..., description="面试官角色风格")

class FollowUpResponse(BaseModel):
    """追问响应"""
    follow_up_questions: List[str] = Field(..., description="追问问题列表")

# ================================
# 多模态评估相关模型
# ================================

class TextAnalysis(BaseModel):
    """文本分析结果"""
    transcript: str = Field(..., description="候选人回答文本")
    keywords_coverage: float = Field(..., description="关键词覆盖率")
    answer_structure: str = Field(..., description="回答结构分析")

class AudioAnalysis(BaseModel):
    """音频分析结果"""
    avg_speech_rate: str = Field(..., description="平均语速")
    sentiment_tone: str = Field(..., description="情感语调")
    pauses_and_fillers: str = Field(..., description="停顿和填充词分析")

class VideoAnalysis(BaseModel):
    """视频分析结果"""
    eye_contact_level: str = Field(..., description="眼神交流水平")
    micro_expressions: List[str] = Field(..., description="关键微表情")
    body_language: str = Field(..., description="肢体语言")

class MultimodalEvaluationRequest(BaseModel):
    """多模态评估请求"""
    question: str = Field(..., description="被提问的问题")
    evaluation_indicators: List[str] = Field(..., description="评估指标")
    text_analysis: TextAnalysis = Field(..., description="文本分析结果")
    audio_analysis: AudioAnalysis = Field(..., description="音频分析结果")
    video_analysis: VideoAnalysis = Field(..., description="视频分析结果")

class IndicatorScore(BaseModel):
    """单项指标评分"""
    indicator: str = Field(..., description="指标名称")
    score: float = Field(..., ge=1, le=10, description="评分(1-10)")
    comment: str = Field(..., description="评语")

class MultimodalEvaluationResponse(BaseModel):
    """多模态评估响应"""
    indicator_scores: List[IndicatorScore] = Field(..., description="各指标评分")

# ================================
# 面试报告相关模型
# ================================

class KeyMoment(BaseModel):
    """关键表现时刻"""
    question: str = Field(..., description="关键问题")
    observation: str = Field(..., description="观察结果")

class InterviewReportRequest(BaseModel):
    """面试报告请求"""
    candidate_name: str = Field(..., description="候选人姓名")
    job_position: str = Field(..., description="面试岗位")
    overall_scores: Dict[str, float] = Field(..., description="综合评分")
    key_moments: List[KeyMoment] = Field(..., description="关键表现时刻")

class CompanyReport(BaseModel):
    """企业决策报告"""
    overall_summary: str = Field(..., description="综合评语")
    radar_chart_data: Dict[str, float] = Field(..., description="雷达图数据")
    strengths: List[str] = Field(..., description="优势")
    areas_for_improvement: List[str] = Field(..., description="待提升点")
    key_moment_highlights: List[str] = Field(..., description="关键表现定位")
    hiring_recommendation: str = Field(..., description="录用建议")

class CandidateReport(BaseModel):
    """候选人反馈报告"""
    positive_opening: str = Field(..., description="积极开场")
    strengths: List[str] = Field(..., description="表现亮点")
    personalized_suggestions: List[str] = Field(..., description="个性化改进建议")
    closing_encouragement: str = Field(..., description="总结与鼓励")

class InterviewReportResponse(BaseModel):
    """面试报告响应"""
    company_report: CompanyReport = Field(..., description="企业报告")
    candidate_report: CandidateReport = Field(..., description="候选人报告")

# ================================
# Prompt 模板相关模型
# ================================

class PromptTemplate(BaseModel):
    """Prompt模板"""
    template_id: str = Field(..., description="模板ID")
    template_name: str = Field(..., description="模板名称")
    template_content: str = Field(..., description="模板内容")
    template_type: str = Field(..., description="模板类型")
    version: str = Field(default="1.0", description="版本号")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class PromptTemplateRequest(BaseModel):
    """Prompt模板请求"""
    template_name: str = Field(..., description="模板名称")
    template_content: str = Field(..., description="模板内容")
    template_type: str = Field(..., description="模板类型")

# ================================
# AI 服务配置相关模型
# ================================

class AIServiceConfig(BaseModel):
    """AI服务配置"""
    service_name: str = Field(..., description="服务名称")
    api_endpoint: str = Field(..., description="API端点")
    api_key: Optional[str] = Field(None, description="API密钥")
    model_name: str = Field(..., description="模型名称")
    temperature: float = Field(default=0.7, description="温度参数")
    max_tokens: int = Field(default=2000, description="最大token数")
    timeout: int = Field(default=30, description="超时时间(秒)")
    enabled: bool = Field(default=True, description="是否启用")

class AIServiceConfigRequest(BaseModel):
    """AI服务配置请求"""
    service_name: str = Field(..., description="服务名称")
    api_endpoint: str = Field(..., description="API端点")
    api_key: Optional[str] = Field(None, description="API密钥")
    model_name: str = Field(..., description="模型名称")
    temperature: Optional[float] = Field(0.7, description="温度参数")
    max_tokens: Optional[int] = Field(2000, description="最大token数")
    timeout: Optional[int] = Field(30, description="超时时间(秒)")
    enabled: Optional[bool] = Field(True, description="是否启用")

# ================================
# 通用响应模型
# ================================

class AIServiceResponse(BaseModel):
    """AI服务通用响应"""
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    message: str = Field(..., description="响应消息")
    request_id: Optional[str] = Field(None, description="请求ID")
    processing_time: float = Field(..., description="处理时间")

class BatchProcessingRequest(BaseModel):
    """批量处理请求"""
    requests: List[Dict[str, Any]] = Field(..., description="请求列表")
    batch_id: Optional[str] = Field(None, description="批次ID")

class BatchProcessingResponse(BaseModel):
    """批量处理响应"""
    batch_id: str = Field(..., description="批次ID")
    total_count: int = Field(..., description="总数")
    success_count: int = Field(..., description="成功数")
    failed_count: int = Field(..., description="失败数")
    results: List[AIServiceResponse] = Field(..., description="结果列表")
