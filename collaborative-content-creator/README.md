# Real-Time Collaborative Content Creator

## A Multi-Agent System for Learning Agent Memory & Collaboration

This project demonstrates how multiple AI agents can collaborate on a complex task using **shared memory**, **consensus mechanisms**, and **role-based reasoning**. Perfect for learning about agent memory systems and multi-agent orchestration.

---

## 🎯 Core Learning Objectives

This project teaches you:

1. **Agent Memory Architecture** (#5-16) - How agents share and manage information
2. 2. **Agent Design Patterns** (#17-26) - Building specialized agents with specific roles
   3. 3. **Orchestration & Consensus** (#27-36) - Coordinating multiple agents toward a goal
    

                                                                               ## 🏗️ System Architecture

                                                                               ```
                                                                               ┌─────────────────────────────────────────────────────┐
                                                                               │        ORCHESTRATOR (The Conductor)                 │
                                                                               │  - Manages workflow sequence                        │
                                                                               │  - Handles consensus                               │
                                                                               │  - Tracks revision rounds                          │
                                                                               └─────────┬──────────────────────────────────────────┘
                                                                                         │
                                                                                         ├─→ RESEARCHER AGENT ──┐
                                                                                         │                       │
                                                                                         ├─→ WRITER AGENT ───────┤─→ SHARED MEMORY
                                                                                         │                       │    (All findings,
                                                                                         ├─→ EDITOR AGENT ───────┤     feedback,
                                                                                         │                       │     history)
                                                                                         └─→ DESIGNER AGENT ─────┘

                                                                               Each agent:
                                                                               - Has a specific role
                                                                               - Can READ from shared memory
                                                                               - Can WRITE to shared memory
                                                                               - Doesn't communicate directly with other agents
                                                                               - Only communicates through orchestrator
                                                                               ```

                                                                               ---

                                                                               ## 🔄 The Workflow

                                                                               ### Phase 1: RESEARCH

                                                                               ```python
                                                                               researcher.act({"topic": "AI agents"})
                                                                               # Output: Findings added to shared memory
                                                                               # Memory updated with credibility scores
                                                                               ```

                                                                               ### Phase 2: WRITING

                                                                               ```python
                                                                               writer.act({
                                                                                   "topic": "AI agents",
                                                                                   "style": "professional"
                                                                               })
                                                                               # Reads credible findings from memory
                                                                               # Creates draft using research
                                                                               ```

                                                                               ### Phase 3: REVIEW LOOP (Iterative)

                                                                               ```
                                                                               Round 1:
                                                                                 editor.act({"draft": draft})     # Reviews draft
                                                                                 designer.act({"draft": draft})   # Validates claims
                                                                                 combined_score = (approval + validation) / 2
                                                                                 If combined_score >= 0.75: DONE ✓
                                                                                 Else: Revise and loop
                                                                               ```

                                                                               ---

                                                                               ## 💾 Memory Deep Dive

                                                                               The **SharedMemory** class is where collaboration happens:

                                                                               ### What Gets Stored?

                                                                               ```
                                                                               Findings:
                                                                                 - content: "Multi-agent systems outperform single agents"
                                                                                 - source: "MIT Tech Review"
                                                                                 - credibility_score: 0.85
                                                                                 - extracted_by: "Researcher"
                                                                                 - disputes: ["Editor"]  # If contested
                                                                                 - timestamp: 2024-01-08

                                                                               EditorialFeedback:
                                                                                 - content_section: "Introduction"
                                                                                 - feedback: "Too vague, needs specific examples"
                                                                                 - category: "clarity"
                                                                                 - severity: 0.7
                                                                                 - was_addressed: True
                                                                               ```

                                                                               ### Memory Operations

                                                                               ```python
                                                                               # Write
                                                                               memory.add_finding(finding)
                                                                               memory.add_feedback(feedback)

                                                                               # Read
                                                                               credible = memory.get_findings(min_credibility=0.7)
                                                                               past_feedback = memory.get_feedback_by_category("accuracy")

                                                                               # Update
                                                                               memory.dispute_finding(id, agent, reason)
                                                                               memory.confirm_finding(id, agent)
                                                                               memory.mark_feedback_resolved(id)

                                                                               # Query
                                                                               summary = memory.get_memory_summary()
                                                                               json_export = memory.export_memory()
                                                                               ```

                                                                               ---

                                                                               ## 🚀 Running the System

                                                                               ### Setup

                                                                               ```bash
                                                                               cd collaborative-content-creator
                                                                               pip install -r requirements.txt
                                                                               ```

                                                                               ### Run with Shell Script (Easiest)

                                                                               ```bash
                                                                               chmod +x run_streamlit.sh
                                                                               ./run_streamlit.sh
                                                                               ```

                                                                               ### Run Directly

                                                                               ```bash
                                                                               streamlit run streamlit_ui.py
                                                                               ```

                                                                               ### What You'll See

                                                                               ```
                                                                               ============================================================
                                                                               Starting content creation for topic: AI agents
                                                                               ============================================================

                                                                               PHASE 1: RESEARCH
                                                                               ✓ Researcher action: success
                                                                                 Findings added: 2

                                                                               PHASE 2: WRITING
                                                                               ✓ Writer created draft (800 chars)

                                                                               PHASE 3: REVIEW & REVISION LOOP
                                                                               Max revisions: 2

                                                                               --- Revision Round 1 ---
                                                                               ✓ Editor approval score: 0.72
                                                                               ✓ Designer validation score: 0.85
                                                                               ✓ Combined quality score: 0.79
                                                                               ✓ Content meets quality threshold!

                                                                               ============================================================
                                                                               Content creation complete!
                                                                               ============================================================
                                                                               ```

                                                                               ---

                                                                               ## 🔑 Key Insights

                                                                               ### 1. Shared Memory is Central

                                                                               Without shared memory, agents can't learn from each other or avoid duplication. This is why it's the heart of the system.

                                                                               ### 2. Credibility Matters

                                                                               Not all sources are equal. By tracking credibility scores, agents can distinguish between reliable and unreliable information.

                                                                               ### 3. Consensus is Hard

                                                                               When Agent A disputes Agent B's finding, we need a resolution strategy. This project shows multiple approaches:

                                                                               - Averaging scores
                                                                               - - Majority vote
                                                                                 - - Credibility-weighted voting
                                                                                  
                                                                                   - ### 4. Iteration Beats Perfection
                                                                                  
                                                                                   - Rather than trying to get everything right in one pass, agents iterate with feedback. This mirrors real human workflows.
                                                                                  
                                                                                   - ### 5. Transparency Enables Debugging
                                                                                  
                                                                                   - By logging every action and exporting memory, we can understand what went wrong and why.
                                                                                  
                                                                                   - ---

                                                                                   ## 💡 Variations to Explore

                                                                                   Once you understand the base system:

                                                                                   1. **Add LLM Integration** - Replace simulated agents with Claude API calls
                                                                                   2. 2. **Implement Vector Similarity** - Use embeddings for semantic duplicate detection
                                                                                      3. 3. **Add Consensus Voting** - Multiple agents vote on findings
                                                                                         4. 4. **Persistent Storage** - Save memory to database between runs
                                                                                            5. 5. **Async Agents** - Run agents in parallel instead of sequentially
                                                                                               6. 6. **Add Rewards** - Track which agents contribute best findings
                                                                                                  7. 7. **Multi-Turn Conversations** - Agents debate before consensus
                                                                                                    
                                                                                                     8. ---
                                                                                                    
                                                                                                     9. ## 📊 Understanding the Output
                                                                                                    
                                                                                                     10. After running, you'll see:
                                                                                                    
                                                                                                     11. ### Workflow Summary
                                                                                                    
                                                                                                     12. ```
                                                                                                         WORKFLOW SUMMARY
                                                                                                         ============================================================
                                                                                                         Total actions: 7
                                                                                                         Revision rounds: 1

                                                                                                         Agent contributions:
                                                                                                           Designer: 1 actions
                                                                                                           Editor: 1 actions
                                                                                                           Researcher: 1 actions
                                                                                                           Writer: 1 actions

                                                                                                         Memory state:
                                                                                                           Total findings: 2
                                                                                                           Credible findings: 2
                                                                                                           Editorial feedback: 1
                                                                                                         ```
                                                                                                         
                                                                                                         ### Memory Export
                                                                                                         
                                                                                                         ```json
                                                                                                         {
                                                                                                           "findings": [
                                                                                                             {
                                                                                                               "content": "AI agents are systems that...",
                                                                                                               "source": "OpenAI Research Paper 2024",
                                                                                                               "credibility": 0.95,
                                                                                                               "extracted_by": "Researcher"
                                                                                                             }
                                                                                                           ],
                                                                                                           "editorial_feedback": [...],
                                                                                                           "summary": {...}
                                                                                                         }
                                                                                                         ```
                                                                                                         
                                                                                                         ---
                                                                                                         
                                                                                                         ## 🎓 Next Steps
                                                                                                         
                                                                                                         1. **Run the code** and understand the workflow
                                                                                                         2. 2. **Modify agent behaviors** - Change how agents act
                                                                                                            3. 3. **Add new agents** - Create specialized agents for new tasks
                                                                                                               4. 4. **Integrate real APIs** - Connect to actual research databases
                                                                                                                  5. 5. **Study the memory** - Understand how agents learn from each other
                                                                                                                    
                                                                                                                     6. ---
                                                                                                                    
                                                                                                                     7. ## 📖 Further Reading
                                                                                                                    
                                                                                                                     8. - Agent Memory: ReAct, CoT with memory, conversational memory
                                                                                                                        - - Multi-Agent Systems: Consensus, communication protocols
                                                                                                                          - - Orchestration: LangGraph, CrewAI, Autogen
                                                                                                                            - - Agent Evaluation: How to measure agent collaboration effectiveness
                                                                                                                             
                                                                                                                              - ---
                                                                                                                              
                                                                                                                              ## 🔗 Files
                                                                                                                              
                                                                                                                              - `config.py` - Configuration and learning points #1-4
                                                                                                                              - - `memory_manager.py` - Shared memory implementation, learning points #5-16
                                                                                                                                - - `agents.py` - Individual agent definitions, learning points #17-26
                                                                                                                                  - - `orchestrator.py` - Coordination and workflow, learning points #27-36
                                                                                                                                    - - `streamlit_ui.py` - Interactive web UI
                                                                                                                                      - - `requirements.txt` - Dependencies
                                                                                                                                        - - `run_streamlit.sh` - Quick start script
                                                                                                                                          - - `README.md` - This file
                                                                                                                                           
                                                                                                                                            - ---
                                                                                                                                            
                                                                                                                                            Built with ❤️ for learning multi-agent systems.
