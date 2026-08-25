import asyncio
import logging
from typing import Optional
from groq_manager import GroqManager
from browser_agent import BrowserAgent
from memory import ConversationMemory
from config import MODEL_ROLES, MAX_INPUT_LENGTH

logger = logging.getLogger(__name__)


class VirtualAI:
    def __init__(self):
        self.groq = GroqManager()
        self.browser = BrowserAgent()
        self.memory = ConversationMemory()
        self.initialized = False

    async def initialize(self):
        if self.initialized:
            return
        await self.browser.initialize()
        self.initialized = True
        logger.info("Virtual AI initialized")

    async def process_message(self, message: str, use_browser: bool = False) -> dict:
        if not message or not message.strip():
            return {"reply": "Please provide a message.", "model_responses": {}, "synthesis_info": {}}

        message = message.strip()[:MAX_INPUT_LENGTH]

        await self.initialize()

        model_responses = {}
        browser_result = None

        if use_browser:
            logger.info("Browser task requested")
            browser_result = await self.browser.execute_task(message)

        context = self.memory.get_context_string(limit=10)
        responses = await self.groq.query_all_models(message, context)

        for i, resp in enumerate(responses):
            model_responses[f"model_{i+1}"] = {
                "role": resp.get("role", f"Model {i+1}"),
                "success": resp["success"],
                "response": resp["response"],
                "error": resp.get("error"),
                "time": resp.get("time", 0),
                "model": resp.get("model", "unknown")
            }

        synthesis = await self.groq.synthesize(message, responses)

        if browser_result and browser_result.get("success"):
            synthesis += f"\n\n--- Browser Research ---\n{browser_result['result']}"

        self.memory.add_user_message(message)
        self.memory.add_assistant_message(synthesis)

        successful = sum(1 for r in responses if r["success"])
        synthesis_info = {
            "total_models": 5,
            "successful": successful,
            "failed": 5 - successful,
        }

        return {
            "reply": synthesis,
            "model_responses": model_responses,
            "synthesis_info": synthesis_info,
            "browser_result": browser_result.get("result") if browser_result else None,
        }

    async def stream_message(self, message: str, use_browser: bool = False):
        if not message or not message.strip():
            yield {"type": "error", "data": "Please provide a message."}
            return

        message = message.strip()[:MAX_INPUT_LENGTH]
        await self.initialize()

        for i in range(5):
            role = MODEL_ROLES.get(i + 1, {})
            yield {
                "type": "model_start",
                "model_index": i + 1,
                "role": role.get("name", f"Model {i+1}"),
                "emoji": role.get("emoji", "🤖")
            }

        context = self.memory.get_context_string(limit=10)
        responses = await self.groq.query_all_models(message, context)

        for i, resp in enumerate(responses):
            status = "success" if resp["success"] else "error"
            yield {
                "type": "model_done",
                "model_index": i + 1,
                "role": resp.get("role", f"Model {i+1}"),
                "status": status,
                "error": resp.get("error"),
                "time": resp.get("time", 0)
            }

        yield {"type": "synthesis_start"}
        synthesis = await self.groq.synthesize(message, responses)

        self.memory.add_user_message(message)
        self.memory.add_assistant_message(synthesis)

        yield {"type": "final_reply", "data": synthesis}

    def get_status(self) -> dict:
        model_status = self.groq.get_status()
        browser_status = self.browser.get_status()
        all_configured = all(
            v.get("configured", False) for v in model_status.values()
        )
        return {
            "status": "ok" if all_configured else "partial",
            "models": model_status,
            "browser_use": browser_status.get("available", False),
            "all_keys_configured": all_configured,
        }

    def clear_memory(self):
        self.memory.clear()

    async def shutdown(self):
        await self.browser.close()
