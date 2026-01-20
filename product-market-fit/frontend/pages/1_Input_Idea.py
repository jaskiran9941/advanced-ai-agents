"""
Page 1: Input Your Idea
"""
import streamlit as st
import sys
sys.path.append('..')
from utils.api_client import APIClient

st.set_page_config(page_title="Input Idea", page_icon="💡", layout="wide")

# Initialize API client
if 'api_client' not in st.session_state:
    st.session_state.api_client = APIClient()

st.title("💡 Input Your Idea")
st.markdown("Share your product concept and target market to get started.")

# Idea input form
with st.form("idea_form"):
    product_name = st.text_input(
        "Product Name",
        placeholder="e.g., AI-powered fitness app",
        help="Give your product a name"
    )

    description = st.text_area(
        "Product Description",
        placeholder="Describe your product, what it does, and what problem it solves...",
        help="Be as detailed as possible. Include key features and value propositions.",
        height=150
    )

    target_market = st.text_input(
        "Target Market",
        placeholder="e.g., Busy professionals aged 25-40",
        help="Who is your ideal customer?"
    )

    submitted = st.form_submit_button("Submit Idea", use_container_width=True)

    if submitted:
        if not product_name or not description or not target_market:
            st.error("Please fill in all fields!")
        else:
            with st.spinner("Creating your idea..."):
                try:
                    result = st.session_state.api_client.create_idea(
                        name=product_name,
                        description=description,
                        target_market=target_market
                    )

                    st.success(f"✅ Idea '{product_name}' created successfully!")
                    st.session_state.current_idea_id = result["id"]

                    st.info("**Next Step:** Go to 'AI Research & ICP' to analyze your idea!")

                    # Show the created idea
                    with st.expander("View Your Idea"):
                        st.json(result)

                except Exception as e:
                    st.error(f"Error creating idea: {str(e)}")

# Show existing ideas
st.markdown("---")
st.markdown("### Your Previous Ideas")

try:
    ideas_data = st.session_state.api_client.list_ideas()
    ideas = ideas_data.get("ideas", [])

    if ideas:
        for idea in ideas:
            with st.expander(f"📝 {idea['name']} - Status: {idea['status']}"):
                st.write(f"**Description:** {idea['description']}")
                st.write(f"**Target Market:** {idea['target_market']}")
                st.write(f"**Created:** {idea['created_at']}")

                if st.button(f"Analyze this idea", key=f"analyze_{idea['id']}"):
                    st.session_state.current_idea_id = idea['id']
                    st.info("Idea selected! Go to 'AI Research & ICP' to continue.")
    else:
        st.info("No ideas yet. Create your first one above!")

except Exception as e:
    st.error(f"Error loading ideas: {str(e)}")
