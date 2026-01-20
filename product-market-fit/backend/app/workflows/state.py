"""
LangGraph state definitions
"""
from typing import TypedDict, List, Dict, Any, Optional


class IdeaToICPState(TypedDict):
    """State for Idea → Research → ICP workflow"""
    idea_id: int
    idea_name: str
    idea_description: str
    target_market: str

    # Research phase
    research_findings: Optional[Dict[str, Any]]

    # ICP phase
    icp_profile: Optional[Dict[str, Any]]

    # Metadata
    current_step: str
    errors: List[str]


class ICPToPersonasState(TypedDict):
    """State for ICP → Persona Generation workflow"""
    icp_id: int
    icp_data: Dict[str, Any]

    # Persona generation
    num_personas: int
    personas_generated: List[Dict[str, Any]]

    # Metadata
    current_step: str
    errors: List[str]
