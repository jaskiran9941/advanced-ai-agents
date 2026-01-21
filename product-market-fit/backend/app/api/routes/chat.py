"""
Chat API endpoints
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import uuid
import base64
from app.database import crud
from app.agents.persona_chat_agent import PersonaChatAgent

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None


class ImageData(BaseModel):
    data: str  # base64 encoded
    media_type: str


class ChatMessageWithImages(BaseModel):
    message: str
    session_id: Optional[str] = None
    images: Optional[List[ImageData]] = None


@router.post("/chat/start/{persona_id}")
def start_conversation(persona_id: int):
    """Start a new conversation session"""
    persona = crud.get_persona(persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    session_id = str(uuid.uuid4())

    return {
        "session_id": session_id,
        "persona_name": persona["name"],
        "message": f"Conversation started with {persona['name']}"
    }


@router.post("/chat/message/{persona_id}")
def send_message(persona_id: int, chat_msg: ChatMessageWithImages):
    """Send a message to a persona, optionally with images"""
    persona = crud.get_persona(persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Get conversation history
    history = []
    session_id = chat_msg.session_id
    if session_id:
        history = crud.get_conversation_history(session_id)
    else:
        # Create new session if not provided
        session_id = str(uuid.uuid4())

    # Prepare images if provided
    images = None
    if chat_msg.images:
        images = [{"data": img.data, "media_type": img.media_type} for img in chat_msg.images]

    # Chat with persona
    chat_agent = PersonaChatAgent()

    try:
        response = chat_agent.chat({
            "persona": persona,
            "message": chat_msg.message,
            "history": history,
            "images": images
        })

        # Save conversation (note: we don't save images to DB for simplicity)
        crud.save_conversation(
            persona_id=persona_id,
            session_id=session_id,
            user_message=chat_msg.message + (" [with image(s)]" if images else ""),
            persona_response=response["response"],
            sentiment=response["sentiment"]
        )

        return {
            "persona_name": persona["name"],
            "response": response["response"],
            "sentiment": response["sentiment"],
            "topics": response["topics"],
            "session_id": session_id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/chat/history/{session_id}")
def get_chat_history(session_id: str):
    """Get conversation history"""
    try:
        history = crud.get_conversation_history(session_id)
        return {"history": history}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
