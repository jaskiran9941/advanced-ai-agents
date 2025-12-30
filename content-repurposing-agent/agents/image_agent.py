"""
Image Generator Agent

✅ REAL MULTI-AGENT VALUE
Why: LLMs cannot generate images. This agent interfaces with DALL-E or
Stable Diffusion APIs to create visual content for social media posts.
"""
from typing import Dict, Any, Optional
from agents.base_agent import BaseAgent
from tools.image_tools import generate_image_dalle, generate_image_replicate, optimize_image_prompt
from pathlib import Path
from datetime import datetime

class ImageGeneratorAgent(BaseAgent):
    """
    Agent specialized in generating images for social media content.

    Responsibilities:
    - Create optimized image prompts for different platforms
    - Generate images using DALL-E or Stable Diffusion
    - Optimize images for platform-specific requirements
    - Save and manage generated images
    """

    def __init__(self, llm_provider: str = "claude", image_provider: str = "openai"):
        """
        Initialize Image Generator Agent.

        Args:
            llm_provider: LLM provider for prompt optimization
            image_provider: Image generation provider ("openai" or "replicate")
        """
        self.image_provider = image_provider

        super().__init__(
            name="Image_Generator",
            role="Visual content creation specialist",
            llm_provider=llm_provider,
            tools=[optimize_image_prompt]
        )

    def _default_instructions(self) -> str:
        return """You are a visual content creation specialist.

Your job is to:
1. Understand the content topic and target platform
2. Create effective image generation prompts
3. Generate platform-appropriate images
4. Ensure images match the content's tone and message

When creating image prompts:
- Be specific about style, mood, and composition
- Consider platform-specific requirements:
  * Instagram: Vibrant, eye-catching, 1:1 or 4:5 ratio
  * Twitter: Clean, impactful, works at small sizes
  * LinkedIn: Professional, business-appropriate
  * Substack: Editorial quality, wide format
- Avoid requesting text in images (hard for AI to generate)
- Focus on visual metaphors and concepts

Output clear, actionable prompts that will generate high-quality images.
"""

    def generate_for_topic(
        self,
        topic: str,
        platform: str,
        style_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an image for a specific topic and platform.

        Args:
            topic: Content topic
            platform: Target platform (instagram, twitter, linkedin, substack)
            style_notes: Optional additional style guidance

        Returns:
            Dictionary with image URL and metadata
        """
        # Create optimized prompt using LLM
        task = f"""Create an image generation prompt for this content:

Topic: {topic}
Platform: {platform}
{f'Style notes: {style_notes}' if style_notes else ''}

Generate a detailed, effective prompt that will create a high-quality,
platform-appropriate image. Focus on visual elements, style, mood, and composition.

Return ONLY the image prompt, nothing else."""

        response = self.run(task)
        image_prompt = response.content if hasattr(response, 'content') else str(response)

        # Clean up the prompt (remove any extra formatting)
        image_prompt = image_prompt.strip().strip('"').strip("'")

        self.logger.info(f"Generated image prompt: {image_prompt[:100]}...")

        # Generate the actual image
        save_filename = self._generate_filename(topic, platform)

        if self.image_provider == "openai":
            result = generate_image_dalle(
                prompt=image_prompt,
                save_path=save_filename
            )
        elif self.image_provider == "replicate":
            result = generate_image_replicate(
                prompt=image_prompt,
                save_path=save_filename
            )
        else:
            raise ValueError(f"Unsupported image provider: {self.image_provider}")

        result["platform"] = platform
        result["topic"] = topic
        result["optimized_prompt"] = image_prompt

        return result

    def generate_multiple(
        self,
        topic: str,
        platforms: list,
        style_notes: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate images for multiple platforms.

        Args:
            topic: Content topic
            platforms: List of platforms
            style_notes: Optional style guidance

        Returns:
            Dictionary mapping platforms to image results
        """
        results = {}

        for platform in platforms:
            try:
                self.logger.info(f"Generating image for {platform}...")
                result = self.generate_for_topic(topic, platform, style_notes)
                results[platform] = result
            except Exception as e:
                self.logger.error(f"Failed to generate image for {platform}: {str(e)}")
                results[platform] = {"error": str(e)}

        return results

    def _generate_filename(self, topic: str, platform: str) -> str:
        """
        Generate a filename for saving the image.

        Args:
            topic: Content topic
            platform: Target platform

        Returns:
            Full path to save the image
        """
        # Clean topic for filename
        clean_topic = "".join(c if c.isalnum() or c in (' ', '_') else '' for c in topic)
        clean_topic = clean_topic.replace(' ', '_')[:50]  # Limit length

        # Add timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create filename
        filename = f"{clean_topic}_{platform}_{timestamp}.png"

        # Full path in data directory
        from config.settings import settings
        images_dir = settings.data_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        return str(images_dir / filename)

    def create_prompt_only(self, topic: str, platform: str) -> str:
        """
        Create an optimized image prompt without generating the image.

        Args:
            topic: Content topic
            platform: Target platform

        Returns:
            Image generation prompt
        """
        task = f"""Create an image generation prompt for:

Topic: {topic}
Platform: {platform}

Return ONLY the prompt text."""

        response = self.run(task)
        prompt = response.content if hasattr(response, 'content') else str(response)

        return prompt.strip().strip('"').strip("'")
