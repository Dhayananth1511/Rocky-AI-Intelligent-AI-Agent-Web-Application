# core/brain.py

import requests
import os

HF_TOKEN = os.getenv("HF_TOKEN")
API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
# print(HF_TOKEN)  # Debug: Check if the token is loaded correctly
# print(API_URL)   # Debug: Check if the API URL is loaded correctly
# print(MODEL)     # Debug: Check if the model is loaded correctly

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def ask_llm(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.9
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
    except requests.RequestException:
        return "AI service timed out or is unreachable right now."

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"AI Error ({response.status_code})"
