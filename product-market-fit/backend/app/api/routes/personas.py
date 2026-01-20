"""
Personas API endpoints
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import crud
from app.workflows.icp_to_personas import run_icp_to_personas_workflow

router = APIRouter()


class PersonaGenerateRequest(BaseModel):
    num_personas: int = 3


@router.post("/personas/generate/{idea_id}")
def generate_personas(idea_id: int, request: PersonaGenerateRequest):
    """Generate personas from ICP"""
    # Get ICP for this idea
    icp = crud.get_icp(idea_id)

    if not icp:
        raise HTTPException(status_code=404, detail="ICP not found. Run research first.")

    try:
        # Run workflow
        result = run_icp_to_personas_workflow(icp["id"], request.num_personas)

        return {
            "message": "Personas generated successfully",
            "icp_id": icp["id"],
            "num_personas": len(result["personas_generated"]),
            "status": result["current_step"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/personas/list/{idea_id}")
def list_personas(idea_id: int):
    """List all personas for an idea"""
    # Get ICP for this idea
    icp = crud.get_icp(idea_id)

    if not icp:
        return {"personas": [], "message": "No ICP found"}

    personas = crud.list_personas(icp["id"])

    return {"personas": personas}


@router.get("/personas/{persona_id}")
def get_persona(persona_id: int):
    """Get persona details"""
    persona = crud.get_persona(persona_id)

    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    return persona
