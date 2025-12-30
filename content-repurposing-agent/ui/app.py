"""
Streamlit UI for Content Repurposing Agent System

This provides an interactive interface to:
- Input content topics
- Select target platforms
- Generate and preview content
- Publish to social media
- View results and analytics
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.orchestrator import ContentOrchestrator
from config.settings import settings
import json

# Page configuration
st.set_page_config(
    page_title="Content Repurposing Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize orchestrator (cached to avoid recreating)
@st.cache_resource
def get_orchestrator():
    return ContentOrchestrator()

def main():
    st.title("🤖 Content Repurposing Agent System")
    st.markdown("""
    **Multi-Agent AI System** that transforms a single topic into platform-specific content
    for Twitter and LinkedIn, then publishes to each platform.
    """)

    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Platform selection
        st.subheader("Select Platforms")
        platforms = []
        if st.checkbox("Twitter", value=True):
            platforms.append("twitter")
        if st.checkbox("LinkedIn", value=True):
            platforms.append("linkedin")

        st.divider()

        # Options
        st.subheader("Options")
        enable_seo = st.checkbox("Enable SEO Research", value=True)
        enable_images = st.checkbox("Generate Images", value=True)
        enable_editing = st.checkbox("Enable Content Editing", value=False)
        dry_run = st.checkbox("Dry Run (don't actually post)", value=True,
                              help="When enabled, content is generated but not posted to platforms")

        st.divider()

        # Agent status
        if st.button("View Agent Status"):
            orchestrator = get_orchestrator()
            status = orchestrator.get_agent_status()
            st.json(status)

        st.divider()
        st.caption("""
        **Multi-Agent Architecture:**
        - ✅ SEO Research Agent (REAL)
        - ✅ Image Generator Agent (REAL)
        - ⚠️ Content Writer Agent (EDUCATIONAL)
        - 🔄 Editor Agent (SEMI-REAL)
        - ✅ Platform Agents x4 (REAL)
        - ✅ Orchestrator (REAL)
        """)

    # Main content area
    tab1, tab2, tab3 = st.tabs(["📝 Create Content", "👀 Preview", "📊 Results"])

    with tab1:
        st.header("Create Content")

        # Topic input
        topic = st.text_input(
            "Enter your content topic:",
            placeholder="e.g., The future of AI in healthcare",
            help="This topic will be used to generate platform-specific content"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("🎨 Generate Content Only", type="secondary", use_container_width=True):
                if not topic:
                    st.error("Please enter a topic")
                elif not platforms:
                    st.error("Please select at least one platform")
                else:
                    with st.spinner("Generating content..."):
                        orchestrator = get_orchestrator()
                        results = orchestrator.generate_content_only(
                            topic=topic,
                            platforms=platforms,
                            include_seo=enable_seo
                        )
                        st.session_state["preview_results"] = results
                        st.success("Content generated! Check the Preview tab.")

        with col2:
            if st.button("🚀 Generate & Publish", type="primary", use_container_width=True):
                if not topic:
                    st.error("Please enter a topic")
                elif not platforms:
                    st.error("Please select at least one platform")
                else:
                    with st.spinner("Running full pipeline..."):
                        orchestrator = get_orchestrator()
                        results = orchestrator.run_full_pipeline(
                            topic=topic,
                            platforms=platforms,
                            enable_editing=enable_editing,
                            enable_images=enable_images,
                            dry_run=dry_run
                        )
                        st.session_state["full_results"] = results
                        st.success(f"Pipeline completed in {results.get('duration_seconds', 0):.2f}s!")
                        st.balloons()

    with tab2:
        st.header("Content Preview")

        if "preview_results" in st.session_state:
            results = st.session_state["preview_results"]

            # SEO Results
            if "seo" in results:
                with st.expander("🔍 SEO Research", expanded=True):
                    seo = results["seo"]
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Primary Keywords")
                        for kw in seo.get("primary_keywords", []):
                            st.markdown(f"- {kw}")
                    with col2:
                        st.subheader("Hashtags")
                        for tag in seo.get("hashtags", []):
                            st.markdown(f"`{tag}`")

            # Platform-specific content
            if "content" in results:
                for platform, content in results["content"].items():
                    with st.expander(f"📱 {platform.upper()}", expanded=True):
                        st.markdown("**Generated Content:**")
                        st.text_area(
                            f"{platform}_content",
                            value=content if isinstance(content, str) else str(content),
                            height=200,
                            label_visibility="collapsed"
                        )

                        # Character count
                        char_count = len(content) if isinstance(content, str) else 0
                        st.caption(f"Character count: {char_count}")

        else:
            st.info("Generate content in the 'Create Content' tab to see preview here.")

    with tab3:
        st.header("Pipeline Results")

        if "full_results" in st.session_state:
            results = st.session_state["full_results"]

            # Success summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Status", "✅ Success" if results.get("success") else "❌ Failed")
            with col2:
                st.metric("Duration", f"{results.get('duration_seconds', 0):.2f}s")
            with col3:
                st.metric("Platforms", len(results.get("platforms", [])))

            # Steps
            if "steps" in results:
                steps = results["steps"]

                # SEO
                if "seo_research" in steps:
                    with st.expander("🔍 SEO Research"):
                        st.json(steps["seo_research"])

                # Content Writing
                if "content_writing" in steps:
                    with st.expander("✍️ Content Writing"):
                        for platform, content in steps["content_writing"].items():
                            st.subheader(platform.upper())
                            st.text(content[:300] + "..." if len(content) > 300 else content)

                # Image Generation
                if "image_generation" in steps:
                    with st.expander("🎨 Image Generation"):
                        for platform, img_data in steps["image_generation"].items():
                            st.subheader(platform.upper())
                            if "url" in img_data:
                                st.image(img_data["url"], width=300)
                            st.json(img_data)

                # Publishing
                if "publishing" in steps:
                    with st.expander("🚀 Publishing Results", expanded=True):
                        for platform, pub_result in steps["publishing"].items():
                            st.subheader(platform.upper())
                            if pub_result.get("success"):
                                st.success(f"✅ Published successfully")
                                if "url" in pub_result:
                                    st.markdown(f"[View Post]({pub_result['url']})")
                            else:
                                st.error(f"❌ {pub_result.get('error', 'Unknown error')}")
                            st.json(pub_result)

            # Raw results
            with st.expander("📄 Raw Results JSON"):
                st.json(results)

            # Download results
            if st.button("Download Results"):
                json_str = json.dumps(results, indent=2)
                st.download_button(
                    label="Download JSON",
                    data=json_str,
                    file_name=f"content_results_{results.get('timestamp', 'unknown')}.json",
                    mime="application/json"
                )

        else:
            st.info("Run the full pipeline in the 'Create Content' tab to see results here.")

    # Footer
    st.divider()
    st.caption("""
    **About this system:**
    This multi-agent system demonstrates both real and educational agent separation:
    - **REAL agents**: SEO research, image generation, platform publishing, orchestration
    - **SEMI-REAL**: Editor (iteration adds value)
    - **EDUCATIONAL**: Content writer (could be single LLM call)

    Built with: Agno AI, Claude, Gemini, Streamlit
    """)

if __name__ == "__main__":
    main()
