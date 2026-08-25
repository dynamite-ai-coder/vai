import logging
import asyncio
from typing import Optional

logger = logging.getLogger(__name__)

BROWSER_USE_AVAILABLE = False
Browser = None
Agent = None

try:
    from browser_use import Browser, Agent
    BROWSER_USE_AVAILABLE = True
    logger.info("browser-use library detected")
except ImportError:
    logger.info("browser-use not installed - browser features will use fallback")


class BrowserAgent:
    def __init__(self):
        self.available = BROWSER_USE_AVAILABLE
        self.browser = None
        self.agent = None
        self.ready = False

    async def initialize(self, model_name: str = "llama-3.3-70b-versatile", api_key: str = ""):
        if not self.available:
            logger.warning("browser-use not available, browser agent disabled")
            return False

        try:
            self.browser = Browser()
            self.ready = True
            logger.info("Browser agent initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser agent: {e}")
            self.ready = False
            return False

    async def execute_task(self, task: str) -> dict:
        if not self.available or not self.ready:
            return {
                "success": False,
                "error": "Browser agent not available",
                "result": None
            }

        try:
            from groq import AsyncGroq
            from config import GROQ_API_KEYS, MODEL_NAMES

            api_key = ""
            for key in GROQ_API_KEYS:
                if key and key.startswith("gsk_"):
                    api_key = key
                    break

            if not api_key:
                return {"success": False, "error": "No API key for browser agent", "result": None}

            agent = Agent(
                task=task,
                llm_model="groq/" + MODEL_NAMES[0],
                browser=self.browser,
            )
            result = await agent.run()
            return {"success": True, "result": str(result), "error": None}
        except Exception as e:
            logger.error(f"Browser task failed: {e}")
            return {"success": False, "error": str(e)[:200], "result": None}

    async def get_screenshot(self) -> Optional[bytes]:
        if not self.available or not self.browser:
            return None
        try:
            page = await self.browser.get_current_page()
            screenshot = await page.screenshot()
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None

    def get_status(self) -> dict:
        return {
            "available": self.available,
            "ready": self.ready,
            "browser_running": self.browser is not None
        }

    async def close(self):
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
            self.browser = None
            self.ready = False
