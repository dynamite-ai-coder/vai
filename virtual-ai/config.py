import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

GROQ_API_KEYS = [
    os.getenv("GROQ_API_KEY_1", ""),
    os.getenv("GROQ_API_KEY_2", ""),
    os.getenv("GROQ_API_KEY_3", ""),
    os.getenv("GROQ_API_KEY_4", ""),
    os.getenv("GROQ_API_KEY_5", ""),
]

MODEL_NAMES = [
    os.getenv("MODEL_1", "llama-3.3-70b-versatile"),
    os.getenv("MODEL_2", "llama-3.3-70b-versatile"),
    os.getenv("MODEL_3", "llama-3.3-70b-versatile"),
    os.getenv("MODEL_4", "llama-3.3-70b-versatile"),
    os.getenv("MODEL_5", "llama-3.3-70b-versatile"),
]

SYNTHESIS_MODEL = os.getenv("SYNTHESIS_MODEL", "llama-3.3-70b-versatile")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "22200"))

MODEL_ROLES = {
    1: {"name": "Reasoning Agent", "emoji": "🧠", "desc": "deep reasoning, problem decomposition, logical solutions"},
    2: {"name": "Research Agent", "emoji": "🔍", "desc": "gathering information, analyzing facts, research"},
    3: {"name": "Critical Agent", "emoji": "⚖️", "desc": "challenging agents, detecting errors, finding contradictions"},
    4: {"name": "Engineering Agent", "emoji": "⚙️", "desc": "technical solutions, programming, architecture"},
    5: {"name": "Strategic Agent", "emoji": "🎯", "desc": "comparing solutions, selecting best approach, optimization"},
}

MAX_HISTORY_MESSAGES = 40
REQUEST_TIMEOUT = 60
MAX_RETRIES = 2
MAX_INPUT_LENGTH = 8000


def validate_keys() -> dict:
    result = {}
    for i, key in enumerate(GROQ_API_KEYS, 1):
        result[f"model_{i}"] = "configured" if key and key.startswith("gsk_") else "missing"
    return result


def validate_all_keys() -> bool:
    return all(k and k.startswith("gsk_") for k in GROQ_API_KEYS)
