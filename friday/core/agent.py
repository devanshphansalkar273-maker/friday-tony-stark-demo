from llm.local_llm import generate_response
from memory.store import recall, remember
from intelligence.strategy import get_best_stock, explain_stock
from voice.input import listen
from voice.output import speak
import re

class StarkAgent:
    def __init__(self):
        self.llm = generate_response

    def process_input(self, text: str) -> str:
        mem = recall(text)
        prompt = f"Context: {mem}\nUser: {text}\nRespond as FRIDAY."
        
        # Route
        if re.search(r'buy|best stock|trade', text.lower()):
            best = get_best_stock()
            from friday.learning.logger import log_prediction
            log_prediction(best['symbol'], best['combined_conf'])
            prompt += f"\nStock intel: {best}"
            remember(f"Recommended {best['symbol']}")
            return f"Best stock: {best['symbol']}, conf {best['combined_conf']:.1f}%."
        
        response = self.llm(prompt)
        return response

    def run_voice_loop(self):
        while True:
            text = listen()
            if text:
                resp = self.process_input(text)
                speak(resp)

