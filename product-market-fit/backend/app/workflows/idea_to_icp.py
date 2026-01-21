"""
LangGraph workflow: Idea → Research → ICP

AGENTIC ENHANCEMENTS:
- Iterative research with quality validation
- ICP creation with retry logic
- Conditional routing based on quality gates
- Observable reasoning traces
"""
from langgraph.graph import StateGraph, END
from app.agents.research_agent import ResearchAgent
from app.agents.icp_agent import ICPAgent
from app.database import crud
from .state import IdeaToICPState


def execute_research_with_retry(state: IdeaToICPState) -> IdeaToICPState:
    """
    Execute market research with iterative improvement

    Uses ResearchAgent.execute_with_retry() for:
    - Quality validation
    - Iterative refinement
    - Real web search via Tavily
    """
    print(f"[Workflow] 🔍 Executing agentic research for: {state['idea_name']}")

    # Get workflow_id from database based on idea_id
    idea_id = state["idea_id"]
    workflow = crud.get_workflow_progress(idea_id, "idea_to_icp")
    workflow_id = workflow.get("id") if workflow else None

    # Update progress: Research starting
    if workflow_id:
        crud.update_workflow_progress(workflow_id, "researching", 15, "🔍 Searching the web for market data...")

    research_agent = ResearchAgent()

    try:
        # Update progress: Analyzing
        if workflow_id:
            crud.update_workflow_progress(workflow_id, "researching", 30, "📊 Analyzing competitors and market trends...")

        # Use agentic execution with retry and validation
        research = research_agent.execute_with_retry({
            "concept": state["idea_description"],
            "market": state["target_market"]
        })

        state["research_findings"] = research
        state["current_step"] = "research_complete"

        # Log reasoning trace
        if "_reasoning_trace" in research:
            print(f"[Workflow] Research completed in {research['_iterations_used']} iterations")
            print(f"[Workflow] Final confidence: {research['_final_confidence']:.2f}")

        # Update progress: Research done
        if workflow_id:
            crud.update_workflow_progress(workflow_id, "research_complete", 50, "✅ Market research complete!")

        # Save to database
        crud.save_research(state["idea_id"], research)

        return state

    except Exception as e:
        state["errors"].append(f"Research failed: {str(e)}")
        state["current_step"] = "research_failed"
        if workflow_id:
            crud.update_workflow_progress(workflow_id, "research_failed", 30, f"❌ Research failed: {str(e)}")
        return state


def create_icp_with_validation(state: IdeaToICPState) -> IdeaToICPState:
    """
    Create ICP with quality validation and retry

    Uses ICPAgent.execute_with_retry() for:
    - Specificity validation
    - Quality gates (MIN_ICP_CONFIDENCE threshold)
    - Iterative refinement
    """
    print(f"[Workflow] 🎯 Creating ICP with quality validation")

    # Get workflow_id from database based on idea_id
    idea_id = state["idea_id"]
    workflow = crud.get_workflow_progress(idea_id, "idea_to_icp")
    workflow_id = workflow.get("id") if workflow else None

    # Update progress: ICP starting
    if workflow_id:
        crud.update_workflow_progress(workflow_id, "creating_icp", 60, "🎯 Creating Ideal Customer Profile...")

    icp_agent = ICPAgent()

    try:
        # Update progress
        if workflow_id:
            crud.update_workflow_progress(workflow_id, "creating_icp", 75, "👤 Defining customer demographics and behaviors...")

        # Use agentic execution with retry and validation
        icp = icp_agent.execute_with_retry({
            "concept": state["idea_description"],
            "market": state["target_market"],
            "research": state["research_findings"]
        })

        state["icp_profile"] = icp

        # Check quality gate
        final_confidence = icp.get("_final_confidence", 0)
        min_confidence = icp_agent.get_min_confidence()

        if final_confidence >= min_confidence:
            state["current_step"] = "icp_complete"
            print(f"[Workflow] ✅ ICP quality gate passed: {final_confidence:.2f} >= {min_confidence:.2f}")

            # Save to database
            crud.save_icp(state["idea_id"], icp)
            crud.update_idea_status(state["idea_id"], "icp_complete")

            if workflow_id:
                crud.update_workflow_progress(workflow_id, "icp_complete", 95, "✅ ICP created successfully!")
        else:
            state["current_step"] = "icp_low_quality"
            print(f"[Workflow] ⚠️  ICP quality gate failed: {final_confidence:.2f} < {min_confidence:.2f}")
            state["errors"].append(
                f"ICP confidence ({final_confidence:.2f}) below threshold ({min_confidence:.2f})"
            )

            # Still save the best attempt
            crud.save_icp(state["idea_id"], icp)
            crud.update_idea_status(state["idea_id"], "icp_low_quality")

            if workflow_id:
                crud.update_workflow_progress(workflow_id, "icp_complete", 95, "⚠️ ICP created (low confidence)")

        # Log reasoning trace
        if "_reasoning_trace" in icp:
            print(f"[Workflow] ICP completed in {icp['_iterations_used']} iterations")

        return state

    except Exception as e:
        state["errors"].append(f"ICP creation failed: {str(e)}")
        state["current_step"] = "icp_failed"
        if workflow_id:
            crud.update_workflow_progress(workflow_id, "icp_failed", 60, f"❌ ICP creation failed: {str(e)}")
        return state


def should_accept_icp(state: IdeaToICPState) -> str:
    """
    Conditional routing based on ICP quality

    Routes to:
    - END: If ICP quality acceptable or failed (end workflow)
    - In future: Could route to human_review or retry nodes
    """
    current_step = state["current_step"]

    if current_step == "icp_complete":
        print("[Workflow] ✅ ICP accepted - ending workflow")
        return "END"
    elif current_step == "icp_low_quality":
        print("[Workflow] ⚠️  ICP quality low but proceeding - ending workflow")
        # Future: Could route to "human_review" node
        return "END"
    else:
        # icp_failed or other errors
        print(f"[Workflow] ❌ ICP creation failed - ending workflow")
        return "END"


def build_idea_to_icp_workflow():
    """
    Build the enhanced workflow graph with quality gates

    Flow:
    1. execute_research_with_retry (iterative with Tavily)
    2. create_icp_with_validation (quality gates)
    3. Conditional routing based on quality
    """
    workflow = StateGraph(IdeaToICPState)

    # Add nodes with agentic capabilities
    workflow.add_node("execute_research", execute_research_with_retry)
    workflow.add_node("create_icp", create_icp_with_validation)

    # Define edges
    workflow.add_edge("execute_research", "create_icp")

    # Conditional edge based on quality gate
    workflow.add_conditional_edges(
        "create_icp",
        should_accept_icp,
        {
            "END": END
        }
    )

    # Set entry point
    workflow.set_entry_point("execute_research")

    return workflow.compile()


def run_idea_to_icp_workflow(idea_id: int, workflow_id: int = None):
    """Run the complete workflow with progress tracking"""
    print(f"[Workflow] Starting Idea → ICP workflow for idea {idea_id}")

    # Get idea from database
    idea = crud.get_idea(idea_id)
    if not idea:
        raise ValueError(f"Idea {idea_id} not found")

    # Update progress: Starting
    if workflow_id:
        crud.update_workflow_progress(workflow_id, "starting", 10, "🚀 Initializing research workflow...")

    # Initialize state
    initial_state: IdeaToICPState = {
        "idea_id": idea_id,
        "idea_name": idea["name"],
        "idea_description": idea["description"],
        "target_market": idea["target_market"],
        "research_findings": None,
        "icp_profile": None,
        "current_step": "starting",
        "errors": [],
        "_workflow_id": workflow_id
    }

    # Build and run workflow
    workflow = build_idea_to_icp_workflow()

    try:
        final_state = workflow.invoke(initial_state)
        print(f"[Workflow] Completed with status: {final_state['current_step']}")

        # Update progress: Complete
        if workflow_id:
            crud.update_workflow_progress(workflow_id, "completed", 100, "✅ Research and ICP creation complete!")

        return final_state

    except Exception as e:
        print(f"[Workflow] Failed: {e}")
        if workflow_id:
            crud.update_workflow_progress(workflow_id, "failed", 0, f"❌ Error: {str(e)}")
        raise
