"""
Persona Chat Agent - enables conversation with synthetic personas using GPT-4

AGENTIC FEATURES:
- Persona consistency validation
- Self-correction for out-of-character responses
- Quality checks for response depth
"""
import json
from typing import Dict, Any, List, Tuple
from .base_agent import BaseAgent


class PersonaChatAgent(BaseAgent):
    """Agent for chatting with personas"""

    def __init__(self):
        super().__init__(name="PersonaChatAgent", provider="openai")

    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute chat (called by execute_with_retry for validation)

        Args:
            input_data: {
                "persona": Dict,
                "message": str,
                "history": List[Dict],
                "refinement_feedback": List[str]  # (Optional) If retrying
            }

        Returns:
            {
                "response": str,
                "sentiment": str,
                "topics": List[str],
                "persona_profile": Dict  # Include for validation
            }
        """
        return self._generate_response(input_data)

    def chat(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Chat with a persona (with self-correction)

        Args:
            input_data: {
                "persona": Dict,  # Persona profile
                "message": str,   # User message
                "history": List[Dict],  # Conversation history (optional)
                "images": List[Dict]  # Optional images [{data: base64, media_type: str}]
            }

        Returns:
            {
                "response": str,
                "sentiment": str,
                "topics": List[str]
            }
        """
        # Use execute_with_retry for self-correction (max 2 iterations)
        result = self.execute_with_retry(input_data, max_iterations=2)

        # Remove validation fields before returning
        result.pop("persona_profile", None)

        return result

    def _generate_response(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal method to generate a single response"""
        persona = input_data.get("persona")
        user_message = input_data.get("message")
        history = input_data.get("history", [])
        images = input_data.get("images", [])
        refinement_feedback = input_data.get("refinement_feedback", [])

        self._log(f"Chatting as {persona.get('name')}")
        if images:
            self._log(f"📷 Processing {len(images)} image(s)")

        # Build system prompt from persona details
        refinement_context = ""
        if refinement_feedback:
            refinement_context = "\n\nIMPORTANT - Previous response was inconsistent. Adjust:\n" + "\n".join(f"- {feedback}" for feedback in refinement_feedback)

        # Add image context to system prompt if images present
        image_context = ""
        if images:
            image_context = "\n\nThe user has shared image(s) with you. Analyze them carefully and provide feedback based on your persona's perspective, expertise, and preferences. Be specific about what you see and give honest, constructive feedback."

        system_prompt = self._build_persona_system_prompt(persona) + refinement_context + image_context

        # Build conversation history
        messages = []
        for msg in history[-10:]:  # Last 10 messages for context
            messages.append({"role": "user", "content": msg.get("user_message", "")})
            messages.append({"role": "assistant", "content": msg.get("persona_response", "")})

        # Add current message
        messages.append({"role": "user", "content": user_message})

        try:
            response_text = self._call_llm(messages, system=system_prompt, temperature=0.8, images=images if images else None)

            # Analyze sentiment
            sentiment = self._analyze_sentiment(response_text)

            # Extract topics (simple keyword extraction)
            topics = self._extract_topics(user_message, response_text)

            return {
                "response": response_text,
                "sentiment": sentiment,
                "topics": topics,
                "persona_profile": persona  # Include for validation
            }

        except Exception as e:
            self._log(f"Chat failed: {e}")
            raise

    def _build_persona_system_prompt(self, persona: Dict) -> str:
        """Build system prompt from persona profile"""
        name = persona.get("name", "Alex")
        age = persona.get("age", 30)
        occupation = persona.get("occupation", "Professional")
        background = persona.get("background_story", "")
        traits = ", ".join(persona.get("personality_traits", []))
        comm_style = persona.get("communication_style", "friendly")

        knowledge = persona.get("knowledge_base", {})
        preferences = persona.get("preferences", {})
        objections = persona.get("objections", [])

        prompt = f"""You are roleplaying as {name}, a {age}-year-old {occupation}.

BACKGROUND:
{background}

PERSONALITY:
You are {traits}. Your communication style is {comm_style}.

KNOWLEDGE & BELIEFS:
"""

        if knowledge.get("expertise"):
            prompt += f"Expertise: {', '.join(knowledge['expertise'])}\n"
        if knowledge.get("beliefs"):
            prompt += f"Beliefs: {', '.join(knowledge['beliefs'])}\n"
        if knowledge.get("awareness_level"):
            prompt += f"Awareness Level: {knowledge['awareness_level']}\n"

        prompt += "\nPREFERENCES:\n"
        if preferences.get("likes"):
            prompt += f"Likes: {', '.join(preferences['likes'])}\n"
        if preferences.get("dislikes"):
            prompt += f"Dislikes: {', '.join(preferences['dislikes'])}\n"
        if preferences.get("priorities"):
            prompt += f"Priorities: {', '.join(preferences['priorities'])}\n"

        if objections:
            prompt += f"\nPOTENTIAL OBJECTIONS:\n{', '.join(objections)}\n"

        prompt += """
INSTRUCTIONS:
- Stay in character at all times
- Respond naturally based on your personality and background
- Express opinions and objections when relevant
- Ask questions when you're curious or skeptical
- Be realistic - you don't know everything
- Keep responses concise (2-4 sentences unless the conversation requires more)
- Show your personality through your language and tone
"""

        return prompt

    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        text_lower = text.lower()

        # Check for objections/negative sentiment
        negative_indicators = ["but", "however", "concern", "worried", "not sure", "don't think",
                              "problem", "issue", "skeptical", "doubt"]
        if any(indicator in text_lower for indicator in negative_indicators):
            return "objection"

        # Check for positive sentiment
        positive_indicators = ["great", "love", "excellent", "perfect", "interested",
                              "sounds good", "definitely", "excited"]
        if any(indicator in text_lower for indicator in positive_indicators):
            return "positive"

        # Check for questions (curiosity)
        if "?" in text:
            return "curious"

        return "neutral"

    def _extract_topics(self, user_msg: str, persona_msg: str) -> List[str]:
        """Extract key topics from conversation"""
        # Simple keyword extraction (can be enhanced with NLP)
        combined = f"{user_msg} {persona_msg}".lower()

        topic_keywords = {
            "pricing": ["price", "cost", "expensive", "cheap", "afford", "budget"],
            "features": ["feature", "functionality", "capability", "can it", "does it"],
            "quality": ["quality", "reliable", "dependable", "trustworthy"],
            "support": ["support", "help", "customer service", "assistance"],
            "competition": ["competitor", "alternative", "versus", "compared to"],
            "value": ["value", "worth", "benefit", "roi", "return"]
        }

        topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in combined for keyword in keywords):
                topics.append(topic)

        return topics if topics else ["general"]

    def validate_output(self, output: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        """
        Validate persona consistency in response

        Checks:
        - Personality trait alignment
        - Knowledge level consistency
        - Response length appropriateness
        - Tone consistency

        Args:
            output: Chat response output

        Returns:
            (is_valid, confidence_score, improvement_suggestions)
        """
        suggestions = []
        score = 1.0

        persona = output.get("persona_profile", {})
        response = output.get("response", "")
        response_lower = response.lower()

        # Check response length
        if len(response) < 20:
            suggestions.append("Response too brief - personas should provide meaningful responses")
            score -= 0.2

        # Check personality traits alignment (heuristic-based)
        traits = persona.get("personality_traits", [])

        # Analytical personas should provide detailed responses
        if "analytical" in [t.lower() for t in traits] and len(response) < 80:
            suggestions.append("Analytical personas should provide more detailed, thorough responses")
            score -= 0.2

        # Skeptical personas shouldn't be overly enthusiastic
        if "skeptical" in [t.lower() for t in traits]:
            enthusiastic_words = ["great", "love it", "amazing", "perfect", "definitely"]
            if sum(1 for word in enthusiastic_words if word in response_lower) > 2:
                suggestions.append("Response too enthusiastic for skeptical persona - add more critical thinking")
                score -= 0.3

        # Cautious personas shouldn't make hasty decisions
        if "cautious" in [t.lower() for t in traits]:
            hasty_words = ["definitely", "absolutely", "right away", "immediately"]
            if any(word in response_lower for word in hasty_words):
                suggestions.append("Cautious persona should be more hesitant and ask more questions")
                score -= 0.2

        # Check knowledge level consistency
        knowledge_level = persona.get("knowledge_base", {}).get("awareness_level", "")
        if "low" in knowledge_level.lower() or "beginner" in knowledge_level.lower():
            if len(response) > 250:
                suggestions.append("Response too detailed for persona's low knowledge level")
                score -= 0.15

        # Check for technical jargon with low knowledge
        if "low" in knowledge_level.lower():
            technical_words = ["algorithm", "optimization", "leverage", "synergy", "paradigm"]
            if any(word in response_lower for word in technical_words):
                suggestions.append("Persona with low knowledge shouldn't use technical jargon")
                score -= 0.2

        # Ensure score stays in valid range
        score = max(0.0, min(1.0, score))

        is_valid = score >= self.get_min_confidence()

        return is_valid, score, suggestions

    def get_min_confidence(self) -> float:
        """Minimum acceptable confidence for persona consistency"""
        return 0.75
