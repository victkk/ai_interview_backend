from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import Dict, Any, Optional, List
import logging
import base64
from models.schemas import (
    AudioProcessingRequest,
    AudioProcessingResponse,
    APIResponse,
    ProcessingType,
    WhisperResponse,
    VideoAnalysisResponse,
    # 新增的模型
    InterviewerPersonaRequest,
    InterviewerPersona,
    QuestionBankRequest,
    QuestionBankResponse,
    FollowUpRequest,
    FollowUpResponse,
    MultimodalEvaluationRequest,
    MultimodalEvaluationResponse,
    InterviewReportRequest,
    InterviewReportResponse,
    BatchProcessingRequest,
    BatchProcessingResponse,
    AIServiceResponse,
)
from services.ai_service import AIService

logger = logging.getLogger(__name__)
router = APIRouter()

# AI服务实例
ai_service = AIService()


@router.post("/process-audio", response_model=APIResponse)
async def process_audio(request: AudioProcessingRequest):
    """
    处理音频数据（语音识别等）

    Args:
        request: 音频处理请求

    Returns:
        处理结果
    """
    try:
        logger.info(
            f"开始处理音频: session_id={request.session_id}, type={request.processing_type}"
        )

        # 调用AI服务处理
        result = await ai_service.process_audio_request(request.dict())

        return APIResponse(success=True, message="音频处理完成", data=result.dict())

    except Exception as e:
        logger.error(f"音频处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"音频处理失败: {str(e)}")


@router.post("/transcribe", response_model=APIResponse)
async def transcribe_audio_file(
    session_id: str = Form(...),
    language: str = Form("zh"),
    audio_file: UploadFile = File(...),
):
    """
    通过文件上传进行语音识别

    Args:
        session_id: 会话ID
        language: 语言代码
        audio_file: 音频文件

    Returns:
        语音识别结果
    """
    try:
        logger.info(
            f"开始文件语音识别: session_id={session_id}, file={audio_file.filename}"
        )

        # 读取音频文件
        audio_data = await audio_file.read()

        # 调用Whisper服务
        transcription = await ai_service.transcribe_audio(
            audio_data, session_id, language
        )

        if not transcription:
            raise HTTPException(status_code=500, detail="语音识别失败")

        return APIResponse(
            success=True, message="语音识别完成", data=transcription.dict()
        )

    except Exception as e:
        logger.error(f"文件语音识别失败: {e}")
        raise HTTPException(status_code=500, detail=f"文件语音识别失败: {str(e)}")


@router.post("/analyze-video", response_model=APIResponse)
async def analyze_video_file(
    session_id: str = Form(...), video_file: UploadFile = File(...)
):
    """
    通过文件上传进行视频分析

    Args:
        session_id: 会话ID
        video_file: 视频文件

    Returns:
        视频分析结果
    """
    try:
        logger.info(
            f"开始视频分析: session_id={session_id}, file={video_file.filename}"
        )

        # 读取视频文件
        video_data = await video_file.read()

        # 调用视频分析服务
        analysis = await ai_service.analyze_video(video_data, session_id)

        if not analysis:
            raise HTTPException(status_code=500, detail="视频分析失败")

        return APIResponse(success=True, message="视频分析完成", data=analysis.dict())

    except Exception as e:
        logger.error(f"视频分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"视频分析失败: {str(e)}")


@router.post("/detect-emotions", response_model=APIResponse)
async def detect_emotions(
    session_id: str = Form(...), image_file: UploadFile = File(...)
):
    """
    情感检测

    Args:
        session_id: 会话ID
        image_file: 图像文件

    Returns:
        情感检测结果
    """
    try:
        logger.info(
            f"开始情感检测: session_id={session_id}, file={image_file.filename}"
        )

        # 读取图像文件
        image_data = await image_file.read()

        # 调用情感检测服务
        emotions = await ai_service.detect_emotions(image_data, session_id)

        if emotions is None:
            raise HTTPException(status_code=500, detail="情感检测失败")

        return APIResponse(
            success=True,
            message="情感检测完成",
            data={
                "session_id": session_id,
                "emotions": emotions,
                "count": len(emotions),
            },
        )

    except Exception as e:
        logger.error(f"情感检测失败: {e}")
        raise HTTPException(status_code=500, detail=f"情感检测失败: {str(e)}")


@router.post("/analyze-speech-quality", response_model=APIResponse)
async def analyze_speech_quality(
    session_id: str = Form(...), audio_file: UploadFile = File(...)
):
    """
    语音质量分析

    Args:
        session_id: 会话ID
        audio_file: 音频文件

    Returns:
        语音质量分析结果
    """
    try:
        logger.info(
            f"开始语音质量分析: session_id={session_id}, file={audio_file.filename}"
        )

        # 读取音频文件
        audio_data = await audio_file.read()

        # 调用语音质量分析服务
        quality_analysis = await ai_service.analyze_speech_quality(
            audio_data, session_id
        )

        if not quality_analysis:
            raise HTTPException(status_code=500, detail="语音质量分析失败")

        return APIResponse(
            success=True,
            message="语音质量分析完成",
            data={"session_id": session_id, "quality_analysis": quality_analysis},
        )

    except Exception as e:
        logger.error(f"语音质量分析失败: {e}")
        raise HTTPException(status_code=500, detail=f"语音质量分析失败: {str(e)}")


@router.get("/models/status", response_model=APIResponse)
async def get_model_status():
    """
    获取AI模型加载状态

    Returns:
        模型状态信息
    """
    try:
        status = ai_service.get_model_status()

        return APIResponse(success=True, message="获取模型状态成功", data=status)

    except Exception as e:
        logger.error(f"获取模型状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取模型状态失败: {str(e)}")


@router.post("/models/load-whisper", response_model=APIResponse)
async def load_whisper_model(model_name: str = "base"):
    """
    加载Whisper模型

    Args:
        model_name: 模型名称

    Returns:
        加载结果
    """
    try:
        logger.info(f"开始加载Whisper模型: {model_name}")

        success = await ai_service.load_whisper_model(model_name)

        if not success:
            raise HTTPException(status_code=500, detail="Whisper模型加载失败")

        return APIResponse(
            success=True,
            message=f"Whisper模型 {model_name} 加载成功",
            data={"model_name": model_name, "loaded": True},
        )

    except Exception as e:
        logger.error(f"加载Whisper模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"加载Whisper模型失败: {str(e)}")


@router.post("/models/load-video-analysis", response_model=APIResponse)
async def load_video_analysis_model():
    """
    加载视频分析模型

    Returns:
        加载结果
    """
    try:
        logger.info("开始加载视频分析模型")

        success = await ai_service.load_video_analysis_model()

        if not success:
            raise HTTPException(status_code=500, detail="视频分析模型加载失败")

        return APIResponse(
            success=True, message="视频分析模型加载成功", data={"loaded": True}
        )

    except Exception as e:
        logger.error(f"加载视频分析模型失败: {e}")
        raise HTTPException(status_code=500, detail=f"加载视频分析模型失败: {str(e)}")


@router.get("/health", response_model=APIResponse)
async def ai_health_check():
    """
    AI服务健康检查

    Returns:
        健康状态
    """
    try:
        health_info = await ai_service.health_check()

        return APIResponse(success=True, message="AI服务运行正常", data=health_info)

    except Exception as e:
        logger.error(f"AI服务健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI服务健康检查失败: {str(e)}")


@router.post("/batch-process", response_model=APIResponse)
async def batch_process_audio(
    session_id: str = Form(...),
    processing_types: str = Form(...),  # 逗号分隔的处理类型
    audio_file: UploadFile = File(...),
):
    """
    批量处理音频（同时进行多种分析）

    Args:
        session_id: 会话ID
        processing_types: 处理类型（逗号分隔）
        audio_file: 音频文件

    Returns:
        批量处理结果
    """
    try:
        logger.info(f"开始批量处理: session_id={session_id}, types={processing_types}")

        # 解析处理类型
        types = [t.strip() for t in processing_types.split(",")]

        # 读取音频文件
        audio_data = await audio_file.read()

        results = {}

        # 逐个处理
        for proc_type in types:
            if proc_type == "transcribe":
                result = await ai_service.transcribe_audio(audio_data, session_id)
                results["transcription"] = result.dict() if result else None
            elif proc_type == "speech_quality":
                result = await ai_service.analyze_speech_quality(audio_data, session_id)
                results["speech_quality"] = result

        return APIResponse(
            success=True,
            message="批量处理完成",
            data={
                "session_id": session_id,
                "processing_types": types,
                "results": results,
            },
        )

    except Exception as e:
        logger.error(f"批量处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}")


# ================================
# 新增的六大核心功能API接口
# ================================

@router.post("/interviewer-persona", response_model=APIResponse)
async def generate_interviewer_persona(request: InterviewerPersonaRequest):
    """
    生成面试官角色
    
    Args:
        request: 面试官角色生成请求
        
    Returns:
        面试官角色信息
    """
    try:
        logger.info(f"开始生成面试官角色: job_position={request.job_position}")
        
        result = await ai_service.generate_interviewer_persona(request)
        
        if result:
            return APIResponse(
                success=True,
                message="面试官角色生成成功",
                data=result.dict()
            )
        else:
            return APIResponse(
                success=False,
                message="面试官角色生成失败",
                data=None
            )
            
    except Exception as e:
        logger.error(f"生成面试官角色失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成面试官角色失败: {str(e)}")


@router.post("/question-bank", response_model=APIResponse)
async def generate_question_bank(request: QuestionBankRequest):
    """
    生成岗位面试题库
    
    Args:
        request: 题库生成请求
        
    Returns:
        面试题库
    """
    try:
        logger.info(f"开始生成面试题库: job_position={request.job_position}")
        
        result = await ai_service.generate_question_bank(request)
        
        if result:
            return APIResponse(
                success=True,
                message="面试题库生成成功",
                data=result.dict()
            )
        else:
            return APIResponse(
                success=False,
                message="面试题库生成失败",
                data=None
            )
            
    except Exception as e:
        logger.error(f"生成面试题库失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成面试题库失败: {str(e)}")


@router.post("/follow-up", response_model=APIResponse)
async def generate_follow_up_questions(request: FollowUpRequest):
    """
    生成动态追问问题
    
    Args:
        request: 追问请求
        
    Returns:
        追问问题列表
    """
    try:
        logger.info(f"开始生成追问问题: original_question={request.original_question[:50]}...")
        
        result = await ai_service.generate_follow_up_questions(request)
        
        if result:
            return APIResponse(
                success=True,
                message="追问问题生成成功",
                data=result.dict()
            )
        else:
            return APIResponse(
                success=False,
                message="追问问题生成失败",
                data=None
            )
            
    except Exception as e:
        logger.error(f"生成追问问题失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成追问问题失败: {str(e)}")


@router.post("/multimodal-evaluation", response_model=APIResponse)
async def evaluate_multimodal_performance(request: MultimodalEvaluationRequest):
    """
    多模态表现综合评估
    
    Args:
        request: 多模态评估请求
        
    Returns:
        评估结果
    """
    try:
        logger.info(f"开始多模态表现评估: question={request.question[:50]}...")
        
        result = await ai_service.evaluate_multimodal_performance(request)
        
        if result:
            return APIResponse(
                success=True,
                message="多模态表现评估成功",
                data=result.dict()
            )
        else:
            return APIResponse(
                success=False,
                message="多模态表现评估失败",
                data=None
            )
            
    except Exception as e:
        logger.error(f"多模态表现评估失败: {e}")
        raise HTTPException(status_code=500, detail=f"多模态表现评估失败: {str(e)}")


@router.post("/interview-report", response_model=APIResponse)
async def generate_interview_report(request: InterviewReportRequest):
    """
    生成最终面试报告
    
    Args:
        request: 面试报告请求
        
    Returns:
        面试报告
    """
    try:
        logger.info(f"开始生成面试报告: candidate={request.candidate_name}, position={request.job_position}")
        
        result = await ai_service.generate_interview_report(request)
        
        if result:
            return APIResponse(
                success=True,
                message="面试报告生成成功",
                data=result.dict()
            )
        else:
            return APIResponse(
                success=False,
                message="面试报告生成失败",
                data=None
            )
            
    except Exception as e:
        logger.error(f"生成面试报告失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成面试报告失败: {str(e)}")


@router.post("/safety-check", response_model=APIResponse)
async def safety_compliance_check(content: str = Form(...)):
    """
    安全合规检查
    
    Args:
        content: 需要检查的内容
        
    Returns:
        安全检查结果
    """
    try:
        logger.info(f"开始安全合规检查: content_length={len(content)}")
        
        result = await ai_service.safety_compliance_check(content)
        
        if result:
            return APIResponse(
                success=True,
                message="安全合规检查完成",
                data=result
            )
        else:
            return APIResponse(
                success=False,
                message="安全合规检查失败",
                data=None
            )
            
    except Exception as e:
        logger.error(f"安全合规检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"安全合规检查失败: {str(e)}")


@router.post("/batch-process", response_model=APIResponse)
async def batch_process_requests(request: BatchProcessingRequest):
    """
    批量处理请求
    
    Args:
        request: 批量处理请求
        
    Returns:
        批量处理结果
    """
    try:
        logger.info(f"开始批量处理: requests_count={len(request.requests)}")
        
        result = await ai_service.batch_process_requests(
            request.requests, 
            request.batch_id
        )
        
        return APIResponse(
            success=True,
            message="批量处理完成",
            data=result
        )
        
    except Exception as e:
        logger.error(f"批量处理失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}")


@router.get("/health", response_model=APIResponse)
async def ai_health_check():
    """
    AI服务健康检查
    
    Returns:
        健康状态信息
    """
    try:
        result = await ai_service.health_check()
        
        return APIResponse(
            success=True,
            message="AI服务健康检查完成",
            data=result
        )
        
    except Exception as e:
        logger.error(f"AI服务健康检查失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI服务健康检查失败: {str(e)}")
