"""
Production-Ready AI Agent Service with HuggingFace Inference API.

Features:
- HuggingFace Inference API (cloud-based, no local model needed)
- Async request handling
- Comprehensive error handling
- Rate limiting support
- Fallback to rule-based processing
- WSL Ubuntu compatible

Environment Variables:
- HF_TOKEN: HuggingFace API token
- HF_MODEL_ID: Model to use (default: Qwen/Qwen2.5-0.5B-Instruct)
- HF_API_TIMEOUT: Request timeout in seconds (default: 30)
"""

import re
import json
import asyncio
import logging
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum

# HTTP client for HF API
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

# Local transformers (fallback)
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ModelMode(Enum):
    """AI model execution mode."""
    HF_API = "huggingface_api"  # Cloud API (recommended)
    LOCAL = "local"  # Local model
    RULE_BASED = "rule_based"  # No model, pattern matching


class AIAgentError(Exception):
    """Base exception for AI agent errors."""
    pass


class ModelLoadError(AIAgentError):
    """Model loading failed."""
    pass


class InferenceError(AIAgentError):
    """Inference API call failed."""
    pass


class RateLimitError(AIAgentError):
    """Rate limit exceeded."""
    pass


class QwenAIAgent:
    """
    Production-ready AI Agent with HuggingFace Inference API.

    Supports three modes:
    1. HuggingFace Inference API (cloud) - Recommended for production
    2. Local model (development/offline)
    3. Rule-based fallback (minimal resources)

    Example Usage:
        agent = QwenAIAgent(hf_token="your_token")
        await agent.initialize()
        result = await agent.process_message("Add task buy milk")
    """

    # HF Inference API endpoint
    HF_API_URL = "https://api-inference.huggingface.co/models/{model_id}"

    # Supported intents
    SUPPORTED_INTENTS = [
        "create_task",
        "list_tasks",
        "summarize_tasks",
        "complete_task",
        "delete_task",
        "update_task",
        "help",
    ]

    def __init__(
        self,
        hf_token: Optional[str] = None,
        model_id: str = "Qwen/Qwen2.5-0.5B-Instruct",
        api_timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize AI Agent.

        Args:
            hf_token: HuggingFace API token (required for HF API mode)
            model_id: HuggingFace model ID
            api_timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for API calls
        """
        self.hf_token = hf_token
        self.model_id = model_id
        self.api_timeout = api_timeout
        self.max_retries = max_retries

        # State
        self.mode = ModelMode.RULE_BASED
        self._initialized = False
        self._http_client: Optional[httpx.AsyncClient] = None

        # Local model (fallback)
        self._local_model = None
        self._local_tokenizer = None
        self._local_generator = None

    async def initialize(self) -> None:
        """
        Initialize the AI agent.

        Determines best available mode based on configuration and resources.

        Raises:
            ModelLoadError: If all initialization attempts fail
        """
        if self._initialized:
            return

        logger.info("🤖 Initializing AI Agent...")

        # Try HuggingFace API mode first (recommended)
        if self.hf_token and HTTPX_AVAILABLE:
            try:
                await self._init_hf_api()
                self.mode = ModelMode.HF_API
                logger.info(f"✅ Mode: HuggingFace Inference API ({self.model_id})")
                self._initialized = True
                return
            except Exception as e:
                logger.warning(f"⚠️  HF API init failed: {e}. Trying local model...")

        # Try local model
        if TRANSFORMERS_AVAILABLE:
            try:
                await self._init_local_model()
                self.mode = ModelMode.LOCAL
                logger.info(f"✅ Mode: Local model ({self.model_id})")
                self._initialized = True
                return
            except Exception as e:
                logger.warning(f"⚠️  Local model init failed: {e}. Using rule-based fallback.")

        # Fallback to rule-based
        self.mode = ModelMode.RULE_BASED
        logger.info("✅ Mode: Rule-based (pattern matching)")
        self._initialized = True

    async def _init_hf_api(self) -> None:
        """Initialize HuggingFace Inference API client."""
        if not self.hf_token:
            raise ModelLoadError("HF_TOKEN is required for API mode")

        if not HTTPX_AVAILABLE:
            raise ModelLoadError("httpx not installed. Run: pip install httpx")

        # Create async HTTP client
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.api_timeout),
            headers={
                "Authorization": f"Bearer {self.hf_token}",
                "Content-Type": "application/json",
            }
        )

        # Test API connection
        await self._test_hf_api()

    async def _test_hf_api(self) -> None:
        """Test HuggingFace API connectivity."""
        try:
            assert self._http_client is not None
            response = await self._http_client.post(
                self.HF_API_URL.format(model_id=self.model_id),
                json={
                    "inputs": "Test",
                    "parameters": {"max_new_tokens": 5}
                }
            )
            response.raise_for_status()
            logger.info("✅ HF API connection successful")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 503:
                logger.warning("⚠️  Model still loading on HF. Will retry on first request.")
            elif e.response.status_code == 401:
                raise ModelLoadError("Invalid HF_TOKEN. Check your token.")
            elif e.response.status_code == 429:
                raise RateLimitError("HF API rate limit exceeded.")
            else:
                raise InferenceError(f"HF API error: {e.response.status_code}")
        except httpx.RequestError as e:
            raise InferenceError(f"Network error: {str(e)}")

    async def _init_local_model(self) -> None:
        """Initialize local model (fallback mode)."""
        try:
            logger.info(f"📥 Loading model: {self.model_id}...")
            self._local_tokenizer = AutoTokenizer.from_pretrained(self.model_id)
            self._local_model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype="auto",
                device_map="auto",
                trust_remote_code=True,
            )
            self._local_generator = pipeline(
                "text-generation",
                model=self._local_model,
                tokenizer=self._local_tokenizer,
                max_new_tokens=256,
                temperature=0.7,
                top_p=0.9,
            )
            logger.info("✅ Local model loaded")
        except Exception as e:
            raise ModelLoadError(f"Failed to load local model: {e}")

    async def close(self) -> None:
        """Cleanup resources."""
        if self._http_client:
            await self._http_client.aclose()

    async def process_message(self, message: str) -> Dict[str, Any]:
        """
        Process user message and return intent + response.

        Args:
            message: User's message

        Returns:
            Dictionary with intent, data, and response

        Raises:
            AIAgentError: If processing fails
        """
        if not self._initialized:
            await self.initialize()

        logger.info(f"Processing message: '{message[:50]}...'")

        # Parse intent (always use rule-based for accuracy)
        intent, data = self._parse_intent_rule_based(message)

        # Generate response based on mode
        if self.mode == ModelMode.HF_API:
            response = await self._generate_response_hf_api(intent, data)
        elif self.mode == ModelMode.LOCAL:
            response = await self._generate_response_local(intent, data)
        else:
            response = self._generate_response_rule_based(intent, data)

        return {
            "intent": intent,
            "data": data,
            "response": response,
            "original_message": message,
            "mode": self.mode.value,
        }

    async def _generate_response_hf_api(
        self,
        intent: str,
        data: Dict[str, Any],
    ) -> str:
        """
        Generate response using HuggingFace Inference API.

        Implements retry logic with exponential backoff.
        """
        assert self._http_client is not None

        prompt = self._create_prompt(intent, data)

        for attempt in range(self.max_retries):
            try:
                response = await self._http_client.post(
                    self.HF_API_URL.format(model_id=self.model_id),
                    json={
                        "inputs": prompt,
                        "parameters": {
                            "max_new_tokens": 256,
                            "temperature": 0.7,
                            "top_p": 0.9,
                            "return_full_text": False,
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()

                # Extract generated text
                if isinstance(result, list) and len(result) > 0:
                    generated = result[0].get("generated_text", "")
                elif isinstance(result, dict):
                    generated = result.get("generated_text", "")
                else:
                    generated = str(result)

                return generated.strip() or self._generate_response_rule_based(intent, data)

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 503:
                    # Model loading, wait and retry
                    wait_time = 2 ** attempt
                    logger.warning(f"⏳ Model loading, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                elif e.response.status_code == 429:
                    raise RateLimitError("HF API rate limit exceeded. Try again later.")
                else:
                    logger.error(f"HF API error: {e}")
                    break

            except httpx.RequestError as e:
                logger.error(f"Network error: {e}")
                if attempt == self.max_retries - 1:
                    break
                await asyncio.sleep(2 ** attempt)

        # Fallback to rule-based response
        logger.warning("Falling back to rule-based response")
        return self._generate_response_rule_based(intent, data)

    async def _generate_response_local(
        self,
        intent: str,
        data: Dict[str, Any],
    ) -> str:
        """Generate response using local model."""
        if not self._local_generator:
            return self._generate_response_rule_based(intent, data)

        try:
            prompt = self._create_prompt(intent, data)
            outputs = self._local_generator(prompt)

            if isinstance(outputs, list) and len(outputs) > 0:
                generated = outputs[0].get("generated_text", "")
                # Extract only the response part
                if prompt in generated:
                    generated = generated.split(prompt)[-1].strip()
                return generated
            return self._generate_response_rule_based(intent, data)

        except Exception as e:
            logger.error(f"Local generation error: {e}")
            return self._generate_response_rule_based(intent, data)

    def _create_prompt(self, intent: str, data: Dict[str, Any]) -> str:
        """Create prompt for LLM."""
        system_prompt = """You are a helpful AI assistant for a Todo application.
You speak English and Roman Urdu (Hindi/Urdu written in Latin script).
Be friendly, concise, and helpful.

Your task is to respond to the user based on their intent and extracted data.

Examples:
- If intent is "create_task", confirm the task was created
- If intent is "list_tasks", show the tasks
- If intent is "delete_task", confirm deletion
- If user speaks Roman Urdu, respond in Roman Urdu

Detected intent: {intent}
Extracted data: {data}

Generate a friendly, natural response (2-3 sentences max)."""

        return system_prompt.format(
            intent=intent,
            data=json.dumps(data, ensure_ascii=False)
        )

    def _parse_intent_rule_based(self, message: str) -> Tuple[str, Dict[str, Any]]:
        """
        Parse user intent using rule-based patterns.

        Supports English and Roman Urdu.

        Args:
            message: User message

        Returns:
            Tuple of (intent, extracted_data)
        """
        message_lower = message.lower().strip()

        # === CREATE TASK ===
        # English patterns
        create_patterns_en = [
            r'(?:add|create|new)\s+(?:task\s+)?(?:to\s+)?(.+)',
            r'i\s+(?:need|want)\s+(?:to\s+)?(.+)',
            r'reminder?\s+(?:to\s+)?(.+)',
        ]
        # Roman Urdu patterns
        create_patterns_ur = [
            r'(?:kal|aaj|parso)\s+(.+)\s+(?:hai|karna)',
            r'(.+)\s+(?:lena|karna|hai)',
        ]

        for pattern in create_patterns_en + create_patterns_ur:
            match = re.search(pattern, message_lower)
            if match:
                task_text = match.group(1).strip()
                # Extract date hints
                date_match = re.search(
                    r'(tomorrow|today|kal|aaj|parso|next\s+\w+|\d+/\d+)',
                    message_lower
                )
                date_info = date_match.group(1) if date_match else None

                return "create_task", {
                    "title": task_text.title(),
                    "description": f"Created via AI chat" + (f" - {date_info}" if date_info else ""),
                }

        # === LIST TASKS ===
        list_patterns = [
            r'(?:show|list|get|view)\s+(?:my\s+)?(?:tasks|todos)',
            r'what\s+(?:are\s+)?my\s+(?:tasks|todos)',
            r'(?:pending|active|completed)\s+(?:tasks|todos)',
            r'(?:mere|mere)\s+(?:tasks|kaam)',  # Roman Urdu
        ]

        for pattern in list_patterns:
            if re.search(pattern, message_lower):
                status_match = re.search(r'(pending|active|completed)', message_lower)
                return "list_tasks", {
                    "status": status_match.group(1) if status_match else None
                }

        # === SUMMARIZE TASKS ===
        if any(word in message_lower for word in ["summarize", "summary", "overview", "kitne tasks"]):
            return "summarize_tasks", {}

        # === COMPLETE TASK ===
        complete_patterns = [
            r'(?:mark|complete|finish|done)\s+(?:task\s+)?(?:id\s+)?(\d+)',
            r'(?:task|kaam)\s+(\d+)\s+(?:complete|khatam|done)',  # Roman Urdu
        ]

        for pattern in complete_patterns:
            match = re.search(pattern, message_lower)
            if match:
                return "complete_task", {"task_id": int(match.group(1))}

        # === DELETE TASK ===
        delete_patterns = [
            r'(?:delete|remove|cancel)\s+(?:task\s+)?(?:id\s+)?(\d+)',
            r'(?:task|kaam)\s+(\d+)\s+(?:delete|hata)',  # Roman Urdu
        ]

        for pattern in delete_patterns:
            match = re.search(pattern, message_lower)
            if match:
                return "delete_task", {"task_id": int(match.group(1))}

        # === UPDATE TASK ===
        update_match = re.search(
            r'(?:update|change|edit)\s+(?:task\s+)?(?:id\s+)?(\d+)\s+(?:to\s+)?(.+)',
            message_lower
        )
        if update_match:
            return "update_task", {
                "task_id": int(update_match.group(1)),
                "new_title": update_match.group(2).strip().title()
            }

        # === HELP ===
        if any(word in message_lower for word in ["help", "help", "kya kar sakte", "commands"]):
            return "help", {}

        # === UNKNOWN ===
        return "unknown", {"original_message": message}

    def _generate_response_rule_based(self, intent: str, data: Dict[str, Any]) -> str:
        """
        Generate response using templates (fallback).

        Supports bilingual responses.
        """
        # Check if input was Roman Urdu
        is_urdu = any(
            word in data.get("original_message", "").lower()
            for word in ["hai", "karna", "kal", "aaj", "mera", "mere", "kaam"]
        )

        if is_urdu:
            responses = {
                "create_task": f"✅ Task ban gaya: '{data.get('title', 'Naya Task')}'",
                "list_tasks": "📋 Ye rahe aapke tasks:",
                "summarize_tasks": "📊 Aapke tasks ka khulasa:",
                "delete_task": f"🗑️ Task #{data.get('task_id')} delete ho gaya",
                "complete_task": f"✅ Shabaash! Task #{data.get('task_id')} complete ho gaya!",
                "update_task": f"✏️ Task update ho gaya: '{data.get('new_title')}'",
                "help": """👋 Main aapki madad kar sakta hoon! Try karein:
- "Add task buy milk tomorrow"
- "Kal doodh lena hai"
- "Show my tasks"
- "Task 1 complete karo"
- "Delete task 3\"""",
                "unknown": "🤔 Samajh nahi aaya. Try karein: 'Add task buy milk' ya 'Show my tasks'",
            }
        else:
            responses = {
                "create_task": f"✅ I've created task: '{data.get('title', 'New Task')}'",
                "list_tasks": "📋 Here are your tasks:",
                "summarize_tasks": "📊 Here's a summary of your tasks:",
                "delete_task": f"🗑️ Task #{data.get('task_id')} has been deleted",
                "complete_task": f"✅ Great job! Task #{data.get('task_id')} marked complete!",
                "update_task": f"✏️ Task updated to: '{data.get('new_title')}'",
                "help": """👋 I can help you manage tasks! Try saying:
- "Add task buy milk tomorrow"
- "Kal doodh lena hai" (Roman Urdu)
- "Show my tasks"
- "Mark task 1 as done"
- "Delete task 3\"""",
                "unknown": "🤔 I didn't understand. Try: 'Add task buy milk' or 'Show my tasks'",
            }

        return responses.get(intent, "I've processed your request!")


# ============================================================================
# Global Agent Management
# ============================================================================

_ai_agent: Optional[QwenAIAgent] = None


def get_ai_agent() -> QwenAIAgent:
    """Get or create the AI agent instance."""
    global _ai_agent
    if _ai_agent is None:
        _ai_agent = QwenAIAgent()
    return _ai_agent


async def initialize_ai_agent(
    hf_token: Optional[str] = None,
    model_id: str = "Qwen/Qwen2.5-0.5B-Instruct",
) -> QwenAIAgent:
    """
    Initialize the AI agent with configuration.

    Args:
        hf_token: HuggingFace API token (from .env)
        model_id: HuggingFace model ID

    Returns:
        Initialized AI agent
    """
    global _ai_agent
    _ai_agent = QwenAIAgent(
        hf_token=hf_token,
        model_id=model_id,
    )
    await _ai_agent.initialize()
    return _ai_agent


async def shutdown_ai_agent() -> None:
    """Cleanup AI agent resources."""
    global _ai_agent
    if _ai_agent:
        await _ai_agent.close()
        _ai_agent = None
