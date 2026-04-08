from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import os
from datetime import datetime, timezone

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHAT_FILE = "chat.json"

# load chat
if os.path.exists(CHAT_FILE):
    try:
        with open(CHAT_FILE, "r", encoding="utf-8") as f:
            chat_history = json.load(f)
    except:
        chat_history = []
else:
    chat_history = []

@app.get("/")
def home():
    return {"status": "online"}

# 📥 get chat (room + DM)
@app.get("/chat")
def get_chat(room: str = "general", user: str = ""):
    result = []
    for m in chat_history:
        if m.get("to"):  # DM
            if m["to"] == user or m["user"] == user:
                result.append(m)
        else:  # public
            if m.get("room") == room:
                result.append(m)
    return result

# 📤 send message
@app.post("/chat")
def send_message(user: str, text: str, room: str = "general", to: str = ""):
    now = datetime.now(timezone.utc)

    new_msg = {
        "room": room,
        "user": user,
        "to": to,
        "msg": text,
        "ts": now.isoformat(),
        "ts_ms": int(now.timestamp() * 1000)
    }

    chat_history.append(new_msg)

    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

    return {"ok": True}

# 🧹 CLEAR CHAT (PER ROOM 🔥)
@app.delete("/chat")
def clear_chat(room: str = "general"):
    global chat_history

    chat_history = [m for m in chat_history if m.get("room") != room]

    with open(CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(chat_history, f, ensure_ascii=False, indent=2)

    return {"ok": True}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("server:app", host="0.0.0.0", port=port)
