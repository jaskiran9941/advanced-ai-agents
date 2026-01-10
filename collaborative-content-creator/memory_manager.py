"""
Memory Manager for Collaborative Content Creator

LEARNING POINT #5: Shared Agent Memory Architecture
This is the critical component that enables agent collaboration.

Why shared memory matters:
1. PERSISTENCE: Findings from Agent 1 (Researcher) are stored so Agent 2 (Writer)
   can reference them without re-fetching
2. CONTEXT AWARENESS: Each agent can see what others have done and avoid duplication
3. CONFLICT RESOLUTION: When agents disagree, we have a record of the conflict
4. LEARNING: The system can identify patterns in what sources work well

Memory Structure:
- Findings: Individual facts/research items with credibility scores and source tracking
- Editorial History: Record of feedback and revisions (memory of "what worked")
- Agent State: What each agent has contributed (accountability)
- Consensus Records: How agents agreed or disagreed (for future conflict resolution)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
from enum import Enum


class CredibilityLevel(Enum):
    """LEARNING POINT #6: Credibility Scoring

    In multi-agent systems, different sources have different reliability.
    We track this to help agents make better decisions.
    """
    HIGH = 0.9        # Academic papers, official sources
    MEDIUM = 0.7      # News sites, industry reports
    LOW = 0.4         # User-generated, unverified
    DISPUTED = 0.5    # Agents disagreed about credibility


@dataclass
class Finding:
    """A single research finding with metadata"""
    content: str                           # The actual finding
    source: str                            # Where it came from
    credibility_score: float               # 0.0 to 1.0
    extracted_by: str                      # Which agent found it
    timestamp: datetime = field(default_factory=datetime.now)
    citations: List[str] = field(default_factory=list)  # Sources cited
    disputes: List[str] = field(default_factory=list)   # Agents who disputed it

    def is_credible(self, threshold: float = 0.6) -> bool:
        """LEARNING POINT #7: Credibility Thresholding

        Agents can query: "Is this finding credible enough to use?"
        This prevents low-credibility information from polluting the content.
        """
        return self.credibility_score >= threshold

    def should_forget(self, memory_ttl_days: int = 30) -> bool:
        """LEARNING POINT #8: Forgetting Strategy (Episodic vs Semantic)

        We don't keep memories forever. Old findings are forgotten to:
        - Reduce storage
        - Keep memory fresh and relevant
        - Simulate human memory decay
        """
        age = datetime.now() - self.timestamp
        return age > timedelta(days=memory_ttl_days)


@dataclass
class EditorialFeedback:
    """Record of feedback from Editor (Agent 3)

    LEARNING POINT #9: Memory of Editorial Decisions
    When the same issue appears again, we remember how it was resolved.
    """
    content_section: str          # What part of content was reviewed
    feedback: str                 # The feedback
    category: str                 # "accuracy", "clarity", "tone", etc.
    severity: float               # 0.0 to 1.0 (how important is this?)
    was_addressed: bool           # Did the writer fix it?
    timestamp: datetime = field(default_factory=datetime.now)


class SharedMemory:
    """
    LEARNING POINT #10: Shared Mutable State

    This is where agent collaboration happens. All agents can:
    1. Write findings to memory (add_finding)
    2. Query memory (get_findings, search_findings)
    3. Update credibility (dispute_finding, confirm_finding)
    4. Track decisions (add_feedback, get_feedback_history)

    The challenge: How do we prevent conflicts when multiple agents
    write to memory simultaneously?
    """

    def __init__(self, max_findings: int = 100):
        self.findings: List[Finding] = []
        self.editorial_history: List[EditorialFeedback] = []
        self.agent_contributions: Dict[str, List[str]] = {}  # Track who did what
        self.consensus_votes: Dict[str, Dict] = {}  # Track voting history
        self.max_findings = max_findings

    def add_finding(self, finding: Finding) -> None:
        """LEARNING POINT #11: Write Operations in Shared Memory

        When Agent 1 (Researcher) finds something, it stores it here.
        We need to:
        1. Check for duplicates (semantic similarity)
        2. Maintain size limits (don't let memory explode)
        3. Track attribution (who added this?)
        """
        # Track contribution
        if finding.extracted_by not in self.agent_contributions:
            self.agent_contributions[finding.extracted_by] = []

        # Prevent duplicates (simple string match; could improve with embeddings)
        for existing in self.findings:
            if existing.content.lower() == finding.content.lower():
                # Update credibility by averaging scores
                existing.credibility_score = (
                    existing.credibility_score + finding.credibility_score
                ) / 2
                return

        # Size management - forget oldest low-credibility findings
        if len(self.findings) >= self.max_findings:
            self.findings = [f for f in self.findings if f.is_credible(0.6)]
            if len(self.findings) >= self.max_findings:
                self.findings = self.findings[-(self.max_findings - 1):]

        self.findings.append(finding)
        self.agent_contributions[finding.extracted_by].append(finding.content)

    def get_findings(self, min_credibility: float = 0.6) -> List[Finding]:
        """Get all credible findings

        LEARNING POINT #12: Read Operations with Filtering
        Agent 2 (Writer) calls this to get reliable information to cite
        """
        return [f for f in self.findings if f.is_credible(min_credibility)]

    def search_findings(self, query: str) -> List[Finding]:
        """Simple keyword search on findings

        In production, this would use vector similarity.
        For now, simple substring matching helps Agent 2 find relevant findings.
        """
        return [
            f for f in self.findings
            if query.lower() in f.content.lower()
        ]

    def dispute_finding(self, finding_id: int, agent_name: str, reason: str) -> None:
        """LEARNING POINT #13: Conflict Recording

        When Agent 3 (Editor) or Agent 4 (Designer) disputes a finding,
        we record it. This helps with consensus mechanisms.
        """
        if 0 <= finding_id < len(self.findings):
            self.findings[finding_id].disputes.append(agent_name)
            # Lower credibility score
            self.findings[finding_id].credibility_score *= 0.8

    def confirm_finding(self, finding_id: int, agent_name: str) -> None:
        """Opposite of dispute - increases confidence in finding"""
        if 0 <= finding_id < len(self.findings):
            self.findings[finding_id].credibility_score = min(
                1.0,
                self.findings[finding_id].credibility_score * 1.1
            )

    def add_feedback(self, feedback: EditorialFeedback) -> None:
        """LEARNING POINT #14: Memory of What Works

        Editor's feedback becomes institutional memory.
        If similar issues appear again, we can reference past solutions.
        """
        self.editorial_history.append(feedback)

    def get_feedback_by_category(self, category: str) -> List[EditorialFeedback]:
        """Get feedback history for a specific category

        E.g., "accuracy" feedback helps us identify recurring accuracy issues
        """
        return [f for f in self.editorial_history if f.category == category]

    def get_unresolved_feedback(self) -> List[EditorialFeedback]:
        """Feedback that wasn't addressed - might need escalation"""
        return [f for f in self.editorial_history if not f.was_addressed]

    def mark_feedback_resolved(self, feedback_id: int) -> None:
        """Mark feedback as addressed by the writer"""
        if 0 <= feedback_id < len(self.editorial_history):
            self.editorial_history[feedback_id].was_addressed = True

    def get_memory_summary(self) -> Dict[str, Any]:
        """LEARNING POINT #15: Memory Introspection

        Agents can query: "What do we know so far?"
        This helps with coherence and prevents redundant work.
        """
        return {
            "total_findings": len(self.findings),
            "credible_findings": len(self.get_findings()),
            "disputed_findings": len([f for f in self.findings if f.disputes]),
            "editorial_feedback_count": len(self.editorial_history),
            "agents_involved": list(self.agent_contributions.keys()),
            "feedback_by_category": {
                cat: len(self.get_feedback_by_category(cat))
                for cat in ["accuracy", "clarity", "tone", "consistency"]
            }
        }

    def export_memory(self) -> str:
        """Export memory as JSON for debugging/analysis

        LEARNING POINT #16: Memory Transparency
        We should be able to see what the agents collectively know.
        """
        return json.dumps({
            "findings": [
                {
                    "content": f.content,
                    "source": f.source,
                    "credibility": f.credibility_score,
                    "extracted_by": f.extracted_by,
                    "timestamp": f.timestamp.isoformat(),
                }
                for f in self.findings
            ],
            "editorial_feedback": [
                {
                    "section": fb.content_section,
                    "category": fb.category,
                    "severity": fb.severity,
                    "resolved": fb.was_addressed,
                }
                for fb in self.editorial_history
            ],
            "summary": self.get_memory_summary()
        }, indent=2)
