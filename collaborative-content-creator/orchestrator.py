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


# Learning point explanations for the UI
LEARNING_POINTS = {
    "research": {
        "number": 21,
        "title": "Check Memory Before Searching",
        "description": "The Researcher checks existing findings before searching. This prevents duplicate work and wasted API calls.",
        "what_happens": "READ: search_findings() to check for existing research\nWRITE: add_finding() for each new finding discovered"
    },
    "writing": {
        "number": 23,
        "title": "Read from Shared Memory",
        "description": "The Writer reads credible findings from memory to base the draft on verified information.",
        "what_happens": "READ: get_findings(min_credibility=0.6) to get reliable sources\nNo writes - only creates draft from existing knowledge"
    },
    "editing": {
        "number": 25,
        "title": "Analyze Recurring Patterns",
        "description": "The Editor looks at past feedback to identify patterns and avoid repeating the same issues.",
        "what_happens": "READ: get_unresolved_feedback() to check past issues\nWRITE: add_feedback() for each new issue found"
    },
    "design_validation": {
        "number": 26,
        "title": "Fact Validation Against Memory",
        "description": "The Designer validates claims in the draft against stored research findings.",
        "what_happens": "READ: get_findings(all) to cross-check claims\nNo writes - only produces validation report"
    },
    "consensus": {
        "number": 31,
        "title": "Consensus Mechanism",
        "description": "The orchestrator combines editor approval and designer validation scores to make a quality decision.",
        "what_happens": "combined_score = (approval_score + validation_score) / 2\nIf combined_score >= 0.75, content is approved"
    }
}

# Phase explanations for step-by-step mode
PHASE_EXPLANATIONS = {
    "research": """**Phase 1: Research**

The Researcher agent will search for information on the topic.

**What will happen:**
1. First, it will CHECK memory to see if we already have research on this topic
2. If no existing research, it will SEARCH for credible sources
3. Each finding gets a credibility score (0.0 to 1.0)
4. Findings are WRITTEN to shared memory for other agents to use

**Memory Operations:**
- READ: `search_findings(topic)` - Check for duplicates
- WRITE: `add_finding()` - Store each new finding""",

    "writing": """**Phase 2: Writing**

The Writer agent will create a draft based on the research findings.

**What will happen:**
1. READ credible findings from memory (credibility >= 0.6)
2. Synthesize information into a coherent draft
3. Include citations to sources
4. The draft will be reviewed in the next phase

**Memory Operations:**
- READ: `get_findings(min_credibility=0.6)` - Get reliable sources
- No writes - draft is passed to review phase""",

    "review": """**Phase 3: Review & Revision**

The Editor and Designer agents will review the draft.

**What will happen:**
1. **Editor** reviews for accuracy, clarity, consistency
   - Reads past feedback to identify patterns
   - Writes new feedback to memory
   - Calculates approval_score

2. **Designer** validates facts against research
   - Reads all findings to cross-check claims
   - Calculates validation_score
   - Suggests visual elements

3. **Consensus**: Scores are combined to decide if more revision is needed

**Memory Operations:**
- READ: `get_unresolved_feedback()` - Check past issues
- WRITE: `add_feedback()` - Store new feedback
- READ: `get_findings(all)` - Validate claims"""
}


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

        # Track memory operations for visualization
        self.memory_operations: List[Dict[str, Any]] = []

        # Track scores per round for visualization
        self.score_history: List[Dict[str, Any]] = []

    def run_research_phase(self, topic: str) -> Dict[str, Any]:
        """Run just the research phase - for step-by-step execution"""
        # Track memory state before
        findings_before = len(self.memory.findings)

        # Log the read operation
        self.memory_operations.append({
            "phase": "research",
            "type": "read",
            "operation": "search_findings",
            "args": f'"{topic}"',
            "result": f"{len(self.memory.search_findings(topic))} existing findings"
        })

        # Run researcher
        research_result = self.researcher.act({"topic": topic})

        # Log write operations
        findings_after = len(self.memory.findings)
        findings_added = findings_after - findings_before

        if findings_added > 0:
            for i, finding in enumerate(self.memory.findings[-findings_added:]):
                self.memory_operations.append({
                    "phase": "research",
                    "type": "write",
                    "operation": "add_finding",
                    "args": f'"{finding.content[:50]}..."',
                    "result": f"credibility={finding.credibility_score:.2f}"
                })

        # Log action with rich details
        self._log_action("research", research_result, {
            "findings_added": findings_added,
            "memory_before": findings_before,
            "memory_after": findings_after
        })

        return {
            "status": research_result.get("status"),
            "findings_added": findings_added,
            "memory_ops": self.memory_operations[-findings_added-1:] if findings_added else self.memory_operations[-1:],
            "learning_point": LEARNING_POINTS["research"]
        }

    def run_writing_phase(self, topic: str) -> Dict[str, Any]:
        """Run just the writing phase - for step-by-step execution"""
        # Log the read operation
        credible_findings = self.memory.get_findings(min_credibility=0.6)
        self.memory_operations.append({
            "phase": "writing",
            "type": "read",
            "operation": "get_findings",
            "args": "min_credibility=0.6",
            "result": f"{len(credible_findings)} credible findings"
        })

        # Run writer
        write_result = self.writer.act({
            "topic": topic,
            "style": "professional"
        })

        if write_result['status'] == 'insufficient_research':
            return {
                "status": "failed",
                "reason": "Not enough credible findings to write from",
                "memory_ops": self.memory_operations[-1:],
                "learning_point": LEARNING_POINTS["writing"]
            }

        self.current_draft = write_result.get('draft', '')

        # Log action
        self._log_action("writing", write_result, {
            "draft_length": len(self.current_draft),
            "findings_cited": len(credible_findings)
        })

        return {
            "status": "success",
            "draft": self.current_draft,
            "draft_length": len(self.current_draft),
            "findings_cited": len(credible_findings),
            "memory_ops": self.memory_operations[-1:],
            "learning_point": LEARNING_POINTS["writing"]
        }

    def run_review_phase(self, topic: str) -> Dict[str, Any]:
        """Run one review iteration - for step-by-step execution"""
        self.revision_round += 1
        memory_ops_start = len(self.memory_operations)

        # Editor phase
        # Log read operation
        unresolved = self.memory.get_unresolved_feedback()
        self.memory_operations.append({
            "phase": f"review_r{self.revision_round}",
            "type": "read",
            "operation": "get_unresolved_feedback",
            "args": "",
            "result": f"{len(unresolved)} unresolved items"
        })

        feedback_before = len(self.memory.editorial_history)
        editor_result = self.editor.act({"draft": self.current_draft})
        feedback_after = len(self.memory.editorial_history)

        # Log feedback writes
        for fb in self.memory.editorial_history[feedback_before:]:
            self.memory_operations.append({
                "phase": f"review_r{self.revision_round}",
                "type": "write",
                "operation": "add_feedback",
                "args": f'"{fb.feedback[:40]}..."',
                "result": f"severity={fb.severity:.2f}, category={fb.category}"
            })

        approval_score = editor_result.get('approval_score', 0.0)

        self._log_action("editing", editor_result, {
            "approval_score": approval_score,
            "feedback_count": feedback_after - feedback_before
        })

        # Designer phase
        # Log read operation
        all_findings = self.memory.get_findings(min_credibility=0.0)
        self.memory_operations.append({
            "phase": f"review_r{self.revision_round}",
            "type": "read",
            "operation": "get_findings",
            "args": "min_credibility=0.0",
            "result": f"{len(all_findings)} findings for validation"
        })

        designer_result = self.designer.act({"draft": self.current_draft})
        validation_score = designer_result.get('validation_score', 0.0)

        self._log_action("design_validation", designer_result, {
            "validation_score": validation_score,
            "visual_suggestions": designer_result.get('visual_suggestions', [])
        })

        # Calculate consensus
        combined_score = (approval_score + validation_score) / 2

        # Track scores for visualization
        self.score_history.append({
            "round": self.revision_round,
            "approval_score": approval_score,
            "validation_score": validation_score,
            "combined_score": combined_score
        })

        # Determine if approved
        approved = combined_score >= 0.75 or approval_score >= 0.7

        if not approved:
            # Simulate revision
            self.current_draft += f"\n\n[Revision {self.revision_round} notes: incorporating feedback]\n"

        return {
            "status": "approved" if approved else "needs_revision",
            "round": self.revision_round,
            "approval_score": approval_score,
            "validation_score": validation_score,
            "combined_score": combined_score,
            "feedback": editor_result.get('feedback', []),
            "visual_suggestions": designer_result.get('visual_suggestions', []),
            "memory_ops": self.memory_operations[memory_ops_start:],
            "learning_point": LEARNING_POINTS["consensus"],
            "draft": self.current_draft
        }

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
        research_result = self.run_research_phase(topic)
        print(f"  Researcher action: {research_result['status']}")
        print(f"  Findings added: {research_result.get('findings_added', 0)}\n")

        # Phase 2: Initial Writing
        print("PHASE 2: WRITING")
        write_result = self.run_writing_phase(topic)

        if write_result['status'] == 'failed':
            return {
                "status": "failed",
                "reason": write_result.get('reason', 'Writing failed'),
                "workflow_history": self.workflow_history,
                "memory_operations": self.memory_operations
            }

        print(f"  Writer created draft ({write_result['draft_length']} chars)\n")

        # Phase 3: Review Loop
        print("PHASE 3: REVIEW & REVISION LOOP")
        print(f"Max revisions: {max_revisions}\n")

        combined_score = 0.0
        for revision_num in range(max_revisions):
            print(f"\n--- Revision Round {revision_num + 1} ---")

            review_result = self.run_review_phase(topic)
            combined_score = review_result['combined_score']

            print(f"  Editor approval: {review_result['approval_score']:.2f}")
            print(f"  Designer validation: {review_result['validation_score']:.2f}")
            print(f"  Combined score: {combined_score:.2f}")

            if review_result['status'] == 'approved':
                print("  Content approved!")
                break
            else:
                print("  Needs revision...")
                for fb in review_result.get('feedback', []):
                    print(f"    - [{fb['category']}] {fb['comment']}")

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
            "workflow_history": self.workflow_history,
            "memory_operations": self.memory_operations,
            "score_history": self.score_history
        }

    def _log_action(self, action_type: str, result: Dict[str, Any], details: Dict[str, Any] = None) -> None:
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
            "timestamp": len(self.workflow_history),
            "details": details or {}
        })

    def get_memory_export(self) -> str:
        """LEARNING POINT #34: Memory Introspection

        Export the entire shared memory for analysis.
        This shows what the agent team collectively learned.
        """
        return self.memory.export_memory()

    def get_phase_explanation(self, phase: str) -> str:
        """Get explanation text for a phase - used by UI"""
        return PHASE_EXPLANATIONS.get(phase, "")

    def get_learning_point(self, action_type: str) -> Dict[str, Any]:
        """Get learning point for an action type - used by UI"""
        return LEARNING_POINTS.get(action_type, {})

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
