# ask.py - send a question to the local LLM, using a system prompt from a file
#
# Usage: python ask.py prompts/property_assistant_v1.txt "What affects house prices?"

import sys
import time

import requests

URL = "http://127.0.0.1:11434/api/chat"   # Ollama's local API
MODEL = "llama3.2"

prompt_file, question = sys.argv[1], sys.argv[2]
system_prompt = open(prompt_file, encoding="utf-8").read()

start = time.time()
response = requests.post(URL, json={
    "model": MODEL,
    "messages": [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ],
    "stream": False,
    "options": {"temperature": 0},   # 0 = same answer every time (repeatable)
})
data = response.json()

print(data["message"]["content"])
print(f"\n--- prompt: {prompt_file} | tokens in: {data['prompt_eval_count']} "
      f"| tokens out: {data['eval_count']} | {time.time() - start:.1f}s")