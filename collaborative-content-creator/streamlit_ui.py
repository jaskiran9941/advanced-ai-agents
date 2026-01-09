"""
Streamlit UI for Real-Time Collaborative Content Creator
Visualize multi-agent collaboration, memory state, and workflow
"""

import streamlit as st
import json
from datetime import datetime
import pandas as pd
from orchestrator import ContentCreationOrchestrator
from memory_manager import SharedMemory

st.set_page_config(
      page_title="🤝 Multi-Agent Content Creator",
      layout="wide",
      initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button {
            font-size: 16px;
                    padding: 10px 20px;
                        }
                            .metric-card {
                                    padding: 20px;
                                            border-radius: 10px;
                                                    background-color: #f0f2f6;
                                                            margin: 10px 0;
                                                                }
                                                                    .agent-box {
                                                                            padding: 15px;
                                                                                    border-radius: 8px;
                                                                                            margin: 10px 0;
                                                                                                    border-left: 4px solid;
                                                                                                        }
                                                                                                            .agent-researcher {
                                                                                                                    background-color: #e3f2fd;
                                                                                                                            border-left-color: #1976d2;
                                                                                                                                }
                                                                                                                                    .agent-writer {
                                                                                                                                            background-color: #f3e5f5;
                                                                                                                                                    border-left-color: #7b1fa2;
                                                                                                                                                        }
                                                                                                                                                            .agent-editor {
                                                                                                                                                                    background-color: #e8f5e9;
                                                                                                                                                                            border-left-color: #388e3c;
                                                                                                                                                                                }
                                                                                                                                                                                    .agent-designer {
                                                                                                                                                                                            background-color: #fff3e0;
                                                                                                                                                                                                    border-left-color: #f57c00;
                                                                                                                                                                                                        }
                                                                                                                                                                                                        </style>
                                                                                                                                                                                                        """, unsafe_allow_html=True)

# Page title
st.title("🤝 Real-Time Collaborative Content Creator")
st.subheader("Multi-Agent System for Content Creation with Shared Memory")

# Initialize session state
if 'orchestrator' not in st.session_state:
      st.session_state.orchestrator = None
  if 'result' not in st.session_state:
        st.session_state.result = None
    if 'workflow_started' not in st.session_state:
          st.session_state.workflow_started = False

# Sidebar: Configuration
st.sidebar.markdown("## ⚙️ Configuration")

topic = st.sidebar.text_input(
      "📝 Content Topic",
      value="AI agents",
      help="The topic the team will create content about"
)

max_revisions = st.sidebar.slider(
      "🔄 Max Revision Rounds",
      min_value=1,
      max_value=5,
      value=2,
      help="Maximum number of review and revision cycles"
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📚 System Info")
st.sidebar.info("""
**Learning Points:**
- **Memory (#5-16)**: Shared findings, feedback, history
- **Agents (#17-26)**: 4 specialized agents
- **Orchestration (#27-36)**: Workflow coordination
""")

# Main content area - Tabs
tab1, tab2, tab3, tab4 = st.tabs(
      ["🎬 Workflow", "🧠 Memory Explorer", "👥 Agent Actions", "📊 Results"]
)

# TAB 1: WORKFLOW
with tab1:
      st.markdown("### Workflow Execution")

    col1, col2 = st.columns([2, 1])

    with col1:
              st.markdown(f"""
                      **Topic:** `{topic}`  
                              **Max Revisions:** {max_revisions}
                                      """)

    with col2:
              run_button = st.button(
                            "▶️ Start Content Creation",
                            use_container_width=True,
                            key="run_button"
              )

    if run_button:
              st.session_state.workflow_started = True
              st.session_state.orchestrator = ContentCreationOrchestrator()

        with st.spinner("🔄 Creating content..."):
                      st.session_state.result = st.session_state.orchestrator.create_content(
                                        topic=topic,
                                        max_revisions=max_revisions
                      )

        st.success("✅ Content creation complete!")

    # Display workflow history if available
    if st.session_state.result:
              result = st.session_state.result

        st.markdown("### Workflow Timeline")

        # Create timeline visualization
        workflow_history = result.get('workflow_history', [])

        if workflow_history:
                      # Create a dataframe for better visualization
                      timeline_data = []
                      for i, action in enumerate(workflow_history):
                                        timeline_data.append({
                                                              "Step": i + 1,
                                                              "Round": action.get('round', 0),
                                                              "Action": action.get('action_type', '').replace('_', ' ').title(),
                                                              "Agent": action.get('agent', 'Unknown'),
                                                              "Status": action.get('status', 'Unknown')
                                        })

                      df_timeline = pd.DataFrame(timeline_data)
                      st.dataframe(df_timeline, use_container_width=True, hide_index=True)

        # Phase breakdown
        st.markdown("### Execution Summary")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
                      st.metric("Total Actions", len(workflow_history))
                  with col2:
                                st.metric("Revision Rounds", result.get('revision_rounds', 0))
                            with col3:
                                          quality = result.get('overall_quality_score', 0)
                                          st.metric("Quality Score", f"{quality:.2%}")
                                      with col4:
                                                    st.metric("Status", result.get('status', 'Unknown').title())

# TAB 2: MEMORY EXPLORER
with tab2:
      st.markdown("### 🧠 Shared Memory State")

    if st.session_state.orchestrator and st.session_state.result:
              memory = st.session_state.orchestrator.memory
              summary = memory.get_memory_summary()

        # Memory overview metrics
              col1, col2, col3, col4 = st.columns(4)

        with col1:
                      st.metric("📊 Total Findings", summary['total_findings'])
                  with col2:
                                st.metric("✅ Credible Findings", summary['credible_findings'])
                            with col3:
                                          st.metric("⚠️ Disputed Findings", summary['disputed_findings'])
                                      with col4:
                                                    st.metric("📝 Feedback Items", summary['editorial_feedback_count'])

        st.markdown("---")

        # Findings explorer
        st.subheader("📌 Research Findings")
        findings = memory.get_findings(min_credibility=0.0)

        if findings:
                      for i, finding in enumerate(findings):
                                        with st.expander(
                                                              f"Finding {i+1}: {finding.content[:50]}...",
                                                              expanded=(i == 0)
                                        ):
                                                              col1, col2 = st.columns(2)

                    with col1:
                                              st.markdown(f"**Content:** {finding.content}")
                                              st.markdown(f"**Source:** {finding.source}")
                                              st.markdown(f"**Extracted by:** {finding.extracted_by}")

                    with col2:
                                              credibility_pct = finding.credibility_score * 100
                                              st.metric("Credibility Score", f"{credibility_pct:.1f}%")

                        if finding.disputes:
                                                      st.warning(f"Disputed by: {', '.join(finding.disputes)}")
else:
                              st.success("No disputes")
else:
            st.info("No findings in memory yet. Run the workflow first!")

        st.markdown("---")

        # Editorial feedback
        st.subheader("📝 Editorial Feedback History")
        feedback_items = memory.editorial_history

        if feedback_items:
                      for i, fb in enumerate(feedback_items):
                                        with st.expander(f"Feedback {i+1}: {fb.category.title()}"):
                                                              col1, col2 = st.columns([2, 1])

                    with col1:
                                              st.markdown(f"**Section:** {fb.content_section}")
                                              st.markdown(f"**Feedback:** {fb.feedback}")
                                              st.markdown(f"**Category:** {fb.category}")

                    with col2:
                                              severity_color = "🔴" if fb.severity > 0.7 else "🟡" if fb.severity > 0.4 else "🟢"
                                              st.metric(f"{severity_color} Severity", f"{fb.severity:.1%}")

                        if fb.was_addressed:
                                                      st.success("✅ Addressed")
else:
                              st.warning("⏳ Unresolved")
else:
            st.info("No feedback recorded yet.")

        st.markdown("---")

        # Raw memory JSON
        st.subheader("📋 Raw Memory Export")
        if st.checkbox("Show JSON Export"):
                      memory_json = memory.export_memory()
                      st.json(json.loads(memory_json))
else:
          st.info("💡 Run the workflow first to see memory state!")

# TAB 3: AGENT ACTIONS
with tab3:
      st.markdown("### 👥 Individual Agent Contributions")

    if st.session_state.orchestrator and st.session_state.result:
              orchestrator = st.session_state.orchestrator
              result = st.session_state.result

        # Create tabs for each agent
              agent_col1, agent_col2, agent_col3, agent_col4 = st.columns(4)

        with agent_col1:
                      if st.checkbox("🔬 Researcher", value=True, key="show_researcher"):
                                        st.markdown("""
                                                        <div class="agent-box agent-researcher">
                                                                        <b>🔬 Researcher Agent</b><br>
                                                                                        <small>Finds reliable sources and extracts information</small>
                                                                                                        </div>
                                                                                                                        """, unsafe_allow_html=True)
                                        st.markdown(f"**Actions taken:** {orchestrator.researcher.action_count}")
                                        st.markdown("**Responsibilities:**")
                                        st.markdown("- Search for credible sources")
                                        st.markdown("- Score source credibility")
                                        st.markdown("- Avoid duplicate research")

                  with agent_col2:
                                if st.checkbox("✍️ Writer", value=True, key="show_writer"):
                                                  st.markdown("""
                                                                  <div class="agent-box agent-writer">
                                                                                  <b>✍️ Writer Agent</b><br>
                                                                                                  <small>Creates engaging content from research</small>
                                                                                                                  </div>
                                                                                                                                  """, unsafe_allow_html=True)
                                                  st.markdown(f"**Actions taken:** {orchestrator.writer.action_count}")
                                                  st.markdown("**Responsibilities:**")
                                                  st.markdown("- Create compelling drafts")
                                                  st.markdown("- Cite sources properly")
                                                  st.markdown("- Maintain tone & style")

                            with agent_col3:
                                          if st.checkbox("✏️ Editor", value=True, key="show_editor"):
                                                            st.markdown("""
                                                                            <div class="agent-box agent-editor">
                                                                                            <b>✏️ Editor Agent</b><br>
                                                                                                            <small>Reviews for accuracy and clarity</small>
                                                                                                                            </div>
                                                                                                                                            """, unsafe_allow_html=True)
                                                            st.markdown(f"**Actions taken:** {orchestrator.editor.action_count}")
                                                            st.markdown("**Responsibilities:**")
                                                            st.markdown("- Check accuracy")
                                                            st.markdown("- Ensure clarity")
                                                            st.markdown("- Track feedback history")

                                      with agent_col4:
                                                    if st.checkbox("🎨 Designer", value=True, key="show_designer"):
                                                                      st.markdown("""
                                                                                      <div class="agent-box agent-designer">
                                                                                                      <b>🎨 Designer Agent</b><br>
                                                                                                                      <small>Validates claims and suggests visuals</small>
                                                                                                                                      </div>
                                                                                                                                                      """, unsafe_allow_html=True)
                                                                      st.markdown(f"**Actions taken:** {orchestrator.designer.action_count}")
                                                                      st.markdown("**Responsibilities:**")
                                                                      st.markdown("- Fact-check claims")
                                                                      st.markdown("- Suggest visuals")
                                                                      st.markdown("- Validate against findings")

                                                st.markdown("---")

        # Agent workflow actions
        st.subheader("🔄 Agent Action Sequence")
        workflow = result.get('workflow_history', [])

        if workflow:
                      # Group by agent
                      agent_workflow = {}
                      for action in workflow:
                                        agent = action.get('agent', 'Unknown')
                                        if agent not in agent_workflow:
                                                              agent_workflow[agent] = []
                                                          agent_workflow[agent].append(action)

                      for agent, actions in agent_workflow.items():
                                        with st.expander(f"{agent} ({len(actions)} actions)"):
                                                              for i, action in enumerate(actions):
                                                                                        st.markdown(f"""
                                                                                                                **Action {i+1}:** {action.get('action_type', '').replace('_', ' ').title()}  
                                                                                                                                        Status: `{action.get('status', 'Unknown')}`
                                                                                                                                                                """)
        else:
        st.info("💡 Run the workflow first to see agent actions!")

          # TAB 4: RESULTS
          with tab4:
              st.markdown("### 📊 Final Results & Content")

                if st.session_state.result:
                          result = st.session_state.result

        # Status
        col1, col2, col3 = st.columns(3)
        with col1:
                      st.metric("Status", result.get('status', 'Unknown').title())
                  with col2:
                                st.metric("Topic", result.get('topic', 'N/A'))
                            with col3:
                                          st.metric("Quality Score", f"{result.get('overall_quality_score', 0):.2%}")

        st.markdown("---")

        # Final content
        st.subheader("📄 Generated Content")
        final_draft = result.get('final_draft', '')

        if final_draft:
                      st.markdown(final_draft)

            # Download button
                      st.download_button(
                          label="📥 Download Content as Text",
                          data=final_draft,
                          file_name=f"content_{result.get('topic', 'output')}.txt",
                          mime="text/plain"
                      )
else:
            st.warning("No content generated")

        st.markdown("---")

        # Memory summary
        st.subheader("🧠 Memory Summary")
        memory_summary = result.get('memory_summary', {})

        col1, col2, col3 = st.columns(3)
        with col1:
                      st.metric(
                                        "Total Findings",
                                        memory_summary.get('total_findings', 0)
                      )
                  with col2:
                                st.metric(
                                                  "Credible Findings",
                                                  memory_summary.get('credible_findings', 0)
                                )
                            with col3:
                                          st.metric(
                                                            "Feedback Items",
                                                            memory_summary.get('editorial_feedback_count', 0)
                                          )

        # Agent contributions
        agents_involved = memory_summary.get('agents_involved', [])
        if agents_involved:
                      st.markdown("**Agents Involved:**")
                      st.markdown(", ".join(agents_involved))
        else:
        st.info("💡 Run the workflow to see results!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; margin-top: 20px;'>
<small>🤖 Real-Time Collaborative Content Creator | Multi-Agent Learning System</small>
</div>
""", unsafe_allow_html=True)
