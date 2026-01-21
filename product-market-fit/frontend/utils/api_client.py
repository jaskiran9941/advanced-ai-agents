"""
API Client for calling backend
"""
import requests
from typing import Dict, Any, Optional


class APIClient:
    """Client for calling FastAPI backend"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    # Ideas
    def create_idea(self, name: str, description: str, target_market: str) -> Dict:
        response = requests.post(
            f"{self.base_url}/api/ideas",
            json={
                "name": name,
                "description": description,
                "target_market": target_market
            }
        )
        response.raise_for_status()
        return response.json()

    def get_idea(self, idea_id: int) -> Dict:
        response = requests.get(f"{self.base_url}/api/ideas/{idea_id}")
        response.raise_for_status()
        return response.json()

    def list_ideas(self) -> Dict:
        response = requests.get(f"{self.base_url}/api/ideas")
        response.raise_for_status()
        return response.json()

    # Research & ICP
    def start_research(self, idea_id: int) -> Dict:
        response = requests.post(f"{self.base_url}/api/research/start/{idea_id}")
        response.raise_for_status()
        return response.json()

    def get_research(self, idea_id: int) -> Dict:
        response = requests.get(f"{self.base_url}/api/research/{idea_id}")
        response.raise_for_status()
        return response.json()

    def get_icp(self, idea_id: int) -> Dict:
        response = requests.get(f"{self.base_url}/api/icp/{idea_id}")
        response.raise_for_status()
        return response.json()

    def get_research_progress(self, idea_id: int) -> Dict:
        response = requests.get(f"{self.base_url}/api/research/progress/{idea_id}")
        response.raise_for_status()
        return response.json()

    # Personas
    def generate_personas(self, idea_id: int, num_personas: int = 3) -> Dict:
        response = requests.post(
            f"{self.base_url}/api/personas/generate/{idea_id}",
            json={"num_personas": num_personas}
        )
        response.raise_for_status()
        return response.json()

    def list_personas(self, idea_id: int) -> Dict:
        response = requests.get(f"{self.base_url}/api/personas/list/{idea_id}")
        response.raise_for_status()
        return response.json()

    def get_persona(self, persona_id: int) -> Dict:
        response = requests.get(f"{self.base_url}/api/personas/{persona_id}")
        response.raise_for_status()
        return response.json()

    # Chat
    def start_chat(self, persona_id: int) -> Dict:
        response = requests.post(f"{self.base_url}/api/chat/start/{persona_id}")
        response.raise_for_status()
        return response.json()

    def send_message(self, persona_id: int, message: str, session_id: str = None, images: list = None) -> Dict:
        """Send a message to a persona, optionally with images

        Args:
            persona_id: The persona to chat with
            message: The text message
            session_id: Optional session ID for conversation continuity
            images: Optional list of dicts with 'data' (base64) and 'media_type'
        """
        payload = {"message": message, "session_id": session_id}
        if images:
            payload["images"] = images

        response = requests.post(
            f"{self.base_url}/api/chat/message/{persona_id}",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    def get_chat_history(self, session_id: str) -> Dict:
        response = requests.get(f"{self.base_url}/api/chat/history/{session_id}")
        response.raise_for_status()
        return response.json()
