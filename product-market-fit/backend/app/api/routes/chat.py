"""
Chat API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from app.database import crud
from app.agents.persona_chat_agent import PersonaChatAgent

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    session_id: str = None


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
def send_message(persona_id: int, chat_msg: ChatMessage):
    """Send a message to a persona"""
    persona = crud.get_persona(persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Get conversation history
    history = []
    if chat_msg.session_id:
        history = crud.get_conversation_history(chat_msg.session_id)
    else:
        # Create new session if not provided
        chat_msg.session_id = str(uuid.uuid4())

    # Chat with persona
    chat_agent = PersonaChatAgent()

    try:
        response = chat_agent.chat({
            "persona": persona,
            "message": chat_msg.message,
            "history": history
        })

        # Save conversation
        crud.save_conversation(
            persona_id=persona_id,
            session_id=chat_msg.session_id,
            user_message=chat_msg.message,
            persona_response=response["response"],
            sentiment=response["sentiment"]
        )

        return {
            "persona_name": persona["name"],
            "response": response["response"],
            "sentiment": response["sentiment"],
            "topics": response["topics"],
            "session_id": chat_msg.session_id
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
