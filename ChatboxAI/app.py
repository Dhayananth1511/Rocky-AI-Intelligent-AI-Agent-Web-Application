from flask import Flask, render_template, request, jsonify
from core.memory import load_memory, save_memory, trim_memory
from core.agent import agent_decide

app = Flask(__name__)

messages = load_memory()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global messages

    user_input = request.json["message"]

    messages.append({"role": "user", "content": user_input})

    messages = trim_memory(messages)

    reply = agent_decide(messages, user_input)

    messages.append({"role": "assistant", "content": reply})

    save_memory(messages)

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(debug=True)
