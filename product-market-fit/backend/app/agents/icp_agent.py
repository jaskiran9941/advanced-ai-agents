"""
ICP Agent - defines Ideal Customer Profile using Claude Sonnet

AGENTIC FEATURES:
- Quality validation for specificity
- Iterative refinement based on feedback
- Confidence scoring
"""
import json
from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent


class ICPAgent(BaseAgent):
    """Agent for creating Ideal Customer Profiles"""

    def __init__(self):
        super().__init__(name="ICPAgent", provider="anthropic")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an Ideal Customer Profile from research

        Args:
            input_data: {
                "concept": str,
                "market": str,
                "research": Dict,  # Research findings
                "refinement_feedback": List[str],  # (Optional) Improvements from validation
                "previous_attempt": Dict  # (Optional) Previous ICP output
            }

        Returns:
            {
                "demographics": {
                    "age_range": str,
                    "gender": str,
                    "income": str,
                    "education": str,
                    "location": str
                },
                "psychographics": {
                    "values": List[str],
                    "interests": List[str],
                    "lifestyle": str
                },
                "behaviors": {
                    "buying_patterns": str,
                    "media_consumption": List[str],
                    "tech_savviness": str
                },
                "pain_points": List[str],
                "goals": List[str],
                "decision_criteria": List[str],
                "confidence_score": float
            }
        """
        concept = input_data.get("concept")
        market = input_data.get("market")
        research = input_data.get("research", {})
        refinement_feedback = input_data.get("refinement_feedback", [])
        previous_attempt = input_data.get("previous_attempt")

        self._log(f"Creating ICP for: {concept}")

        # Build system prompt with refinement context if retrying
        refinement_context = ""
        if refinement_feedback:
            refinement_context = "\n\nIMPORTANT - Previous ICP was too generic. Address these specific issues:\n" + "\n".join(f"- {feedback}" for feedback in refinement_feedback)

        system_prompt = f"""You are a customer research expert specializing in creating Ideal Customer Profiles (ICP).{refinement_context}

An ICP is a detailed description of the perfect customer for a product. It includes:
- Demographics (age, gender, income, education, location)
- Psychographics (values, interests, lifestyle)
- Behaviors (buying patterns, media consumption, tech-savviness)
- Pain points (problems they face)
- Goals (what they want to achieve)
- Decision criteria (what influences their purchase)

Create a highly specific, realistic ICP based on the provided information.

Format your response as JSON with this exact structure:
{{
  "demographics": {{
    "age_range": "...",
    "gender": "...",
    "income": "...",
    "education": "...",
    "location": "..."
  }},
  "psychographics": {{
    "values": ["value1", "value2"],
    "interests": ["interest1", "interest2"],
    "lifestyle": "..."
  }},
  "behaviors": {{
    "buying_patterns": "...",
    "media_consumption": ["platform1", "platform2"],
    "tech_savviness": "..."
  }},
  "pain_points": ["pain1", "pain2", "pain3"],
  "goals": ["goal1", "goal2", "goal3"],
  "decision_criteria": ["criterion1", "criterion2"],
  "confidence_score": 0.85
}}

The confidence_score should be between 0.0 and 1.0, representing how well-defined this ICP is based on available data."""

        research_summary = json.dumps(research, indent=2)

        user_message = f"""Create an Ideal Customer Profile for this product:

Product: {concept}
Target Market: {market}

Market Research:
{research_summary}

Generate a detailed ICP in JSON format."""

        messages = [{"role": "user", "content": user_message}]

        try:
            response = self._call_llm(messages, system=system_prompt, temperature=0.5)

            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            icp_data = json.loads(json_str)

            # Ensure confidence score exists
            if "confidence_score" not in icp_data:
                icp_data["confidence_score"] = 0.75

            self._log(f"ICP created with confidence: {icp_data['confidence_score']}")
            return icp_data

        except json.JSONDecodeError as e:
            self._log(f"Failed to parse JSON response: {e}")
            # Return minimal ICP
            return {
                "demographics": {},
                "psychographics": {},
                "behaviors": {},
                "pain_points": [],
                "goals": [],
                "decision_criteria": [],
                "confidence_score": 0.3
            }
        except Exception as e:
            self._log(f"ICP creation failed: {e}")
            raise

    def validate_output(self, output: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        """
        Validate ICP quality and specificity

        Checks:
        - Demographics specificity (concrete data, not vague ranges)
        - Pain points depth (specific, not generic)
        - Goals measurability (specific, not vague like "success")
        - Overall completeness

        Args:
            output: ICP output to validate

        Returns:
            (is_valid, confidence_score, improvement_suggestions)
        """
        suggestions = []
        score = output.get("confidence_score", 0.5)

        # Check demographics specificity
        demographics = output.get("demographics", {})

        age_range = demographics.get("age_range", "")
        if not age_range or "N/A" in str(age_range):
            suggestions.append("Specify concrete age range (e.g., 28-42, not 25-40)")
            score -= 0.15
        elif "varies" in str(age_range).lower() or len(str(age_range)) < 5:
            suggestions.append("Make age range more specific based on research data")
            score -= 0.1

        income = demographics.get("income", "")
        if not income or "varies" in str(income).lower() or "N/A" in str(income):
            suggestions.append("Provide specific income range with data (e.g., $75K-$120K annually)")
            score -= 0.15

        location = demographics.get("location", "")
        if not location or len(str(location)) < 10:
            suggestions.append("Be more specific about location (cities, regions, not just country)")
            score -= 0.1

        # Check pain points depth
        pain_points = output.get("pain_points", [])
        if len(pain_points) < 3:
            suggestions.append("Identify at least 5 specific pain points")
            score -= 0.2
        elif len(pain_points) < 5:
            suggestions.append("Add more pain points for comprehensive profile")
            score -= 0.1

        # Check for generic pain points
        generic_pain_words = ["time", "money", "efficiency", "difficulty", "challenges"]
        generic_count = sum(
            1 for pain in pain_points
            if any(word in str(pain).lower() for word in generic_pain_words)
            and len(str(pain)) < 50
        )
        if generic_count > len(pain_points) / 2:
            suggestions.append("Pain points too generic - make them specific and detailed")
            score -= 0.15

        # Check goals specificity
        goals = output.get("goals", [])
        if len(goals) < 3:
            suggestions.append("Define at least 3 specific goals")
            score -= 0.15

        # Check for generic goal statements
        generic_goal_words = ["success", "growth", "better", "improve", "increase"]
        generic_goal_count = sum(
            1 for goal in goals
            if any(word in str(goal).lower() for word in generic_goal_words)
            and len(str(goal)) < 40
        )
        if generic_goal_count > len(goals) / 2:
            suggestions.append("Goals are too vague - make them specific and measurable (e.g., 'lose 15 pounds in 3 months' not 'get healthier')")
            score -= 0.2

        # Check psychographics
        psychographics = output.get("psychographics", {})
        values = psychographics.get("values", [])
        if len(values) < 3:
            suggestions.append("Define more specific values (at least 4-5)")
            score -= 0.1

        interests = psychographics.get("interests", [])
        if len(interests) < 3:
            suggestions.append("Define more specific interests (at least 5)")
            score -= 0.1

        # Check behaviors
        behaviors = output.get("behaviors", {})
        media_consumption = behaviors.get("media_consumption", [])
        if len(media_consumption) < 2:
            suggestions.append("Specify media consumption channels (at least 3-4 platforms)")
            score -= 0.1

        # Check decision criteria
        decision_criteria = output.get("decision_criteria", [])
        if len(decision_criteria) < 2:
            suggestions.append("Define more decision criteria (at least 3)")
            score -= 0.1

        # Ensure score stays in valid range
        score = max(0.0, min(1.0, score))

        # Update confidence in output
        output["confidence_score"] = score

        is_valid = score >= self.get_min_confidence()

        return is_valid, score, suggestions

    def get_min_confidence(self) -> float:
        """Minimum acceptable confidence for ICP quality"""
        from app.config import settings
        return settings.MIN_ICP_CONFIDENCE  # 0.7
