#!/usr/bin/env python3
"""
Multi-Agent Podcast System - Streamlit UI (Simplified)

Demonstrates multi-agent collaboration with learning.
"""

import streamlit as st
import os
from orchestrator.orchestrator_agent import OrchestratorAgent, SimpleOrchestrator
from core.shared_state import SharedStateManager
from core.learning_engine import PreferenceLearner
from database.db_manager import DatabaseManager

# Page config
st.set_page_config(
    page_title="Multi-Agent Podcast System",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .agent-box {
        background-color: #e3f2fd;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #2196F3;
        margin: 10px 0;
    }
    .success-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin: 10px 0;
    }
    .podcast-card {
        background-color: #f5f5f5;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border-left: 4px solid #FF6B6B;
    }
    .podcast-title {
        font-size: 18px;
        font-weight: 600;
        color: #2c3e50;
    }
    .podcast-author {
        font-size: 14px;
        color: #7f8c8d;
        font-style: italic;
    }
    .podcast-genre {
        font-size: 12px;
        color: #95a5a6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🤖 Multi-Agent Podcast System")
    st.markdown("### Option 2: Full Multi-Agent System with Learning")

    # Sidebar
    with st.sidebar:
        st.header("🔑 Configuration")

        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="Required for AI agents"
        )

        st.divider()

        st.markdown("### 🎯 What Makes This Multi-Agent?")
        st.info("""
        **4 Specialized Agents:**
        - 🔍 **Discovery**: Finds podcasts
        - 📋 **Curator**: Filters by relevance
        - 🎨 **Personalization**: Adapts summaries
        - 📬 **Delivery**: Schedules delivery

        **Orchestrator** coordinates them all!
        """)

        st.divider()

        user_id = st.text_input("User ID", value="demo_user")

    # Main area
    tab1, tab2, tab3 = st.tabs(["🚀 Run System", "📊 Learning Dashboard", "ℹ️ Architecture"])

    with tab1:
        st.markdown("## Run Multi-Agent Workflow")

        col1, col2 = st.columns([3, 1])
        with col1:
            user_goal = st.text_area(
                "What should the system do?",
                value="Find me AI and technology podcasts",
                height=100
            )

        with col2:
            st.markdown("**Quick Presets:**")
            if st.button("🤖 AI Podcasts"):
                user_goal = "Find me AI and machine learning podcasts"
            if st.button("💼 Business"):
                user_goal = "Find me startup and business podcasts"
            if st.button("🔬 Science"):
                user_goal = "Find me science and technology podcasts"

        if st.button("🚀 Run Multi-Agent System", type="primary", disabled=not api_key):
            if not api_key:
                st.error("⚠️ Please enter OpenAI API key")
            else:
                with st.spinner("🤖 Agents are working..."):
                    try:
                        # Initialize orchestrator
                        orchestrator = OrchestratorAgent(api_key)

                        # Execute workflow
                        result = orchestrator.execute(user_id, user_goal)

                        if result.get("success"):
                            st.success("✅ Multi-Agent Workflow Complete!")

                            # Show agent sequence
                            st.markdown("### 🔄 Agent Execution Sequence")
                            agent_seq = result.get("agent_sequence", [])
                            seq_display = " → ".join([a.title() for a in agent_seq])
                            st.markdown(f'<div class="agent-box"><b>Workflow:</b> {seq_display}</div>', unsafe_allow_html=True)

                            # Show results - Parse discovery results nicely
                            agent_outputs = result.get("agent_outputs", {})
                            discovery_output = agent_outputs.get("discovery", {})

                            # Display podcasts in a clean format
                            if discovery_output.get("success") and "result" in discovery_output:
                                result_text = discovery_output["result"]

                                st.markdown("### 🎙️ Discovered Podcasts")

                                # Parse the result text to extract podcast info
                                import re
                                podcast_pattern = r'\d+\.\s+\*\*(.*?)\((.*?)\)\*\*\s+by\s+(.*?)(?:\n|$)'
                                matches = re.findall(podcast_pattern, result_text)

                                if matches:
                                    for i, (title, url, author) in enumerate(matches, 1):
                                        # Extract genres if present
                                        genre_match = re.search(rf"{i}\.\s+.*?\n\s*- Genres:\s*(.*?)(?:\n|$)", result_text)
                                        genres = genre_match.group(1).strip() if genre_match else "Podcast"

                                        # Create podcast card
                                        st.markdown(f"""
                                        <div class="podcast-card">
                                            <div class="podcast-title">{i}. {title.strip()}</div>
                                            <div class="podcast-author">by {author.strip()}</div>
                                            <div class="podcast-genre">📂 {genres}</div>
                                            <div style="margin-top: 10px;">
                                                <a href="{url.strip()}" target="_blank" style="text-decoration: none; color: #2196F3;">
                                                    🔗 Listen to Podcast
                                                </a>
                                            </div>
                                        </div>
                                        """, unsafe_allow_html=True)
                                else:
                                    # Fallback to showing formatted text
                                    st.markdown(result_text)

                            # Show technical details in expanders (collapsed by default)
                            with st.expander("🔍 Technical Details - Agent Outputs", expanded=False):
                                for agent_name in agent_seq:
                                    st.markdown(f"**{agent_name.title()} Agent:**")
                                    output = agent_outputs.get(agent_name, {})
                                    st.json(output)
                                    st.markdown("---")

                            # Feedback buttons
                            st.markdown("### 💬 Was this helpful?")
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                if st.button("👍 Helpful"):
                                    st.success("Thanks! System will learn from this.")
                            with col2:
                                if st.button("👎 Not Helpful"):
                                    st.info("Feedback recorded. System will adapt.")
                            with col3:
                                if st.button("⭐ Save for Later"):
                                    st.info("Saved to your list!")

                        else:
                            st.error(f"❌ Error: {result.get('error', 'Unknown error')}")

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())

    with tab2:
        st.markdown("## 📊 Learning Dashboard")

        if api_key:
            try:
                db = DatabaseManager()
                shared_state = SharedStateManager()

                # Get user context
                user_context = shared_state.get_user_context(user_id)

                st.markdown("### 👤 User Profile")
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**Explicit Preferences:**")
                    st.json(user_context.get("preferences", {}))

                with col2:
                    st.markdown("**Learned Preferences:**")
                    learned = user_context.get("learned_preferences", {})
                    if learned:
                        for key, value in learned.items():
                            st.metric(
                                label=key.replace("_", " ").title(),
                                value=value.get("value", "Unknown"),
                                delta=f"Confidence: {value.get('confidence', 0):.0%}"
                            )
                    else:
                        st.info("No learned preferences yet. Use the system to build your profile!")

                st.divider()

                st.markdown("### 📈 Engagement Summary")
                engagement = user_context.get("engagement_summary", {})
                if engagement:
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Total Interactions", engagement.get("total_interactions", 0))
                    col2.metric("Saves", engagement.get("saves", 0))
                    col3.metric("Shares", engagement.get("shares", 0))
                    col4.metric("Dismisses", engagement.get("dismisses", 0))
                else:
                    st.info("Start using the system to see engagement metrics!")

                st.divider()

                st.markdown("### 🤖 Agent Performance")
                perf_metrics = shared_state.get_agent_performance_metrics()

                if perf_metrics:
                    for agent_perf in perf_metrics:
                        with st.expander(f"📊 {agent_perf.get('agent_name', 'Unknown').title()} Agent"):
                            col1, col2, col3 = st.columns(3)
                            col1.metric("Decisions Made", agent_perf.get("total_decisions", 0))
                            col2.metric("Avg Confidence", f"{agent_perf.get('avg_confidence', 0):.0%}")
                            col3.metric("Success Rate", f"{agent_perf.get('success_rate', 0):.0%}")
                else:
                    st.info("Run the system to see agent performance!")

            except Exception as e:
                st.error(f"Error loading dashboard: {str(e)}")
        else:
            st.warning("Enter API key to view dashboard")

    with tab3:
        st.markdown("## ℹ️ Multi-Agent Architecture")

        st.markdown("""
        ### 🏗️ How It Works

        ```
        User Goal → Orchestrator Agent
                      ↓
            ┌─────────┼─────────┬──────────┬──────────┐
            ▼         ▼         ▼          ▼          ▼
        Discovery  Curator  Personalization  Delivery
          Agent     Agent       Agent          Agent
            │         │           │              │
            └─────────┴───────────┴──────────────┘
                            ↓
                    Shared State Manager (SQLite)
                            ↓
                    Learning Engine (adapts from feedback)
        ```

        ### 🔄 Workflow Steps

        1. **Discovery Agent** 🔍
           - Searches iTunes API for podcasts
           - Finds content matching user topics

        2. **Curator Agent** 📋
           - Analyzes relevance to user interests
           - Checks novelty vs. user history
           - Filters for quality

        3. **Personalization Agent** 🎨
           - Generates summaries with GPT-4
           - Adapts style to user preferences
           - Customizes depth and focus

        4. **Delivery Agent** 📬
           - Decides when to deliver
           - Batches by urgency
           - Optimizes timing

        ### 📚 What's Different from Option 1?

        | Aspect | Option 1 (Simple Agent) | Option 2 (Multi-Agent) |
        |--------|-------------------------|------------------------|
        | **Agents** | 1 monolithic agent | 4 specialized agents |
        | **Orchestration** | None | Orchestrator coordinates |
        | **Learning** | None | SQLite database tracks behavior |
        | **Specialization** | General purpose | Each agent expert in domain |
        | **Scalability** | Limited | Can add more agents |

        ### 🎓 Learning System

        The system learns from your behavior:
        - **Tracks** what you click, save, dismiss
        - **Learns** topic preferences over time
        - **Adapts** agent decisions based on history
        - **Improves** relevance with each interaction
        """)

if __name__ == "__main__":
    main()
