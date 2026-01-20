"""
Base Agent class with multi-LLM support and agentic capabilities
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
import anthropic
import openai
from app.config import settings


class BaseAgent(ABC):
    """Base class for all agents with multi-LLM support"""

    def __init__(self, name: str, provider: str = "anthropic", model: str = None):
        self.name = name
        self.provider = provider.lower()

        # Default models
        if model is None:
            if self.provider == "anthropic":
                model = settings.CLAUDE_MODEL
            else:  # openai
                model = settings.GPT4_MODEL

        self.model = model

        # Initialize clients
        if self.provider == "anthropic":
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )
            self.openai_client = None
        else:
            self.openai_client = openai.OpenAI(
                api_key=settings.OPENAI_API_KEY
            )
            self.anthropic_client = None

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main execution method - to be implemented by subclasses"""
        pass

    def _call_llm(
        self,
        messages: List[Dict],
        system: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> str:
        """Unified LLM calling interface"""
        if self.provider == "anthropic":
            return self._call_anthropic(messages, system, max_tokens, temperature)
        else:
            return self._call_openai(messages, system, max_tokens, temperature)

    def _call_anthropic(
        self,
        messages: List[Dict],
        system: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> str:
        """Call Anthropic Claude"""
        try:
            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }
            if system:
                kwargs["system"] = system

            response = self.anthropic_client.messages.create(**kwargs)
            return response.content[0].text
        except Exception as e:
            self._log(f"Anthropic API error: {e}")
            raise

    def _call_openai(
        self,
        messages: List[Dict],
        system: str = None,
        max_tokens: int = 4096,
        temperature: float = 1.0
    ) -> str:
        """Call OpenAI GPT"""
        try:
            # Add system message if provided
            if system:
                messages = [{"role": "system", "content": system}] + messages

            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            self._log(f"OpenAI API error: {e}")
            raise

    def _log(self, message: str):
        """Log messages"""
        print(f"[{self.name}] {message}")

    @abstractmethod
    def validate_output(self, output: Dict[str, Any]) -> Tuple[bool, float, List[str]]:
        """
        Validate agent output quality

        Args:
            output: The agent's output to validate

        Returns:
            Tuple of (is_valid, confidence_score, improvement_suggestions)
                - is_valid: Whether output meets minimum quality threshold
                - confidence_score: Quality score between 0.0 and 1.0
                - improvement_suggestions: List of specific improvements needed
        """
        pass

    @abstractmethod
    def get_min_confidence(self) -> float:
        """
        Get minimum acceptable confidence score for this agent

        Returns:
            Minimum confidence threshold (0.0 to 1.0)
        """
        pass

    def execute_with_retry(
        self,
        input_data: Dict[str, Any],
        max_iterations: int = None
    ) -> Dict[str, Any]:
        """
        Execute agent with iterative self-correction

        This implements the agentic pattern:
        1. Execute agent
        2. Validate output quality
        3. If quality insufficient, refine and retry
        4. Track reasoning trace for transparency

        Args:
            input_data: Input data for the agent
            max_iterations: Maximum retry attempts (defaults to config.MAX_RESEARCH_ITERATIONS)

        Returns:
            Best output produced, with _reasoning_trace and _final_confidence fields
        """
        if max_iterations is None:
            max_iterations = settings.MAX_RESEARCH_ITERATIONS

        best_output = None
        best_score = 0.0
        reasoning_trace = []

        for iteration in range(max_iterations):
            self._log(f"🔄 Iteration {iteration + 1}/{max_iterations}")

            try:
                # Execute agent
                output = self.execute(input_data)

                # Validate output quality
                is_valid, confidence, suggestions = self.validate_output(output)

                # Record reasoning trace
                trace_entry = {
                    "iteration": iteration + 1,
                    "confidence": confidence,
                    "is_valid": is_valid,
                    "suggestions": suggestions
                }
                reasoning_trace.append(trace_entry)

                self._log(
                    f"📊 Confidence: {confidence:.2f} | "
                    f"Valid: {is_valid} | "
                    f"Suggestions: {len(suggestions)}"
                )

                # Track best output
                if confidence > best_score:
                    best_score = confidence
                    best_output = output

                # Check if quality threshold met
                if is_valid and confidence >= self.get_min_confidence():
                    self._log(f"✅ Acceptable quality reached: {confidence:.2f}")
                    break

                # Prepare refinement for next iteration
                if iteration < max_iterations - 1:
                    input_data["refinement_feedback"] = suggestions
                    input_data["previous_attempt"] = output
                    self._log(f"🔧 Retrying with {len(suggestions)} refinements")

            except Exception as e:
                self._log(f"❌ Error in iteration {iteration + 1}: {str(e)}")
                trace_entry = {
                    "iteration": iteration + 1,
                    "error": str(e),
                    "confidence": 0.0,
                    "is_valid": False
                }
                reasoning_trace.append(trace_entry)

                # If this is the last iteration, raise the error
                if iteration == max_iterations - 1:
                    raise

        # Ensure we have output
        if best_output is None:
            raise RuntimeError(f"{self.name} failed to produce valid output after {max_iterations} iterations")

        # Attach reasoning metadata
        best_output["_reasoning_trace"] = reasoning_trace
        best_output["_final_confidence"] = best_score
        best_output["_iterations_used"] = len(reasoning_trace)

        if best_score < self.get_min_confidence():
            self._log(
                f"⚠️  Warning: Final confidence {best_score:.2f} below threshold "
                f"{self.get_min_confidence():.2f}"
            )

        return best_output
