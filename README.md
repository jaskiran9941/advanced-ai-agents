# Advanced AI Agents

A collection of advanced multi-agent AI systems demonstrating sophisticated agentic patterns, agent collaboration, and learning capabilities.

## 🎯 Overview

This repository contains production-grade multi-agent systems that go beyond single-agent architectures. Each project demonstrates advanced AI engineering concepts including agent specialization, orchestration patterns, inter-agent communication, and learning from user behavior.

## 📂 Projects

### 1. [Multi-Agent Podcast Discovery System](./multi-agent-podcast-system)

A sophisticated system with 4 specialized agents coordinated by an orchestrator:
- 🔍 **Discovery Agent**: Finds podcasts using iTunes API
- 📋 **Curator Agent**: Filters content by relevance and novelty
- 🎨 **Personalization Agent**: Adapts summaries to user preferences
- 📬 **Delivery Agent**: Optimizes timing and delivery

**Key Features:**
- True multi-agent architecture with orchestrator pattern
- Learning system that adapts from user behavior
- Persistent state management with SQLite
- Inter-agent communication protocol
- Clean UI with podcast cards

**Tech Stack:** Python, OpenAI GPT-4, Streamlit, SQLite, iTunes API

---

## 🏗️ Evolution Path

These projects build upon foundational work in other repositories:

```
llm-apps ([Podcast summarizer](https://github.com/jaskiran9941/llm-apps/tree/main/podcast-summarizer) - Basic LLM Applications)
    ↓
basic-ai-agents (Single Agentic Agents)
    ↓
advanced-ai-agents (Multi-Agent Systems) ← You are here
```

### From Basic to Advanced

1. **llm-apps/podcast-summarizer**
   - Direct GPT-4 API calls
   - No autonomy or decision-making
   - Single-purpose prompts

2. **basic-ai-agents/agentic-podcast-summarizer**
   - Single agent with tool calling
   - Autonomous decision-making
   - Agentic loop (perceive → reason → act)

3. **advanced-ai-agents/multi-agent-podcast-system**
   - Multiple specialized agents
   - Agent collaboration and communication
   - Learning from user behavior
   - Persistent state management

---

## 🤖 What Makes These "Advanced"?

### Multi-Agent Coordination
- **Orchestrator Pattern**: Central coordinator delegates to specialists
- **Inter-Agent Communication**: Standardized message protocols
- **Shared State**: Centralized database for coordination
- **Parallel Execution**: Agents can work simultaneously

### Learning & Adaptation
- **Behavioral Tracking**: SQLite database tracks all interactions
- **Preference Learning**: Implicit learning from user behavior
- **Feedback Loops**: Decisions linked to outcomes for improvement
- **Multi-Armed Bandit**: 90% exploit best strategies, 10% explore

### Agent Specialization
- Each agent is an expert in its domain
- Modular architecture (add agents without breaking existing ones)
- Independent testing and optimization
- Clear separation of concerns

### Production Patterns
- Error handling and recovery
- Decision traceability (full audit logs)
- Performance tracking per agent
- Scalable architecture

---

## 🚀 Getting Started

Each project has its own detailed README with:
- Setup instructions
- Architecture diagrams
- Usage examples
- Learning outcomes

Navigate to individual project folders to get started!

---

## 📚 Learning Outcomes

By exploring these projects, you'll learn:

### Multi-Agent Systems
- ✅ Orchestrator pattern for coordination
- ✅ Specialized agent architecture
- ✅ Inter-agent communication protocols
- ✅ Shared state management

### Agentic AI
- ✅ Autonomous decision-making
- ✅ Tool calling with OpenAI
- ✅ Perception-reasoning-action-adaptation loop
- ✅ Learning from feedback

### System Design
- ✅ Database-backed state persistence
- ✅ Preference learning algorithms
- ✅ Agent performance tracking
- ✅ Scalable architecture

---

## 🔗 Related Repositories

- **[llm-apps](https://github.com/jaskiran9941/llm-apps)**: Basic LLM applications
- **[basic-ai-agents](https://github.com/jaskiran9941/basic-ai-agents)**: Single agentic agents with tool calling

---

## 🤝 Contributing

These are educational projects demonstrating advanced multi-agent AI systems. Feel free to:
- Experiment with different agent configurations
- Add new specialized agents
- Improve learning algorithms
- Extend to other domains

---

## 📄 License

Educational projects for learning advanced AI agent systems.
