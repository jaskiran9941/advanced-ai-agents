"""
Research & ICP API endpoints
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.database import crud
from app.workflows.idea_to_icp import run_idea_to_icp_workflow

router = APIRouter()


def run_workflow_background(idea_id: int, workflow_id: int):
    """Run workflow in background with progress tracking"""
    try:
        run_idea_to_icp_workflow(idea_id, workflow_id)
        crud.complete_workflow(workflow_id, {"status": "completed"})
    except Exception as e:
        print(f"Workflow failed: {e}")
        crud.complete_workflow(workflow_id, {"status": "failed"}, str(e))


@router.post("/research/start/{idea_id}")
def start_research(idea_id: int, background_tasks: BackgroundTasks):
    """Trigger research workflow"""
    idea = crud.get_idea(idea_id)

    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    # Create workflow tracking record
    workflow_id = crud.start_workflow(idea_id, "idea_to_icp", {"idea_id": idea_id})

    # Update initial progress
    crud.update_workflow_progress(workflow_id, "starting", 0, "🚀 Starting research workflow...")

    # Run workflow in background with workflow_id for progress tracking
    background_tasks.add_task(run_workflow_background, idea_id, workflow_id)

    return {
        "message": "Research started",
        "idea_id": idea_id,
        "workflow_id": workflow_id,
        "status": "running"
    }


@router.get("/research/progress/{idea_id}")
def get_research_progress(idea_id: int):
    """Get research workflow progress for polling"""
    progress = crud.get_workflow_progress(idea_id, "idea_to_icp")

    if not progress:
        return {
            "status": "not_started",
            "progress_percent": 0,
            "step_message": "Research has not been started yet"
        }

    return {
        "status": progress.get("status", "unknown"),
        "current_step": progress.get("current_step", "unknown"),
        "progress_percent": progress.get("progress_percent", 0),
        "step_message": progress.get("step_message", ""),
        "error_message": progress.get("error_message")
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
