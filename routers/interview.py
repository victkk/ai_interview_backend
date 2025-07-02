from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import uuid
import logging
from datetime import datetime
from models.schemas import (
    InterviewSession,
    InterviewSessionCreate,
    InterviewResult,
    APIResponse,
    InterviewStatus,
)

logger = logging.getLogger(__name__)
router = APIRouter()

# 简单的内存存储，生产环境应该使用数据库
interview_sessions: Dict[str, InterviewSession] = {}
interview_results: Dict[str, InterviewResult] = {}


@router.post("/start", response_model=APIResponse)
async def start_interview_session(request: InterviewSessionCreate):
    """
    开始新的面试会话

    Args:
        request: 创建面试会话的请求

    Returns:
        包含会话ID的响应
    """
    try:
        # 生成会话ID
        session_id = str(uuid.uuid4())

        # 创建面试会话
        session = InterviewSession(
            session_id=session_id,
            user_id=request.user_id,
            status=InterviewStatus.WAITING,
            start_time=datetime.now(),
            metadata=request.metadata,
        )

        # 存储会话
        interview_sessions[session_id] = session

        logger.info(f"新的面试会话已创建: {session_id}")

        return APIResponse(
            success=True,
            message="面试会话创建成功",
            data={
                "session_id": session_id,
                "status": session.status,
                "start_time": session.start_time.isoformat(),
            },
        )

    except Exception as e:
        logger.error(f"创建面试会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建面试会话失败: {str(e)}")


@router.get("/session/{session_id}", response_model=APIResponse)
async def get_interview_session(session_id: str):
    """
    获取面试会话信息

    Args:
        session_id: 会话ID

    Returns:
        会话信息
    """
    try:
        if session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="面试会话不存在")

        session = interview_sessions[session_id]

        return APIResponse(
            success=True, message="获取会话信息成功", data=session.dict()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取面试会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取面试会话失败: {str(e)}")


@router.put("/session/{session_id}/status", response_model=APIResponse)
async def update_session_status(session_id: str, status: InterviewStatus):
    """
    更新面试会话状态

    Args:
        session_id: 会话ID
        status: 新的状态

    Returns:
        更新结果
    """
    try:
        if session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="面试会话不存在")

        session = interview_sessions[session_id]
        old_status = session.status
        session.status = status

        # 如果状态变为完成，设置结束时间
        if status == InterviewStatus.COMPLETED:
            session.end_time = datetime.now()

        logger.info(f"会话状态更新: {session_id} {old_status} -> {status}")

        return APIResponse(
            success=True,
            message="会话状态更新成功",
            data={
                "session_id": session_id,
                "old_status": old_status,
                "new_status": status,
                "end_time": session.end_time.isoformat() if session.end_time else None,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新会话状态失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新会话状态失败: {str(e)}")


@router.get("/sessions", response_model=APIResponse)
async def list_interview_sessions(skip: int = 0, limit: int = 100):
    """
    获取面试会话列表

    Args:
        skip: 跳过的记录数
        limit: 返回的最大记录数

    Returns:
        会话列表
    """
    try:
        sessions_list = list(interview_sessions.values())

        # 按开始时间排序
        sessions_list.sort(key=lambda x: x.start_time or datetime.min, reverse=True)

        # 分页
        paginated_sessions = sessions_list[skip : skip + limit]

        return APIResponse(
            success=True,
            message="获取会话列表成功",
            data={
                "sessions": [session.dict() for session in paginated_sessions],
                "total": len(sessions_list),
                "skip": skip,
                "limit": limit,
            },
        )

    except Exception as e:
        logger.error(f"获取会话列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")


@router.delete("/session/{session_id}", response_model=APIResponse)
async def delete_interview_session(session_id: str):
    """
    删除面试会话

    Args:
        session_id: 会话ID

    Returns:
        删除结果
    """
    try:
        if session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="面试会话不存在")

        # 删除会话
        del interview_sessions[session_id]

        # 同时删除相关结果
        if session_id in interview_results:
            del interview_results[session_id]

        logger.info(f"面试会话已删除: {session_id}")

        return APIResponse(
            success=True, message="面试会话删除成功", data={"session_id": session_id}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除面试会话失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除面试会话失败: {str(e)}")


@router.get("/results/{session_id}", response_model=APIResponse)
async def get_interview_results(session_id: str):
    """
    获取面试结果

    Args:
        session_id: 会话ID

    Returns:
        面试结果
    """
    try:
        if session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="面试会话不存在")

        if session_id not in interview_results:
            # 如果没有结果，创建一个基本结果
            session = interview_sessions[session_id]
            basic_result = InterviewResult(
                session_id=session_id,
                user_id=session.user_id,
                transcript=["暂无转录内容"],
                overall_score=None,
                feedback="面试进行中或暂无分析结果",
                duration=None,
            )
            interview_results[session_id] = basic_result

        result = interview_results[session_id]

        return APIResponse(success=True, message="获取面试结果成功", data=result.dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取面试结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取面试结果失败: {str(e)}")


@router.post("/results/{session_id}", response_model=APIResponse)
async def update_interview_results(session_id: str, result_data: Dict[str, Any]):
    """
    更新面试结果

    Args:
        session_id: 会话ID
        result_data: 结果数据

    Returns:
        更新结果
    """
    try:
        if session_id not in interview_sessions:
            raise HTTPException(status_code=404, detail="面试会话不存在")

        session = interview_sessions[session_id]

        # 如果结果不存在，创建新结果
        if session_id not in interview_results:
            interview_results[session_id] = InterviewResult(
                session_id=session_id, user_id=session.user_id
            )

        result = interview_results[session_id]

        # 更新结果字段
        for key, value in result_data.items():
            if hasattr(result, key):
                setattr(result, key, value)

        logger.info(f"面试结果已更新: {session_id}")

        return APIResponse(success=True, message="面试结果更新成功", data=result.dict())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新面试结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新面试结果失败: {str(e)}")


@router.get("/statistics", response_model=APIResponse)
async def get_interview_statistics():
    """
    获取面试统计信息

    Returns:
        统计信息
    """
    try:
        total_sessions = len(interview_sessions)
        status_counts = {}

        for session in interview_sessions.values():
            status = session.status
            status_counts[status] = status_counts.get(status, 0) + 1

        return APIResponse(
            success=True,
            message="获取统计信息成功",
            data={
                "total_sessions": total_sessions,
                "status_distribution": status_counts,
                "total_results": len(interview_results),
            },
        )

    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")
