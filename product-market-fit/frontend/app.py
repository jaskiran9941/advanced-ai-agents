"""
Product Market Fit - Single Page Application
"""
import streamlit as st
import time
import os
from utils.api_client import APIClient

st.set_page_config(
    page_title="Product Market Fit",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient(base_url="http://localhost:8000")

st.title("🚀 Product Market Fit - AI-Powered Product Validation")

# API Key Configuration Section
with st.expander("⚙️ API Configuration (Click to configure)", expanded=False):
    st.markdown("### Configure API Keys")
    st.info("💡 **Important**: Add your API keys to `backend/.env` file and restart the backend server")

    col1, col2 = st.columns(2)

    with col1:
        st.code("""
# Edit: backend/.env

ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
TAVILY_API_KEY=tvly-your-key-here
        """, language="bash")

    with col2:
        st.markdown("**Steps:**")
        st.markdown("1. Open `backend/.env` in a text editor")
        st.markdown("2. Replace `your-key-here` with actual keys")
        st.markdown("3. Restart backend: `cd backend && python3 -m uvicorn app.main:app --reload`")

        if st.button("🔄 Test Connection"):
            try:
                ideas = st.session_state.api_client.list_ideas()
                st.success("✅ Backend connected successfully!")
            except Exception as e:
                st.error(f"❌ Connection failed: {e}")

st.markdown("---")

# Single Page Workflow
col_left, col_right = st.columns([1, 1])

with col_left:
    # ===== STEP 1: INPUT IDEA =====
    st.markdown("## 1️⃣ Input Your Idea")

    with st.form("idea_form"):
        product_name = st.text_input("Product Name", placeholder="e.g., AI Fitness App")
        description = st.text_area("Description", placeholder="What does it do? What problem does it solve?", height=100)
        target_market = st.text_input("Target Market", placeholder="e.g., Busy professionals aged 25-40")

        submitted = st.form_submit_button("💡 Submit Idea", use_container_width=True, type="primary")

        if submitted and product_name and description and target_market:
            try:
                result = st.session_state.api_client.create_idea(
                    name=product_name,
                    description=description,
                    target_market=target_market
                )
                st.session_state.current_idea_id = result["id"]
                st.success(f"✅ Idea created! ID: {result['id']}")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    # Show existing ideas
    try:
        ideas_data = st.session_state.api_client.list_ideas()
        ideas = ideas_data.get("ideas", [])

        if ideas:
            st.markdown("### Recent Ideas")
            for idea in ideas[:3]:
                with st.expander(f"📝 {idea['name']}"):
                    st.write(f"**Description:** {idea['description']}")
                    st.write(f"**Target:** {idea['target_market']}")
                    if st.button(f"Select this idea", key=f"select_{idea['id']}"):
                        st.session_state.current_idea_id = idea['id']
                        st.rerun()
    except Exception as e:
        st.warning("Could not load ideas. Check backend connection.")

with col_right:
    # ===== STEP 2: RESEARCH & ICP =====
    if 'current_idea_id' in st.session_state:
        idea_id = st.session_state.current_idea_id

        st.markdown("## 2️⃣ AI Research & ICP")

        try:
            idea = st.session_state.api_client.get_idea(idea_id)
            st.info(f"**Working on:** {idea['name']}")

            if st.button("🔬 Start AI Research", use_container_width=True, type="primary"):
                with st.spinner("AI analyzing market... (~60 seconds)"):
                    try:
                        st.session_state.api_client.start_research(idea_id)
                        time.sleep(5)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Research failed: {e}\n\n**Check if API keys are configured in backend/.env**")

            # Show research results
            research = st.session_state.api_client.get_research(idea_id)
            if "status" not in research or research["status"] != "pending":
                st.success("✅ Research Complete")

                with st.expander("📊 Research Findings", expanded=True):
                    st.markdown(f"**Market Size:** {research.get('market_size', 'N/A')}")
                    st.markdown("**Pain Points:**")
                    for pain in research.get("pain_points", [])[:3]:
                        st.write(f"• {pain}")

                    # Show search queries used
                    if research.get("search_queries"):
                        st.markdown("**Web Searches Performed:**")
                        for query in research["search_queries"][:3]:
                            st.caption(f"🔍 {query}")

                # Display Research Reasoning Trace
                if research.get("_reasoning_trace"):
                    with st.expander("🧠 Research Reasoning Trace"):
                        st.markdown("**Agentic Research Process:**")

                        final_confidence = research.get("_final_confidence", 0)
                        iterations_used = research.get("_iterations_used", 0)

                        st.metric("Research Quality", f"{final_confidence:.0%}", delta=f"{iterations_used} iterations")

                        st.markdown("---")

                        for trace in research["_reasoning_trace"]:
                            iteration = trace.get("iteration", 0)
                            confidence = trace.get("confidence", 0)
                            is_valid = trace.get("is_valid", False)
                            suggestions = trace.get("suggestions", [])

                            status_icon = "✅" if is_valid else "🔄"
                            status_text = "PASSED" if is_valid else "REFINING"

                            st.markdown(f"**{status_icon} Iteration {iteration}** - {status_text}")
                            st.progress(confidence)
                            st.caption(f"Quality: {confidence:.0%}")

                            if suggestions:
                                st.markdown("*Improvements needed:*")
                                for suggestion in suggestions[:3]:
                                    st.write(f"  • {suggestion}")

                            if iteration < len(research["_reasoning_trace"]):
                                st.markdown("---")

                        st.info("💡 The AI agent used web search and iteratively refined research until quality thresholds were met.")

            # Show ICP
            icp = st.session_state.api_client.get_icp(idea_id)
            if "status" not in icp or icp["status"] != "pending":
                st.success("✅ ICP Created")

                with st.expander("👤 Ideal Customer Profile", expanded=True):
                    demographics = icp.get("demographics", {})
                    st.write(f"**Age:** {demographics.get('age_range', 'N/A')}")
                    st.write(f"**Income:** {demographics.get('income', 'N/A')}")

                    st.markdown("**Goals:**")
                    for goal in icp.get("goals", [])[:3]:
                        st.write(f"• {goal}")

                # Display AI Reasoning Trace
                if icp.get("_reasoning_trace"):
                    with st.expander("🧠 AI Reasoning Trace (Agentic Process)"):
                        st.markdown("**Iterative Quality Improvement:**")

                        final_confidence = icp.get("_final_confidence", 0)
                        iterations_used = icp.get("_iterations_used", 0)

                        st.metric("Final Quality Score", f"{final_confidence:.0%}", delta=f"{iterations_used} iterations")

                        st.markdown("---")

                        for trace in icp["_reasoning_trace"]:
                            iteration = trace.get("iteration", 0)
                            confidence = trace.get("confidence", 0)
                            is_valid = trace.get("is_valid", False)
                            suggestions = trace.get("suggestions", [])

                            # Color code based on validity
                            status_icon = "✅" if is_valid else "🔄"
                            status_text = "PASSED" if is_valid else "REFINING"

                            st.markdown(f"**{status_icon} Iteration {iteration}** - {status_text}")
                            st.progress(confidence)
                            st.caption(f"Quality: {confidence:.0%}")

                            if suggestions:
                                st.markdown("*Refinements needed:*")
                                for suggestion in suggestions:
                                    st.write(f"  • {suggestion}")

                            if iteration < len(icp["_reasoning_trace"]):
                                st.markdown("---")

                        st.info("💡 The AI agent iteratively refined the ICP until quality thresholds were met.")

        except Exception as e:
            st.warning("Select an idea from Step 1 first")
    else:
        st.info("👈 Create or select an idea first")

# ===== STEP 3: PERSONAS =====
st.markdown("---")
st.markdown("## 3️⃣ Generate & Chat with Personas")

if 'current_idea_id' in st.session_state:
    col1, col2 = st.columns([1, 2])

    with col1:
        num_personas = st.slider("Number of personas", 2, 5, 3)

        if st.button("🎭 Generate Personas", use_container_width=True, type="primary"):
            with st.spinner(f"Creating {num_personas} personas... (~60 seconds)"):
                try:
                    result = st.session_state.api_client.generate_personas(idea_id, num_personas)
                    st.success(f"✅ Generated {result.get('num_personas')} personas!")
                    time.sleep(2)
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}\n\nMake sure research is complete and API keys are set")

    with col2:
        # Show personas
        try:
            personas_data = st.session_state.api_client.list_personas(idea_id)
            personas = personas_data.get("personas", [])

            if personas:
                st.markdown(f"### {len(personas)} Personas Generated")

                # Persona tabs
                tabs = st.tabs([f"{p['name']}" for p in personas])

                for i, persona in enumerate(personas):
                    with tabs[i]:
                        col_profile, col_chat = st.columns([1, 1])

                        with col_profile:
                            st.markdown(f"**{persona.get('age')} years old, {persona.get('occupation')}**")
                            st.markdown(f"📍 {persona.get('location')}")

                            with st.expander("📖 Background"):
                                st.write(persona.get('background_story', 'N/A')[:300] + "...")

                            traits = persona.get('personality_traits', [])
                            if traits:
                                st.write("**Personality:**")
                                st.write(", ".join(traits[:3]))

                        with col_chat:
                            st.markdown("💬 **Chat**")

                            # Initialize chat
                            chat_key = f"chat_{persona['id']}"
                            if chat_key not in st.session_state:
                                st.session_state[chat_key] = {"session_id": None, "messages": []}

                            # Display messages
                            for msg in st.session_state[chat_key]["messages"][-5:]:
                                st.chat_message("user").write(msg["user"])
                                st.chat_message("assistant").write(msg["assistant"])

                            # Chat input
                            user_msg = st.chat_input(f"Message {persona['name']}...", key=f"input_{persona['id']}")

                            if user_msg:
                                try:
                                    response = st.session_state.api_client.send_message(
                                        persona_id=persona['id'],
                                        message=user_msg,
                                        session_id=st.session_state[chat_key]["session_id"]
                                    )

                                    st.session_state[chat_key]["session_id"] = response.get("session_id")
                                    st.session_state[chat_key]["messages"].append({
                                        "user": user_msg,
                                        "assistant": response.get("response")
                                    })
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Chat error: {e}")
            else:
                st.info("👆 Generate personas to start chatting")

        except Exception as e:
            st.info("Generate personas after completing research")
else:
    st.info("Complete steps 1 & 2 first to generate personas")

# Footer
st.markdown("---")
st.caption("🤖 Powered by Claude Sonnet (Research/ICP) + GPT-4 (Chat) | Made with Streamlit + FastAPI + LangGraph")
