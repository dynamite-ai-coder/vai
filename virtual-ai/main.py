import asyncio
import json
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from config import HOST, PORT, validate_keys, MAX_INPUT_LENGTH
from schemas import ChatRequest, StatusResponse
from virtual_ai import VirtualAI

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Virtual AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

virtual_ai = VirtualAI()


@app.on_event("startup")
async def startup():
    await virtual_ai.initialize()
    logger.info("Virtual AI server started")


@app.on_event("shutdown")
async def shutdown():
    await virtual_ai.shutdown()
    logger.info("Virtual AI server stopped")


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).resolve().parent / "static" / "index.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse("<h1>Virtual AI</h1><p>Static files not found.</p>")


@app.get("/api/status")
async def status():
    status_data = virtual_ai.get_status()
    return status_data


@app.post("/api/chat")
async def chat(request: Request):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    message = body.get("message", "").strip()
    use_browser = body.get("use_browser", False)

    if not message:
        raise HTTPException(status_code=400, detail="Message is required")
    if len(message) > MAX_INPUT_LENGTH:
        raise HTTPException(status_code=400, detail=f"Message too long (max {MAX_INPUT_LENGTH} chars)")

    try:
        result = await virtual_ai.process_message(message, use_browser)
        return result
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e)[:200])


@app.post("/api/clear")
async def clear_chat():
    virtual_ai.clear_memory()
    return {"status": "ok", "message": "Conversation cleared"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                message = msg.get("message", "").strip()
                use_browser = msg.get("use_browser", False)

                if not message:
                    await websocket.send_json({"type": "error", "data": "Empty message"})
                    continue

                async for event in virtual_ai.stream_message(message, use_browser):
                    await websocket.send_json(event)

            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "data": "Invalid JSON"})
            except Exception as e:
                logger.error(f"WS error: {e}")
                await websocket.send_json({"type": "error", "data": str(e)[:200]})

    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


app.mount("/static", StaticFiles(directory=str(Path(__file__).resolve().parent / "static")), name="static")


def main():
    import uvicorn
    keys = validate_keys()
    configured = sum(1 for v in keys.values() if v == "configured")
    logger.info(f"API Keys configured: {configured}/5")
    if configured == 0:
        logger.warning("No API keys configured! Create a .env file with your Groq API keys.")
    
    workers = int(os.getenv("WEB_CONCURRENCY", "1"))
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info",
        workers=workers,
        timeout_keep_alive=30,
    )


if __name__ == "__main__":
    main()
