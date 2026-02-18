# core/memory.py

import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return [{"role": "system", "content": "You are a smart AI agent."}]

def save_memory(messages):
    with open(MEMORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)

def trim_memory(messages, max_chars=4000):
    total = sum(len(m["content"]) for m in messages)
    while total > max_chars and len(messages) > 2:
        messages.pop(1)
        total = sum(len(m["content"]) for m in messages)
    return messages
