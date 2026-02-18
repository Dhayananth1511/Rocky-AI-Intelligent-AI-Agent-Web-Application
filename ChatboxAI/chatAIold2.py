from flask import Flask, render_template, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# 🔐 Secure Token
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable not set")

API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

MEMORY_FILE = "memory.json"
MAX_EXCHANGES = 6   # 6 user+assistant exchanges


# ---------------------------
# MEMORY MANAGEMENT
# ---------------------------

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except:
            pass

    return [{"role": "system", "content": "You are a helpful AI assistant."}]


def save_memory():
    with open(MEMORY_FILE, "w") as f:
        json.dump(messages, f, indent=2)


def summarize_old_memory():
    """
    Instead of deleting old memory,
    summarize older conversations.
    """
    global messages

    if len(messages) > (MAX_EXCHANGES * 2 + 1):

        old_part = messages[1:-MAX_EXCHANGES*2]

        summary_prompt = "Summarize this conversation briefly:\n"
        for m in old_part:
            summary_prompt += f"{m['role']}: {m['content']}\n"

        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": summary_prompt}],
            "max_tokens": 150
        }

        try:
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        except:
            return jsonify({"reply": "⚠ Server busy. Try again."})

        if response.status_code == 200:
            summary = response.json()["choices"][0]["message"]["content"]

            # Replace old memory with summary
            messages[:] = [
                messages[0],
                {"role": "assistant", "content": f"Previous conversation summary: {summary}"}
            ] + messages[-MAX_EXCHANGES*2:]

def trim_by_size(max_chars=4000):
    """
    Keep total conversation under safe size limit
    """
    global messages

    total_chars = sum(len(m["content"]) for m in messages)

    while total_chars > max_chars and len(messages) > 3:
        # Remove oldest user+assistant pair (keep system)
        messages.pop(1)
        total_chars = sum(len(m["content"]) for m in messages)

# Initialize memory
messages = load_memory()


# ---------------------------
# ROUTES
# ---------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    global messages

    user_message = request.json["message"]

    messages.append({"role": "user", "content": user_message})
    trim_by_size()   # 🔥 Control size BEFORE sending
    summarize_old_memory()

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
        return jsonify({"reply": f"Error: {response.status_code}"})


if __name__ == "__main__":
    app.run(debug=True)
