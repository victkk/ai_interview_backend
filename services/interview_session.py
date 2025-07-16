from fastapi import WebSocket
import asyncio
import uuid
from collections import deque
from typing import Deque, Optional, Dict, Any
from utils.util import base64_to_image

from services.audio_processor import AudioProcessor
from services.ai_service import AIService
from models.schemas import (
    FollowUpRequest,
    MultimodalEvaluationRequest,
    TextAnalysis,
    AudioAnalysis,
    VideoAnalysis,
    InterviewReportRequest,
    KeyMoment,
)


class InterviewSession:
    def __init__(self, session_id: str, loop: asyncio.AbstractEventLoop):
        self.session_id: str = session_id
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
        
        # 4. AI服务实例
        self.ai_service: AIService = AIService()
        
        # 5. 面试数据存储
        self.interview_data: Dict[str, Any] = {
            "questions": [],  # 已问的问题
            "answers": [],    # 候选人回答
            "evaluations": [],  # 评估结果
            "current_question": None,  # 当前问题
            "interviewer_persona": None,  # 面试官角色
        }

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
        3. 调用AI服务进行多模态分析
        4. 处理结果并存储
        """
        while self.is_active:
            try:
                # 获取音频转写结果
                sentence = await self.audio_results_queue.get()
                print(f"[{self.session_id}] 获取到音频转写的句子: {sentence}")
                self.audio_results_queue.task_done()
                
                # 获取对应的视频帧
                if self.video_buffer:
                    timestamp, base64_img = self.video_buffer.pop()
                    img = base64_to_image(base64_img)
                    
                    # 存储候选人回答
                    answer_data = {
                        "text": sentence,
                        "timestamp": timestamp,
                        "image": base64_img
                    }
                    self.interview_data["answers"].append(answer_data)
                    
                    # 如果有当前问题，进行多模态评估
                    if self.interview_data["current_question"]:
                        await self._evaluate_answer(sentence, base64_img)
                    
                    # 检查是否需要生成追问
                    if len(self.interview_data["answers"]) > 0:
                        await self._generate_follow_up_if_needed(sentence)

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"[{self.session_id}] 整合器处理错误: {e}")
                
        print(f"[{self.session_id}] Integrator logic stopped.")
    
    async def _evaluate_answer(self, answer_text: str, image_base64: str):
        """
        评估候选人回答
        
        Args:
            answer_text: 回答文本
            image_base64: 视频帧base64
        """
        try:
            current_question = self.interview_data["current_question"]
            if not current_question:
                return
            
            # 构建多模态评估请求
            evaluation_request = MultimodalEvaluationRequest(
                question=current_question,
                evaluation_indicators=["专业知识水平", "语言表达能力", "逻辑思维能力"],
                text_analysis=TextAnalysis(
                    transcript=answer_text,
                    keywords_coverage=0.8,  # 这里应该是实际的关键词覆盖率分析
                    answer_structure="结构化回答"  # 这里应该是实际的结构分析
                ),
                audio_analysis=AudioAnalysis(
                    avg_speech_rate="150字/分钟",
                    sentiment_tone="自信",
                    pauses_and_fillers="少量停顿"
                ),
                video_analysis=VideoAnalysis(
                    eye_contact_level="良好",
                    micro_expressions=["自信", "思考"],
                    body_language="坐姿端正"
                )
            )
            
            # 调用AI服务进行评估
            evaluation_result = await self.ai_service.evaluate_multimodal_performance(evaluation_request)
            
            if evaluation_result:
                self.interview_data["evaluations"].append({
                    "question": current_question,
                    "answer": answer_text,
                    "evaluation": evaluation_result.dict(),
                    "timestamp": timestamp if 'timestamp' in locals() else None
                })
                print(f"[{self.session_id}] 完成回答评估")
            
        except Exception as e:
            print(f"[{self.session_id}] 评估回答失败: {e}")
    
    async def _generate_follow_up_if_needed(self, answer_text: str):
        """
        根据回答生成追问问题
        
        Args:
            answer_text: 候选人回答
        """
        try:
            current_question = self.interview_data["current_question"]
            if not current_question:
                return
            
            # 简单的追问逻辑：如果回答较短或包含某些关键词，生成追问
            if len(answer_text) < 50 or "简单" in answer_text or "基本" in answer_text:
                follow_up_request = FollowUpRequest(
                    original_question=current_question,
                    candidate_answer=answer_text,
                    target_competency="逻辑思维能力",
                    interviewer_persona=self.interview_data.get("interviewer_persona", "专业严谨")
                )
                
                # 调用AI服务生成追问
                follow_up_result = await self.ai_service.generate_follow_up_questions(follow_up_request)
                
                if follow_up_result and follow_up_result.follow_up_questions:
                    # 选择第一个追问问题
                    next_question = follow_up_result.follow_up_questions[0]
                    self.interview_data["current_question"] = next_question
                    self.interview_data["questions"].append(next_question)
                    
                    # 通过WebSocket发送追问问题给前端
                    await self._send_question_to_frontend(next_question)
                    
                    print(f"[{self.session_id}] 生成追问问题: {next_question}")
                
        except Exception as e:
            print(f"[{self.session_id}] 生成追问失败: {e}")
    
    async def _send_question_to_frontend(self, question: str):
        """
        发送问题到前端
        
        Args:
            question: 问题内容
        """
        try:
            if self.video_websocket:
                await self.video_websocket.send_text(f"QUESTION:{question}")
            elif self.audio_websocket:
                await self.audio_websocket.send_text(f"QUESTION:{question}")
        except Exception as e:
            print(f"[{self.session_id}] 发送问题到前端失败: {e}")
    
    async def set_current_question(self, question: str):
        """
        设置当前问题
        
        Args:
            question: 问题内容
        """
        self.interview_data["current_question"] = question
        self.interview_data["questions"].append(question)
        print(f"[{self.session_id}] 设置当前问题: {question}")
    
    async def set_interviewer_persona(self, persona: str):
        """
        设置面试官角色
        
        Args:
            persona: 面试官角色描述
        """
        self.interview_data["interviewer_persona"] = persona
        print(f"[{self.session_id}] 设置面试官角色: {persona}")
    
    async def generate_final_report(self, candidate_name: str, job_position: str):
        """
        生成最终面试报告
        
        Args:
            candidate_name: 候选人姓名
            job_position: 面试岗位
            
        Returns:
            面试报告
        """
        try:
            if not self.interview_data["evaluations"]:
                print(f"[{self.session_id}] 没有评估数据，无法生成报告")
                return None
            
            # 计算综合评分
            overall_scores = {}
            for evaluation in self.interview_data["evaluations"]:
                eval_data = evaluation["evaluation"]
                for indicator_score in eval_data["indicator_scores"]:
                    indicator = indicator_score["indicator"]
                    score = indicator_score["score"]
                    
                    if indicator not in overall_scores:
                        overall_scores[indicator] = []
                    overall_scores[indicator].append(score)
            
            # 计算平均分
            for indicator in overall_scores:
                overall_scores[indicator] = sum(overall_scores[indicator]) / len(overall_scores[indicator])
            
            # 构建关键时刻
            key_moments = []
            for i, evaluation in enumerate(self.interview_data["evaluations"]):
                key_moments.append(KeyMoment(
                    question=evaluation["question"],
                    observation=f"第{i+1}个问题的回答表现"
                ))
            
            # 生成报告请求
            report_request = InterviewReportRequest(
                candidate_name=candidate_name,
                job_position=job_position,
                overall_scores=overall_scores,
                key_moments=key_moments
            )
            
            # 调用AI服务生成报告
            report_result = await self.ai_service.generate_interview_report(report_request)
            
            if report_result:
                print(f"[{self.session_id}] 生成最终报告成功")
                return report_result
            else:
                print(f"[{self.session_id}] 生成最终报告失败")
                return None
                
        except Exception as e:
            print(f"[{self.session_id}] 生成最终报告错误: {e}")
            return None
    
    def get_interview_summary(self) -> Dict[str, Any]:
        """
        获取面试摘要信息
        
        Returns:
            面试摘要
        """
        return {
            "session_id": self.session_id,
            "questions_count": len(self.interview_data["questions"]),
            "answers_count": len(self.interview_data["answers"]),
            "evaluations_count": len(self.interview_data["evaluations"]),
            "current_question": self.interview_data["current_question"],
            "interviewer_persona": self.interview_data["interviewer_persona"]
        }

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
