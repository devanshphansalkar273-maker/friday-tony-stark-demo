import requests
import json
from typing import Generator

MODEL = "mistral"  # The model we pulled earlier
OLLAMA_URL = "http://localhost:11434/api/chat"

def generate_response(prompt: str, stream=False) -> str | Generator:
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": stream
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        if stream:
            # For streaming, we yield chunks. Ollama sends newline-delimited JSON.
            def stream_gen():
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        yield chunk['message']['content']
            return stream_gen()
        else:
            data = response.json()
            return data['message']['content']
            
    except Exception as e:
        print(f"Ollama Error: {e}")
        return fallback_response(prompt)

def fallback_response(prompt: str) -> str:
    # Simple rule-based fallback
    if "stock" in prompt.lower():
        return "Checking markets, boss. Tech up 1.2%, energy flat."
    return "I'm having trouble connecting to my cognitive processing unit, boss. Standing by on local backup."
