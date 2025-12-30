"""
Image generation tools using DALL-E and Stable Diffusion.

✅ REAL MULTI-AGENT VALUE: LLMs cannot generate images
"""
import os
import requests
from typing import Optional, Dict, Any
from pathlib import Path
from config.settings import settings
from utils.logger import setup_logger

logger = setup_logger("image_tools")

def generate_image_dalle(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "standard",
    save_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate an image using OpenAI's DALL-E.

    Args:
        prompt: Image description
        size: Image size ("1024x1024", "1792x1024", "1024x1792")
        quality: Image quality ("standard" or "hd")
        save_path: Optional path to save the image

    Returns:
        Dictionary with image URL and local path (if saved)
    """
    if not settings.image.openai_api_key:
        logger.warning("OpenAI API key not configured, returning mock data")
        return _mock_image_generation(prompt, save_path)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.image.openai_api_key)

        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size=size,
            quality=quality,
            n=1
        )

        image_url = response.data[0].url
        logger.info(f"Generated image with DALL-E: {prompt[:50]}...")

        result = {
            "url": image_url,
            "prompt": prompt,
            "provider": "dall-e-3"
        }

        # Download and save if path provided
        if save_path:
            local_path = _download_image(image_url, save_path)
            result["local_path"] = local_path

        return result

    except Exception as e:
        logger.error(f"DALL-E generation failed: {str(e)}")
        return _mock_image_generation(prompt, save_path)

def generate_image_replicate(
    prompt: str,
    width: int = 1024,
    height: int = 1024,
    save_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate an image using Stable Diffusion via Replicate.

    Args:
        prompt: Image description
        width: Image width
        height: Image height
        save_path: Optional path to save the image

    Returns:
        Dictionary with image URL and local path (if saved)
    """
    if not settings.image.replicate_api_token:
        logger.warning("Replicate API token not configured, returning mock data")
        return _mock_image_generation(prompt, save_path)

    try:
        import replicate

        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "width": width,
                "height": height,
                "num_outputs": 1
            }
        )

        # Replicate returns a list of URLs
        image_url = output[0] if isinstance(output, list) else output
        logger.info(f"Generated image with Stable Diffusion: {prompt[:50]}...")

        result = {
            "url": image_url,
            "prompt": prompt,
            "provider": "stable-diffusion-xl"
        }

        # Download and save if path provided
        if save_path:
            local_path = _download_image(image_url, save_path)
            result["local_path"] = local_path

        return result

    except Exception as e:
        logger.error(f"Replicate generation failed: {str(e)}")
        return _mock_image_generation(prompt, save_path)

def optimize_image_prompt(topic: str, platform: str) -> str:
    """
    Create an optimized image generation prompt based on content topic and platform.

    Args:
        topic: Content topic
        platform: Target platform (instagram, twitter, linkedin, substack)

    Returns:
        Optimized image generation prompt
    """
    platform_styles = {
        "instagram": "vibrant, eye-catching, modern aesthetic, professional photography style",
        "twitter": "clean, minimal, impactful, suitable for small preview",
        "linkedin": "professional, corporate-friendly, business aesthetic, clean design",
        "substack": "editorial style, sophisticated, article header quality, wide format"
    }

    style = platform_styles.get(platform.lower(), "professional, clean, modern")

    prompt = f"""Create a {style} image representing: {topic}.
High quality, detailed, visually appealing, suitable for social media.
No text or watermarks in the image."""

    return prompt

def _download_image(url: str, save_path: str) -> str:
    """
    Download image from URL and save locally.

    Args:
        url: Image URL
        save_path: Local path to save image

    Returns:
        Full path to saved image
    """
    try:
        # Create directory if it doesn't exist
        save_dir = Path(save_path).parent
        save_dir.mkdir(parents=True, exist_ok=True)

        # Download image
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Save to file
        with open(save_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Image saved to: {save_path}")
        return save_path

    except Exception as e:
        logger.error(f"Failed to download image: {str(e)}")
        raise

def _mock_image_generation(prompt: str, save_path: Optional[str]) -> Dict[str, Any]:
    """Return mock image data for testing without API keys."""
    result = {
        "url": "https://via.placeholder.com/1024x1024.png?text=Generated+Image",
        "prompt": prompt,
        "provider": "mock"
    }

    if save_path:
        # Create a placeholder file
        save_dir = Path(save_path).parent
        save_dir.mkdir(parents=True, exist_ok=True)

        # Create empty placeholder
        Path(save_path).touch()
        result["local_path"] = save_path
        logger.info(f"Created mock image placeholder at: {save_path}")

    return result
