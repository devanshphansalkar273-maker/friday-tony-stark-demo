import tkinter as tk
from tkinter import scrolledtext
import threading
import time
import sys
sys.path.insert(0, 'friday')
from friday.core.agent import StarkAgent
from friday.voice.input import listen
from friday.voice.output import speak

agent = StarkAgent()

def insert_message(sender, msg):
    chat.config(state=tk.NORMAL)
    chat.insert(tk.END, f"{sender}: {msg}\n")
    chat.see(tk.END)
    chat.config(state=tk.DISABLED)

def send_message():
    text = entry.get("1.0", tk.END).strip()
    if text:
        insert_message("You", text)
        entry.delete("1.0", tk.END)
        try:
            resp = agent.process_input(text)
            insert_message("FRIDAY", resp)
        except Exception as e:
            insert_message("FRIDAY", f"Error: {str(e)}")
        speak(resp)

def voice_input():
    def _listen():
        text = listen()
        if text:
            entry.insert(tk.END, text + '\n')
            entry.see(tk.END)
    threading.Thread(target=_listen, daemon=True).start()

def greeting_thread():
    time.sleep(10)
    speak("Hello sir")

# Dark theme window
root = tk.Tk()
root.title("FRIDAY AI")
root.geometry("500x600")
root.configure(bg='black')

# Chat area
chat = scrolledtext.ScrolledText(root, wrap=tk.WORD, state=tk.DISABLED, bg='black', fg='lime', insertbackground='white', font=('Courier', 10))
chat.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Initial greeting
insert_message("FRIDAY", "Hello sir.")

# Input frame
entry_frame = tk.Frame(root, bg='black')
entry_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

entry = tk.Text(entry_frame, height=3, bg='gray20', fg='white', insertbackground='white', font=('Courier', 10))
entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

button = tk.Button(entry_frame, text="Send", command=send_message, bg='gray30', fg='lime', relief='flat')
button.pack(side=tk.RIGHT, padx=(5, 0))

voice_btn = tk.Button(entry_frame, text="🎤", command=voice_input, bg='gray30', fg='lime', relief='flat', font=('Arial', 16))
voice_btn.pack(side=tk.RIGHT, padx=(0, 5))

entry.bind("<Control-Return>", lambda e: (send_message(), "break"))
entry.bind("<Return>", lambda e: "break")

threading.Thread(target=greeting_thread, daemon=True).start()

root.mainloop()

