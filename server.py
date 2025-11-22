from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from datetime import datetime, timezone

app = FastAPI()

# Allow browser connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHAT_FILE = "chat.json"

# Load chat history (if present)
if os.path.exists(CHAT_FILE):
    try:
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            chat_history = json.load(f)
    except Exception:
        # if file is corrupted, start fresh but keep a backup
        try:
            os.rename(CHAT_FILE, CHAT_FILE + ".broken")
        except Exception:
            pass
        chat_history = []
else:
    chat_history = []

@app.get("/")
def home():
    return {"status": "online", "message": "Multiplayer server is running with timestamps!"}

@app.get("/chat")
def get_chat():
    # return messages in order (oldest first)
    return chat_history

# POST /chat?user=...&text=...
@app.post("/chat")
def send_message(user: str, text: str):
    # timestamp in ISO format (UTC) and ms epoch
    now = datetime.now(timezone.utc)
    iso = now.isoformat()   # e.g. "2025-11-17T10:23:45.123456+00:00"
    epoch_ms = int(now.timestamp() * 1000)

    new_msg = {
        "user": user,
        "msg": text,
        "ts": iso,
        "ts_ms": epoch_ms
    }

    chat_history.append(new_msg)

    # write to disk (UTF-8 to preserve emojis)
    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

    return {"ok": True, "saved": new_msg}

if __name__ == "__main__":
    uvicorn.run("server:app", reload=True)
