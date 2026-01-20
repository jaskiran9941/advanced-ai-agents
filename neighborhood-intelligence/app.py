"""
Neighborhood Intelligence Agent - Streamlit Frontend
"""
import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.orchestrator import UserProfile, run_full_analysis
from config import USE_MOCK_DATA

# Page config
st.set_page_config(
    page_title="Neighborhood Intelligence Agent",
    page_icon="🏠",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-top: 0;
    }
    .score-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
    }
    .score-number {
        font-size: 3rem;
        font-weight: 700;
    }
    .highlight-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
        color: #1b5e20 !important;
    }
    .concern-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 15px;
        margin: 10px 0;
        border-radius: 0 10px 10px 0;
        color: #e65100 !important;
    }
    .agent-card {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        border: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">🏠 Neighborhood Intelligence Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Discover what life would really be like at any address</p>', unsafe_allow_html=True)

# Mock data notice
if USE_MOCK_DATA:
    st.info("🧪 **Demo Mode**: Using mock data. Add API keys to `.env` for real analysis.")

st.divider()

# Sidebar for inputs
with st.sidebar:
    st.header("📝 Your Profile")
    
    # Address inputs
    st.subheader("Location to Analyze")
    address = st.text_input(
        "Street Address",
        placeholder="123 Example St, Fremont, CA 94539",
        help="The address you want to analyze"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        city = st.text_input("City", placeholder="Fremont")
    with col2:
        state = st.text_input("State", placeholder="CA", max_chars=2)
    
    st.divider()
    
    # Work info
    st.subheader("🏢 Work Details")
    work_address = st.text_input(
        "Work Address",
        placeholder="1600 Amphitheatre Pkwy, Mountain View, CA",
        help="Your workplace address for commute analysis"
    )
    
    work_schedule = st.selectbox(
        "Work Schedule",
        ["Standard 9am-5pm, Monday-Friday",
         "Flexible hours",
         "Hybrid (3 days in office)",
         "Mostly remote",
         "Shift work"]
    )
    
    st.divider()
    
    # Family info
    st.subheader("👨‍👩‍👧‍👦 Family")
    has_kids = st.checkbox("I have children")
    
    child_ages = []
    if has_kids:
        child_ages_str = st.text_input(
            "Child ages (comma-separated)",
            placeholder="6, 10",
            help="Ages of your children for school analysis"
        )
        if child_ages_str:
            try:
                child_ages = [int(age.strip()) for age in child_ages_str.split(",")]
            except:
                st.error("Please enter valid ages (e.g., 6, 10)")
    
    st.divider()
    
    # Lifestyle preferences
    st.subheader("🏃 Lifestyle Preferences")
    
    lifestyle_options = st.multiselect(
        "What's important to you?",
        ["gym", "park", "temple", "grocery", "coffee", "restaurant", "school"],
        default=["park", "grocery"],
        help="Select amenities you care about"
    )
    
    st.divider()
    
    # Concerns
    st.subheader("⚠️ Your Concerns")
    concerns = st.multiselect(
        "What worries you?",
        ["safety", "traffic noise", "construction", "schools", "crime", "property values"],
        default=[],
        help="We'll pay extra attention to these areas"
    )
    
    st.divider()
    
    # Analyze button
    analyze_button = st.button(
        "🔍 Analyze Neighborhood",
        type="primary",
        use_container_width=True,
        disabled=not (address and city and state)
    )

# Main content area
if analyze_button:
    # Create user profile
    full_address = f"{address}, {city}, {state}" if address else ""
    
    profile = UserProfile(
        address=full_address,
        city=city,
        state=state,
        work_address=work_address if work_address else None,
        has_kids=has_kids,
        child_ages=child_ages,
        lifestyle_preferences=lifestyle_options,
        concerns=concerns,
        work_schedule=work_schedule
    )
    
    # Run analysis
    with st.spinner("🔍 Analyzing neighborhood... This may take a moment..."):
        results = run_full_analysis(profile)
    
    # Display results
    st.success("✅ Analysis Complete!")
    
    # Scores overview
    st.header("📊 Overall Scores")
    
    scores = results.get("synthesis", {}).get("scores", {})
    
    score_cols = st.columns(5)
    
    with score_cols[0]:
        st.metric(
            label="🎯 Overall",
            value=f"{scores.get('overall', 'N/A')}/10",
            delta="Good fit" if scores.get('overall', 0) >= 7 else None
        )
    
    with score_cols[1]:
        st.metric(
            label="🚗 Commute",
            value=f"{scores.get('commute', 'N/A')}/10"
        )
    
    with score_cols[2]:
        st.metric(
            label="🏃 Lifestyle",
            value=f"{scores.get('lifestyle', 'N/A')}/10"
        )
    
    with score_cols[3]:
        st.metric(
            label="🛡️ Safety",
            value=f"{scores.get('safety', 'N/A')}/10"
        )
    
    with score_cols[4]:
        if has_kids:
            st.metric(
                label="🏫 Schools",
                value=f"{scores.get('schools', 'N/A')}/10"
            )
        else:
            st.metric(
                label="🏫 Schools",
                value="N/A",
                help="Add children to see school analysis"
            )
    
    st.divider()
    
    # Highlights and Concerns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("✅ Highlights")
        highlights = results.get("synthesis", {}).get("highlights", [])
        for h in highlights:
            st.markdown(f'<div class="highlight-box">✅ {h}</div>', unsafe_allow_html=True)
        if not highlights:
            st.info("Run analysis with more preferences for detailed highlights")
    
    with col2:
        st.subheader("⚠️ Things to Consider")
        concerns_list = results.get("synthesis", {}).get("concerns", [])
        for c in concerns_list:
            st.markdown(f'<div class="concern-box">⚠️ {c}</div>', unsafe_allow_html=True)
        if not concerns_list:
            st.info("No major concerns identified")
    
    st.divider()
    
    # Full narrative
    st.header("📋 Full Report")
    
    narrative = results.get("synthesis", {}).get("narrative", "No narrative generated")
    st.markdown(narrative)
    
    st.divider()
    
    # Detailed agent analyses (expandable)
    st.header("🔬 Detailed Analyses")
    
    agent_results = results.get("agents", {})
    
    # Commute
    with st.expander("🚗 Commute Analysis", expanded=False):
        commute = agent_results.get("commute", {})
        if commute.get("skipped"):
            st.info(f"Skipped: {commute.get('reason')}")
        else:
            st.subheader("Summary")
            summary = commute.get("summary", {})
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rush Hour", summary.get("rush_hour_driving", "N/A"))
            with col2:
                st.metric("Off-Peak", summary.get("off_peak_driving", "N/A"))
            with col3:
                st.metric("Transit", summary.get("transit", "N/A"))
            
            st.subheader("Full Analysis")
            st.markdown(commute.get("analysis", ""))
    
    # Lifestyle
    with st.expander("🏃 Lifestyle Analysis", expanded=False):
        lifestyle = agent_results.get("lifestyle", {})
        if lifestyle.get("skipped"):
            st.info(f"Skipped: {lifestyle.get('reason')}")
        else:
            st.subheader("Summary")
            summary = lifestyle.get("summary", {})
            st.metric("Lifestyle Fit Score", f"{summary.get('overall_score', 'N/A')}/10")
            
            st.subheader("Full Analysis")
            st.markdown(lifestyle.get("analysis", ""))
    
    # Development
    with st.expander("📰 Future Development", expanded=False):
        development = agent_results.get("development", {})
        st.markdown(development.get("analysis", ""))
    
    # Schools
    with st.expander("🏫 School Analysis", expanded=False):
        schools = agent_results.get("schools", {})
        if schools.get("skipped"):
            st.info(f"Skipped: {schools.get('reason')}")
        else:
            st.markdown(schools.get("analysis", ""))
    
    # Safety
    with st.expander("🛡️ Safety Analysis", expanded=False):
        safety = agent_results.get("safety", {})
        summary = safety.get("summary", {})
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Overall Safety", f"{summary.get('overall_score', 'N/A')}/10")
        with col2:
            st.metric("Daytime", f"{summary.get('daytime_score', 'N/A')}/10")
        with col3:
            st.metric("Nighttime", f"{summary.get('nighttime_score', 'N/A')}/10")
        
        st.markdown(safety.get("analysis", ""))

else:
    # Welcome screen
    st.markdown("""
    ## 👋 Welcome!
    
    This AI-powered tool analyzes any US neighborhood and tells you what daily life would 
    really be like living there — based on **your** specific situation.
    
    ### What We Analyze:
    
    | Agent | What It Does |
    |-------|--------------|
    | 🚗 **Commute Analyst** | Real rush-hour commute times (not just distance) |
    | 🏃 **Lifestyle Scout** | Finds your preferred amenities (gyms, temples, parks) |
    | 📰 **City Planner** | Tracks upcoming construction & zoning changes |
    | 🏫 **School Analyst** | School ratings with trend analysis |
    | 🛡️ **Safety Analyst** | Crime patterns by time of day |
    
    ### Get Started:
    
    1. **Enter an address** in the sidebar
    2. **Add your work location** for commute analysis
    3. **Tell us about your family** for school insights
    4. **Select your lifestyle priorities**
    5. **Click Analyze!**
    
    ---
    
    *Built with ❤️ using Streamlit, Gemini, and multiple specialist AI agents.*
    """)
    
    # Sample addresses
    st.subheader("🎯 Try These Sample Addresses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **Fremont, CA (Family-Friendly)**
        - 123 Example St, Fremont, CA 94539
        - Great schools, safe, near tech hubs
        """)
    
    with col2:
        st.info("""
        **Mountain View, CA (Tech Hub)**
        - 456 Castro St, Mountain View, CA 94041
        - Walkable downtown, near Google
        """)


# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.9rem;">
    Neighborhood Intelligence Agent v1.0 | Powered by Gemini & Specialist AI Agents
</div>
""", unsafe_allow_html=True)
