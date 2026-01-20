"""
Research & ICP API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.database import crud
from app.workflows.idea_to_icp import run_idea_to_icp_workflow

router = APIRouter()


def run_workflow_background(idea_id: int):
    """Run workflow in background"""
    try:
        run_idea_to_icp_workflow(idea_id)
    except Exception as e:
        print(f"Workflow failed: {e}")


@router.post("/research/start/{idea_id}")
def start_research(idea_id: int, background_tasks: BackgroundTasks):
    """Trigger research workflow"""
    idea = crud.get_idea(idea_id)

    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Run workflow in background
    background_tasks.add_task(run_workflow_background, idea_id)

    return {
        "message": "Research started",
        "idea_id": idea_id,
        "status": "running"
    }


@router.get("/research/{idea_id}")
def get_research(idea_id: int):
    """Get research results"""
    research = crud.get_research(idea_id)

    if not research:
        return {"message": "Research not yet completed", "status": "pending"}

    return research


@router.get("/icp/{idea_id}")
def get_icp(idea_id: int):
    """Get ICP profile"""
    icp = crud.get_icp(idea_id)

    if not icp:
        return {"message": "ICP not yet created", "status": "pending"}

    return icp
