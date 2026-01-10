# Multi-Agent Memory Learning Tool

**Learn how AI agents collaborate through shared memory**

An interactive educational tool that demonstrates how multiple AI agents work together to create content using a shared "bulletin board" (memory system). Perfect for understanding multi-agent systems, memory architecture, and agent orchestration.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## What is This?

Imagine a **newsroom** where 4 people collaborate on writing an article:

| Agent | Real-World Analogy | What They Do |
|-------|-------------------|--------------|
| **Researcher** | Librarian | Finds facts and pins them to the bulletin board |
| **Writer** | Author | Reads facts from the board, writes the article |
| **Editor** | Teacher | Reviews the article, pins suggestions to the board |
| **Fact Checker** | Detective | Verifies claims against the original facts |

**The catch?** They can't talk directly to each other. They can only communicate by pinning notes (data) to a shared **bulletin board** (memory).

This is exactly how multi-agent AI systems work!

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run streamlit_ui.py
```

Then open http://localhost:8501 in your browser.

---

## What You'll Learn

### 1. Shared Memory Architecture
How agents store and retrieve information from a common data store:
- **Findings** (yellow sticky notes) - Facts discovered by the Researcher
- **Feedback** (pink sticky notes) - Suggestions from the Editor

### 2. READ vs WRITE Operations
- **READ**: Agent looks at the bulletin board to get information
- **WRITE**: Agent pins new information to the bulletin board

### 3. Agent Collaboration Without Direct Communication
Agents don't talk to each other. They only:
1. Read from shared memory
2. Do their job
3. Write results to shared memory

### 4. Orchestration & Consensus
How a central coordinator (Orchestrator) decides:
- Which agent acts next
- When the work is good enough (quality scores)
- When to stop iterating

---

## The Workflow

```
Step 1: RESEARCH
├── Researcher checks if facts already exist (READ)
├── Researcher finds new facts
└── Researcher pins facts to board (WRITE)

Step 2: WRITING
├── Writer reads facts from board (READ)
└── Writer creates article draft (no write)

Step 3: REVIEW
├── Editor reads past suggestions (READ)
├── Editor reviews draft, pins new suggestions (WRITE)
├── Fact Checker reads original facts (READ)
├── Fact Checker validates claims (no write)
└── Both give quality scores

Step 4: CONSENSUS
├── Combined Score = (Editor Score + Fact Checker Score) / 2
├── If score >= 75%: DONE!
└── If score < 75%: Revise and repeat Step 3
```

---

## Project Structure

```
collaborative-content-creator/
├── streamlit_ui.py      # Interactive web UI (what you see)
├── orchestrator.py      # Coordinates the agents
├── agents.py            # The 4 agents (Researcher, Writer, Editor, Designer)
├── memory_manager.py    # Shared memory (the bulletin board)
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

---

## Key Concepts Explained

### What is "Memory" in AI Agents?

Think of it like a **bulletin board** in an office:
- Anyone can **pin** notes to it
- Anyone can **read** notes from it
- Notes stay there until removed

In code, it's a data structure that all agents can access:

```python
# Researcher WRITES a finding
memory.add_finding(Finding(
    content="AI market will reach $65B by 2028",
    source="McKinsey Report",
    credibility=0.92
))

# Writer READS findings
facts = memory.get_findings(min_credibility=0.6)
```

### Why Do Agents Need Shared Memory?

Without it:
- Writer wouldn't know what facts to use
- Editor couldn't remember past problems
- Everyone would duplicate work

**Memory lets agents collaborate without talking directly!**

### What is "Credibility Score"?

Not all sources are equally trustworthy:
- Academic paper: 0.95 (very credible)
- News article: 0.80 (credible)
- Random blog: 0.50 (less credible)

Agents can filter: "Only give me facts with credibility > 0.7"

---

## Topics with Built-in Research Data

The tool includes realistic research data for these topics:

| Topic | Sample Findings |
|-------|-----------------|
| **AI Agents** | Market projections, collaboration research |
| **Climate Change** | IPCC data, renewable energy stats |
| **Remote Work** | Gallup surveys, productivity research |
| **Electric Vehicles** | Sales data, battery cost trends |
| **Mental Health** | NIMH statistics, therapy app research |
| **Cryptocurrency** | Adoption rates, energy consumption |
| **Space Exploration** | NASA programs, SpaceX economics |

Try any topic - unknown topics get contextual placeholder data.

---

## Understanding the UI

### Left Side: What's Happening
- Step-by-step workflow execution
- Current agent's status
- Results after each phase

### Right Side: The Bulletin Board
- **Yellow notes**: Facts found by Researcher
- **Pink notes**: Suggestions from Editor
- Updates in real-time as agents work

### Bottom: How It Works
- Explanation of memory concepts
- Why agents need shared memory
- READ vs WRITE operations

---

## Technical Details

### Memory Data Structures

```python
# A research finding
Finding(
    content="Global EV sales reached 14 million in 2023",
    source="BloombergNEF",
    credibility_score=0.94,
    extracted_by="Researcher",
    disputes=[],  # Agents who contested this
    timestamp=datetime.now()
)

# Editorial feedback
EditorialFeedback(
    content_section="introduction",
    feedback="Add more context for beginners",
    category="clarity",
    severity=0.5,
    was_addressed=False
)
```

### Orchestrator Flow

```python
orchestrator = ContentCreationOrchestrator()

# Phase 1: Research
result = orchestrator.run_research_phase("AI agents")

# Phase 2: Writing
result = orchestrator.run_writing_phase("AI agents")

# Phase 3: Review (can loop)
result = orchestrator.run_review_phase("AI agents")
# Returns: approval_score, validation_score, combined_score
```

---

## Extending the Project

Ideas for enhancement:

1. **Add Real LLM Calls** - Replace simulated agents with Claude/GPT API calls
2. **Vector Similarity** - Use embeddings for semantic duplicate detection
3. **Persistent Storage** - Save memory to database between sessions
4. **More Agents** - Add a "Social Media Agent" or "SEO Agent"
5. **Async Execution** - Run agents in parallel
6. **Agent Debates** - Let agents discuss before consensus

---

## Learning Points Reference

The code includes numbered "Learning Points" as comments:

| # | Topic | File |
|---|-------|------|
| 1-4 | Configuration Management | config.py |
| 5-16 | Memory Architecture | memory_manager.py |
| 17-26 | Agent Design Patterns | agents.py |
| 27-36 | Orchestration & Consensus | orchestrator.py |

Search for `LEARNING POINT #` in the code to find detailed explanations.

---

## Requirements

- Python 3.8+
- Streamlit 1.28+
- Pandas

Install with:
```bash
pip install streamlit pandas
```

---

## License

MIT License - Feel free to use for learning and projects.

---

## Contributing

Found a bug or have an improvement? Open an issue or PR!

---

Built for learning multi-agent AI systems.
