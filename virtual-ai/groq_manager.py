import asyncio
import time
import logging
from typing import Optional
from groq import AsyncGroq, APIError, RateLimitError, APITimeoutError
from config import GROQ_API_KEYS, MODEL_NAMES, SYNTHESIS_MODEL, REQUEST_TIMEOUT, MAX_RETRIES, MODEL_ROLES

logger = logging.getLogger(__name__)


class GroqManager:
    def __init__(self):
        self.clients = []
        for i, key in enumerate(GROQ_API_KEYS):
            if key and key.startswith("gsk_"):
                self.clients.append(AsyncGroq(api_key=key, timeout=REQUEST_TIMEOUT))
            else:
                self.clients.append(None)
                logger.warning(f"Model {i+1}: API key not configured or invalid")

    async def query_model(self, model_index: int, user_message: str, context: str = "", system_prompt: str = "") -> dict:
        client = self.clients[model_index] if model_index < len(self.clients) else None
        model_name = MODEL_NAMES[model_index] if model_index < len(MODEL_NAMES) else MODEL_NAMES[0]
        role = MODEL_ROLES.get(model_index + 1, {})

        if not client:
            return {
                "success": False,
                "model": model_name,
                "role": role.get("name", f"Model {model_index+1}"),
                "response": "",
                "error": "API key not configured",
                "time": 0
            }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if context:
            messages.append({"role": "system", "content": f"Conversation context:\n{context}"})
        messages.append({"role": "user", "content": user_message})

        start = time.time()
        last_error = None

        for attempt in range(MAX_RETRIES):
            try:
                response = await client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    temperature=0.7,
                    max_tokens=4096,
                )
                elapsed = round(time.time() - start, 2)
                content = response.choices[0].message.content or ""
                return {
                    "success": True,
                    "model": model_name,
                    "role": role.get("name", f"Model {model_index+1}"),
                    "response": content,
                    "error": None,
                    "time": elapsed
                }
            except RateLimitError as e:
                last_error = f"Rate limited"
                logger.warning(f"Model {model_index+1} rate limited, attempt {attempt+1}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(2 ** attempt)
            except APITimeoutError as e:
                last_error = f"Timeout"
                logger.warning(f"Model {model_index+1} timeout, attempt {attempt+1}")
            except APIError as e:
                last_error = f"API error: {str(e)[:100]}"
                logger.error(f"Model {model_index+1} API error: {e}")
                break
            except Exception as e:
                last_error = f"Error: {str(e)[:100]}"
                logger.error(f"Model {model_index+1} unexpected error: {e}")
                break

        elapsed = round(time.time() - start, 2)
        return {
            "success": False,
            "model": model_name,
            "role": role.get("name", f"Model {model_index+1}"),
            "response": "",
            "error": last_error or "Unknown error",
            "time": elapsed
        }

    async def query_all_models(self, user_message: str, context: str = "") -> list:
        tasks = []
        system_prompts = {
            0: "You are a Reasoning Agent. Focus on deep reasoning, problem decomposition, identifying assumptions, and finding logical solutions. Think step by step.",
            1: "You are a Research Agent. Focus on gathering information, analyzing facts, identifying useful data, and providing comprehensive research.",
            2: "You are a Critical Agent. Challenge other perspectives, detect potential errors, identify contradictions, and propose corrections.",
            3: "You are an Engineering Agent. Focus on technical solutions, programming, architecture, implementation details, and debugging approaches.",
            4: "You are a Strategic Agent. Compare proposed solutions, select the strongest approach, optimize results, and make final recommendations.",
        }
        for i in range(5):
            tasks.append(self.query_model(i, user_message, context, system_prompts.get(i, "")))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        final = []
        for i, r in enumerate(results):
            if isinstance(r, Exception):
                role = MODEL_ROLES.get(i + 1, {})
                final.append({
                    "success": False,
                    "model": MODEL_NAMES[i] if i < len(MODEL_NAMES) else "unknown",
                    "role": role.get("name", f"Model {i+1}"),
                    "response": "",
                    "error": str(r)[:100],
                    "time": 0
                })
            else:
                final.append(r)
        return final

    async def synthesize(self, user_message: str, model_responses: list) -> str:
        successful = [r for r in model_responses if r["success"]]
        if not successful:
            return "All AI models failed to respond. Please check your API keys and try again."

        synthesis_context = f"User request: {user_message}\n\n"
        for i, resp in enumerate(model_responses):
            role = resp.get("role", f"Model {i+1}")
            status = "OK" if resp["success"] else f"FAILED: {resp['error']}"
            synthesis_context += f"--- {role} ({resp['model']}) [{status}] ---\n"
            if resp["success"]:
                synthesis_context += f"{resp['response']}\n\n"

        synthesis_prompt = f"""You are the Virtual AI Synthesis Engine. You have received responses from multiple AI specialists.

Your task:
1. Compare all responses from the agents.
2. Identify areas of agreement and contradiction.
3. Detect weak reasoning or potential hallucinations.
4. Use the best information from each response.
5. Produce ONE coherent, comprehensive final answer.
6. Do NOT mention the internal architecture or agent roles unless the user asked.
7. Do NOT blindly trust one model - synthesize intelligently.
8. Be clear, helpful, and direct.

{synthesis_context}

Provide the final synthesized answer to the user:"""

        client = None
        for c in self.clients:
            if c is not None:
                client = c
                break

        if not client:
            parts = []
            for resp in model_responses:
                if resp["success"] and resp["response"]:
                    parts.append(resp["response"])
            return "\n\n".join(parts) if parts else "No models responded successfully."

        try:
            response = await client.chat.completions.create(
                model=SYNTHESIS_MODEL,
                messages=[{"role": "user", "content": synthesis_prompt}],
                temperature=0.3,
                max_tokens=4096,
            )
            return response.choices[0].message.content or "Synthesis produced no output."
        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            parts = []
            for resp in model_responses:
                if resp["success"] and resp["response"]:
                    parts.append(f"**{resp['role']}:** {resp['response']}")
            return "\n\n".join(parts) if parts else f"Synthesis failed: {str(e)[:200]}"

    def get_status(self) -> dict:
        status = {}
        for i in range(5):
            key = GROQ_API_KEYS[i] if i < len(GROQ_API_KEYS) else ""
            role = MODEL_ROLES.get(i + 1, {})
            status[f"model_{i+1}"] = {
                "name": role.get("name", f"Model {i+1}"),
                "role": role.get("desc", ""),
                "model": MODEL_NAMES[i] if i < len(MODEL_NAMES) else "unknown",
                "configured": bool(key and key.startswith("gsk_"))
            }
        return status
