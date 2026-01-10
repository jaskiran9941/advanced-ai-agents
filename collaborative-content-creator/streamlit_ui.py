"""
Streamlit UI - Educational Dashboard for Multi-Agent Collaboration
Designed to be understood by anyone, using real-world analogies
"""

import streamlit as st
import json
import pandas as pd
from orchestrator import ContentCreationOrchestrator, PHASE_EXPLANATIONS, LEARNING_POINTS

st.set_page_config(
    page_title="AI Team Writing an Article",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for kid-friendly design - ALL TEXT IS BLACK for readability
st.markdown("""
<style>
    .big-title { font-size: 28px; font-weight: bold; margin-bottom: 10px; color: #000; }
    .analogy-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 15px;
        margin: 15px 0;
    }
    .memory-board {
        background-color: #fff9c4;
        border: 3px solid #f9a825;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
    }
    .memory-board, .memory-board * {
        color: #000 !important;
    }
    .sticky-note {
        background-color: #ffeb3b;
        padding: 10px;
        margin: 8px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
        display: inline-block;
        transform: rotate(-1deg);
    }
    .sticky-note, .sticky-note * {
        color: #000 !important;
    }
    .sticky-note-pink {
        background-color: #f8bbd9;
        padding: 10px;
        margin: 8px;
        border-radius: 5px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.2);
    }
    .sticky-note-pink, .sticky-note-pink * {
        color: #000 !important;
    }
    .agent-card {
        padding: 15px;
        border-radius: 15px;
        margin: 10px 0;
        text-align: center;
    }
    .agent-card, .agent-card * {
        color: #000 !important;
    }
    .researcher { background-color: #e3f2fd; border: 2px solid #1976d2; }
    .writer { background-color: #f3e5f5; border: 2px solid #7b1fa2; }
    .editor { background-color: #e8f5e9; border: 2px solid #388e3c; }
    .designer { background-color: #fff3e0; border: 2px solid #f57c00; }
    .phase-active { background-color: #e3f2fd; border: 3px solid #1976d2; }
    .phase-done { background-color: #e8f5e9; border: 3px solid #388e3c; }
    .phase-waiting { background-color: #f5f5f5; border: 2px dashed #999; }
</style>
""", unsafe_allow_html=True)

# ===========================================
# HEADER - WHAT IS THIS?
# ===========================================
st.markdown("# Writing an Article with an AI Team")

st.markdown("""
<div class="analogy-box">
<b>Imagine you're in a newsroom...</b><br><br>
You have a team of 4 people writing an article together. They can't talk to each other directly,
but they share a <b>bulletin board</b> where they pin notes for everyone to see.<br><br>
<b>The Bulletin Board = Shared Memory</b><br>
When one person learns something, they write it on a sticky note and pin it to the board.
Others can read those notes to do their job better.
</div>
""", unsafe_allow_html=True)

# ===========================================
# SIDEBAR - SIMPLE CONTROLS
# ===========================================
st.sidebar.markdown("## What should they write about?")

topic = st.sidebar.text_input(
    "Topic",
    value="AI agents",
    help="Pick any topic - like 'dogs', 'space', or 'pizza'"
)

st.sidebar.markdown("---")

# Reset button
if st.sidebar.button("Start Over", type="secondary", use_container_width=True):
    st.session_state.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### The Team")
st.sidebar.markdown("""
- **Researcher** - Finds facts
- **Writer** - Writes the article
- **Editor** - Checks for problems
- **Designer** - Makes sure facts are true
""")

# ===========================================
# INITIALIZE STATE
# ===========================================
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = None
if 'phase' not in st.session_state:
    st.session_state.phase = 'start'
if 'memory_items' not in st.session_state:
    st.session_state.memory_items = {'findings': [], 'feedback': []}
if 'scores' not in st.session_state:
    st.session_state.scores = []

# ===========================================
# MAIN CONTENT - TWO COLUMNS
# ===========================================
left_col, right_col = st.columns([3, 2])

# ===========================================
# LEFT COLUMN - THE WORKFLOW
# ===========================================
with left_col:
    st.markdown("## What's Happening")

    # MEET THE TEAM
    if st.session_state.phase == 'start':
        st.markdown("### Meet the Team")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            <div class="agent-card researcher">
                <h3>Researcher</h3>
                <p><b>Job:</b> Go to the library, find facts</p>
                <p><b>Writes to board:</b> Facts they found</p>
                <p><i>Like a librarian finding books</i></p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="agent-card editor">
                <h3>Editor</h3>
                <p><b>Job:</b> Read the article, find problems</p>
                <p><b>Writes to board:</b> Suggestions to fix</p>
                <p><i>Like a teacher grading homework</i></p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown("""
            <div class="agent-card writer">
                <h3>Writer</h3>
                <p><b>Job:</b> Write the article using facts</p>
                <p><b>Reads from board:</b> Facts to include</p>
                <p><i>Like an author writing a story</i></p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="agent-card designer">
                <h3>Fact Checker</h3>
                <p><b>Job:</b> Make sure nothing is made up</p>
                <p><b>Reads from board:</b> Original facts to compare</p>
                <p><i>Like a detective checking clues</i></p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown(f"### Ready to write about: **{topic}**")

        if st.button("Start Writing!", type="primary", use_container_width=True):
            st.session_state.orchestrator = ContentCreationOrchestrator()
            st.session_state.phase = 'research'
            st.rerun()

    # PHASE 1: RESEARCH
    elif st.session_state.phase == 'research':
        st.markdown("### Step 1: Researcher Finds Facts")

        st.markdown("""
        <div class="agent-card researcher">
            <h3>Researcher is working...</h3>
            <p>Going to the library to find facts about <b>{}</b></p>
        </div>
        """.format(topic), unsafe_allow_html=True)

        st.info("""
        **What's happening:**
        1. First, check if we already have facts (READ from board)
        2. If not, search for new facts
        3. Write each fact on a sticky note (WRITE to board)
        """)

        if st.button("Find Facts!", type="primary", use_container_width=True):
            result = st.session_state.orchestrator.run_research_phase(topic)

            # Store findings in simple format
            for finding in st.session_state.orchestrator.memory.findings:
                st.session_state.memory_items['findings'].append({
                    'fact': finding.content,
                    'source': finding.source,
                    'trust': f"{finding.credibility_score:.0%}"
                })

            st.session_state.phase = 'research_done'
            st.rerun()

    elif st.session_state.phase == 'research_done':
        st.markdown("### Step 1 Complete!")
        st.success(f"Researcher found {len(st.session_state.memory_items['findings'])} facts!")

        st.markdown("**Facts found:**")
        for i, item in enumerate(st.session_state.memory_items['findings']):
            st.markdown(f"""
            <div class="sticky-note">
                <b>Fact {i+1}:</b> {item['fact'][:80]}...<br>
                <small>Source: {item['source']} | Trust: {item['trust']}</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Next: Writer will use these facts")

        if st.button("Write the Article!", type="primary", use_container_width=True):
            st.session_state.phase = 'writing'
            st.rerun()

    # PHASE 2: WRITING
    elif st.session_state.phase == 'writing':
        st.markdown("### Step 2: Writer Creates Article")

        st.markdown("""
        <div class="agent-card writer">
            <h3>Writer is working...</h3>
            <p>Reading facts from the board and writing an article</p>
        </div>
        """, unsafe_allow_html=True)

        st.info("""
        **What's happening:**
        1. Read all the facts from the board (READ)
        2. Turn those facts into a nice article
        3. (Writer doesn't write anything to the board)
        """)

        if st.button("Write It!", type="primary", use_container_width=True):
            result = st.session_state.orchestrator.run_writing_phase(topic)
            st.session_state.draft = result.get('draft', '')
            st.session_state.phase = 'writing_done'
            st.rerun()

    elif st.session_state.phase == 'writing_done':
        st.markdown("### Step 2 Complete!")
        st.success("Writer finished the first draft!")

        with st.expander("Read the Draft", expanded=True):
            st.markdown(st.session_state.draft)

        st.markdown("---")
        st.markdown("### Next: Editor & Fact Checker will review")

        if st.button("Review the Article!", type="primary", use_container_width=True):
            st.session_state.phase = 'review'
            st.rerun()

    # PHASE 3: REVIEW
    elif st.session_state.phase == 'review':
        st.markdown("### Step 3: Editor & Fact Checker Review")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div class="agent-card editor">
                <h3>Editor checking...</h3>
                <p>Looking for problems</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div class="agent-card designer">
                <h3>Fact Checker checking...</h3>
                <p>Comparing to original facts</p>
            </div>
            """, unsafe_allow_html=True)

        st.info("""
        **What's happening:**
        1. Editor reads past suggestions (READ)
        2. Editor writes new suggestions (WRITE)
        3. Fact Checker reads original facts (READ)
        4. Both give a score
        5. If scores are good enough, we're done!
        """)

        if st.button("Check It!", type="primary", use_container_width=True):
            result = st.session_state.orchestrator.run_review_phase(topic)

            # Store feedback
            for fb in result.get('feedback', []):
                st.session_state.memory_items['feedback'].append({
                    'suggestion': fb['comment'],
                    'category': fb['category'],
                    'importance': f"{fb['severity']:.0%}"
                })

            st.session_state.scores.append({
                'editor': result.get('approval_score', 0),
                'fact_checker': result.get('validation_score', 0),
                'combined': result.get('combined_score', 0)
            })

            st.session_state.phase = 'done'
            st.rerun()

    # DONE
    elif st.session_state.phase == 'done':
        st.markdown("### All Done!")
        st.balloons()

        scores = st.session_state.scores[-1]

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Editor Score", f"{scores['editor']:.0%}")
        with col2:
            st.metric("Fact Checker Score", f"{scores['fact_checker']:.0%}")
        with col3:
            st.metric("Final Score", f"{scores['combined']:.0%}")

        st.markdown("---")
        st.markdown("### The Final Article")
        st.markdown(st.session_state.orchestrator.current_draft)

        st.download_button(
            "Download Article",
            st.session_state.orchestrator.current_draft,
            file_name=f"article_about_{topic.replace(' ', '_')}.txt"
        )

# ===========================================
# RIGHT COLUMN - THE BULLETIN BOARD (MEMORY)
# ===========================================
with right_col:
    st.markdown("## The Bulletin Board")
    st.markdown("*This is the shared memory - everyone can see it!*")

    # Visual bulletin board
    st.markdown("""
    <div class="memory-board">
        <h3 style="text-align: center; margin-top: 0;">TEAM BULLETIN BOARD</h3>
        <p style="text-align: center; color: #666;">Pin notes here for others to read</p>
    </div>
    """, unsafe_allow_html=True)

    # FACTS SECTION
    st.markdown("### Facts Found")
    if st.session_state.memory_items['findings']:
        for i, item in enumerate(st.session_state.memory_items['findings']):
            st.markdown(f"""
            <div class="sticky-note">
                <b>#{i+1}</b> {item['fact'][:60]}...<br>
                <small>From: {item['source']}</small><br>
                <small>Trust level: {item['trust']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("*No facts yet - Researcher hasn't started*")

    st.markdown("---")

    # FEEDBACK SECTION
    st.markdown("### Editor's Suggestions")
    if st.session_state.memory_items['feedback']:
        for i, item in enumerate(st.session_state.memory_items['feedback']):
            st.markdown(f"""
            <div class="sticky-note-pink">
                <b>Suggestion:</b> {item['suggestion']}<br>
                <small>Type: {item['category']} | Importance: {item['importance']}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("*No suggestions yet - Editor hasn't reviewed*")

    st.markdown("---")

    # SIMPLE STATS
    st.markdown("### Board Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Facts Pinned", len(st.session_state.memory_items['findings']))
    with col2:
        st.metric("Suggestions Pinned", len(st.session_state.memory_items['feedback']))

# ===========================================
# BOTTOM - HOW IT WORKS
# ===========================================
st.markdown("---")
st.markdown("## How Does This Work?")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    ### What is "Memory"?

    Think of it like a **bulletin board** in an office.

    - Anyone can **pin** notes to it
    - Anyone can **read** notes from it
    - Notes stay there until removed

    In this app, the board stores:
    - **Facts** (yellow sticky notes)
    - **Suggestions** (pink sticky notes)
    """)

with col2:
    st.markdown("""
    ### Why Do Agents Need Memory?

    Imagine if the team couldn't share notes:

    - Writer wouldn't know what facts to use
    - Editor couldn't remember past problems
    - Everyone would duplicate work

    **Memory lets agents collaborate** without talking directly!
    """)

with col3:
    st.markdown("""
    ### The Key Concept

    **READ** = Look at the board

    **WRITE** = Pin something to the board

    Each agent READs what they need, then WRITEs what they learned.

    This is how AI teams work together!
    """)

# Footer
st.markdown("---")
st.caption("Multi-Agent Memory Learning Tool | Understanding how AI teams collaborate through shared memory")
