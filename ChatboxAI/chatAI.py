# import requests
# import json
# import os

# # 🔐 Get token from environment variable
# HF_TOKEN = os.getenv("HF_TOKEN")

# if not HF_TOKEN:
#     print("❌ HF_TOKEN not found. Set environment variable first.")
#     exit()

# API_URL = "https://router.huggingface.co/v1/chat/completions"
# MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

# headers = {
#     "Authorization": f"Bearer {HF_TOKEN}",
#     "Content-Type": "application/json"
# }

# MEMORY_FILE = "memory.json"
# MAX_MEMORY = 6  # keep last 6 exchanges

# # 🔄 Load memory if exists
# if os.path.exists(MEMORY_FILE):
#     with open(MEMORY_FILE, "r") as f:
#         messages = json.load(f)
# else:
#     messages = [
#         {"role": "system", "content": "You are a helpful AI assistant."}
#     ]


# def save_memory():
#     with open(MEMORY_FILE, "w") as f:
#         json.dump(messages, f, indent=2)


# def limit_memory():
#     global messages
#     if len(messages) > MAX_MEMORY * 2 + 1:
#         messages = [messages[0]] + messages[-(MAX_MEMORY * 2):]


# def chat_with_bot(user_message):
#     global messages

#     messages.append({"role": "user", "content": user_message})
#     limit_memory()

#     payload = {
#         "model": MODEL,
#         "messages": messages,
#         "max_tokens": 100
#     }

#     response = requests.post(API_URL, headers=headers, json=payload)

#     if response.status_code == 200:
#         reply = response.json()["choices"][0]["message"]["content"]
#         messages.append({"role": "assistant", "content": reply})
#         limit_memory()
#         save_memory()
#         return reply
#     else:
#         return f"Error: {response.status_code} - {response.text}"


# print("🤖 AI Chatbot (Memory + Persistent Storage Enabled)")
# print("Type 'exit' to quit\n")

# while True:
#     user_input = input("You: ")

#     if user_input.lower() == "exit":
#         print("Bot: Goodbye 👋")
#         break

#     reply = chat_with_bot(user_input)
#     print("Bot:", reply)
from flask import Flask, render_template, request, jsonify
import requests
import os
import json

app = Flask(__name__)

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

MEMORY_FILE = "memory.json"
MAX_MEMORY = 20

# Load memory
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r") as f:
        messages = json.load(f)
else:
    messages = [{"role": "system", "content": "You are a helpful AI assistant."}]

def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)

def limit_memory():
    global messages
    if len(messages) > MAX_MEMORY * 2 + 1:
        messages[:] = [messages[0]] + messages[-(MAX_MEMORY * 2):]

def summarize_memory():
    global messages

    if len(messages) > 12:
        summary_prompt = "Summarize this conversation briefly:\n"
        for m in messages:
            summary_prompt += f"{m['role']}: {m['content']}\n"

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": summary_prompt}],
            "max_tokens": 150
        }

        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            summary = response.json()["choices"][0]["message"]["content"]
            messages[:] = [
                {"role": "system", "content": "You are a helpful AI assistant."},
                {"role": "assistant", "content": f"Previous conversation summary: {summary}"}
            ]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global messages

    user_message = request.json["message"]

    messages.append({"role": "user", "content": user_message})
    limit_memory()
    summarize_memory()

    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 200
    }

    response = requests.post(API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        reply = response.json()["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": reply})
        save_memory()
        return jsonify({"reply": reply})
    else:
        return jsonify({"reply": "Error occurred."})

if __name__ == "__main__":
    app.run(debug=True)
