"""
Conversation API Endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services.conversation_service import get_conversation_service

router = APIRouter(prefix="/api/chat", tags=["conversation"])


# ===== REQUEST/RESPONSE MODELS =====

class StartSessionRequest(BaseModel):
    """Request body untuk start session"""
    user_id: int = Field(..., description="ID of the user")
    language: str = Field(default="id", description="Preferred language (id/en)")


class StartSessionResponse(BaseModel):
    """Response untuk start session"""
    session_id: int
    greeting: str
    phase: str = "bercerita"


class SendMessageRequest(BaseModel):
    """Request body untuk send message"""
    message: str = Field(..., min_length=1, max_length=2000, description="User message")


class SendMessageResponse(BaseModel):
    """Response untuk send message"""
    response: str
    phase: str
    session_complete: bool = False
    emotion_detected: Optional[Dict[str, Any]] = None
    questions_completed: Optional[int] = None
    escalation: bool = False
    error: Optional[str] = None


class SessionStatusResponse(BaseModel):
    """Response untuk session status"""
    session_id: int
    phase: str
    wellness_zone: Optional[str] = None
    questions_completed: int = 0
    is_complete: bool = False


# ===== ENDPOINTS =====

@router.post("/start", response_model=StartSessionResponse)
async def start_session(
    request: StartSessionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new chat session
    
    Creates a new session and returns a greeting message.
    """
    try:
        service = get_conversation_service()
        session, greeting = await service.start_session(
            db=db,
            user_id=request.user_id,
            language=request.language
        )
        
        return StartSessionResponse(
            session_id=session.id,
            greeting=greeting,
            phase="bercerita"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start session: {str(e)}"
        )


@router.post("/{session_id}/message", response_model=SendMessageResponse)
async def send_message(
    session_id: int,
    request: SendMessageRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to the chatbot
    
    Processes the user message and returns the bot's response.
    The response depends on the current conversation phase.
    """
    try:
        service = get_conversation_service()
        result = await service.process_message(
            db=db,
            session_id=session_id,
            user_message=request.message
        )
        
        if "error" in result and result.get("error"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["error"]
            )
        
        return SendMessageResponse(
            response=result.get("response", ""),
            phase=result.get("phase", "unknown"),
            session_complete=result.get("session_complete", False),
            emotion_detected=result.get("emotion_detected"),
            questions_completed=result.get("questions_completed"),
            escalation=result.get("escalation", False),
            error=result.get("error")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process message: {str(e)}"
        )


@router.get("/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current session status
    
    Returns the current phase, wellness zone, and progress.
    """
    try:
        from database.models.session import ChatSession
        
        session = await db.get(ChatSession, session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        questions_completed = 0
        if session.reflection_progress:
            questions_completed = len(session.reflection_progress.get("answers", []))
        
        return SessionStatusResponse(
            session_id=session.id,
            phase=session.current_phase.value,
            wellness_zone=session.wellness_zone.value if session.wellness_zone else None,
            questions_completed=questions_completed,
            is_complete=session.current_phase.value == "selesai"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get session status: {str(e)}"
        )


@router.post("/{session_id}/end")
async def end_session(
    session_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    End a chat session early
    
    Marks the session as complete and returns a closing message.
    """
    try:
        from database.models.session import ChatSession, PhaseEnum
        from datetime import datetime
        
        session = await db.get(ChatSession, session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        session.current_phase = PhaseEnum.SELESAI
        session.ended_at = datetime.utcnow()
        await db.commit()
        
        return {
            "session_id": session_id,
            "status": "ended",
            "message": "Session ended successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to end session: {str(e)}"
        )
