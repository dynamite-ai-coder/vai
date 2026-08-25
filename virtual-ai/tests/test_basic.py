import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
from unittest.mock import AsyncMock, patch, MagicMock


def test_config_loads():
    from config import GROQ_API_KEYS, MODEL_NAMES, HOST, PORT, MODEL_ROLES
    assert len(GROQ_API_KEYS) == 5
    assert len(MODEL_NAMES) == 5
    assert HOST == "127.0.0.1"
    assert PORT == 22200
    assert len(MODEL_ROLES) == 5


def test_validate_keys():
    from config import validate_keys
    result = validate_keys()
    assert isinstance(result, dict)
    assert len(result) == 5
    for key in result:
        assert key.startswith("model_")
        assert result[key] in ("configured", "missing")


def test_validate_all_keys():
    from config import validate_all_keys
    result = validate_all_keys()
    assert isinstance(result, bool)


def test_memory():
    from memory import ConversationMemory
    mem = ConversationMemory(max_messages=5)
    assert mem.message_count == 0

    mem.add_user_message("Hello")
    assert mem.message_count == 1

    mem.add_assistant_message("Hi there")
    assert mem.message_count == 2

    msgs = mem.get_messages()
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"

    ctx = mem.get_context_string()
    assert "Hello" in ctx
    assert "Hi there" in ctx

    mem.clear()
    assert mem.message_count == 0


def test_memory_trim():
    from memory import ConversationMemory
    mem = ConversationMemory(max_messages=3)
    for i in range(5):
        mem.add_user_message(f"msg {i}")
    assert mem.message_count == 3
    assert mem.history[0]["content"] == "msg 2"


def test_schemas():
    from schemas import ChatRequest, ChatResponse, StatusResponse
    req = ChatRequest(message="test")
    assert req.message == "test"
    assert req.use_browser is False

    resp = ChatResponse(reply="hello")
    assert resp.reply == "hello"


def test_groq_manager_init():
    from groq_manager import GroqManager
    gm = GroqManager()
    assert len(gm.clients) == 5


def test_browser_agent_status():
    from browser_agent import BrowserAgent
    ba = BrowserAgent()
    status = ba.get_status()
    assert "available" in status
    assert "ready" in status


def test_agents():
    from agents import AGENTS, get_agent, get_all_agents
    assert len(AGENTS) == 5
    agent = get_agent(1)
    assert agent is not None
    assert agent.index == 1
    assert agent.name == "Reasoning Agent"
    all_agents = get_all_agents()
    assert len(all_agents) == 5


def test_virtual_ai_init():
    from virtual_ai import VirtualAI
    vai = VirtualAI()
    status = vai.get_status()
    assert status["status"] in ("ok", "partial")
    assert "models" in status
    assert len(status["models"]) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
