# Phase III: AI Chatbot - Architecture Plan

**Feature Name**: AI-Powered Natural Language Task Management
**Phase**: Phase III (Split into III-A, III-B, III-C)
**Date**: 2026-02-28
**Status**: Planned

---

## Phase Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Phase III-A: Backend Chat API                              │
│  └─ /chat endpoint, HuggingFace model integration           │
│           ↓                                                 │
│  Phase III-B: NLP Task Parser                               │
│  └─ Natural language → task operations, /tasks API connect  │
│           ↓                                                 │
│  Phase III-C: Frontend + Deployment                         │
│  └─ Chat UI, Vercel deployment, HuggingFace backend         │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase III-A: Backend Chat API

### Goal
Create `/chat` API endpoint with HuggingFace Qwen2.5 model integration.

### Architecture

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │────▶│  /chat API   │────▶│  Qwen2.5     │
│   Request    │     │  (FastAPI)   │     │  Model       │
└──────────────┘     └──────────────┘     └──────────────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  PostgreSQL  │
                     │  (conversations,
                     │   messages)  │
                     └──────────────┘
```

### Components

| Component | File | Responsibility |
|-----------|------|----------------|
| Chat Router | `routers/chat.py` | `/chat` endpoint, request/response handling |
| AI Agent | `services/ai_agent.py` | Qwen2.5 model loading, inference |
| MCP Tools | `services/mcp_tools.py` | Task operations interface |
| Models | `models/conversation.py`, `models/message.py` | Database schemas |
| Repositories | `repositories/*_repository.py` | DB operations |

### API Endpoints

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/chat` | POST | `{message, session_id}` | `{response, action, task?, tasks?}` |
| `/api/chat/history/{session_id}` | GET | - | `{messages[]}` |
| `/api/chat/health` | GET | - | `{status}` |

### Model Loading Strategy

**Decision:** Lazy Loading (on first request)

**Rationale:**
- Faster startup time
- HuggingFace Spaces cold start optimization
- Fallback to rule-based if model fails

```python
# services/ai_agent.py
_ai_agent = None

def get_ai_agent():
    global _ai_agent
    if _ai_agent is None:
        _ai_agent = QwenAIAgent()
        _ai_agent.load_model()  # Lazy load
    return _ai_agent
```

### Database Schema

```sql
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversations_session ON conversations(session_id);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
```

### Acceptance Criteria

- [ ] `/api/chat` endpoint accepts messages
- [ ] Qwen2.5 model loads successfully
- [ ] Fallback to rule-based if model fails
- [ ] Conversations saved to PostgreSQL
- [ ] Response time < 3s (p95)
- [ ] Health check endpoint works

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `backend/routers/chat.py` | Create | Chat API routes |
| `backend/services/ai_agent.py` | Create | AI model service |
| `backend/services/mcp_tools.py` | Create | Task tools |
| `backend/models/conversation.py` | Create | Conversation model |
| `backend/models/message.py` | Create | Message model |
| `backend/repositories/conversation_repository.py` | Create | Conversation DB ops |
| `backend/repositories/message_repository.py` | Create | Message DB ops |
| `backend/schemas/chat.py` | Create | Chat schemas |
| `backend/main.py` | Modify | Add chat router |
| `backend/database.py` | Modify | Import new models |
| `backend/requirements.txt` | Modify | Add transformers |

---

## Phase III-B: NLP Task Parser

### Goal
Parse natural language into task operations and connect with `/tasks` API.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  User Message                                               │
│  "Add task buy milk tomorrow"                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Qwen2.5 Model + Prompt Engineering                         │
│  System: "You are a todo assistant. Extract intent..."      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Intent Classification                                      │
│  intent: "create_task"                                      │
│  data: {title: "Buy milk", description: "tomorrow"}         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  MCP Tool Execution                                         │
│  mcp_tools.create_task(title, description)                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Task Repository → PostgreSQL                               │
│  INSERT INTO tasks (title, description) VALUES (...)        │
└─────────────────────────────────────────────────────────────┘
```

### Intent Types

| Intent | Example | Action |
|--------|---------|--------|
| `create_task` | "Add task buy milk" | POST /tasks |
| `list_tasks` | "Show my tasks" | GET /tasks |
| `summarize_tasks` | "Summarize my tasks" | GET /tasks + aggregate |
| `complete_task` | "Mark task 1 as done" | PATCH /tasks/1/complete |
| `delete_task` | "Delete task 3" | DELETE /tasks/3 |
| `update_task` | "Update task 2 to new title" | PUT /tasks/2 |
| `help` | "Help" | Return help text |
| `unknown` | "Random text" | Ask for clarification |

### Prompt Engineering

**System Prompt:**
```
You are a helpful AI assistant for a Todo application.
You support English and Roman Urdu.

Extract intent and parameters from user messages.

Supported intents:
- create_task: {title, description}
- list_tasks: {status?: "pending"|"completed"}
- complete_task: {task_id}
- delete_task: {task_id}
- update_task: {task_id, title}

Examples:
"Add task buy milk tomorrow" → create_task {title: "Buy milk", description: "tomorrow"}
"Kal doodh lena hai" → create_task {title: "Doodh lena", description: "kal"}
"Show pending tasks" → list_tasks {status: "pending"}
```

### Language Support

| Input | Processing | Response |
|-------|------------|----------|
| English | English intent | English |
| Roman Urdu | English intent | Roman Urdu |

**Example:**
```
User (Urdu): "Kal meeting hai"
Intent: create_task {title: "Meeting", description: "kal"}
Response (Urdu): "✅ Kal meeting ka task ban gaya"
```

### Confirmation Strategy (Hybrid)

| Operation | Confirmation? | Example |
|-----------|---------------|---------|
| Create task | ❌ No | Auto-create |
| List tasks | ❌ No | Show immediately |
| Complete task | ❌ No | Auto-complete |
| Delete task | ✅ Yes | "Are you sure?" |
| Update task | ❌ No | Auto-update |

### Error Handling

```python
try:
    result = mcp_tools.create_task(title, description)
    return ChatResponse(response="✅ Task created", task=result)
except TaskNotFoundError:
    return ChatResponse(response="❌ Task not found", action="error")
except Exception as e:
    return ChatResponse(response="Sorry, error occurred", action="error")
```

### Acceptance Criteria

- [ ] English intent detection works (90%+ accuracy)
- [ ] Roman Urdu intent detection works (80%+ accuracy)
- [ ] All CRUD operations connected to /tasks API
- [ ] Delete confirmation implemented
- [ ] Error handling graceful
- [ ] Bilingual responses (English + Urdu)

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `backend/services/ai_agent.py` | Modify | Add prompt engineering |
| `backend/services/mcp_tools.py` | Modify | Connect to /tasks API |
| `backend/tests/test_chat.py` | Create | Chat API tests |

---

## Phase III-C: Frontend + Deployment

### Goal
Build chat UI and deploy to Vercel + HuggingFace.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Next.js on Vercel)                               │
│  /chat page → ChatWindow component                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Backend (FastAPI on HuggingFace Spaces)                    │
│  /api/chat endpoint                                         │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  Database (Neon PostgreSQL)                                 │
│  conversations, messages, tasks                             │
└─────────────────────────────────────────────────────────────┘
```

### Frontend Components

```
frontend/
├── app/
│   └── chat/
│       └── page.tsx              # Chat page route
├── components/
│   ├── ChatWindow.tsx            # Main chat interface
│   ├── MessageBubble.tsx         # Individual message
│   ├── ChatInput.tsx             # Message input
│   └── TypingIndicator.tsx       # Loading state
├── lib/
│   └── chat-api.ts               # API client
└── types/
    └── chat.ts                   # TypeScript types
```

### Chat UI Design

```
┌─────────────────────────────────────────────────────────────┐
│  🤖 AI Chatbot Assistant              [Back to Tasks]       │
│  Manage your tasks with natural language                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ AI: 👋 Welcome! Try:                                │   │
│  │     • "Add task buy milk tomorrow"                  │   │
│  │     • "Show my tasks"                               │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ You: Add task buy milk                              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ AI: ✅ Task created: "Buy milk"                     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  [Type a message...                        ] [Send]         │
└─────────────────────────────────────────────────────────────┘
```

### Session Management

**Decision:** Anonymous sessions with localStorage

```typescript
// frontend/app/chat/page.tsx
function getSessionId(): string {
  let sessionId = localStorage.getItem('chat_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random()}`;
    localStorage.setItem('chat_session_id', sessionId);
  }
  return sessionId;
}
```

### Deployment Configuration

#### HuggingFace Backend

```yaml
# HuggingFace Space Settings
sdk: docker
python_version: "3.12"
gpu: false  # CPU-only for 0.5B model
env:
  DATABASE_URL: ${DATABASE_URL}
  CORS_ORIGINS: https://your-space.hf.space,https://your-app.vercel.app
  TRANSFORMERS_CACHE: /tmp/transformers_cache
```

#### Vercel Frontend

```json
// frontend/vercel.json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-space.hf.space"
  }
}
```

### CORS Configuration

```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",
        "https://your-space.hf.space"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Acceptance Criteria

- [ ] Chat UI accessible at `/chat`
- [ ] Messages display correctly (user/AI bubbles)
- [ ] Loading indicator during AI processing
- [ ] Conversation history loads on page refresh
- [ ] Backend deployed to HuggingFace Spaces
- [ ] Frontend deployed to Vercel
- [ ] CORS configured correctly
- [ ] End-to-end chat works

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `frontend/app/chat/page.tsx` | Create | Chat page |
| `frontend/components/ChatWindow.tsx` | Create | Chat interface |
| `frontend/lib/chat-api.ts` | Create | API client |
| `frontend/types/chat.ts` | Create | TypeScript types |
| `frontend/components/TaskList.tsx` | Modify | Add chat link |
| `frontend/vercel.json` | Create | Vercel config |
| `huggingface-deploy/Dockerfile.huggingface` | Modify | AI deps |
| `huggingface-deploy/requirements.txt` | Modify | transformers |

---

## Implementation Timeline

| Phase | Tasks | Est. Time | Dependencies |
|-------|-------|-----------|--------------|
| **III-A** | Backend API, Models, AI Agent | 4-6 hours | Phase II complete |
| **III-B** | NLP Parser, Task Integration | 3-4 hours | Phase III-A complete |
| **III-C** | Frontend UI, Deployment | 3-4 hours | Phase III-B complete |
| **Total** | | **10-14 hours** | |

---

## Risk Analysis

| Risk | Phase | Impact | Mitigation |
|------|-------|--------|------------|
| Model loading fails | III-A | High | Rule-based fallback |
| NLP accuracy low | III-B | Medium | Prompt engineering, examples |
| Memory limit exceeded | III-A | Medium | INT8 quantization |
| CORS issues | III-C | Low | Test locally first |
| HuggingFace cold start | III-C | Medium | Pre-warm model |

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Intent accuracy (English) | ≥90% | Test suite |
| Intent accuracy (Urdu) | ≥80% | Test suite |
| Response time (p95) | <3s | API monitoring |
| Chat UI load time | <2s | Lighthouse |
| Deployment success | 100% | Manual test |

---

## Next Steps

1. ✅ Phase III Clarification complete
2. ✅ Phase III Plan complete
3. ⏸️ **Next:** Create Phase III Tasks (`sp.tasks`)
4. ⏸️ Implement Phase III-A
5. ⏸️ Implement Phase III-B
6. ⏸️ Implement Phase III-C

---

**Version:** 1.0.0
**Created:** 2026-02-28
**Author:** AI Assistant
**Status:** Planned - Ready for Task Breakdown
