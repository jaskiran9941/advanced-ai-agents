"""
Persona Generator - creates synthetic personas from ICP

AGENTIC FEATURES:
- Diversity validation (personas should be distinct)
- Quality checks for depth and realism
- Iterative refinement for better variety
"""
import json
from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent


class PersonaGenerator(BaseAgent):
    """Agent for generating synthetic personas"""

    def __init__(self):
        super().__init__(name="PersonaGenerator", provider="anthropic")

    def execute(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate synthetic personas from ICP

        Args:
            input_data: {
                "icp": Dict,  # ICP profile
                "num_personas": int  # Number of personas to generate (default: 3)
            }

        Returns:
            List of persona dictionaries
        """
        icp = input_data.get("icp")
        num_personas = input_data.get("num_personas", 3)

        self._log(f"Generating {num_personas} personas from ICP")

        system_prompt = """You are a character designer specializing in creating realistic customer personas for product validation.

Create diverse, realistic personas that represent different archetypes within the ICP. Each persona should:
- Have a unique name, age, occupation, and location
- Have a compelling background story
- Have distinct personality traits
- Have a specific communication style
- Have knowledge and beliefs relevant to the product domain
- Have preferences and potential objections

Make personas feel like real people, not stereotypes. They should have depth, quirks, and specific details.

Format response as JSON array:
[
  {
    "name": "Full Name",
    "age": 35,
    "occupation": "...",
    "location": "City, State",
    "background_story": "Detailed story about their life, career, and relevant experiences...",
    "personality_traits": ["trait1", "trait2", "trait3"],
    "communication_style": "How they talk and communicate...",
    "knowledge_base": {
      "expertise": ["area1", "area2"],
      "beliefs": ["belief1", "belief2"],
      "awareness_level": "How much they know about this product category"
    },
    "preferences": {
      "likes": ["thing1", "thing2"],
      "dislikes": ["thing1", "thing2"],
      "priorities": ["priority1", "priority2"]
    },
    "objections": ["potential objection1", "potential objection2"]
  }
]"""

        icp_summary = json.dumps(icp, indent=2)

        user_message = f"""Generate {num_personas} diverse, realistic personas based on this ICP:

{icp_summary}

Create personas that represent different archetypes within this ICP. Make them feel like real people with unique personalities and stories.

Return JSON array of personas."""

        messages = [{"role": "user", "content": user_message}]

        try:
            response = self._call_llm(messages, system=system_prompt, temperature=0.9)

            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            personas = json.loads(json_str)

            if not isinstance(personas, list):
                personas = [personas]

            self._log(f"Generated {len(personas)} personas successfully")
            return personas

        except json.JSONDecodeError as e:
            self._log(f"Failed to parse JSON response: {e}")
            # Return minimal personas
            return self._generate_fallback_personas(num_personas, icp)
        except Exception as e:
            self._log(f"Persona generation failed: {e}")
            raise

    def _generate_fallback_personas(self, num: int, icp: Dict) -> List[Dict]:
        """Generate basic personas if JSON parsing fails"""
        personas = []
        names = ["Alex Chen", "Maria Rodriguez", "David Thompson", "Samantha Lee", "James Wilson"]

        for i in range(min(num, len(names))):
            personas.append({
                "name": names[i],
                "age": 30 + i * 5,
                "occupation": "Professional",
                "location": "United States",
                "background_story": f"A professional interested in {icp.get('demographics', {}).get('interests', ['various topics'])}",
                "personality_traits": ["curious", "analytical", "pragmatic"],
                "communication_style": "Direct and professional",
                "knowledge_base": {"expertise": [], "beliefs": [], "awareness_level": "moderate"},
                "preferences": {"likes": [], "dislikes": [], "priorities": []},
                "objections": []
            })

        return personas

    def validate_output(self, output: List[Dict[str, Any]]) -> Tuple[bool, float, List[str]]:
        """
        Validate persona diversity and quality

        Checks:
        - Number of personas generated
        - Diversity between personas (personality traits overlap)
        - Background story depth
        - Name uniqueness
        - Detail level

        Args:
            output: List of persona dictionaries

        Returns:
            (is_valid, confidence_score, improvement_suggestions)
        """
        suggestions = []
        score = 1.0

        if len(output) < 2:
            return False, 0.0, ["Need at least 2 personas"]

        # Check diversity of personality traits
        personality_sets = [
            set(p.get("personality_traits", []))
            for p in output
        ]

        # Calculate pairwise similarity
        similarities = []
        for i in range(len(personality_sets)):
            for j in range(i + 1, len(personality_sets)):
                overlap = len(personality_sets[i] & personality_sets[j])
                total = len(personality_sets[i] | personality_sets[j])
                similarity = overlap / total if total > 0 else 0
                similarities.append(similarity)

        if similarities:
            avg_similarity = sum(similarities) / len(similarities)

            if avg_similarity > 0.7:
                suggestions.append("Personas too similar - create more distinct personalities and traits")
                score -= 0.4
            elif avg_similarity > 0.6:
                suggestions.append("Increase personality diversity - personas should be more distinct")
                score -= 0.2

        # Check for generic names
        names = [p.get("name", "") for p in output]
        generic_names = {"Alex", "John", "Sarah", "Mike", "Emily", "Chris"}
        generic_name_count = sum(1 for name in names if any(gn in name for gn in generic_names))

        if generic_name_count > len(names) / 2:
            suggestions.append("Use more unique, memorable names (avoid common names like Alex, John, Sarah)")
            score -= 0.15

        # Check background story depth
        for i, persona in enumerate(output):
            story = persona.get("background_story", "")
            if len(story) < 100:
                suggestions.append(f"Persona {i+1} ('{persona.get('name', 'Unknown')}') needs a deeper, more detailed background story (at least 150 characters)")
                score -= 0.15

        # Check for unique occupations
        occupations = [p.get("occupation", "") for p in output]
        unique_occupations = len(set(occupations))
        if unique_occupations < len(output) * 0.8:  # At least 80% should be unique
            suggestions.append("Make occupations more diverse - personas should have different jobs")
            score -= 0.1

        # Check communication style depth
        for i, persona in enumerate(output):
            comm_style = persona.get("communication_style", "")
            if len(comm_style) < 30:
                suggestions.append(f"Persona {i+1} needs more detailed communication style description")
                score -= 0.1

        # Check objections
        for i, persona in enumerate(output):
            objections = persona.get("objections", [])
            if len(objections) < 2:
                suggestions.append(f"Persona {i+1} needs at least 2-3 potential objections")
                score -= 0.1

        # Check knowledge base
        for i, persona in enumerate(output):
            kb = persona.get("knowledge_base", {})
            if not kb.get("expertise") or not kb.get("beliefs"):
                suggestions.append(f"Persona {i+1} needs more detailed knowledge base (expertise and beliefs)")
                score -= 0.1

        # Ensure score stays in valid range
        score = max(0.0, min(1.0, score))

        is_valid = score >= self.get_min_confidence()

        return is_valid, score, suggestions

    def get_min_confidence(self) -> float:
        """Minimum acceptable confidence for persona quality"""
        return 0.7
