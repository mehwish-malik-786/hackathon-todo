# Phase III: AI Chatbot - Clarification Document

**Feature Name**: AI-Powered Natural Language Task Management
**Phase**: Phase III
**Date**: 2026-02-28
**Status**: Clarified

---

## Clarification Decisions

### 1. Database Storage

**Decision:** PostgreSQL (Neon)

**Rationale:**
- Already configured in Phase II
- Production-ready for HuggingFace deployment
- Supports concurrent connections
- Conversation history persists across sessions

**Configuration:**
```bash
# backend/.env
DATABASE_URL=postgresql://user:pass@host.db.neon.tech/dbname
```

**Tables Used:**
- `tasks` (existing from Phase II)
- `conversations` (new for Phase III)
- `messages` (new for Phase III)

---

### 2. Auto-Create Tasks

**Decision:** Hybrid Approach

**Auto-Execute (No Confirmation):**
- ✅ Create tasks
- ✅ List tasks
- ✅ Summarize tasks
- ✅ Mark tasks complete

**Require Confirmation:**
- ⚠️ Delete tasks - "Are you sure you want to delete task X?"
- ⚠️ Bulk operations (future)

**Rationale:**
- Fast UX for common operations (create, list, complete)
- Safety for destructive actions (delete)
- Best for demo + personal use

**Example Flow:**
```
User: "Add task buy milk"
AI: "✅ I've created task: 'Buy milk'"  ← Auto

User: "Delete task 3"
AI: "⚠️ Are you sure you want to delete 'Buy milk'? Reply 'yes' to confirm"
User: "yes"
AI: "🗑️ Task deleted"  ← After confirmation
```

---

### 3. Language Support

**Decision:** English + Roman Urdu (Bilingual)

**Primary:** English
**Secondary:** Roman Urdu support via prompt engineering

**Example:**
```
User: "Kal doodh lena hai"  (Roman Urdu)
AI: "✅ Kal doodh lene ka task ban gaya: 'Doodh lena'"

User: "Add task buy milk"  (English)
AI: "✅ I've created task: 'Buy milk'"
```

**Implementation:**
- Qwen2.5 model handles multilingual input
- System prompt updated for Urdu understanding
- Responses match user's language

---

### 4. Memory Requirements

**Decision:** Qwen2.5-0.5B-Instruct (INT8 quantized)

**Resource Budget:**
| Component | RAM | Storage |
|-----------|-----|---------|
| Model (INT8) | ~800 MB | ~500 MB |
| Transformers | ~200 MB | ~100 MB |
| Application | ~200 MB | ~50 MB |
| **Total** | **~1.2 GB** | **~650 MB** |

**HuggingFace Free Tier:** 16GB RAM, 50GB storage ✅

**Fallback:** Rule-based mode if model fails to load (~50MB)

---

### 5. Response Length

**Decision:** Medium (256 tokens max)

**Token Budget:**
- **Short responses:** 20-50 tokens ("✅ Task created")
- **Medium responses:** 100-200 tokens (current)
- **Long responses:** 256 tokens max (explanations)

**Example:**
```
User: "Add task buy milk tomorrow"

AI (Medium): "✅ I've created a task: 'Buy milk' for tomorrow. 
              The task has been added to your list with status 'pending'. 
              You can mark it complete later by saying 'Mark task 1 as done'."
```

**Configuration:**
```python
# backend/services/ai_agent.py
max_new_tokens=256  # Medium length
temperature=0.7     # Balanced creativity
top_p=0.9           # Diverse responses
```

---

## Technical Specifications

### AI Model

| Property | Value |
|----------|-------|
| Model | Qwen/Qwen2.5-0.5B-Instruct |
| Quantization | INT8 (default), FP16 (fallback) |
| Context Window | 10 messages (conversation history) |
| Max Tokens | 256 |
| Temperature | 0.7 |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send message to AI |
| `/api/chat/history/{session_id}` | GET | Get conversation history |
| `/api/chat/health` | GET | Health check |

### Response Format

```json
{
  "response": "AI message text",
  "action": "task_created|tasks_listed|task_deleted|etc",
  "task": { "id": 1, "title": "...", ... },  // optional
  "tasks": [...],  // optional, for list operations
  "conversation_id": 42,
  "metadata": {
    "intent": "create_task",
    "original_message": "Add task buy milk"
  }
}
```

---

## Acceptance Criteria

### Must Have (P0)

- [ ] User can create tasks via natural language (English)
- [ ] User can create tasks via Roman Urdu ("Kal meeting hai")
- [ ] Tasks persist to PostgreSQL database
- [ ] Delete operations require confirmation
- [ ] Conversation history saved per session
- [ ] Response time < 3 seconds (p95)
- [ ] Works on HuggingFace Spaces free tier

### Should Have (P1)

- [ ] Bilingual responses (match user's language)
- [ ] Smart task parsing (extract dates, priorities)
- [ ] Context-aware conversations (remember previous messages)

### Won't Have (Phase III)

- [ ] Urdu script (اردو) support
- [ ] Voice input/output
- [ ] Multi-language beyond Urdu+English
- [ ] Proactive reminders
- [ ] Task attachments

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Model loading fails | High | Auto-fallback to rule-based mode |
| High memory usage | Medium | Use INT8 quantization, limit context |
| Slow responses | Medium | Cache model, use GPU if available |
| Urdu misunderstanding | Low | Clarify with user, show parsed task |
| HuggingFace cold start | Medium | Pre-warm model on deployment |

---

## Dependencies

### External
- HuggingFace Transformers (4.37.0)
- PyTorch (2.2.0)
- Qwen2.5-0.5B-Instruct model

### Internal
- Phase II Task API (existing)
- Phase II Database (PostgreSQL)

---

## Open Questions for sp.plan

1. **Model Caching Strategy:** Should we cache model in `/tmp` or use HuggingFace cache?
2. **GPU vs CPU:** Default to CPU or request GPU in HuggingFace?
3. **Session Management:** Anonymous sessions or require user auth?
4. **Rate Limiting:** Limit chat requests per user?

---

## Next Steps

1. ✅ Clarification complete
2. ⏸️ **Next:** Create `sp.plan` (architecture plan)
3. ⏸️ Create `sp.tasks` (implementation tasks)
4. ✅ Code already implemented (adjust per plan)

---

**Version:** 1.0.0
**Created:** 2026-02-28
**Author:** AI Assistant
**Status:** Clarified - Ready for Planning
