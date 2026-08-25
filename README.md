# Virtual AI

Multi-model intelligent system for Termux on Android. Combines 5 specialized Groq AI agents into one coordinated Virtual AI.

## Architecture

```
User → Web UI → Orchestrator → 5 Groq Models (parallel) → Synthesis → Answer
```

### Model Roles

| Model | Role | Groq Model | Specialty |
|-------|------|------------|-----------|
| 1 | 🧠 Reasoning | deepseek-r1-distill-llama-70b | Problem decomposition, logic |
| 2 | 🔍 Research | llama-3.3-70b-versatile | Information gathering, analysis |
| 3 | ⚖️ Critical | mixtral-8x7b-32768 | Error detection, challenges |
| 4 | ⚙️ Engineering | llama-3.1-8b-instant | Technical solutions, code |
| 5 | 🎯 Strategic | gemma2-9b-it | Comparison, optimization |

## Quick Start (Termux)

```bash
# Install dependencies
pkg install python git
git clone https://github.com/dynamite-ai-coder/vai.git
cd vai/virtual-ai

# Setup
./setup_termux.sh

# Configure API keys
nano .env

# Run
./run.sh
```

Then open: **http://127.0.0.1:22200**

## Manual Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your 5 Groq API keys
python main.py
```

## Configuration (.env)

```env
GROQ_API_KEY_1=gsk_xxxxx
GROQ_API_KEY_2=gsk_xxxxx
GROQ_API_KEY_3=gsk_xxxxx
GROQ_API_KEY_4=gsk_xxxxx
GROQ_API_KEY_5=gsk_xxxxx

MODEL_1=deepseek-r1-distill-llama-70b
MODEL_2=llama-3.3-70b-versatile
MODEL_3=mixtral-8x7b-32768
MODEL_4=llama-3.1-8b-instant
MODEL_5=gemma2-9b-it

SYNTHESIS_MODEL=llama-3.3-70b-versatile
HOST=127.0.0.1
PORT=22200
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web UI |
| `/api/chat` | POST | Send message |
| `/api/status` | GET | System status |
| `/api/clear` | POST | Clear conversation |
| `/ws` | WebSocket | Streaming chat |

## Running Tests

```bash
cd virtual-ai
python -m pytest tests/ -v
```

## License

MIT
