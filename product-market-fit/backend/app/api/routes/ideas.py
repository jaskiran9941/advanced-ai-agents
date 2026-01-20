"""
Ideas API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.database import crud

router = APIRouter()


class IdeaCreate(BaseModel):
    name: str
    description: str
    target_market: str
    user_id: str = "default_user"


class IdeaResponse(BaseModel):
    id: int
    name: str
    description: str
    target_market: str
    status: str
    created_at: str


@router.post("/ideas")
def create_idea(idea: IdeaCreate):
    """Submit a new product idea"""
    try:
        idea_id = crud.create_idea(
            name=idea.name,
            description=idea.description,
            target_market=idea.target_market,
            user_id=idea.user_id
        )

        return {
            "id": idea_id,
            "name": idea.name,
            "description": idea.description,
            "target_market": idea.target_market,
            "status": "draft",
            "message": "Idea created successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ideas/{idea_id}")
def get_idea(idea_id: int):
    """Get idea details"""
    idea = crud.get_idea(idea_id)

    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    return idea


@router.get("/ideas")
def list_ideas(user_id: str = "default_user"):
    """List all ideas for a user"""
    try:
        ideas = crud.list_ideas(user_id)
        return {"ideas": ideas}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
