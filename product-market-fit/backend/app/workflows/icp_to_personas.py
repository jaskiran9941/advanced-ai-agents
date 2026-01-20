"""
LangGraph workflow: ICP → Personas
"""
from langgraph.graph import StateGraph, END
from app.agents.persona_generator import PersonaGenerator
from app.database import crud
from .state import ICPToPersonasState


def generate_personas(state: ICPToPersonasState) -> ICPToPersonasState:
    """Generate personas from ICP"""
    print(f"[Workflow] Generating {state['num_personas']} personas")

    generator = PersonaGenerator()

    try:
        personas = generator.execute({
            "icp": state["icp_data"],
            "num_personas": state["num_personas"]
        })

        state["personas_generated"] = personas
        state["current_step"] = "personas_complete"

        # Save personas to database
        for persona in personas:
            crud.save_persona(state["icp_id"], persona)

        return state

    except Exception as e:
        state["errors"].append(f"Persona generation failed: {str(e)}")
        state["current_step"] = "personas_failed"
        return state


def build_icp_to_personas_workflow():
    """Build the workflow graph"""
    workflow = StateGraph(ICPToPersonasState)

    # Add nodes
    workflow.add_node("generate_personas", generate_personas)

    # Define edges
    workflow.add_edge("generate_personas", END)

    # Set entry point
    workflow.set_entry_point("generate_personas")

    return workflow.compile()


def run_icp_to_personas_workflow(icp_id: int, num_personas: int = 3):
    """Run the complete workflow"""
    print(f"[Workflow] Starting ICP → Personas workflow for ICP {icp_id}")

    # Get ICP from database
    icp = crud.get_icp_by_id(icp_id)
    if not icp:
        raise ValueError(f"ICP {icp_id} not found")

    # Initialize state
    initial_state: ICPToPersonasState = {
        "icp_id": icp_id,
        "icp_data": icp,
        "num_personas": num_personas,
        "personas_generated": [],
        "current_step": "starting",
        "errors": []
    }

    # Build and run workflow
    workflow = build_icp_to_personas_workflow()

    try:
        final_state = workflow.invoke(initial_state)
        print(f"[Workflow] Completed with status: {final_state['current_step']}")
        return final_state

    except Exception as e:
        print(f"[Workflow] Failed: {e}")
        raise
