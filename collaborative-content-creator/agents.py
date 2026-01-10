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
                "findings_reused": len(existing),
                "agent": self.name
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
        """Simulate research results with realistic, detailed findings"""

        # Comprehensive research database with real-world style findings
        simulated_findings = {
            "ai agents": [
                {
                    "content": "AI agents are autonomous software programs that perceive their environment through sensors, make decisions using algorithms, and take actions to achieve specific goals. Unlike simple automation, agents can adapt their behavior based on feedback.",
                    "source": "Stanford AI Index Report 2024",
                    "credibility": 0.95
                },
                {
                    "content": "The global AI agent market is projected to reach $65 billion by 2028, growing at 45% annually. Key sectors include customer service (34%), healthcare (22%), and finance (18%).",
                    "source": "McKinsey Global AI Survey 2024",
                    "credibility": 0.92
                },
                {
                    "content": "Multi-agent systems, where multiple AI agents collaborate, have shown 3x improvement in complex problem-solving compared to single agents. Examples include Google's AlphaFold team and OpenAI's research clusters.",
                    "source": "Nature Machine Intelligence Journal",
                    "credibility": 0.94
                }
            ],
            "climate change": [
                {
                    "content": "Global temperatures have risen 1.1°C since pre-industrial times. The Paris Agreement aims to limit warming to 1.5°C, but current policies put us on track for 2.7°C by 2100.",
                    "source": "IPCC Sixth Assessment Report 2023",
                    "credibility": 0.98
                },
                {
                    "content": "Renewable energy now accounts for 30% of global electricity generation. Solar costs have dropped 89% since 2010, making it cheaper than coal in most countries.",
                    "source": "International Energy Agency (IEA) 2024",
                    "credibility": 0.96
                },
                {
                    "content": "Sea levels have risen 8-9 inches since 1880 and are accelerating. By 2050, 300 million people in coastal areas face annual flooding risks.",
                    "source": "NASA Climate Science Division",
                    "credibility": 0.97
                }
            ],
            "remote work": [
                {
                    "content": "58% of American workers can work remotely at least one day per week. Fully remote workers report 22% higher job satisfaction but 17% feel more isolated.",
                    "source": "Gallup Workplace Study 2024",
                    "credibility": 0.91
                },
                {
                    "content": "Companies with hybrid policies see 12% higher retention rates. However, remote workers are 38% less likely to receive promotions than in-office peers.",
                    "source": "Harvard Business Review Research",
                    "credibility": 0.89
                },
                {
                    "content": "Remote work reduces commute-related carbon emissions by 54 million tons annually in the US alone, equivalent to taking 10 million cars off the road.",
                    "source": "Environmental Protection Agency (EPA)",
                    "credibility": 0.93
                }
            ],
            "electric vehicles": [
                {
                    "content": "Global EV sales reached 14 million units in 2023, representing 18% of all car sales. China leads with 60% of global EV production.",
                    "source": "BloombergNEF Electric Vehicle Outlook",
                    "credibility": 0.94
                },
                {
                    "content": "Average EV battery costs have fallen from $1,100/kWh in 2010 to $139/kWh in 2023. Experts predict $80/kWh by 2030, achieving price parity with gas cars.",
                    "source": "MIT Energy Initiative Research",
                    "credibility": 0.92
                },
                {
                    "content": "EVs produce 50-70% fewer lifetime emissions than gas cars, even accounting for battery manufacturing. This gap widens as grids become greener.",
                    "source": "Union of Concerned Scientists Study",
                    "credibility": 0.90
                }
            ],
            "mental health": [
                {
                    "content": "1 in 5 adults experience mental illness each year. Anxiety disorders are most common, affecting 40 million Americans, yet only 36.9% receive treatment.",
                    "source": "National Institute of Mental Health (NIMH)",
                    "credibility": 0.97
                },
                {
                    "content": "Therapy apps and digital mental health tools have grown 300% since 2020. Studies show they can reduce depression symptoms by 30-50% for mild to moderate cases.",
                    "source": "American Psychological Association",
                    "credibility": 0.88
                },
                {
                    "content": "Workplace mental health programs return $4 for every $1 invested through reduced absenteeism and increased productivity.",
                    "source": "World Health Organization (WHO)",
                    "credibility": 0.95
                }
            ],
            "cryptocurrency": [
                {
                    "content": "Bitcoin's market cap reached $1.2 trillion in 2024. Over 420 million people worldwide own cryptocurrency, with highest adoption in Nigeria (32%), Vietnam (21%), and Philippines (20%).",
                    "source": "Chainalysis Global Crypto Adoption Index",
                    "credibility": 0.87
                },
                {
                    "content": "Bitcoin mining consumes 150 TWh annually, comparable to Argentina's electricity usage. However, 59% now comes from renewable sources, up from 25% in 2019.",
                    "source": "Cambridge Centre for Alternative Finance",
                    "credibility": 0.91
                },
                {
                    "content": "Central Bank Digital Currencies (CBDCs) are being explored by 130 countries representing 98% of global GDP. China's digital yuan has 260 million users.",
                    "source": "Atlantic Council CBDC Tracker",
                    "credibility": 0.93
                }
            ],
            "space exploration": [
                {
                    "content": "NASA's Artemis program aims to land the first woman and person of color on the Moon by 2025, establishing a permanent lunar base by 2030.",
                    "source": "NASA Artemis Program Official Documentation",
                    "credibility": 0.98
                },
                {
                    "content": "SpaceX has reduced launch costs by 90% through reusable rockets. A Falcon 9 launch costs $67 million versus $450 million for Space Shuttle missions.",
                    "source": "Space Foundation Annual Report 2024",
                    "credibility": 0.94
                },
                {
                    "content": "The James Webb Space Telescope has discovered over 5,000 new exoplanets, including 12 potentially habitable Earth-like worlds within 100 light-years.",
                    "source": "Nature Astronomy Journal",
                    "credibility": 0.96
                }
            ],
            "artificial intelligence": [
                {
                    "content": "ChatGPT reached 100 million users in 2 months, the fastest-growing consumer app ever. By 2024, 77% of companies are using or exploring AI tools.",
                    "source": "Reuters Technology Survey 2024",
                    "credibility": 0.93
                },
                {
                    "content": "AI could automate 30% of work hours by 2030, affecting 800 million jobs globally. However, it's expected to create 97 million new jobs in emerging fields.",
                    "source": "World Economic Forum Future of Jobs Report",
                    "credibility": 0.91
                },
                {
                    "content": "Training GPT-4 cost over $100 million and used 25,000 GPUs. The AI industry's compute demand doubles every 3.4 months, far outpacing Moore's Law.",
                    "source": "Stanford Human-Centered AI Institute",
                    "credibility": 0.89
                }
            ]
        }

        # Try exact match first, then partial match
        topic_lower = topic.lower()
        if topic_lower in simulated_findings:
            return simulated_findings[topic_lower]

        # Check for partial matches
        for key in simulated_findings:
            if key in topic_lower or topic_lower in key:
                return simulated_findings[key]

        # Generate contextual default findings for unknown topics
        return [
            {
                "content": f"{topic} is a growing field of interest with significant developments in recent years. Industry experts predict continued growth and innovation through 2025 and beyond.",
                "source": "Industry Analysis Report 2024",
                "credibility": 0.75
            },
            {
                "content": f"Recent studies show that {topic.lower()} impacts approximately 45% of related industries, with adoption rates increasing 23% year-over-year.",
                "source": "Market Research Institute",
                "credibility": 0.72
            },
            {
                "content": f"Leading universities including MIT, Stanford, and Oxford have established dedicated research programs for {topic.lower()}, publishing over 500 peer-reviewed papers in 2023.",
                "source": "Academic Research Database",
                "credibility": 0.80
            }
        ]


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
                "message": "Not enough credible findings to write from",
                "agent": self.name
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
        """Create a professional, well-structured draft based on findings"""

        # Build citations from findings
        citations = []
        key_points = []
        for i, f in enumerate(findings[:3]):
            citations.append(f"[{i+1}] {f.source}")
            key_points.append(f.content)

        # Create a more substantial, realistic article
        draft = f"""# {topic.title()}: What You Need to Know

## Introduction

{topic.title()} has become one of the most discussed topics in recent years, attracting attention from researchers, businesses, and the general public alike. This article examines the latest findings and what they mean for the future.

## Key Findings

### Finding 1: The Big Picture
{key_points[0] if len(key_points) > 0 else 'Research is ongoing in this area.'}

### Finding 2: The Numbers
{key_points[1] if len(key_points) > 1 else 'Quantitative data is being collected.'}

### Finding 3: Looking Ahead
{key_points[2] if len(key_points) > 2 else 'Experts continue to monitor developments.'}

## Why This Matters

Understanding {topic.lower()} is crucial for several reasons:

1. **Economic Impact**: The developments in this field affect industries worth billions of dollars
2. **Social Implications**: Changes here impact how people live and work
3. **Future Preparedness**: Staying informed helps individuals and organizations adapt

## Conclusion

The research presented here demonstrates that {topic.lower()} is a dynamic and evolving field. As our sources indicate, significant changes are underway that will shape the coming years. Staying informed and engaged with these developments is essential for anyone looking to understand or participate in this space.

---

**Sources:**
{chr(10).join(citations)}

*Article generated by {self.name}*
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
        """Generate realistic, specific editorial feedback"""
        feedback_items = []
        draft_lower = draft.lower()

        # Check article length
        word_count = len(draft.split())
        if word_count < 200:
            feedback_items.append({
                "section": "overall",
                "comment": f"Article is only {word_count} words. Aim for at least 300 words for adequate coverage.",
                "category": "completeness",
                "severity": 0.7
            })

        # Check for proper structure
        if "## Introduction" not in draft:
            feedback_items.append({
                "section": "structure",
                "comment": "Missing clear introduction section. Add context for readers.",
                "category": "structure",
                "severity": 0.5
            })

        if "## Conclusion" not in draft and "conclusion" not in draft_lower:
            feedback_items.append({
                "section": "structure",
                "comment": "No conclusion found. Summarize key takeaways for readers.",
                "category": "structure",
                "severity": 0.4
            })

        # Check for sources/citations
        if "source" not in draft_lower and "[1]" not in draft:
            feedback_items.append({
                "section": "credibility",
                "comment": "No sources cited. Add references to support claims.",
                "category": "accuracy",
                "severity": 0.8
            })

        # Check for engagement elements
        if "?" not in draft:
            feedback_items.append({
                "section": "engagement",
                "comment": "Consider adding rhetorical questions to engage readers.",
                "category": "tone",
                "severity": 0.2
            })

        # Check for actionable content
        if "you" not in draft_lower and "your" not in draft_lower:
            feedback_items.append({
                "section": "engagement",
                "comment": "Article feels impersonal. Consider addressing the reader directly.",
                "category": "tone",
                "severity": 0.3
            })

        # If everything looks good
        if not feedback_items:
            feedback_items.append({
                "section": "overall",
                "comment": "Well-structured article with good flow. Minor polish recommended.",
                "category": "quality",
                "severity": 0.15
            })

        return feedback_items


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
        """Validate claims against findings with detailed analysis"""

        draft_lower = draft.lower()
        validated_claims = 0
        total_claims = 0

        # Check if findings content appears in draft (simplified fact-checking)
        for finding in findings:
            # Check if key parts of the finding appear in the draft
            key_words = finding.content.lower().split()[:5]  # First 5 words
            if any(word in draft_lower for word in key_words if len(word) > 4):
                validated_claims += 1
            total_claims += 1

        # Calculate validation score
        if total_claims > 0:
            base_score = validated_claims / total_claims
            # Boost score if sources are cited
            if "[1]" in draft or "source" in draft_lower:
                base_score = min(1.0, base_score + 0.1)
        else:
            base_score = 0.5

        # Generate contextual visual suggestions based on content
        visual_suggestions = []

        if "billion" in draft_lower or "million" in draft_lower or "%" in draft:
            visual_suggestions.append("Add a bar chart to visualize the statistics mentioned")

        if "grow" in draft_lower or "increase" in draft_lower or "rise" in draft_lower:
            visual_suggestions.append("Include a line graph showing growth trends over time")

        if "compare" in draft_lower or "versus" in draft_lower or "vs" in draft_lower:
            visual_suggestions.append("Add a comparison table or side-by-side infographic")

        if len(findings) >= 3:
            visual_suggestions.append("Create an infographic summarizing the 3 key findings")

        if not visual_suggestions:
            visual_suggestions = [
                "Add a hero image related to the topic",
                "Include pull quotes to highlight key statistics"
            ]

        return {
            "score": round(base_score, 2),
            "unsubstantiated": total_claims - validated_claims,
            "validated": validated_claims,
            "total_claims": total_claims,
            "visual_suggestions": visual_suggestions
        }
