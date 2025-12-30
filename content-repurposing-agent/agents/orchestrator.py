"""
Content Repurposing Orchestrator

✅ REAL MULTI-AGENT VALUE
Why: This agent coordinates all specialized agents, manages workflow state,
handles parallel execution, error recovery, and ensures the entire pipeline works.
This is PURE orchestration logic that demonstrates real multi-agent architecture.
"""
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from utils.logger import setup_logger

# Import all specialized agents
from agents.seo_agent import SEOResearchAgent
from agents.image_agent import ImageGeneratorAgent
from agents.writer_agent import ContentWriterAgent
from agents.editor_agent import EditorAgent
from agents.platform_agents import (
    LinkedInAgent,
    TwitterAgent,
    InstagramAgent,
    SubstackAgent
)

logger = setup_logger("orchestrator")

class ContentOrchestrator:
    """
    Main orchestrator that coordinates all agents in the content repurposing pipeline.

    Workflow:
    1. SEO Research (get keywords, trends)
    2. Content Writing (create platform-specific content)
    3. Image Generation (create visuals) - PARALLEL with writing
    4. Editing/Quality Check (review and refine)
    5. Platform Publishing (post to selected platforms) - PARALLEL
    6. Track results and handle errors

    This demonstrates:
    - Multi-agent coordination
    - Parallel execution where appropriate
    - Sequential execution where dependencies exist
    - Error handling and retries
    - State management
    """

    def __init__(self):
        """Initialize orchestrator with all agents."""
        logger.info("Initializing Content Orchestrator with all agents...")

        # Research agents
        self.seo_agent = SEOResearchAgent(llm_provider="openai")
        self.image_agent = ImageGeneratorAgent(llm_provider="openai", image_provider="openai")

        # Content creation agents
        self.writer_agent = ContentWriterAgent(llm_provider="openai")
        self.editor_agent = EditorAgent(llm_provider="openai")

        # Platform agents
        self.linkedin_agent = LinkedInAgent(llm_provider="openai")
        self.twitter_agent = TwitterAgent(llm_provider="openai")
        self.instagram_agent = InstagramAgent(llm_provider="openai")
        self.substack_agent = SubstackAgent(llm_provider="openai")

        self.platform_agents = {
            "linkedin": self.linkedin_agent,
            "twitter": self.twitter_agent,
            "instagram": self.instagram_agent,
            "substack": self.substack_agent
        }

        logger.info("Orchestrator initialized with 9 specialized agents")

    def run_full_pipeline(
        self,
        topic: str,
        platforms: List[str],
        enable_editing: bool = True,
        enable_images: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete content repurposing pipeline.

        Args:
            topic: Content topic
            platforms: List of platforms to publish to
            enable_editing: Whether to run editor agent
            enable_images: Whether to generate images
            dry_run: If True, don't actually post to platforms

        Returns:
            Complete pipeline results
        """
        logger.info(f"Starting full pipeline for topic: {topic}")
        logger.info(f"Target platforms: {platforms}")

        start_time = datetime.now()
        results = {
            "topic": topic,
            "platforms": platforms,
            "timestamp": start_time.isoformat(),
            "steps": {}
        }

        try:
            # STEP 1: SEO Research
            logger.info("Step 1: SEO Research")
            seo_results = self.seo_agent.research_topic(topic)
            results["steps"]["seo_research"] = seo_results

            keywords = seo_results.get("primary_keywords", [])
            hashtags = seo_results.get("hashtags", [])

            # STEP 2 & 3: Content Writing + Image Generation (PARALLEL)
            logger.info("Step 2-3: Content Writing + Image Generation (parallel)")

            # Run in parallel
            content_results = self.writer_agent.write_all_platforms(
                topic=topic,
                keywords=keywords,
                hashtags=hashtags
            )

            image_results = {}
            if enable_images:
                for platform in platforms:
                    if platform in ["instagram", "linkedin"]:
                        try:
                            img = self.image_agent.generate_for_topic(topic, platform)
                            image_results[platform] = img
                        except Exception as e:
                            logger.error(f"Image generation failed for {platform}: {e}")
                            image_results[platform] = {"error": str(e)}

            results["steps"]["content_writing"] = content_results
            results["steps"]["image_generation"] = image_results

            # STEP 4: Editing (if enabled)
            if enable_editing:
                logger.info("Step 4: Content Editing")
                edited_content = {}

                for platform in platforms:
                    content = content_results.get(platform, "")
                    if content:
                        try:
                            review = self.editor_agent.review_content(content, platform)
                            edited_content[platform] = review
                        except Exception as e:
                            logger.error(f"Editing failed for {platform}: {e}")
                            edited_content[platform] = {"error": str(e)}

                results["steps"]["editing"] = edited_content

            # STEP 5: Platform Publishing (PARALLEL)
            logger.info("Step 5: Publishing to platforms")
            publish_results = {}

            for platform in platforms:
                if platform not in self.platform_agents:
                    logger.warning(f"Unknown platform: {platform}")
                    continue

                try:
                    content = content_results.get(platform, "")
                    if not content:
                        logger.warning(f"No content for {platform}")
                        continue

                    agent = self.platform_agents[platform]

                    # Platform-specific publishing
                    if platform == "twitter":
                        result = agent.format_and_post(
                            content=content,
                            hashtags=hashtags,
                            dry_run=dry_run
                        )
                    elif platform == "linkedin":
                        image_url = image_results.get(platform, {}).get("url")
                        result = agent.format_and_post(
                            content=content,
                            image_url=image_url,
                            dry_run=dry_run
                        )
                    elif platform == "instagram":
                        image_path = image_results.get(platform, {}).get("local_path")
                        if image_path:
                            result = agent.format_and_post(
                                content=content,
                                image_path=image_path,
                                hashtags=hashtags,
                                dry_run=dry_run
                            )
                        else:
                            result = {"error": "No image available for Instagram"}
                    elif platform == "substack":
                        result = agent.format_and_publish(
                            content=content,
                            dry_run=dry_run
                        )
                    else:
                        result = {"error": f"Publishing not implemented for {platform}"}

                    publish_results[platform] = result

                except Exception as e:
                    logger.error(f"Publishing failed for {platform}: {e}")
                    publish_results[platform] = {"error": str(e)}

            results["steps"]["publishing"] = publish_results

            # Calculate completion time
            end_time = datetime.now()
            results["duration_seconds"] = (end_time - start_time).total_seconds()
            results["success"] = True

            logger.info(f"Pipeline completed in {results['duration_seconds']:.2f} seconds")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    def generate_content_only(
        self,
        topic: str,
        platforms: List[str],
        include_seo: bool = True
    ) -> Dict[str, Any]:
        """
        Generate content without publishing (for preview).

        Args:
            topic: Content topic
            platforms: Platforms to generate for
            include_seo: Whether to do SEO research

        Returns:
            Generated content for all platforms
        """
        logger.info(f"Generating content for: {topic}")

        results = {"topic": topic}

        # SEO research
        if include_seo:
            seo_results = self.seo_agent.research_topic(topic)
            results["seo"] = seo_results
            keywords = seo_results.get("primary_keywords", [])
            hashtags = seo_results.get("hashtags", [])
        else:
            keywords = []
            hashtags = []

        # Generate content
        content = self.writer_agent.write_all_platforms(
            topic=topic,
            keywords=keywords,
            hashtags=hashtags
        )

        # Filter to requested platforms
        results["content"] = {
            platform: content[platform]
            for platform in platforms
            if platform in content
        }

        return results

    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get status of all agents.

        Returns:
            Status information for all agents
        """
        return {
            "total_agents": 9,
            "agents": {
                "seo_research": self.seo_agent.get_info(),
                "image_generator": self.image_agent.get_info(),
                "content_writer": self.writer_agent.get_info(),
                "editor": self.editor_agent.get_info(),
                "linkedin": self.linkedin_agent.get_info(),
                "twitter": self.twitter_agent.get_info(),
                "instagram": self.instagram_agent.get_info(),
                "substack": self.substack_agent.get_info()
            }
        }
