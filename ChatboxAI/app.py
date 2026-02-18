import os
from flask import Flask, render_template, request, jsonify
from core.memory import load_memory, save_memory, trim_memory
from core.agent import agent_decide

app = Flask(__name__)

messages = load_memory()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200

@app.route("/chat", methods=["POST"])
def chat():
    global messages

    data = request.get_json(silent=True) or {}
    user_input = (data.get("message") or "").strip()
    if not user_input:
        return jsonify({"error": "Message is required."}), 400

    messages.append({"role": "user", "content": user_input})

    messages = trim_memory(messages)

    try:
        reply = agent_decide(messages, user_input)
    except Exception:
        return jsonify({"error": "AI service failed. Please try again."}), 502

    messages.append({"role": "assistant", "content": reply})

    try:
        save_memory(messages)
    except Exception:
        pass

    return jsonify({"reply": reply})
@app.route("/reset", methods=["POST"])
def reset_memory():
    global messages
    messages = [{"role": "system", "content": "You are a smart AI agent."}]
    
    if os.path.exists("memory.json"):
        os.remove("memory.json")

    return jsonify({"status": "memory cleared"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
