# core/brain.py

import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "mistralai/Mistral-7B-Instruct-v0.2"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def ask_llm(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 200
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    except requests.RequestException:
        return "AI service timed out or is unreachable right now."

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"AI Error ({response.status_code})"
