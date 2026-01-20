"""
Page 3: Synthetic Personas & Chat
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.api_client import APIClient

st.set_page_config(page_title="Synthetic Personas", page_icon="👥", layout="wide")

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

st.title("👥 Synthetic Personas")
st.markdown("Generate AI-powered customer personas and chat with them to validate your idea")

# Check if we have a current idea
if 'current_idea_id' not in st.session_state:
    st.warning("⚠️ No idea selected. Please go through the previous steps first.")
    st.stop()

idea_id = st.session_state.current_idea_id

# Persona generation section
st.markdown("### Generate Personas")

num_personas = st.slider("Number of personas to generate", min_value=2, max_value=5, value=3)

if st.button("🎭 Generate Personas", use_container_width=True, type="primary"):
    with st.spinner(f"Generating {num_personas} unique personas... This may take 30-60 seconds."):
        try:
            result = st.session_state.api_client.generate_personas(idea_id, num_personas)
            st.success(f"✅ Generated {result.get('num_personas')} personas!")
            st.rerun()

        except Exception as e:
            st.error(f"Error generating personas: {e}")

# Display personas
st.markdown("---")
st.markdown("### Your Personas")

try:
    personas_data = st.session_state.api_client.list_personas(idea_id)
    personas = personas_data.get("personas", [])

    if not personas:
        st.info("No personas generated yet. Click 'Generate Personas' above to create them.")
    else:
        # Display persona cards
        for persona in personas:
            with st.expander(f"🙋 {persona['name']} - {persona.get('age')} years old, {persona.get('occupation')}"):
                col1, col2 = st.columns([1, 2])

                with col1:
                    st.markdown("#### Profile")
                    st.write(f"**Age:** {persona.get('age')}")
                    st.write(f"**Occupation:** {persona.get('occupation')}")
                    st.write(f"**Location:** {persona.get('location')}")

                    st.markdown("**Personality Traits:**")
                    for trait in persona.get("personality_traits", []):
                        st.write(f"• {trait}")

                with col2:
                    st.markdown("#### Background Story")
                    st.write(persona.get("background_story", "No background story available"))

                    st.markdown("**Communication Style:**")
                    st.write(persona.get("communication_style", "N/A"))

                st.markdown("---")

                # Chat interface for this persona
                st.markdown(f"#### Chat with {persona['name']}")

                # Initialize chat session for this persona
                chat_key = f"chat_{persona['id']}"
                if chat_key not in st.session_state:
                    st.session_state[chat_key] = {
                        "session_id": None,
                        "messages": []
                    }

                # Display chat history
                for msg in st.session_state[chat_key]["messages"]:
                    with st.chat_message("user"):
                        st.write(msg["user"])
                    with st.chat_message("assistant"):
                        st.write(msg["assistant"])
                        if msg.get("sentiment"):
                            sentiment_emoji = {
                                "positive": "😊",
                                "neutral": "😐",
                                "curious": "🤔",
                                "objection": "🤨"
                            }
                            st.caption(f"Sentiment: {sentiment_emoji.get(msg['sentiment'], '😐')} {msg['sentiment']}")

                # Chat input
                user_message = st.chat_input(f"Message {persona['name']}...", key=f"input_{persona['id']}")

                if user_message:
                    with st.spinner(f"{persona['name']} is typing..."):
                        try:
                            # Send message
                            response = st.session_state.api_client.send_message(
                                persona_id=persona['id'],
                                message=user_message,
                                session_id=st.session_state[chat_key]["session_id"]
                            )

                            # Update session ID
                            st.session_state[chat_key]["session_id"] = response.get("session_id")

                            # Add to chat history
                            st.session_state[chat_key]["messages"].append({
                                "user": user_message,
                                "assistant": response.get("response"),
                                "sentiment": response.get("sentiment"),
                                "topics": response.get("topics", [])
                            })

                            st.rerun()

                        except Exception as e:
                            st.error(f"Error chatting with {persona['name']}: {e}")

except Exception as e:
    st.error(f"Error loading personas: {e}")

# Summary section
if 'personas' in locals() and personas:
    st.markdown("---")
    st.markdown("### Conversation Insights")

    total_conversations = sum(
        len(st.session_state.get(f"chat_{p['id']}", {}).get("messages", []))
        for p in personas
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Personas", len(personas))

    with col2:
        st.metric("Total Messages", total_conversations)

    with col3:
        # Count sentiments
        all_sentiments = []
        for p in personas:
            chat_key = f"chat_{p['id']}"
            if chat_key in st.session_state:
                all_sentiments.extend([
                    msg.get("sentiment", "neutral")
                    for msg in st.session_state[chat_key].get("messages", [])
                ])

        positive = sum(1 for s in all_sentiments if s == "positive")
        objection = sum(1 for s in all_sentiments if s == "objection")

        if all_sentiments:
            st.metric("Positive Sentiment", f"{positive/len(all_sentiments)*100:.0f}%")
        else:
            st.metric("Positive Sentiment", "N/A")

    st.markdown("---")
    st.info("💡 **Tip:** Have conversations with each persona to understand different customer perspectives on your product!")
