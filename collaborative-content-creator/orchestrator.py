"""
Orchestrator: The Conductor of the Agent Team

LEARNING POINT #27: Orchestration Patterns
This is the "conductor" that coordinates agents. Key responsibilities:
1. Sequencing: Decide which agent acts when
2. Context Passing: Share information between agents
3. Consensus: Resolve disagreements between agents
4. Iteration: Manage revision loops

LEARNING POINT #28: State Management
The orchestrator maintains the state of the entire collaboration:
- Current draft version
- Which agents have acted
- Revision round number
- Overall quality score

This is critical for handling failures, resuming workflows, and debugging.
"""

from typing import Dict, List, Any, Optional
from agents import Agent, ResearcherAgent, WriterAgent, EditorAgent, DesignerAgent
from memory_manager import SharedMemory


class ContentCreationOrchestrator:
      """
          LEARNING POINT #29: The Orchestrator Pattern

                  Rather than agents operating independently, we have a central coordinator
                      that decides:
                          1. Which agent acts next
                              2. What context to give them
                                  3. How to handle conflicts
                                      4. When to stop iterating

                                              This is similar to human editorial workflows.
                                                  """

    def __init__(self):
              self.memory = SharedMemory()

        # Initialize agents with shared memory
              self.researcher = ResearcherAgent("Researcher", self.memory)
              self.writer = WriterAgent("Writer", self.memory)
              self.editor = EditorAgent("Editor", self.memory)
              self.designer = DesignerAgent("Designer", self.memory)

        # Maintain workflow state
              self.current_draft: str = ""
              self.revision_round = 0
              self.overall_quality_score = 0.0
              self.workflow_history: List[Dict[str, Any]] = []

    def create_content(self, topic: str, max_revisions: int = 2) -> Dict[str, Any]:
              """
                      LEARNING POINT #30: The Main Workflow Loop

                                      This orchestrates the entire content creation process:
                                              1. Research Phase: Researcher finds sources
                                                      2. Writing Phase: Writer creates draft
                                                              3. Review Loop: Editor reviews, Designer validates, Writer revises
                                                                      4. Finalization: Return final content

                                                                                      The key insight: It's not a simple pipeline. It's a loop
                                                                                              with feedback and iteration.
                                                                                                      """
              print(f"\n{'='*60}")
              print(f"Starting content creation for topic: {topic}")
              print(f"{'='*60}\n")

        # Phase 1: Research
              print("PHASE 1: RESEARCH")
              research_result = self.researcher.act({"topic": topic})
              self._log_action("research", research_result)
              print(f"✓ Researcher action: {research_result['status']}")
              print(f"  Findings added: {research_result.get('findings_added', 0)}\n")

        # Phase 2: Initial Writing
              print("PHASE 2: WRITING")
              write_result = self.writer.act({
                  "topic": topic,
                  "style": "professional"
              })
              self._log_action("writing", write_result)

        if write_result['status'] == 'insufficient_research':
                      return {
                                        "status": "failed",
                                        "reason": "Not enough research to write from",
                                        "workflow_history": self.workflow_history
                      }

        self.current_draft = write_result.get('draft', '')
        print(f"✓ Writer created draft ({len(self.current_draft)} chars)\n")

        # Phase 3: Review Loop
        print("PHASE 3: REVIEW & REVISION LOOP")
        print(f"Max revisions: {max_revisions}\n")

        for revision_num in range(max_revisions):
                      self.revision_round = revision_num + 1
                      print(f"\n--- Revision Round {self.revision_round} ---")

            # Step 1: Editor reviews
                      editor_result = self.editor.act({"draft": self.current_draft})
                      self._log_action("editing", editor_result)

            approval_score = editor_result.get('approval_score', 0.0)
            print(f"✓ Editor approval score: {approval_score:.2f}")

            if approval_score >= 0.7:
                              print("✓ Draft approved by editor!")
                              break

            # Step 2: Designer validates
            designer_result = self.designer.act({"draft": self.current_draft})
            self._log_action("design_validation", designer_result)

            validation_score = designer_result.get('validation_score', 0.0)
            print(f"✓ Designer validation score: {validation_score:.2f}")
            print(f"  Visual suggestions: {len(designer_result.get('visual_suggestions', []))}")

            # Step 3: Determine consensus
            # LEARNING POINT #31: Consensus Mechanism
            # We combine editor and designer feedback
            combined_score = (approval_score + validation_score) / 2
            print(f"✓ Combined quality score: {combined_score:.2f}")

            if combined_score >= 0.75:
                              print("✓ Content meets quality threshold!")
                              break

            # Step 4: Identify what needs fixing
            print(f"\n  Feedback from editor:")
            for feedback in editor_result.get('feedback', []):
                              print(f"    - [{feedback['category']}] {feedback['comment']}")

            # Step 5: Writer revises
            # LEARNING POINT #32: Revision Strategy
            # Writer gets feedback and improves the draft
            print(f"\n  Writer revising based on feedback...")
            revision_context = {
                              "draft": self.current_draft,
                              "feedback": editor_result.get('feedback', []),
                              "validation_score": validation_score,
                              "topic": topic
            }
            # In production: Pass feedback to writer's LLM context
            # For now, just update the draft with a note
            self.current_draft += f"\n\n[Revision {self.revision_round} notes: incorporating feedback]\n"

        print(f"\n{'='*60}")
        print(f"Content creation complete!")
        print(f"{'='*60}\n")

        return {
                      "status": "success",
                      "topic": topic,
                      "final_draft": self.current_draft,
                      "revision_rounds": self.revision_round,
                      "overall_quality_score": combined_score,
                      "memory_summary": self.memory.get_memory_summary(),
                      "workflow_history": self.workflow_history
        }

    def _log_action(self, action_type: str, result: Dict[str, Any]) -> None:
              """LEARNING POINT #33: Workflow Logging

                              We log every action for:
                                      - Debugging: What went wrong?
                                              - Analysis: Which agents were most useful?
                                                      - Transparency: Show the user what happened
                                                              - Learning: Improve the workflow over time
                                                                      """
              self.workflow_history.append({
                  "round": self.revision_round,
                  "action_type": action_type,
                  "agent": result.get('agent', 'unknown'),
                  "status": result.get('status', 'unknown'),
                  "timestamp": len(self.workflow_history)
              })

    def get_memory_export(self) -> str:
              """LEARNING POINT #34: Memory Introspection

                              Export the entire shared memory for analysis.
                                      This shows what the agent team collectively learned.
                                              """
              return self.memory.export_memory()

    def print_workflow_summary(self) -> None:
              """LEARNING POINT #35: Workflow Analysis"""
              print("\n" + "="*60)
              print("WORKFLOW SUMMARY")
              print("="*60)
              print(f"Total actions: {len(self.workflow_history)}")
              print(f"Revision rounds: {self.revision_round}")
              print(f"\nAgent contributions:")

        agent_actions = {}
        for action in self.workflow_history:
                      agent = action['agent']
                      agent_actions[agent] = agent_actions.get(agent, 0) + 1

        for agent, count in sorted(agent_actions.items()):
                      print(f"  {agent}: {count} actions")

        print(f"\nMemory state:")
        summary = self.memory.get_memory_summary()
        print(f"  Total findings: {summary['total_findings']}")
        print(f"  Credible findings: {summary['credible_findings']}")
        print(f"  Editorial feedback: {summary['editorial_feedback_count']}")


def run_demo():
      """
          LEARNING POINT #36: Demo/Testing

                  Run a simple demo to show the system in action.
                      This helps understand the workflow and identify issues.
                          """
      orchestrator = ContentCreationOrchestrator()

    # Topic for content creation
      topic = "AI agents"

    # Run the workflow
    result = orchestrator.create_content(topic, max_revisions=2)

    # Show results
    print("\nFINAL CONTENT:")
    print("-" * 60)
    print(result['final_draft'])
    print("-" * 60)

    # Show summary
    orchestrator.print_workflow_summary()

    # Show memory state
    print("\n" + "="*60)
    print("SHARED MEMORY STATE")
    print("="*60)
    print(orchestrator.get_memory_export())

    return result


if __name__ == "__main__":
      result = run_demo()
