"""
Page 2: AI Research & ICP
"""
import streamlit as st
import time
import sys
sys.path.append('..')
from utils.api_client import APIClient

st.set_page_config(page_title="Research & ICP", page_icon="🔬", layout="wide")

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

st.title("🔬 AI Research & ICP")
st.markdown("Let AI research your market and create an Ideal Customer Profile")

# Check if we have a current idea
if 'current_idea_id' not in st.session_state:
    st.warning("⚠️ No idea selected. Please go to 'Input Idea' first.")
    st.stop()

idea_id = st.session_state.current_idea_id

# Load idea details
try:
    idea = st.session_state.api_client.get_idea(idea_id)

    st.markdown("### Current Idea")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.info(f"**{idea['name']}**\n\n{idea['description']}")

    with col2:
        st.metric("Target Market", idea['target_market'])
        st.metric("Status", idea['status'])

except Exception as e:
    st.error(f"Error loading idea: {e}")
    st.stop()

st.markdown("---")

# Check if research is in progress
def check_progress():
    """Check research progress and return status"""
    try:
        progress = st.session_state.api_client.get_research_progress(idea_id)
        return progress
    except:
        return None

# Show progress if research is running
progress = check_progress()
is_running = progress and progress.get("status") == "running"

# Start research button (disabled if already running)
if st.button("🚀 Start AI Research", use_container_width=True, type="primary", disabled=is_running):
    try:
        result = st.session_state.api_client.start_research(idea_id)
        st.rerun()
    except Exception as e:
        st.error(f"Error starting research: {e}")

# Show progress bar if research is running
if is_running:
    st.markdown("### 🔄 Research in Progress")

    progress_percent = progress.get("progress_percent", 0)
    step_message = progress.get("step_message", "Processing...")

    # Progress bar
    progress_bar = st.progress(progress_percent / 100)
    st.markdown(f"**{step_message}**")
    st.caption(f"{progress_percent}% complete")

    # Auto-refresh every 2 seconds
    time.sleep(2)
    st.rerun()

# Show completion message
elif progress and progress.get("status") == "completed":
    st.success("✅ Research workflow completed!")

# Try to load research results
st.markdown("### Research Results")

try:
    research = st.session_state.api_client.get_research(idea_id)

    if "status" in research and research["status"] == "pending":
        st.info("🔄 Research in progress... Refresh the page in a moment.")
    else:
        # Display research findings
        st.success("✅ Research Complete!")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Market Size")
            st.write(research.get("market_size", "N/A"))

            st.markdown("#### Key Competitors")
            competitors = research.get("competitors", [])
            for comp in competitors:
                with st.expander(f"🏢 {comp.get('name', 'Unknown')}"):
                    st.write(f"**Description:** {comp.get('description', 'N/A')}")
                    st.write(f"**Strengths:** {comp.get('strengths', 'N/A')}")
                    st.write(f"**Weaknesses:** {comp.get('weaknesses', 'N/A')}")

        with col2:
            st.markdown("#### Market Trends")
            trends = research.get("trends", [])
            for trend in trends:
                st.write(f"• {trend}")

            st.markdown("#### Customer Pain Points")
            pain_points = research.get("pain_points", [])
            for pain in pain_points:
                st.write(f"• {pain}")

            st.markdown("#### Opportunities")
            opportunities = research.get("opportunities", [])
            for opp in opportunities:
                st.write(f"• {opp}")

except Exception as e:
    st.info("No research data yet. Click 'Start AI Research' above.")

# Try to load ICP
st.markdown("---")
st.markdown("### Ideal Customer Profile (ICP)")

try:
    icp = st.session_state.api_client.get_icp(idea_id)

    if "status" in icp and icp["status"] == "pending":
        st.info("ICP will be created automatically after research completes.")
    else:
        # Display ICP
        st.success("✅ ICP Created!")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("#### Demographics")
            demographics = icp.get("demographics", {})
            st.write(f"**Age Range:** {demographics.get('age_range', 'N/A')}")
            st.write(f"**Gender:** {demographics.get('gender', 'N/A')}")
            st.write(f"**Income:** {demographics.get('income', 'N/A')}")
            st.write(f"**Education:** {demographics.get('education', 'N/A')}")
            st.write(f"**Location:** {demographics.get('location', 'N/A')}")

        with col2:
            st.markdown("#### Psychographics")
            psycho = icp.get("psychographics", {})
            st.write("**Values:**")
            for val in psycho.get("values", []):
                st.write(f"• {val}")
            st.write("**Interests:**")
            for interest in psycho.get("interests", []):
                st.write(f"• {interest}")
            st.write(f"**Lifestyle:** {psycho.get('lifestyle', 'N/A')}")

        with col3:
            st.markdown("#### Behaviors")
            behaviors = icp.get("behaviors", {})
            st.write(f"**Buying Patterns:** {behaviors.get('buying_patterns', 'N/A')}")
            st.write("**Media Consumption:**")
            for media in behaviors.get("media_consumption", []):
                st.write(f"• {media}")
            st.write(f"**Tech Savviness:** {behaviors.get('tech_savviness', 'N/A')}")

        st.markdown("#### Pain Points & Goals")
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Pain Points:**")
            for pain in icp.get("pain_points", []):
                st.write(f"• {pain}")

        with col2:
            st.write("**Goals:**")
            for goal in icp.get("goals", []):
                st.write(f"• {goal}")

        st.markdown("#### Decision Criteria")
        for criteria in icp.get("decision_criteria", []):
            st.write(f"• {criteria}")

        st.metric("Confidence Score", f"{icp.get('confidence_score', 0):.0%}")

        st.markdown("---")
        st.success("**Next Step:** Go to 'Synthetic Personas' to create AI personas based on this ICP!")

except Exception as e:
    st.info("ICP not yet created. It will appear here after research completes.")
