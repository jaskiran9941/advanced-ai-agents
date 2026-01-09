"""
Multi-Agent Implementations

LEARNING POINT #17: Agent Interface & Contract
Each agent implements the same interface (act method) but has different responsibilities.
This pattern allows us to swap agents, add new ones, or remove ones easily.

LEARNING POINT #18: Role-Based Reasoning
Notice how each agent's prompt emphasizes its role and constraints.
This helps the LLM stay focused on its specific job.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
from memory_manager import SharedMemory, Finding, EditorialFeedback


class Agent(ABC):
      """Base class for all agents

              LEARNING POINT #19: Polymorphism in Multi-Agent Systems
                  All agents inherit from this base class and implement act() method.
                      This allows the orchestrator to treat all agents uniformly.
                          """

    def __init__(self, name: str, memory: SharedMemory):
              self.name = name
              self.memory = memory
              self.action_count = 0  # Track how many actions this agent has taken

    @abstractmethod
    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
              """
                      Execute the agent's action.

                                      Args:
                                                  context: Information provided by the orchestrator
                                                                      (e.g., topic, current draft, previous feedback)

                                                                                      Returns:
                                                                                                  Result of the action (findings, feedback, analysis, etc.)
                                                                                                          """
              pass

    def _get_memory_context(self) -> str:
              """Helper: Get current memory state for agent awareness"""
              summary = self.memory.get_memory_summary()
              return f"""
              Current Memory State:
              - Total findings: {summary['total_findings']}
              - Credible findings: {summary['credible_findings']}
              - Disputed findings: {summary['disputed_findings']}
              - Feedback categories: {summary['feedback_by_category']}
              """


class ResearcherAgent(Agent):
      """
          LEARNING POINT #20: Agent 1 - The Researcher

                  Role: Find and extract reliable information
                      Memory: WRITES findings to shared memory
                          Constraints:
                              - Only cites credible sources
                                  - Records credibility scores
                                      - Avoids duplication (checks memory first)
                                          - Must cite at least min_sources_required

                                                  This agent is the KNOWLEDGE GENERATOR for the team.
                                                      """

    def __init__(self, name: str, memory: SharedMemory):
              super().__init__(name, memory)
              self.role = "Research Specialist"

    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
              """
                      Find research on the given topic

                                      In production, this would:
                                              1. Call real APIs (Google Scholar, academic DBs, news APIs)
                                                      2. Parse and rank results by credibility
                                                              3. Extract structured information

                                                                              For now, we simulate with example findings.
                                                                                      """
              topic = context.get("topic", "")

        # LEARNING POINT #21: Check Memory Before Searching
              # Don't re-research what we already know!
              existing = self.memory.search_findings(topic)

        if len(existing) > 0:
                      return {
                                        "status": "already_researched",
                                        "message": f"Found {len(existing)} existing findings on '{topic}'",
                                        "findings_reused": len(existing)
                      }

        # Simulate finding research
        # In production: call APIs, parse responses, score credibility
        findings = self._simulate_research(topic)

        # Store in shared memory
        for finding_data in findings:
                      finding = Finding(
                                        content=finding_data["content"],
                                        source=finding_data["source"],
                                        credibility_score=finding_data["credibility"],
                                        extracted_by=self.name,
                                        citations=[finding_data["source"]]
                      )
                      self.memory.add_finding(finding)

        self.action_count += 1

        return {
                      "status": "success",
                      "findings_added": len(findings),
                      "agent": self.name,
                      "action_count": self.action_count
        }

    def _simulate_research(self, topic: str) -> List[Dict[str, Any]]:
              """Simulate research results"""
              simulated_findings = {
                  "AI agents": [
                      {
                          "content": "AI agents are systems that perceive their environment and take actions to achieve goals",
                          "source": "OpenAI Research Paper 2024",
                          "credibility": 0.95
                      },
                      {
                          "content": "Multi-agent systems outperform single agents on complex decomposable tasks",
                          "source": "MIT Technology Review",
                          "credibility": 0.85
                      }
                  ],
                  "content creation": [
                      {
                          "content": "Collaborative content creation reduces error rates by 40% compared to solo creation",
                          "source": "Content Marketing Institute",
                          "credibility": 0.8
                      },
                      {
                          "content": "Editorial feedback improves content quality by 65% across major metrics",
                          "source": "Journal of Applied Writing Research",
                          "credibility": 0.9
                      }
                  ]
              }

        return simulated_findings.get(topic.lower(), [
                      {
                                        "content": f"Default research finding about {topic}",
                                        "source": "Default Source",
                                        "credibility": 0.6
                      }
        ])


class WriterAgent(Agent):
      """
          LEARNING POINT #22: Agent 2 - The Writer

                  Role: Create engaging content based on research
                      Memory: READS findings from memory, WRITES drafts
                          Constraints:
                              - Must cite at least min_sources_required findings
                                  - Maintains tone consistency
                                      - Targets specific word count
                                          - References memory to avoid repeating info

                                                  This agent is the CONTENT SYNTHESIZER.
                                                      """

    def __init__(self, name: str, memory: SharedMemory):
              super().__init__(name, memory)
              self.role = "Content Writer"

    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
              """Create content draft using research findings"""
              topic = context.get("topic", "")
              style = context.get("style", "professional")

        # LEARNING POINT #23: Read from Shared Memory
              credible_findings = self.memory.get_findings(min_credibility=0.6)

        if not credible_findings:
                      return {
                                        "status": "insufficient_research",
                                        "message": "Not enough credible findings to write from"
                      }

        # Create draft (simulated)
        draft = self._create_draft(topic, credible_findings, style)

        self.action_count += 1

        return {
                      "status": "success",
                      "draft": draft,
                      "findings_cited": len(credible_findings),
                      "agent": self.name,
                      "action_count": self.action_count
        }

    def _create_draft(self, topic: str, findings: List[Finding], style: str) -> str:
              """Create a draft based on findings"""
              finding_summaries = [f"- {f.content} (Source: {f.source})" for f in findings[:2]]

        draft = f"""
        # {topic.title()}

        ## Introduction
        This article explores key aspects of {topic}.

        ## Key Findings
        {chr(10).join(finding_summaries)}

        ## Conclusion
        Based on the research findings above, we can see that {topic} is an important topic.
        Further research and collaboration is recommended.

        ---
        *Draft created by {self.name}*
                """
        return draft


class EditorAgent(Agent):
      """
          LEARNING POINT #24: Agent 3 - The Editor

                  Role: Review content for accuracy, clarity, consistency
                      Memory: READS findings and drafts, WRITES feedback
                          Constraints:
                              - Feedback must be specific and actionable
                                  - Tracks recurring issues (learning from history)
                                      - Approves or rejects based on threshold

                                              This agent is the QUALITY GATEKEEPER.
                                                  It maintains institutional memory of editorial standards.
                                                      """

    def __init__(self, name: str, memory: SharedMemory):
              super().__init__(name, memory)
              self.role = "Editor"

    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
              """Review content and provide feedback"""
              draft = context.get("draft", "")

        # LEARNING POINT #25: Analyze Recurring Patterns
              # Look at past feedback to identify patterns
        past_feedback = self.memory.get_unresolved_feedback()

        feedback_items = self._generate_feedback(draft, past_feedback)

        # Store feedback in memory
        for feedback in feedback_items:
                      fb = EditorialFeedback(
                                        content_section=feedback["section"],
                                        feedback=feedback["comment"],
                                        category=feedback["category"],
                                        severity=feedback["severity"],
                                        was_addressed=False
                      )
                      self.memory.add_feedback(fb)

        # Calculate approval score
        avg_severity = sum(f["severity"] for f in feedback_items) / len(feedback_items) if feedback_items else 0
        approval_score = 1.0 - avg_severity

        self.action_count += 1

        return {
                      "status": "reviewed",
                      "approval_score": approval_score,
                      "feedback_count": len(feedback_items),
                      "feedback": feedback_items,
                      "agent": self.name,
                      "action_count": self.action_count
        }

    def _generate_feedback(self, draft: str, past_feedback: List) -> List[Dict[str, Any]]:
              """Generate editorial feedback"""
              feedback_items = []

        # Check for common issues
              if len(draft) < 200:
                            feedback_items.append({
                                              "section": "overall",
                                              "comment": "Draft is too short, needs more content",
                                              "category": "clarity",
                                              "severity": 0.7
                            })

        if "Conclusion" not in draft:
                      feedback_items.append({
                                        "section": "structure",
                                        "comment": "Missing conclusion section",
                                        "category": "consistency",
                                        "severity": 0.5
                      })

        return feedback_items if feedback_items else [
                      {
                                        "section": "overall",
                                        "comment": "Good draft, minor refinements needed",
                                        "category": "tone",
                                        "severity": 0.2
                      }
        ]


class DesignerAgent(Agent):
      """
          LEARNING POINT #26: Agent 4 - The Fact Checker/Designer

                  Role: Validate claims and suggest visuals
                      Memory: READS findings, cross-checks claims, WRITES validation report
                          Constraints:
                              - Claims must match research with 80%+ confidence
                                  - Suggests visual representations
                                      - Flags unsubstantiated claims

                                              This agent is the FACT VALIDATOR.
                                                  It acts as the last line of defense against misinformation.
                                                      """

    def __init__(self, name: str, memory: SharedMemory):
              super().__init__(name, memory)
              self.role = "Fact Checker & Designer"

    def act(self, context: Dict[str, Any]) -> Dict[str, Any]:
              """Validate claims in the draft against research findings"""
              draft = context.get("draft", "")

        # Get all findings for validation
              all_findings = self.memory.get_findings(min_credibility=0.0)

        # Check for unsubstantiated claims (simplified)
        validation_report = self._validate_claims(draft, all_findings)

        self.action_count += 1

        return {
                      "status": "validated",
                      "validation_score": validation_report["score"],
                      "unsubstantiated_claims": validation_report["unsubstantiated"],
                      "visual_suggestions": validation_report["visual_suggestions"],
                      "agent": self.name,
                      "action_count": self.action_count
        }

    def _validate_claims(self, draft: str, findings: List[Finding]) -> Dict[str, Any]:
              """Validate claims against findings"""
              return {
                  "score": 0.85 if len(findings) > 0 else 0.6,
                  "unsubstantiated": 0 if len(findings) > 0 else 2,
                  "visual_suggestions": [
                      "Add a chart showing research findings",
                      "Include diagrams for key concepts"
                  ]
              }
