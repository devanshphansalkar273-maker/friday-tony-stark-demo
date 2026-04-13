import ollama
from typing import Generator

MODEL = "mistral"  # or 'llama3.1'

def generate_response(prompt: str, stream=False) -> str | Generator:
    response = ollama.chat(model=MODEL, messages=[{'role': 'user', 'content': prompt}], stream=stream)
    if stream:
        return (r['message']['content'] for r in response)
    return response['message']['content']

def fallback_response(prompt: str) -> str:
    # Simple rule-based fallback
    if "stock" in prompt.lower():
        return "Checking markets, boss. Tech up 1.2%, energy flat."
    return "Standing by, boss."

