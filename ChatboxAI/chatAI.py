import requests
import json
import os

# 🔐 Get token from environment variable
HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    print("❌ HF_TOKEN not found. Set environment variable first.")
    exit()

API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

MEMORY_FILE = "memory.json"
MAX_MEMORY = 6  # keep last 6 exchanges

# 🔄 Load memory if exists
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        messages = json.load(f)
else:
    messages = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]


def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)


def limit_memory():
    global messages
    if len(messages) > MAX_MEMORY * 2 + 1:
        messages = [messages[0]] + messages[-(MAX_MEMORY * 2):]


def chat_with_bot(user_message):
    global messages

    messages.append({"role": "user", "content": user_message})
    limit_memory()

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 100
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": reply})
        limit_memory()
        save_memory()
        return reply
    else:
        return f"Error: {response.status_code} - {response.text}"


print("🤖 AI Chatbot (Memory + Persistent Storage Enabled)")
print("Type 'exit' to quit\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("Bot: Goodbye 👋")
        break

    reply = chat_with_bot(user_input)
    print("Bot:", reply)
