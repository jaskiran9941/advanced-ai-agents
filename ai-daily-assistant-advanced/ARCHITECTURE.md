# Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         SLACK WORKSPACE                         │
│  ┌──────────────┐              ┌──────────────┐                 │
│  │   Channels   │              │  Direct DMs  │                 │
│  │              │              │              │                 │
│  │  @EmailBot   │              │   User ↔ Bot │                 │
│  └──────┬───────┘              └──────┬───────┘                 │
│         │                              │                         │
└─────────┼──────────────────────────────┼─────────────────────────┘
          │         Socket Mode           │
          │      (WebSocket)              │
          ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SLACK BOT LAYER                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  src/slack/bot.py - Slack Bolt App                       │   │
│  │  - Socket Mode Handler                                   │   │
│  │  - Event routing                                         │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │  src/slack/handlers.py - Message Handlers                │   │
│  │  - App mentions (@bot)                                   │   │
│  │  - Direct messages                                       │   │
│  │  - Thread context management                            │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     AI AGENT LAYER                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  src/agent/runner.py - Agent Executor                    │   │
│  │  - LangChain agent orchestration                         │   │
│  │  - Session management (per thread)                       │   │
│  │  - Chat history tracking                                 │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
│          ┌──────────┼──────────┐                                │
│          ▼          ▼          ▼                                │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐                  │
│  │ Anthropic  │ │  OpenAI    │ │  Future... │                  │
│  │   Claude   │ │   GPT-4    │ │   (Ollama) │                  │
│  └────────────┘ └────────────┘ └────────────┘                  │
│         │                                                        │
│  src/agent/providers.py - AI Provider Factory                   │
│  - Multi-provider abstraction                                   │
│  - Provider switching                                           │
│                                                                 │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TOOL LAYER                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  src/agent/tools/registry.py - Tool Registry             │   │
│  │  - Tool registration                                     │   │
│  │  - Allowlist/blocklist filtering                        │   │
│  │  - LangChain tool conversion                            │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │  src/agent/tools/email_tools.py - Email Tools           │   │
│  │                                                          │   │
│  │  ┌─────────────────┐  ┌─────────────────┐              │   │
│  │  │  list_unread    │  │ search_emails   │              │   │
│  │  └─────────────────┘  └─────────────────┘              │   │
│  │  ┌─────────────────┐  ┌─────────────────┐              │   │
│  │  │ get_email_by_id │  │get_sender_emails│              │   │
│  │  └─────────────────┘  └─────────────────┘              │   │
│  │  ┌─────────────────┐                                   │   │
│  │  │summarize_thread │                                   │   │
│  │  └─────────────────┘                                   │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   GMAIL INTEGRATION LAYER                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  src/gmail/client.py - Gmail API Client                 │   │
│  │  - OAuth 2.0 authentication                             │   │
│  │  - Email search & retrieval                             │   │
│  │  - Thread operations                                    │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
│  ┌──────────────────▼───────────────────────────────────────┐   │
│  │  src/gmail/parser.py - Email Parser                     │   │
│  │  - HTML to text conversion                              │   │
│  │  - Header extraction                                    │   │
│  │  - Multipart handling                                   │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                           │
└─────────────────────┼───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    GMAIL API (Google)                           │
│  - OAuth secured                                                │
│  - Read-only access                                             │
│  - 250 quota units/second                                       │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### User Query Flow

```
1. User sends message in Slack
   └─> "@EmailBot What are my unread emails?"

2. Slack sends event to bot (Socket Mode WebSocket)
   └─> Event type: app_mention or message.im

3. MessageHandler receives event
   └─> Extracts text, user, channel, thread info
   └─> Sends "thinking" indicator

4. AgentRunner processes query
   └─> Creates session ID (channel:thread)
   └─> Loads chat history for context
   └─> Invokes LangChain agent with query + history

5. AI Provider (Claude/GPT) analyzes query
   └─> Determines which tools to call
   └─> Plans execution steps

6. ToolRegistry executes requested tool
   └─> Filters by allowlist/blocklist
   └─> Calls tool function (e.g., list_unread)

7. EmailTools queries Gmail API
   └─> GmailClient authenticates with OAuth
   └─> Fetches messages matching criteria
   └─> EmailParser extracts structured data

8. Tool returns results to agent
   └─> Agent formats response
   └─> Updates session history

9. Bot sends response to Slack
   └─> Formatted message in thread
   └─> User sees answer

10. Session preserved for follow-up questions
    └─> Context maintained in SessionManager
```

## Component Interactions

### Configuration Flow
```
.env file
    ↓
settings.py (Pydantic validation)
    ↓
┌───────────┬───────────┬───────────┐
│   Slack   │  Gmail    │    AI     │
│  Settings │ Settings  │ Settings  │
└─────┬─────┴─────┬─────┴─────┬─────┘
      │           │           │
      ▼           ▼           ▼
   SlackBot  GmailClient  AIProvider
```

### Tool Execution Flow
```
User Query → Agent → Tool Selection
                         ↓
                    ToolRegistry
                         ↓
                 Check allowlist/blocklist
                         ↓
                    Execute Tool
                         ↓
              Tool calls GmailClient
                         ↓
              Gmail API returns data
                         ↓
              Parser formats data
                         ↓
              Return to Agent
                         ↓
              AI formats response
                         ↓
              Send to Slack
```

## Key Design Patterns

### 1. Provider Pattern (AI)
```python
AIProviderFactory
    ├─> AnthropicProvider (Claude)
    ├─> OpenAIProvider (GPT-4)
    └─> Future: OllamaProvider (local)

Benefits:
- Easy to switch providers
- Fallback support
- Consistent interface
```

### 2. Registry Pattern (Tools)
```python
ToolRegistry
    ├─> register(tool)
    ├─> filter(allowlist/blocklist)
    └─> execute(tool_name, **kwargs)

Benefits:
- Centralized tool management
- Policy enforcement
- Dynamic tool loading
```

### 3. Session Pattern (Conversations)
```python
SessionManager
    ├─> get_history(session_id)
    ├─> add_message(session_id, role, content)
    └─> clear_session(session_id)

Sessions keyed by: channel_id:thread_ts

Benefits:
- Isolated conversations
- Context preservation
- Multi-user support ready
```

### 4. Adapter Pattern (Messaging)
```python
SlackBot (current)
    └─> handlers.py

Future: WhatsAppBot, TelegramBot
    └─> Same handler interface

Benefits:
- Channel-agnostic core
- Easy to add channels
- Unified message handling
```

## Extensibility Points

### Adding New Tools
```
1. Create tool function in email_tools.py
2. Register with ToolRegistry
3. Add to allowlist in settings
4. Tool automatically available to AI
```

### Adding New AI Provider
```
1. Add provider case in providers.py
2. Install provider's SDK
3. Add config to settings.py
4. Add API key to .env
5. Set as default or use selectively
```

### Adding New Channel
```
1. Create src/[channel]/ directory
2. Implement bot.py, handlers.py
3. Register handlers in main.py
4. Channel works with same agent/tools
```

### Adding New Data Source
```
1. Create src/[datasource]/ client
2. Create tools/[datasource]_tools.py
3. Register tools with registry
4. AI can now use new data source
```

## Security Architecture

### Authentication Flow
```
User ──────────────────────> Slack Workspace
                                    │
                      OAuth 2.0     │
                    ┌───────────────▼
                    │   Slack API
                    │   (validates bot token)
                    │
Bot <───────────────┘

Bot ─────────────> Gmail API
         │              │
         │    OAuth 2.0 │
         │              │
         └──────────────▼
              Google Auth Server
                    │
          Token cached locally
          (token.json)
```

### Data Privacy
- **Gmail**: Read-only access, OAuth secured
- **Slack**: Bot can only read messages it's mentioned in
- **AI Providers**: Data sent to Claude/OpenAI APIs
- **Local Storage**: OAuth tokens stored locally (encrypted in production)

### Future Security Enhancements
1. Token encryption at rest
2. User-based authentication
3. Audit logging
4. Rate limiting
5. Secret management service

## Deployment Architecture (Future - Phase 4)

### Development (Current)
```
Local Machine
    ├─> Python process (main.py)
    ├─> Socket Mode (WebSocket to Slack)
    ├─> Gmail API (direct calls)
    └─> AI Provider APIs (direct calls)
```

### Production (Planned)
```
Cloud Platform (AWS/GCP/Azure)
    ├─> Load Balancer
    │       └─> Bot Instances (auto-scaling)
    │
    ├─> Redis (caching + sessions)
    │
    ├─> PostgreSQL (user data + audit logs)
    │
    ├─> ChromaDB (vector search)
    │
    └─> Pub/Sub (Gmail real-time updates)
```

## Performance Characteristics

### Current (MVP)
- **Latency**: 3-7 seconds per query
- **Concurrency**: Single-threaded (dev)
- **Caching**: None
- **Rate limits**: Gmail 250/sec, AI provider limits

### Target (Production)
- **Latency**: <2 seconds per query
- **Concurrency**: Multi-process with load balancing
- **Caching**: Redis for frequent queries
- **Rate limits**: Managed with queuing + backoff

## Monitoring & Observability (Future)

### Planned Metrics
- Query latency (p50, p95, p99)
- Tool execution time
- AI provider response time
- Gmail API quota usage
- Error rates by component
- Active sessions count

### Planned Logging
- Structured logs (JSON)
- Centralized logging (CloudWatch/Stackdriver)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Correlation IDs for request tracing

## Scalability Considerations

### Vertical Scaling
- Increase instance size
- Add more workers
- Optimize tool execution

### Horizontal Scaling
- Multiple bot instances
- Load balancer
- Shared Redis for sessions
- Shared database

### Caching Strategy
- Redis: Session data, frequent queries
- ChromaDB: Pre-indexed emails
- Local: OAuth tokens (encrypted)

## Future Architecture Enhancements

### Phase 3: Vector Database
```
Background Worker
    ↓
Gmail Sync ──> Embeddings ──> ChromaDB
                                 ↓
                            Semantic Search Tool
```

### Phase 4: Production
```
Pub/Sub (Gmail) ──> Queue ──> Background Workers
                                      ↓
                              Real-time Updates
```

### Phase 5: Multi-Channel
```
WhatsApp ─┐
Telegram  ├──> Unified Message Handler ──> Agent
iMessage  ─┘
Discord
```

---

**Current Status:** ✅ Phase 1 Architecture Complete

The architecture is designed to be:
- **Modular**: Easy to modify components independently
- **Extensible**: Simple to add tools, channels, providers
- **Scalable**: Ready for production deployment
- **Secure**: OAuth, secrets management, audit logging
- **Observable**: Structured logging, metrics ready
