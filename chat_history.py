"""
Chat history manager for Roxy — saves and loads conversations.
"""
import json
import os
from datetime import datetime

HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".roxy_chats")

def get_history_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)
    return HISTORY_DIR

def save_conversation(conversation_id, messages):
    path = os.path.join(get_history_dir(), f"{conversation_id}.json")
    data = {
        "id": conversation_id,
        "updated": datetime.now().isoformat(),
        "messages": messages
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def load_conversation(conversation_id):
    path = os.path.join(get_history_dir(), f"{conversation_id}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return None

def list_conversations():
    """Return list of (conversation_id, preview, timestamp) sorted by newest first."""
    convs = []
    history_dir = get_history_dir()
    if not os.path.exists(history_dir):
        return convs
    for fname in os.listdir(history_dir):
        if fname.endswith(".json"):
            path = os.path.join(history_dir, fname)
            try:
                with open(path) as f:
                    data = json.load(f)
                conv_id = data.get("id", fname.replace(".json", ""))
                msgs = data.get("messages", [])
                preview = ""
                if msgs:
                    last_msg = msgs[-1].get("text", "")
                    preview = last_msg[:60]
                convs.append((conv_id, preview, data.get("updated", "")))
            except:
                continue
    convs.sort(key=lambda x: x[2], reverse=True)
    return convs

def delete_conversation(conversation_id):
    path = os.path.join(get_history_dir(), f"{conversation_id}.json")
    if os.path.exists(path):
        os.remove(path)
        return True
    return False
