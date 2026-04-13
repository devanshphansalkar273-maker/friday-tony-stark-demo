 #!/usr/bin/env python
\"\"\"\nFRIDAY Stark Local Main.\n\"\"\"

Modes:
python main.py voice  # Voice loop
python main.py cli  # Text CLI
python main.py auto  # Autonomous
\"\"\"
import sys
from friday.core.agent import StarkAgent
from friday.autonomous.scheduler import start_scheduler
from friday.llm.local_llm import generate_response

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "voice"
    
    agent = StarkAgent()
    from friday.autonomous.scheduler import start_learning_loop
    start_learning_loop()
    
    if mode == "voice":
        agent.run_voice_loop()
    elif mode == "cli":
        while True:
            text = input("> ")
            resp = agent.process_input(text)
            print(resp)
    elif mode == "auto":
        start_scheduler()
    elif mode == "stats":
        from friday.learning.metrics import print_stats
        print_stats()
    else:
        print("Mode: voice/cli/auto/stats")



