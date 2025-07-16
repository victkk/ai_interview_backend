import asyncio
import logging
import base64
import time
import json
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from models.schemas import (
    WhisperResponse,
    VideoAnalysisResponse,
    AudioProcessingResponse,
    ProcessingType,
    # 新增的模型
    InterviewerPersona,
    InterviewerPersonaRequest,
    InterviewQuestion,
    QuestionBankRequest,
    QuestionBankResponse,
    FollowUpRequest,
    FollowUpResponse,
    MultimodalEvaluationRequest,
    MultimodalEvaluationResponse,
    InterviewReportRequest,
    InterviewReportResponse,
    AIServiceResponse,
)
from services.prompt_manager import prompt_manager
from services.openai_client import openai_client

logger = logging.getLogger(__name__)


class AIService:
    """AI服务类 - 提供各种AI模型的调用接口"""

    def __init__(self):
        self.whisper_model_loaded = False
        self.video_analysis_model_loaded = False
        logger.info("AI服务初始化完成")

    async def transcribe_audio(
        self, audio_data: bytes, session_id: str, language: str = "zh"
    ) -> Optional[WhisperResponse]:
        """
        使用Whisper模型进行语音识别

        Args:
            audio_data: 音频数据字节
            session_id: 会话ID
            language: 语言代码

        Returns:
            Whisper识别结果
        """
        try:
            start_time = time.time()
            logger.info(
                f"开始Whisper语音识别: session_id={session_id}, audio_size={len(audio_data)}"
            )

            # TODO: 这里应该调用真实的Whisper模型
            # 目前返回模拟数据
            await asyncio.sleep(0.5)  # 模拟处理时间

            # 模拟Whisper响应
            mock_response = WhisperResponse(
                text=f"这是模拟的语音识别结果 - 会话ID: {session_id}",
                language=language,
                segments=[
                    {
                        "start": 0.0,
                        "end": 2.5,
                        "text": "这是模拟的语音识别结果",
                        "confidence": 0.95,
                    },
                    {
                        "start": 2.5,
                        "end": 4.0,
                        "text": f"会话ID: {session_id}",
                        "confidence": 0.89,
                    },
                ],
                confidence=0.92,
            )

            processing_time = time.time() - start_time
            logger.info(f"Whisper语音识别完成: 耗时 {processing_time:.2f}s")

            return mock_response

        except Exception as e:
            logger.error(f"Whisper语音识别失败: {e}")
            return None

    async def analyze_video(
        self, video_data: bytes, session_id: str
    ) -> Optional[VideoAnalysisResponse]:
        """
        视频分析（表情识别、手势检测等）

        Args:
            video_data: 视频数据字节
            session_id: 会话ID

        Returns:
            视频分析结果
        """
        try:
            start_time = time.time()
            logger.info(
                f"开始视频分析: session_id={session_id}, video_size={len(video_data)}"
            )

            # TODO: 这里应该调用真实的视频分析模型
            # 目前返回模拟数据
            await asyncio.sleep(1.0)  # 模拟处理时间

            # 模拟视频分析结果
            mock_response = VideoAnalysisResponse(
                emotions=[
                    {"emotion": "confident", "confidence": 0.85, "timestamp": 0.0},
                    {"emotion": "neutral", "confidence": 0.72, "timestamp": 2.5},
                ],
                gestures=[
                    {
                        "gesture": "hand_gesture",
                        "type": "pointing",
                        "confidence": 0.78,
                        "timestamp": 1.2,
                    }
                ],
                eye_contact=0.82,
                posture_score=0.75,
            )

            processing_time = time.time() - start_time
            logger.info(f"视频分析完成: 耗时 {processing_time:.2f}s")

            return mock_response

        except Exception as e:
            logger.error(f"视频分析失败: {e}")
            return None

    async def detect_emotions(
        self, image_data: bytes, session_id: str
    ) -> Optional[List[Dict[str, Any]]]:
        """
        情感检测

        Args:
            image_data: 图像数据字节
            session_id: 会话ID

        Returns:
            情感检测结果列表
        """
        try:
            start_time = time.time()
            logger.info(f"开始情感检测: session_id={session_id}")

            # TODO: 调用真实的情感检测模型
            await asyncio.sleep(0.3)  # 模拟处理时间

            # 模拟情感检测结果
            emotions = [
                {
                    "emotion": "happy",
                    "confidence": 0.82,
                    "bbox": [100, 150, 200, 250],  # 人脸边界框
                },
                {
                    "emotion": "confident",
                    "confidence": 0.75,
                    "bbox": [100, 150, 200, 250],
                },
            ]

            processing_time = time.time() - start_time
            logger.info(f"情感检测完成: 耗时 {processing_time:.2f}s")

            return emotions

        except Exception as e:
            logger.error(f"情感检测失败: {e}")
            return None

    async def analyze_speech_quality(
        self, audio_data: bytes, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        语音质量分析（语速、音量、清晰度等）

        Args:
            audio_data: 音频数据字节
            session_id: 会话ID

        Returns:
            语音质量分析结果
        """
        try:
            start_time = time.time()
            logger.info(f"开始语音质量分析: session_id={session_id}")

            # TODO: 调用真实的语音质量分析模型
            await asyncio.sleep(0.4)

            # 模拟语音质量分析结果
            quality_analysis = {
                "speech_rate": {
                    "words_per_minute": 150,
                    "score": 0.85,
                    "feedback": "语速适中",
                },
                "volume": {"average_db": -12.5, "score": 0.90, "feedback": "音量合适"},
                "clarity": {"score": 0.88, "feedback": "发音清晰"},
                "fluency": {
                    "pause_count": 3,
                    "filler_words": 2,
                    "score": 0.82,
                    "feedback": "表达较为流畅",
                },
                "overall_score": 0.86,
            }

            processing_time = time.time() - start_time
            logger.info(f"语音质量分析完成: 耗时 {processing_time:.2f}s")

            return quality_analysis

        except Exception as e:
            logger.error(f"语音质量分析失败: {e}")
            return None

    async def process_audio_request(
        self, request_data: Dict[str, Any]
    ) -> AudioProcessingResponse:
        """
        处理音频处理请求的统一接口

        Args:
            request_data: 请求数据字典

        Returns:
            音频处理响应
        """
        try:
            session_id = request_data.get("session_id")
            processing_type = ProcessingType(
                request_data.get("processing_type", "audio_to_text")
            )
            language = request_data.get("language", "zh")

            start_time = time.time()

            # 解码音频数据
            audio_data = None
            if "audio_data" in request_data and request_data["audio_data"]:
                audio_data = base64.b64decode(request_data["audio_data"])

            result = {}
            confidence = None

            # 根据处理类型调用不同的AI服务
            if processing_type == ProcessingType.AUDIO_TO_TEXT:
                if audio_data:
                    transcription = await self.transcribe_audio(
                        audio_data, session_id, language
                    )
                    if transcription:
                        result = transcription.dict()
                        confidence = transcription.confidence
                else:
                    result = {"error": "缺少音频数据"}

            elif processing_type == ProcessingType.EMOTION_DETECTION:
                # 这里可以扩展其他处理类型
                result = {"message": "情感检测功能待实现"}

            processing_time = time.time() - start_time

            return AudioProcessingResponse(
                session_id=session_id,
                processing_type=processing_type,
                result=result,
                confidence=confidence,
                processing_time=processing_time,
            )

        except Exception as e:
            logger.error(f"音频处理请求失败: {e}")
            return AudioProcessingResponse(
                session_id=request_data.get("session_id", "unknown"),
                processing_type=ProcessingType.AUDIO_TO_TEXT,
                result={"error": str(e)},
                processing_time=0.0,
            )

    async def load_whisper_model(self, model_name: str = "base") -> bool:
        """
        加载Whisper模型

        Args:
            model_name: 模型名称 (tiny, base, small, medium, large)

        Returns:
            是否加载成功
        """
        try:
            logger.info(f"开始加载Whisper模型: {model_name}")

            # TODO: 实际加载Whisper模型
            # import whisper
            # self.whisper_model = whisper.load_model(model_name)

            await asyncio.sleep(2.0)  # 模拟加载时间
            self.whisper_model_loaded = True

            logger.info(f"Whisper模型加载完成: {model_name}")
            return True

        except Exception as e:
            logger.error(f"Whisper模型加载失败: {e}")
            return False

    async def load_video_analysis_model(self) -> bool:
        """
        加载视频分析模型

        Returns:
            是否加载成功
        """
        try:
            logger.info("开始加载视频分析模型")

            # TODO: 实际加载视频分析相关模型
            await asyncio.sleep(3.0)  # 模拟加载时间
            self.video_analysis_model_loaded = True

            logger.info("视频分析模型加载完成")
            return True

        except Exception as e:
            logger.error(f"视频分析模型加载失败: {e}")
            return False

    def get_model_status(self) -> Dict[str, bool]:
        """
        获取模型加载状态

        Returns:
            模型状态字典
        """
        return {
            "whisper_loaded": self.whisper_model_loaded,
            "video_analysis_loaded": self.video_analysis_model_loaded,
        }

    async def health_check(self) -> Dict[str, Any]:
        """
        AI服务健康检查

        Returns:
            健康状态信息
        """
        # 检查OpenAI客户端健康状态
        openai_health = await openai_client.health_check()
        
        return {
            "status": "healthy" if openai_health.get("status") == "healthy" else "unhealthy",
            "models": self.get_model_status(),
            "openai_status": openai_health,
            "timestamp": datetime.now().isoformat(),
        }

    # ================================
    # 任务1：生成面试官角色
    # ================================
    
    async def generate_interviewer_persona(
        self, request: InterviewerPersonaRequest
    ) -> Optional[InterviewerPersona]:
        """
        生成面试官角色
        
        Args:
            request: 面试官角色生成请求
            
        Returns:
            面试官角色信息
        """
        try:
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            logger.info(f"开始生成面试官角色: request_id={request_id}")
            
            # 格式化Prompt
            formatted_prompt = prompt_manager.format_prompt(
                "interviewer_persona_generation",
                job_position=request.job_position,
                key_focus_areas=", ".join(request.key_focus_areas),
                personality_style=request.personality_style,
                interviewer_name=request.interviewer_name
            )
            
            if not formatted_prompt:
                logger.error("面试官角色生成Prompt格式化失败")
                return None
            
            # 调用OpenAI API
            response = await openai_client.call_openai_api(
                formatted_prompt,
                temperature=0.7,
                max_tokens=1000
            )
            
            if not response:
                logger.error("OpenAI API调用失败")
                return None
            
            # 解析JSON响应
            parsed_response = await openai_client.parse_json_response(response)
            if not parsed_response:
                logger.error("面试官角色响应解析失败")
                return None
            
            # 创建面试官角色对象
            persona = InterviewerPersona(**parsed_response)
            
            processing_time = time.time() - start_time
            logger.info(f"面试官角色生成完成: request_id={request_id}, 耗时={processing_time:.2f}s")
            
            return persona
            
        except Exception as e:
            logger.error(f"生成面试官角色失败: {e}")
            return None

    # ================================
    # 任务2：生成岗位面试题库
    # ================================
    
    async def generate_question_bank(
        self, request: QuestionBankRequest
    ) -> Optional[QuestionBankResponse]:
        """
        生成岗位面试题库
        
        Args:
            request: 题库生成请求
            
        Returns:
            面试题库响应
        """
        try:
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            logger.info(f"开始生成面试题库: request_id={request_id}")
            
            # 格式化Prompt
            formatted_prompt = prompt_manager.format_prompt(
                "question_bank_generation",
                job_position=request.job_position,
                technical_field=request.technical_field,
                core_competency_indicators=", ".join(request.core_competency_indicators)
            )
            
            if not formatted_prompt:
                logger.error("面试题库生成Prompt格式化失败")
                return None
            
            # 调用OpenAI API
            response = await openai_client.call_openai_api(
                formatted_prompt,
                temperature=0.8,
                max_tokens=2000
            )
            
            if not response:
                logger.error("OpenAI API调用失败")
                return None
            
            # 解析JSON响应
            parsed_response = await openai_client.parse_json_response(response)
            if not parsed_response:
                logger.error("面试题库响应解析失败")
                return None
            
            # 创建题库响应对象
            questions = [InterviewQuestion(**q) for q in parsed_response]
            question_bank = QuestionBankResponse(
                questions=questions,
                total_count=len(questions)
            )
            
            processing_time = time.time() - start_time
            logger.info(f"面试题库生成完成: request_id={request_id}, 题目数量={len(questions)}, 耗时={processing_time:.2f}s")
            
            return question_bank
            
        except Exception as e:
            logger.error(f"生成面试题库失败: {e}")
            return None

    # ================================
    # 任务3：动态追问与交互
    # ================================
    
    async def generate_follow_up_questions(
        self, request: FollowUpRequest
    ) -> Optional[FollowUpResponse]:
        """
        生成动态追问问题
        
        Args:
            request: 追问请求
            
        Returns:
            追问响应
        """
        try:
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            logger.info(f"开始生成追问问题: request_id={request_id}")
            
            # 格式化Prompt
            formatted_prompt = prompt_manager.format_prompt(
                "dynamic_follow_up",
                original_question=request.original_question,
                candidate_answer=request.candidate_answer,
                target_competency=request.target_competency,
                interviewer_persona=request.interviewer_persona
            )
            
            if not formatted_prompt:
                logger.error("动态追问Prompt格式化失败")
                return None
            
            # 调用OpenAI API
            response = await openai_client.call_openai_api(
                formatted_prompt,
                temperature=0.8,
                max_tokens=800
            )
            
            if not response:
                logger.error("OpenAI API调用失败")
                return None
            
            # 解析JSON响应
            parsed_response = await openai_client.parse_json_response(response)
            if not parsed_response:
                logger.error("追问响应解析失败")
                return None
            
            # 确保响应是列表格式
            if isinstance(parsed_response, list):
                follow_up_questions = parsed_response
            else:
                # 如果不是列表，尝试提取单个问题
                follow_up_questions = [str(parsed_response)]
            
            # 创建追问响应对象
            follow_up_response = FollowUpResponse(
                follow_up_questions=follow_up_questions
            )
            
            processing_time = time.time() - start_time
            logger.info(f"追问问题生成完成: request_id={request_id}, 问题数量={len(follow_up_questions)}, 耗时={processing_time:.2f}s")
            
            return follow_up_response
            
        except Exception as e:
            logger.error(f"生成追问问题失败: {e}")
            return None

    # ================================
    # 任务4：单题回答的多模态表现综合评估
    # ================================
    
    async def evaluate_multimodal_performance(
        self, request: MultimodalEvaluationRequest
    ) -> Optional[MultimodalEvaluationResponse]:
        """
        多模态表现综合评估
        
        Args:
            request: 多模态评估请求
            
        Returns:
            多模态评估响应
        """
        try:
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            logger.info(f"开始多模态表现评估: request_id={request_id}")
            
            # 构建评估数据
            evaluation_data = {
                "question": request.question,
                "evaluation_indicators": request.evaluation_indicators,
                "data": {
                    "text_analysis": request.text_analysis.dict(),
                    "audio_analysis": request.audio_analysis.dict(),
                    "video_analysis": request.video_analysis.dict()
                }
            }
            
            # 格式化Prompt
            formatted_prompt = prompt_manager.format_prompt(
                "multimodal_evaluation",
                evaluation_data=json.dumps(evaluation_data, ensure_ascii=False, indent=2)
            )
            
            if not formatted_prompt:
                logger.error("多模态评估Prompt格式化失败")
                return None
            
            # 调用OpenAI API
            response = await openai_client.call_openai_api(
                formatted_prompt,
                temperature=0.3,  # 评估需要更稳定的输出
                max_tokens=1500
            )
            
            if not response:
                logger.error("OpenAI API调用失败")
                return None
            
            # 解析JSON响应
            parsed_response = await openai_client.parse_json_response(response)
            if not parsed_response:
                logger.error("多模态评估响应解析失败")
                return None
            
            # 创建多模态评估响应对象
            evaluation_response = MultimodalEvaluationResponse(**parsed_response)
            
            processing_time = time.time() - start_time
            logger.info(f"多模态表现评估完成: request_id={request_id}, 指标数量={len(evaluation_response.indicator_scores)}, 耗时={processing_time:.2f}s")
            
            return evaluation_response
            
        except Exception as e:
            logger.error(f"多模态表现评估失败: {e}")
            return None

    # ================================
    # 任务5：生成最终评测报告与个性化建议
    # ================================
    
    async def generate_interview_report(
        self, request: InterviewReportRequest
    ) -> Optional[InterviewReportResponse]:
        """
        生成最终面试报告
        
        Args:
            request: 面试报告请求
            
        Returns:
            面试报告响应
        """
        try:
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            logger.info(f"开始生成面试报告: request_id={request_id}")
            
            # 构建报告数据
            report_data = {
                "candidate_name": request.candidate_name,
                "job_position": request.job_position,
                "overall_scores": request.overall_scores,
                "key_moments": [moment.dict() for moment in request.key_moments]
            }
            
            # 格式化Prompt
            formatted_prompt = prompt_manager.format_prompt(
                "interview_report_generation",
                report_data=json.dumps(report_data, ensure_ascii=False, indent=2)
            )
            
            if not formatted_prompt:
                logger.error("面试报告生成Prompt格式化失败")
                return None
            
            # 调用OpenAI API
            response = await openai_client.call_openai_api(
                formatted_prompt,
                temperature=0.4,  # 报告需要相对稳定但有一定创造性
                max_tokens=3000
            )
            
            if not response:
                logger.error("OpenAI API调用失败")
                return None
            
            # 解析JSON响应
            parsed_response = await openai_client.parse_json_response(response)
            if not parsed_response:
                logger.error("面试报告响应解析失败")
                return None
            
            # 创建面试报告响应对象
            report_response = InterviewReportResponse(**parsed_response)
            
            processing_time = time.time() - start_time
            logger.info(f"面试报告生成完成: request_id={request_id}, 耗时={processing_time:.2f}s")
            
            return report_response
            
        except Exception as e:
            logger.error(f"生成面试报告失败: {e}")
            return None

    # ================================
    # 任务6：全局安全与防偏见卫士
    # ================================
    
    async def safety_compliance_check(
        self, content_to_check: str
    ) -> Optional[Dict[str, Any]]:
        """
        安全与合规性检查
        
        Args:
            content_to_check: 需要检查的内容
            
        Returns:
            安全检查结果
        """
        try:
            start_time = time.time()
            request_id = str(uuid.uuid4())
            
            logger.info(f"开始安全合规检查: request_id={request_id}")
            
            # 格式化Prompt
            formatted_prompt = prompt_manager.format_prompt(
                "safety_guardrail",
                content_to_check=content_to_check
            )
            
            if not formatted_prompt:
                logger.error("安全检查Prompt格式化失败")
                return None
            
            # 调用OpenAI API
            response = await openai_client.call_openai_api(
                formatted_prompt,
                temperature=0.1,  # 安全检查需要非常稳定的输出
                max_tokens=800
            )
            
            if not response:
                logger.error("OpenAI API调用失败")
                return None
            
            # 解析JSON响应
            parsed_response = await openai_client.parse_json_response(response)
            if not parsed_response:
                logger.error("安全检查响应解析失败")
                return None
            
            processing_time = time.time() - start_time
            logger.info(f"安全合规检查完成: request_id={request_id}, 合规状态={parsed_response.get('is_compliant')}, 耗时={processing_time:.2f}s")
            
            return parsed_response
            
        except Exception as e:
            logger.error(f"安全合规检查失败: {e}")
            return None
    
    # ================================
    # 通用工具方法
    # ================================
    
    async def batch_process_requests(
        self, requests: List[Dict[str, Any]], batch_id: str = None
    ) -> Dict[str, Any]:
        """
        批量处理请求
        
        Args:
            requests: 请求列表
            batch_id: 批次ID
            
        Returns:
            批量处理结果
        """
        try:
            if not batch_id:
                batch_id = str(uuid.uuid4())
            
            start_time = time.time()
            logger.info(f"开始批量处理: batch_id={batch_id}, 请求数量={len(requests)}")
            
            results = []
            success_count = 0
            failed_count = 0
            
            # 并发处理请求
            tasks = []
            for i, request in enumerate(requests):
                task = self._process_single_request(request, f"{batch_id}_{i}")
                tasks.append(task)
            
            # 等待所有任务完成
            task_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理结果
            for i, result in enumerate(task_results):
                if isinstance(result, Exception):
                    failed_count += 1
                    results.append({
                        "success": False,
                        "data": None,
                        "message": str(result),
                        "request_id": f"{batch_id}_{i}",
                        "processing_time": 0.0
                    })
                else:
                    success_count += 1
                    results.append(result)
            
            processing_time = time.time() - start_time
            logger.info(f"批量处理完成: batch_id={batch_id}, 成功={success_count}, 失败={failed_count}, 总耗时={processing_time:.2f}s")
            
            return {
                "batch_id": batch_id,
                "total_count": len(requests),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"批量处理失败: {e}")
            return {
                "batch_id": batch_id or "unknown",
                "total_count": len(requests),
                "success_count": 0,
                "failed_count": len(requests),
                "results": []
            }
    
    async def _process_single_request(
        self, request: Dict[str, Any], request_id: str
    ) -> Dict[str, Any]:
        """
        处理单个请求
        
        Args:
            request: 请求数据
            request_id: 请求ID
            
        Returns:
            处理结果
        """
        try:
            start_time = time.time()
            request_type = request.get("type")
            
            result = None
            
            if request_type == "interviewer_persona":
                req = InterviewerPersonaRequest(**request.get("data", {}))
                result = await self.generate_interviewer_persona(req)
            elif request_type == "question_bank":
                req = QuestionBankRequest(**request.get("data", {}))
                result = await self.generate_question_bank(req)
            elif request_type == "follow_up":
                req = FollowUpRequest(**request.get("data", {}))
                result = await self.generate_follow_up_questions(req)
            elif request_type == "multimodal_evaluation":
                req = MultimodalEvaluationRequest(**request.get("data", {}))
                result = await self.evaluate_multimodal_performance(req)
            elif request_type == "interview_report":
                req = InterviewReportRequest(**request.get("data", {}))
                result = await self.generate_interview_report(req)
            elif request_type == "safety_check":
                content = request.get("data", {}).get("content", "")
                result = await self.safety_compliance_check(content)
            else:
                raise ValueError(f"不支持的请求类型: {request_type}")
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "data": result.dict() if hasattr(result, 'dict') else result,
                "message": "处理成功",
                "request_id": request_id,
                "processing_time": processing_time
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"处理单个请求失败: request_id={request_id}, error={e}")
            
            return {
                "success": False,
                "data": None,
                "message": str(e),
                "request_id": request_id,
                "processing_time": processing_time
            }
