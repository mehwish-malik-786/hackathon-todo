# Phase III: AI Chatbot - Implementation Tasks

**Feature Name**: AI-Powered Natural Language Task Management
**Phase**: Phase III (A, B, C)
**Date**: 2026-02-28
**Status**: Ready for Implementation

---

## Task Overview

```
┌─────────────────────────────────────────────────────────────┐
│ Phase III-A: Backend (T001-T003)                            │
│ Phase III-B: Integration (T004-T005)                        │
│ Phase III-C: Frontend + Deploy (T006-T009)                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Phase III-A: Backend Tasks

### T001: Create backend/chat_router.py

**Status:** ✅ Complete (already implemented)

**File:** `backend/routers/chat.py`

**Implementation:**
```python
from fastapi import APIRouter, Depends
from sqlmodel import Session
from schemas.chat import ChatRequest, ChatResponse
from services.ai_agent import get_ai_agent
from services.mcp_tools import MCPTaskTools
from database import get_session

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    session: Session = Depends(get_session),
):
    """Process chat message and return AI response."""
    # 1. Get AI agent
    ai_agent = get_ai_agent()
    
    # 2. Process message
    result = ai_agent.process_message(request.message)
    
    # 3. Execute MCP tool based on intent
    mcp_tools = MCPTaskTools(session)
    # ... tool execution
    
    # 4. Return response
    return ChatResponse(
        response=ai_response,
        action=action,
        task=task_data,
        conversation_id=conversation.id
    )
```

**Acceptance Criteria:**
- [x] `/api/chat` POST endpoint works
- [x] Accepts `{message, session_id}`
- [x] Returns `{response, action, task?, conversation_id}`
- [x] Health check endpoint `/api/chat/health`

**Testing:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task test", "session_id": "test-123"}'
```

**Time:** 1 hour
**Priority:** P0

---

### T002: Add huggingface_client.py (AI Agent Service)

**Status:** ✅ Complete (already implemented)

**File:** `backend/services/ai_agent.py`

**Implementation:**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

class QwenAIAgent:
    def __init__(self, model_name="Qwen/Qwen2.5-0.5B-Instruct"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self.generator = None
    
    def load_model(self):
        """Load Qwen2.5 model from HuggingFace."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto",
        )
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=256,
        )
    
    def process_message(self, message: str) -> dict:
        """Parse intent and generate response."""
        # Rule-based intent detection (fallback)
        intent, data = self._parse_intent_rule_based(message)
        
        # LLM response generation
        response = self._generate_response(intent, data)
        
        return {
            "intent": intent,
            "data": data,
            "response": response
        }
```

**Acceptance Criteria:**
- [x] Qwen2.5 model loads from HuggingFace
- [x] Lazy loading (on first request)
- [x] Fallback to rule-based if model fails
- [x] Supports English + Roman Urdu
- [x] Response time < 3s

**Testing:**
```python
from services.ai_agent import QwenAIAgent

agent = QwenAIAgent()
agent.load_model()

result = agent.process_message("Add task buy milk")
assert result["intent"] == "create_task"
```

**Time:** 2 hours
**Priority:** P0

---

### T003: Add Environment Variable HF_TOKEN

**Status:** ⏸️ TODO

**Files to Modify:**
- `backend/.env`
- `backend/.env.example`
- `huggingface-deploy/.env`

**Implementation:**

**backend/.env:**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host.db.neon.tech/dbname
API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000

# AI Configuration
HF_TOKEN=your_huggingface_token_here
TRANSFORMERS_CACHE=/tmp/transformers_cache
HF_HOME=/tmp/huggingface
```

**backend/.env.example:**
```bash
DATABASE_URL=postgresql://...
API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000

# Get HF_TOKEN from: https://huggingface.co/settings/tokens
HF_TOKEN=
TRANSFORMERS_CACHE=/tmp/transformers_cache
```

**How to Get HF_TOKEN:**
1. Go to https://huggingface.co/settings/tokens
2. Login/Signup
3. Create new token (type: "read")
4. Copy token to `.env`

**Acceptance Criteria:**
- [ ] `.env` file has HF_TOKEN
- [ ] `.env.example` has HF_TOKEN placeholder
- [ ] Token used in ai_agent.py for model loading
- [ ] Token not committed to git

**Time:** 15 minutes
**Priority:** P0

---

## Phase III-B: Integration Tasks

### T004: Connect NLP Parser with /tasks API

**Status:** ✅ Complete (already implemented)

**File:** `backend/services/mcp_tools.py`

**Implementation:**
```python
class MCPTaskTools:
    def __init__(self, session: Session):
        self.session = session
        self.repository = TaskRepository(session)
    
    def create_task(self, title: str, description: str = None) -> dict:
        """Create task via repository."""
        task = Task(title=title, description=description)
        created = self.repository.add(task)
        return {
            "success": True,
            "action": "task_created",
            "task": self._task_to_dict(created)
        }
    
    def list_tasks(self, status: str = None) -> dict:
        """List tasks with optional filter."""
        tasks = self.repository.get_all()
        if status:
            tasks = [t for t in tasks if t.status == status]
        return {
            "success": True,
            "tasks": [self._task_to_dict(t) for t in tasks]
        }
```

**Intent → API Mapping:**

| Intent | MCP Tool | API Endpoint |
|--------|----------|--------------|
| create_task | `create_task()` | POST /tasks |
| list_tasks | `list_tasks()` | GET /tasks |
| complete_task | `complete_task()` | PATCH /tasks/{id}/complete |
| delete_task | `delete_task()` | DELETE /tasks/{id} |
| update_task | `update_task()` | PUT /tasks/{id} |

**Acceptance Criteria:**
- [x] All CRUD operations connected
- [x] Delete requires confirmation (hybrid approach)
- [x] Error handling implemented
- [x] Bilingual responses (English + Urdu)

**Testing:**
```bash
# Test create
curl -X POST http://localhost:8000/api/chat \
  -d '{"message": "Add task buy milk", "session_id": "test"}'

# Test list
curl -X POST http://localhost:8000/api/chat \
  -d '{"message": "Show my tasks", "session_id": "test"}'

# Test delete (with confirmation)
curl -X POST http://localhost:8000/api/chat \
  -d '{"message": "Delete task 1", "session_id": "test"}'
```

**Time:** 1.5 hours
**Priority:** P0

---

## Phase III-C: Frontend + Deployment

### T005: Create frontend ChatBox.jsx (ChatWindow.tsx)

**Status:** ✅ Complete (already implemented)

**File:** `frontend/components/ChatWindow.tsx`

**Implementation:**
```tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { chatApi } from '@/lib/chat-api';
import { ChatMessage } from '@/types/chat';

export default function ChatWindow({ sessionId }: { sessionId: string }) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const sendMessage = async () => {
    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);

    // Send to API
    const response = await chatApi.sendMessage({
      message: userMessage,
      session_id: sessionId
    });

    // Add AI response
    setMessages(prev => [...prev, {
      role: 'assistant',
      content: response.data.response
    }]);

    setIsLoading(false);
  };

  return (
    <div className="chat-window">
      {/* Messages */}
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>

      {/* Input */}
      <form onSubmit={sendMessage}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button type="submit" disabled={isLoading}>
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </form>
    </div>
  );
}
```

**Acceptance Criteria:**
- [x] Chat UI at `/chat` route
- [x] User/AI message bubbles
- [x] Loading indicator
- [x] Conversation history loads
- [x] Auto-scroll to bottom

**Time:** 2 hours
**Priority:** P0

---

### T006: Test Locally

**Status:** ⏸️ TODO

**Steps:**

**1. Start Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**2. Start Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**3. Test Chat:**
- Open http://localhost:3000/chat
- Send message: "Add task buy milk"
- Verify task created in database
- Send: "Show my tasks"
- Verify tasks listed

**4. Test API Directly:**
```bash
# Health check
curl http://localhost:8000/api/chat/health

# Create task via chat
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task test locally", "session_id": "local-test"}'

# Get history
curl http://localhost:8000/api/chat/history/local-test
```

**5. Run Tests:**
```bash
cd backend
pytest tests/test_chat.py -v
```

**Acceptance Criteria:**
- [ ] Backend starts without errors
- [ ] Frontend builds successfully
- [ ] Chat UI accessible
- [ ] Messages send/receive
- [ ] Tasks created in DB
- [ ] All tests pass

**Time:** 1 hour
**Priority:** P0

---

### T007: Deploy Backend to HuggingFace

**Status:** ⏸️ TODO

**Steps:**

**1. Update HuggingFace Space Settings:**
- Go to https://huggingface.co/spaces/YOUR_USERNAME/hackathon-todo-backend
- Settings → Variables
- Add environment variables:
  ```
  DATABASE_URL=your-neon-db-url
  API_URL=https://your-space.hf.space
  CORS_ORIGINS=https://your-app.vercel.app
  HF_TOKEN=your-token
  ```

**2. Update Files:**
```bash
# Ensure huggingface-deploy/ has:
- Dockerfile.huggingface (with transformers)
- requirements.txt (with AI deps)
- backend/ (all code)
```

**3. Push to HuggingFace:**
```bash
cd huggingface-deploy
git add .
git commit -m "Phase III: Add AI chatbot with Qwen2.5"
git push origin main
```

**4. Factory Rebuild:**
- Go to Space dashboard
- Settings → Factory Rebuild
- Click "Rebuild"
- Wait 5-10 minutes

**5. Test Deployment:**
```bash
# Health check
curl https://your-space.hf.space/api/chat/health

# Test chat
curl -X POST https://your-space.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task deployed", "session_id": "hf-test"}'
```

**Acceptance Criteria:**
- [ ] Space builds successfully
- [ ] Health check returns 200
- [ ] Chat API works
- [ ] CORS configured for Vercel
- [ ] Model loads (or fallback works)

**Time:** 2 hours (including model download)
**Priority:** P0

---

### T008: Redeploy Frontend to Vercel

**Status:** ⏸️ TODO

**Steps:**

**1. Update Environment Variables:**
```bash
cd frontend
vercel env add NEXT_PUBLIC_API_URL production
# Enter: https://your-space.hf.space
```

**2. Update vercel.json:**
```json
{
  "env": {
    "NEXT_PUBLIC_API_URL": "https://your-space.hf.space"
  }
}
```

**3. Deploy:**
```bash
cd frontend
vercel --prod
```

**4. Update CORS in Backend:**
- Edit backend `.env` on HuggingFace
- Add Vercel URL to CORS_ORIGINS:
  ```
  CORS_ORIGINS=https://your-app.vercel.app,http://localhost:3000
  ```
- Rebuild Space

**5. Test:**
- Open https://your-app.vercel.app/chat
- Send test message
- Verify end-to-end works

**Acceptance Criteria:**
- [ ] Frontend deploys successfully
- [ ] `/chat` page accessible
- [ ] Chat connects to HuggingFace backend
- [ ] No CORS errors
- [ ] Messages send/receive

**Time:** 1 hour
**Priority:** P0

---

## Summary Table

| ID | Task | Phase | Status | Est. Time | Priority |
|----|------|-------|--------|-----------|----------|
| T001 | Create chat_router.py | III-A | ✅ Complete | 1h | P0 |
| T002 | Add huggingface_client.py | III-A | ✅ Complete | 2h | P0 |
| T003 | Add env HF_TOKEN | III-A | ⏸️ TODO | 15m | P0 |
| T004 | Connect NLP with /tasks API | III-B | ✅ Complete | 1.5h | P0 |
| T005 | Create frontend ChatBox.jsx | III-C | ✅ Complete | 2h | P0 |
| T006 | Test locally | III-C | ⏸️ TODO | 1h | P0 |
| T007 | Deploy backend to HF | III-C | ⏸️ TODO | 2h | P0 |
| T008 | Redeploy frontend to Vercel | III-C | ⏸️ TODO | 1h | P0 |

**Total:** 8 tasks (5 complete, 3 TODO)
**Remaining Time:** ~4.25 hours

---

## Next Actions

1. **T003:** Add HF_TOKEN to `.env`
2. **T006:** Test locally
3. **T007:** Deploy backend
4. **T008:** Redeploy frontend

---

## Testing Checklist

### Backend Tests
```bash
cd backend
pytest tests/test_chat.py -v
```

**Expected Output:**
```
✅ test_chat_health
✅ test_chat_create_task
✅ test_chat_list_tasks
✅ test_chat_complete_task
✅ test_chat_delete_task
✅ test_conversation_history
```

### Frontend Tests
```bash
cd frontend
npm run build
npm run test
```

**Expected Output:**
```
✅ Compiled successfully
✅ No TypeScript errors
✅ Tests pass
```

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] `.env` has HF_TOKEN
- [ ] CORS configured
- [ ] Database migrations run

### Backend (HuggingFace)
- [ ] Space builds
- [ ] Model loads
- [ ] API responds
- [ ] Health check passes

### Frontend (Vercel)
- [ ] Build succeeds
- [ ] `/chat` accessible
- [ ] Backend connects
- [ ] No console errors

### Post-Deployment
- [ ] End-to-end chat works
- [ ] Tasks persist to DB
- [ ] Conversation history loads
- [ ] Mobile responsive

---

**Version:** 1.0.0
**Created:** 2026-02-28
**Author:** AI Assistant
**Status:** Ready for Implementation (5/8 complete)
