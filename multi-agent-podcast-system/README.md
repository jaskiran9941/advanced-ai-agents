# Multi-Agent Podcast Discovery System

## 🎯 Overview

A sophisticated multi-agent system that coordinates specialized AI agents to discover, curate, personalize, and deliver podcast recommendations. This system demonstrates advanced agentic AI patterns through autonomous agent collaboration, learning from user behavior, and persistent state management.

## 📊 Project Evolution

This project represents the **third iteration** in a learning progression:

```
llm-apps/podcast-summarizer (Basic LLM)
    ↓
basic-ai-agents/agentic-podcast-summarizer (Single Agentic Agent) 
    ↓
basic-ai-agents/multi-agent-podcast-system (Multi-Agent System) ← You are here
```

### Evolution Path

1. **podcast-summarizer** (llm-apps)
   - Basic GPT-4 summarization
   - Direct API calls with prompts
   - No autonomy or decision-making

2. **agentic-podcast-summarizer** (basic-ai-agents)
   - Single agent with tool calling
   - Autonomous decision-making
   - Agentic loop (perceive → reason → act)
   - Real data integration (iTunes API, RSS)

3. **multi-agent-podcast-system** (THIS PROJECT)
   - **4 specialized agents** + orchestrator
   - **Agent collaboration** and communication
   - **Learning system** that adapts to user behavior
   - **Persistent state** with SQLite database
   - **True multi-agent architecture**

---

## 🤖 What Makes This Agentic?

### Core Agentic Properties

This system is **truly agentic** because each agent exhibits:

#### 1. **Autonomy**
- Agents make independent decisions without explicit instructions
- Example: Discovery Agent decides which search strategy to use (broad vs. niche)
- Example: Curator Agent autonomously determines relevance thresholds

#### 2. **Perception**
- Agents observe their environment through tools and shared state
- Discovery Agent: Reads iTunes API responses
- Curator Agent: Analyzes user history from database
- Personalization Agent: Perceives user preferences and context

#### 3. **Reasoning**
- Each agent uses GPT-4 to explain its thinking
- All decisions include reasoning text stored in database
- Example: "Recommending AI podcasts because user saved 5 AI episodes last week"

#### 4. **Action**
- Agents execute tools to affect the environment
- Discovery: Calls iTunes Search API
- Curator: Queries user history database
- Personalization: Generates summaries with GPT-4
- Delivery: Schedules content delivery

#### 5. **Learning & Adaptation**
- System tracks all decisions and outcomes
- Learns user preferences over time (topics, reading times, summary depth)
- Agents query learned preferences to improve future decisions
- Multi-armed bandit approach: 90% exploit best strategies, 10% explore new ones

#### 6. **Goal-Oriented Behavior**
- Each agent has a specific goal
- Discovery: "Find relevant podcasts for user topics"
- Curator: "Filter content by relevance and novelty"
- Personalization: "Adapt presentation to user context"
- Delivery: "Optimize timing and batching"

#### 7. **Proactivity**
- Agents don't just respond—they anticipate needs
- Curator proactively filters low-quality content
- Personalization adapts style without being asked
- Delivery batches content intelligently

### Agentic Loop Pattern

Every agent follows this loop:

```python
while not goal_achieved:
    # 1. PERCEIVE: Get current state
    context = shared_state.get_user_context(user_id)

    # 2. REASON: AI decides what to do
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": goal}],
        tools=self.tools  # Agent chooses which tools to use
    )

    # 3. ACT: Execute chosen tools
    if response.tool_calls:
        for tool_call in response.tool_calls:
            result = execute_tool(tool_call)

    # 4. ADAPT: Observe results, update state
    shared_state.record_decision(agent_name, reasoning, result)
```

---

## 🎭 Why Each Multi-Agent Adds Value

### The Power of Specialization

Instead of one monolithic agent trying to do everything, we have **4 specialized agents** that excel in their domains:

### 1. 🔍 Discovery Agent

**Specialized Role:** Finding podcasts from various sources

**Unique Value:**
- **Search Expertise**: Knows how to query iTunes API effectively
  - Handles rate limits
  - Optimizes search terms
  - Filters by quality (ratings, review count)
- **Multiple Strategies**: Can switch between:
  - Broad discovery (explore new topics)
  - Niche discovery (deep dive on specific interests)
  - Trending content (what's popular now)
- **Source Diversity**: Can integrate multiple APIs (iTunes, Spotify, RSS directories)

**Why Not Just One Agent?**
- Discovery requires specialized knowledge of API quirks and limits
- Different search strategies for different user goals
- Can run in parallel with other agents (async discovery while curator processes previous results)

**Example Decision:**
```
User: "Find me AI podcasts"
Discovery Agent Reasoning:
"User prefers technical content (learned from history).
Using 'artificial intelligence machine learning' as search term
instead of just 'AI' to get higher quality results.
Setting min rating threshold to 4.0."
```

---

### 2. 📋 Curator Agent

**Specialized Role:** Deciding what content deserves attention

**Unique Value:**
- **Relevance Expertise**: Deep understanding of content-user matching
  - Analyzes episode descriptions semantically
  - Compares to user's past interactions
  - Scores relevance 0-1 with confidence intervals
- **Novelty Detection**: Prevents recommendation fatigue
  - Detects duplicate topics
  - Identifies truly new perspectives
  - Balances familiar vs. novel (80/20 rule)
- **Quality Filtering**: Removes low-value content
  - Checks for clickbait
  - Validates episode length vs. topic depth
  - Filters out promotional content

**Why Not Just One Agent?**
- Curation is a distinct skill from discovery
- Requires deep user history analysis
- Different quality heuristics for different content types
- Can prioritize differently based on user context (morning commute = short episodes)

**Example Decision:**
```
Curator Agent Reasoning:
"Episode 'GPT-4 Deep Dive' has 0.89 relevance score
(user saved 3 GPT-related episodes).
However, novelty score is 0.3 - user already listened to
similar content this week. Recommending but with lower priority."
```

---

### 3. 🎨 Personalization Agent

**Specialized Role:** Adapting content presentation

**Unique Value:**
- **Style Adaptation**: Masters different communication styles
  - Technical depth varies by user expertise
  - Casual vs. professional tone
  - Summary length (brief/detailed/comprehensive)
- **Context Awareness**: Adjusts to user situation
  - Time of day (morning brief vs. evening deep dive)
  - Device (mobile = shorter, desktop = detailed)
  - User mood (inferred from interaction patterns)
- **GPT-4 Mastery**: Specialized in prompt engineering
  - Optimizes summary generation
  - Handles edge cases (missing metadata, unclear topics)
  - Maintains consistent voice

**Why Not Just One Agent?**
- Personalization requires separate expertise from content discovery
- Different prompts for different user segments
- Can learn style preferences independently
- Allows A/B testing of presentation strategies

**Example Decision:**
```
Personalization Agent Reasoning:
"User reads content at 7am on weekdays (learned preference).
Generating 3-4 bullet point summary (brief style).
Using technical terminology—user has ML background.
Highlighting practical applications over theory."
```

---

### 4. 📬 Delivery Agent

**Specialized Role:** Optimizing when and how content reaches users

**Unique Value:**
- **Timing Optimization**: Finds best delivery windows
  - Analyzes historical read patterns
  - Identifies high-engagement time slots
  - Avoids low-attention periods
- **Batching Intelligence**: Groups content strategically
  - Related topics together
  - Urgent vs. can-wait separation
  - Digest creation (daily/weekly)
- **Channel Selection**: Chooses optimal delivery method
  - In-app notification
  - Email digest
  - Push notification
  - Scheduled delivery

**Why Not Just One Agent?**
- Delivery optimization is a unique skill set
- Requires temporal analysis of user behavior
- Different strategies for different content urgency
- Can learn scheduling independently from content quality

**Example Decision:**
```
Delivery Agent Reasoning:
"User has 85% read rate at 7:15am on weekdays.
Batching 3 AI podcast summaries for tomorrow 7am delivery.
Using email digest format (user prefers email over push).
Adding 'Urgent: Industry news' tag for one time-sensitive episode."
```

---

## 🏗️ Orchestrator: The Coordinator

**Role:** Routes tasks and aggregates results

**Value of Orchestrator Pattern:**
- **Single Entry Point**: User interacts with one interface
- **Workflow Management**: Coordinates agent execution order
- **Error Handling**: Manages failures gracefully
- **Result Aggregation**: Combines outputs into coherent response
- **Task Decomposition**: Breaks user goals into agent-specific subtasks

**Workflow Example:**
```
User: "Find me AI podcasts"
    ↓
Orchestrator classifies intent: "discovery_with_curation"
    ↓
Discovery Agent: Finds 10 AI podcasts
    ↓
Curator Agent: Filters to 5 most relevant
    ↓
Personalization Agent: Generates custom summaries
    ↓
Delivery Agent: Schedules for 7am tomorrow
    ↓
Result returned to user
```

---

## 💡 Multi-Agent Benefits Over Single Agent

### Comparison Table

| Aspect | Single Agent | Multi-Agent System |
|--------|-------------|-------------------|
| **Specialization** | General-purpose, jack-of-all-trades | Experts in specific domains |
| **Scalability** | Adding features makes it more complex | Add new agents without touching existing ones |
| **Parallel Execution** | Sequential only | Discovery + Curator can run in parallel |
| **Learning** | One model learns everything | Each agent learns its specialty |
| **Debugging** | Hard to trace which part failed | Clear agent responsibility |
| **Testing** | Must test entire system | Can test agents independently |
| **Maintainability** | Monolithic codebase | Modular, clean separation |
| **Performance** | All or nothing | Can optimize each agent separately |

### Concrete Example: Why Multi-Agent Wins

**User Request:** "Find me ML podcasts but I'm in a rush"

**Single Agent Approach:**
```
Agent: Searches, filters, summarizes, schedules all in one loop
- 45 second total latency
- Hard to optimize (which step is slow?)
- Must redo everything if summary style changes
```

**Multi-Agent Approach:**
```
Discovery (5s) ──┐
                 ├──> Curator (3s) ──> Personalization (4s, detects "rush", uses brief style) ──> Delivery (1s, immediate delivery)
                 │
                 └──> Can cache discovery results for future requests

- 13 second total latency (optimized each agent)
- Clear bottleneck identification
- Can reuse discovery results with different personalization
```

---

## 🧠 Learning System

### How the System Gets Smarter

**Data Collection:**
- Every user interaction (click, save, dismiss) → `interactions` table
- Every agent decision → `agent_decisions` table
- Links between decisions and outcomes → `decision_outcomes` table

**Learning Cycle:**
```
1. User clicks "Save" on AI podcast summary
   ↓
2. System links save action to Discovery Agent's decision
   ↓
3. Updates learned_preferences: {"preferred_topics": "AI", confidence: 0.85}
   ↓
4. Next time Discovery Agent queries preferences
   ↓
5. Prioritizes AI content in search results
```

**Feedback Loop:**
- **Explicit signals**: Saves (weight: 1.0), Dismisses (weight: -0.5)
- **Implicit signals**: Reading time (weight: 0.6), Scroll depth (weight: 0.4)
- **Temporal decay**: Recent behavior matters more (last 30 days weighted 2x)

---

## 🏛️ Architecture

```
User Goal → Orchestrator Agent
              ↓
    ┌─────────┼─────────┬──────────┬──────────┐
    ▼         ▼         ▼          ▼          ▼
Discovery  Curator  Personalization  Delivery
  Agent     Agent       Agent          Agent
    │         │           │              │
    └─────────┴───────────┴──────────────┘
                    ↓
            Shared State Manager (SQLite)
                    ↓
            Learning Engine
```

### Key Components

1. **Shared State Manager**: Central database for agent coordination
2. **Message Protocol**: Standardized inter-agent communication
3. **Learning Engine**: Preference learning and adaptation
4. **Tool Layer**: Abstracts external APIs (iTunes, RSS, GPT-4)

---

## 🚀 Setup & Usage

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

```bash
cd multi-agent-podcast-system
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your OpenAI API key to .env
```

### Run the System

```bash
streamlit run app.py
```

Visit `http://localhost:8503` and:
1. Enter your OpenAI API key in the sidebar
2. Type a goal: "Find me AI and machine learning podcasts"
3. Click "🚀 Run Multi-Agent System"
4. Watch agents collaborate!

---

## 📂 Project Structure

```
multi-agent-podcast-system/
├── README.md                       # This file
├── requirements.txt                # Dependencies
├── app.py                          # Streamlit UI
│
├── database/
│   ├── schema.sql                  # SQLite schema (learning data)
│   └── db_manager.py               # Database operations
│
├── core/
│   ├── shared_state.py             # Central state management
│   ├── message_protocol.py         # Inter-agent communication
│   └── learning_engine.py          # Preference learning
│
├── orchestrator/
│   └── orchestrator_agent.py       # Coordinator agent
│
├── agents/
│   ├── base_agent.py               # Abstract base class
│   ├── discovery_agent.py          # 🔍 Podcast discovery
│   ├── curator_agent.py            # 📋 Content curation
│   ├── personalization_agent.py    # 🎨 Summary personalization
│   └── delivery_agent.py           # 📬 Delivery optimization
│
└── tools/
    ├── podcast_tools.py            # iTunes API, RSS parsing
    ├── summarization_tools.py      # GPT-4 summarization
    ├── analysis_tools.py           # Relevance scoring
    └── scheduling_tools.py         # Delivery timing
```

---

## 🎓 Learning Outcomes

By studying this project, you'll learn:

### Multi-Agent Patterns
- ✅ Orchestrator pattern for agent coordination
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

## 🔮 Future Enhancements

1. **More Agents**:
   - Research Agent (deep dives via arXiv, papers)
   - Social Agent (sharing recommendations)
   - Analytics Agent (performance insights)

2. **Advanced Learning**:
   - Embeddings for semantic similarity
   - Reinforcement learning for agent strategies
   - Multi-user collaborative filtering

3. **Production Features**:
   - Multi-user support (already in schema!)
   - Voice interface (Delivery agent speaks)
   - Mobile app (React Native frontend)
   - Real-time updates (WebSockets)

---

## 📚 Related Projects

- **podcast-summarizer** (llm-apps): Basic GPT-4 summarization
- **agentic-podcast-summarizer** (basic-ai-agents): Single agentic agent with tools

---

## 🤝 Contributing

This is an educational project demonstrating multi-agent AI systems. Feel free to:
- Experiment with different agent configurations
- Add new specialized agents
- Improve learning algorithms
- Extend to other content types (articles, videos, etc.)

---

## 📄 License

Educational project for learning multi-agent AI systems.

---

**Built to demonstrate:**
- True multi-agent architecture
- Agent specialization and collaboration
- Learning from user behavior
- Autonomous decision-making
- Scalable system design
