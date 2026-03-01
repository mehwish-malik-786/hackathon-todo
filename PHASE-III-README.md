# Phase III: AI Chatbot Deployment Guide

## Overview

Phase III adds an AI-powered chatbot interface to your Todo app using:
- **Qwen2.5-0.5B-Instruct** - Lightweight LLM from HuggingFace
- **Natural Language Processing** - Understand commands like "Add task buy milk tomorrow"
- **MCP Tools** - AI can create, list, update, delete, and complete tasks
- **Conversation History** - Chat sessions are persisted in database

---

## Quick Start

### 1. Update Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create/update `backend/.env`:

```bash
DATABASE_URL=postgresql://user:pass@host/db
API_URL=http://localhost:8000
CORS_ORIGINS=http://localhost:3000

# AI Configuration (optional - uses rule-based fallback if not set)
OPENAI_API_KEY=your-key-if-using-openai
```

### 3. Run Backend

```bash
cd backend
uvicorn main:app --reload --port 8000
```

The AI agent will initialize with Qwen2.5 model. If the model fails to load (due to memory constraints), it automatically falls back to rule-based pattern matching.

### 4. Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit:
- **Main App**: http://localhost:3000
- **AI Chat**: http://localhost:3000/chat
- **API Docs**: http://localhost:8000/docs

---

## Chat API Endpoints

### POST /api/chat

Send a message to the AI chatbot.

**Request:**
```json
{
  "message": "Add task buy milk tomorrow",
  "session_id": "my-session-123"
}
```

**Response:**
```json
{
  "response": "✅ I've created task: 'Buy milk'",
  "action": "task_created",
  "task": {
    "id": 1,
    "title": "Buy milk",
    "description": "Created via AI chat - tomorrow",
    "status": "pending"
  },
  "conversation_id": 42,
  "metadata": {
    "intent": "create_task",
    "original_message": "Add task buy milk tomorrow"
  }
}
```

### GET /api/chat/history/{session_id}

Get conversation history for a session.

**Response:**
```json
{
  "session_id": "my-session-123",
  "messages": [
    {
      "id": 1,
      "role": "user",
      "content": "Add task buy milk",
      "created_at": "2026-02-28T10:30:00Z"
    },
    {
      "id": 2,
      "role": "assistant",
      "content": "✅ I've created task: 'Buy milk'",
      "created_at": "2026-02-28T10:30:01Z"
    }
  ]
}
```

---

## Supported Commands

The AI chatbot understands natural language commands:

### Task Creation
- "Add task buy milk tomorrow"
- "Create a task to call John"
- "I need to finish the report"
- "Reminder: Meeting at 3pm"

### Task Queries
- "Show my tasks"
- "List pending tasks"
- "What are my completed tasks?"
- "Summarize my tasks"

### Task Updates
- "Mark task 1 as done"
- "Complete task 3"
- "Delete task 5"
- "Update task 2 to 'New title'"

### Help
- "Help"
- "What can you do?"
- "Show commands"

---

## HuggingFace Spaces Deployment

### 1. Update Space Settings

In your HuggingFace Space dashboard:

1. Go to **Settings** → **Variables**
2. Add environment variables:
   ```
   DATABASE_URL=your-neon-db-url
   API_URL=https://your-space.hf.space
   CORS_ORIGINS=https://your-space.hf.space,http://localhost:3000
   ```

3. Go to **Files** → Edit `.env` (if exists)
4. Add the same variables

### 2. Rebuild Space

1. Go to **Settings** → **Factory Rebuild**
2. Click **Rebuild**
3. Wait for deployment (~5-10 minutes for model download)

### 3. Test Chat

Once deployed, test the chat endpoint:

```bash
curl -X POST https://your-space.hf.space/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task test", "session_id": "test-123"}'
```

---

## AI Agent Modes

### 1. Qwen2.5 LLM Mode (Default)

Uses the Qwen2.5-0.5B-Instruct model for:
- Better intent classification
- Natural language responses
- Context-aware conversations

**Requirements:**
- ~2GB RAM for model
- Model download on first run (~1GB)
- GPU recommended (but works on CPU)

### 2. Rule-Based Fallback

Automatically activated if:
- Transformers not installed
- Model fails to load
- Insufficient memory

Uses regex patterns for intent detection:
- Fast and lightweight
- Works offline
- Limited to predefined patterns

---

## Database Schema

New tables for chat functionality:

```sql
-- Conversations
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Messages
CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    conversation_id INTEGER REFERENCES conversations(id),
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Indexes
CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_conversations_session ON conversations(session_id);
```

---

## Troubleshooting

### Model Loading Fails

**Error:** "Error loading model: ..."

**Solution:**
- Check internet connection for model download
- Ensure sufficient disk space (~2GB)
- Set `TRANSFORMERS_CACHE=/tmp/transformers_cache`
- System will fallback to rule-based mode automatically

### CORS Errors

**Error:** "CORS policy blocked"

**Solution:**
- Update `CORS_ORIGINS` in backend `.env`
- Include both frontend URL and HuggingFace Space URL
- Rebuild backend after changes

### Chat Not Working

**Check:**
1. Backend logs for AI initialization
2. Database tables created (conversations, messages)
3. API endpoint accessible: `GET /api/chat/health`
4. Frontend API_URL configured correctly

### Slow Responses

**Solutions:**
- Use smaller model: `Qwen/Qwen2.5-0.5B-Instruct` (default)
- Enable GPU in HuggingFace Space settings
- Reduce `max_new_tokens` in ai_agent.py
- Use rule-based fallback (disable LLM)

---

## Performance Optimization

### For HuggingFace Free Tier

1. **Use Rule-Based Mode Only**
   - Edit `ai_agent.py` to skip LLM loading
   - Faster responses, no model download

2. **Cache Model**
   - Set `TRANSFORMERS_CACHE` to persistent storage
   - Model downloads once, reuses on restart

3. **Limit Context**
   - Reduce conversation history limit
   - Default: last 10 messages

### For Production

1. **Use OpenAI API** (if budget allows)
   - Set `OPENAI_API_KEY` in `.env`
   - Better quality responses
   - No model hosting

2. **GPU Acceleration**
   - Upgrade HuggingFace Space to GPU
   - Faster inference

3. **Model Quantization**
   - Use quantized Qwen2.5 model
   - Smaller memory footprint

---

## Testing

### Manual Testing

```bash
# Test task creation
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Add task buy milk", "session_id": "test"}'

# Test task listing
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show my tasks", "session_id": "test"}'

# Test task completion
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Mark task 1 as done", "session_id": "test"}'
```

### Automated Testing

```bash
cd backend
pytest tests/test_chat.py -v
```

---

## Next Steps

After Phase III:
- **Phase IV**: Kubernetes deployment
- **Phase V**: Cloud deployment (DigitalOcean)

---

## References

- Qwen2.5 Model: https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct
- Transformers Docs: https://huggingface.co/docs/transformers
- MCP Protocol: https://modelcontextprotocol.io/
- Project Specs: `specs/features/phase-iii-ai-chatbot.md`
