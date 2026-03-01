"""
Async Chat Router for AI Chatbot.

Production-ready implementation with:
- Async request handling
- Comprehensive error handling
- Conversation persistence
- MCP tool integration
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session
from schemas.chat import ChatRequest, ChatResponse, TaskData, MessageResponse, ConversationHistoryResponse
from services.ai_agent import get_ai_agent, AIAgentError, RateLimitError
from services.mcp_tools import MCPTaskTools
from repositories.conversation_repository import ConversationRepository
from repositories.message_repository import MessageRepository
from database import get_session

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


def get_conversation_repo(session: Session = Depends(get_session)) -> ConversationRepository:
    """Get conversation repository instance."""
    return ConversationRepository(session)


def get_message_repo(session: Session = Depends(get_session)) -> MessageRepository:
    """Get message repository instance."""
    return MessageRepository(session)


@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    conversation_repo: ConversationRepository = Depends(get_conversation_repo),
    message_repo: MessageRepository = Depends(get_message_repo),
    session: Session = Depends(get_session),
):
    """
    Chat with AI assistant to manage tasks using natural language.

    Supports English and Roman Urdu commands like:
    - "Add task buy milk tomorrow"
    - "Kal doodh lena hai"
    - "Show my pending tasks"
    - "Mark task 1 as done"
    - "Delete task 3"
    - "Summarize my tasks"

    Args:
        request: Chat request with message and session_id
        conversation_repo: Conversation repository
        message_repo: Message repository
        session: Database session

    Returns:
        ChatResponse with AI message and optional task data

    Raises:
        HTTPException: 500 on internal errors, 429 on rate limits
    """
    try:
        # Get or create conversation
        conversation = conversation_repo.get_or_create(request.session_id)

        # Save user message
        user_message = message_repo.add(
            conversation_id=conversation.id,
            role="user",
            content=request.message,
        )

        # Process message with AI agent
        ai_agent = get_ai_agent()
        result = await ai_agent.process_message(request.message)

        intent = result["intent"]
        data = result["data"]
        ai_response = result["response"]

        # Execute MCP tool based on intent
        mcp_tools = MCPTaskTools(session)
        task_data = None
        tasks_data = None
        action = None

        # === INTENT HANDLING ===

        if intent == "create_task":
            tool_result = mcp_tools.create_task(
                title=data.get("title", "New Task"),
                description=data.get("description")
            )
            if tool_result["success"]:
                task_data = TaskData(**tool_result["task"])
                action = "task_created"
                # Keep AI-generated response or use template
                if "ban gaya" in ai_response.lower() or "created" in ai_response.lower():
                    pass  # Use AI response
                else:
                    ai_response = f"✅ Task created: '{task_data.title}'"

        elif intent == "list_tasks":
            tool_result = mcp_tools.list_tasks(status=data.get("status"))
            if tool_result["success"]:
                tasks_data = [TaskData(**t) for t in tool_result["tasks"]]
                action = "tasks_listed"
                count = tool_result["count"]
                ai_response = f"📋 You have {count} task" + ("s" if count != 1 else "")
                if data.get("status"):
                    ai_response += f" with status '{data['status']}'"

        elif intent == "summarize_tasks":
            tool_result = mcp_tools.summarize_tasks()
            if tool_result["success"]:
                tasks_data = [TaskData(**t) for t in tool_result.get("pending_tasks", [])]
                action = "tasks_summarized"
                summary = tool_result["summary"]
                ai_response = f"📊 You have {summary['total']} tasks: {summary['pending']} pending, {summary['completed']} completed"

        elif intent == "delete_task":
            # Require confirmation for delete
            task_id = data.get("task_id")
            tool_result = mcp_tools.get_task_by_id(task_id) if hasattr(mcp_tools, 'get_task_by_id') else None

            # Check if user confirmed
            if "yes" in request.message.lower() or "confirm" in request.message.lower():
                tool_result = mcp_tools.delete_task(task_id=task_id)
                if tool_result["success"]:
                    action = "task_deleted"
                    ai_response = f"🗑️ Task #{task_id} has been deleted"
                else:
                    ai_response = f"❌ Task #{task_id} not found"
            else:
                # Ask for confirmation
                task = mcp_tools.repository.get_by_id(task_id)
                if task:
                    ai_response = f"⚠️ Are you sure you want to delete '{task.title}'? Reply 'yes' to confirm"
                    action = "delete_confirmation"
                else:
                    ai_response = f"❌ Task #{task_id} not found"

        elif intent == "complete_task":
            tool_result = mcp_tools.complete_task(task_id=data.get("task_id"))
            if tool_result["success"]:
                task_data = TaskData(**tool_result["task"])
                action = "task_completed"
                ai_response = f"✅ Great job! Task '{task_data.title}' marked complete!"
            else:
                ai_response = f"❌ Task not found"

        elif intent == "update_task":
            tool_result = mcp_tools.update_task(
                task_id=data.get("task_id"),
                title=data.get("new_title")
            )
            if tool_result["success"]:
                task_data = TaskData(**tool_result["task"])
                action = "task_updated"
                ai_response = f"✏️ Task updated to: '{task_data.title}'"
            else:
                ai_response = f"❌ Task not found"

        elif intent == "help":
            action = "help_provided"
            # Keep AI-generated help response

        elif intent == "unknown":
            action = "unknown_intent"
            # Keep AI-generated clarification response

        # Save AI response
        assistant_message = message_repo.add(
            conversation_id=conversation.id,
            role="assistant",
            content=ai_response,
            metadata={"intent": intent, "action": action, "mode": result.get("mode")}
        )

        # Update conversation timestamp
        conversation_repo.update_timestamp(conversation)

        return ChatResponse(
            response=ai_response,
            action=action,
            task=task_data,
            tasks=tasks_data,
            conversation_id=conversation.id,
            metadata={
                "intent": intent,
                "original_message": request.message,
                "mode": result.get("mode", "rule_based")
            }
        )

    except RateLimitError as e:
        logger.warning(f"Rate limit exceeded: {e}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again in a few minutes."
        )

    except AIAgentError as e:
        logger.error(f"AI Agent error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI service temporarily unavailable: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat error: {str(e)}"
        )


@router.get("/history/{session_id}", response_model=ConversationHistoryResponse)
def get_conversation_history(
    session_id: str,
    conversation_repo: ConversationRepository = Depends(get_conversation_repo),
    message_repo: MessageRepository = Depends(get_message_repo),
):
    """
    Get conversation history for a session.

    Args:
        session_id: Session identifier
        conversation_repo: Conversation repository
        message_repo: Message repository

    Returns:
        Conversation history with messages

    Raises:
        HTTPException: 404 if conversation not found
    """
    conversation = conversation_repo.get_by_session_id(session_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found for session: {session_id}"
        )

    messages = message_repo.get_latest(conversation.id, limit=50)

    return ConversationHistoryResponse(
        session_id=session_id,
        messages=[
            MessageResponse(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at,
                metadata=msg.metadata
            )
            for msg in messages
        ]
    )


@router.get("/health")
def chat_health():
    """
    Health check for chat service.

    Returns:
        Health status with mode information
    """
    ai_agent = get_ai_agent()
    return {
        "status": "healthy",
        "service": "chat",
        "mode": ai_agent.mode.value if ai_agent._initialized else "not_initialized",
    }
