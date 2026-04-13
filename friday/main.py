#!/usr/bin/env python
\"\"\"FRIDAY Stark Local Main - 100% Local AI Assistant.

Usage:
  python friday/main.py voice     # Voice interaction (say 'friday' to wake)
  python friday/main.py cli       # Text CLI loop
  python friday/main.py auto      # Start autonomous scheduler/learning
  python friday/main.py stats     # Print learning metrics
\"\"\"

import sys
import friday
from friday.core.agent import StarkAgent
from friday.automation.scheduler import scheduler, start_scheduler
from friday.learning.metrics import print_stats

if __name__ == '__main__':
    print('FRIDAY - Tony Stark\\'s Local AI Online.')
    
    agent = friday.agent
    
    mode = sys.argv[1] if len(sys.argv) > 1 else 'voice'
    
    # Start background
    scheduler.start()
    print('Automation and learning background started.')
    
    if mode == 'voice':
        agent.run_voice_loop()
    elif mode == 'cli':
        print('FRIDAY CLI. Type \\'exit\\' to quit.')
        while True:
            text = input('You: ')
            if text.lower() == 'exit':
                break
            resp = agent.process_input(text)
            print(f'FRIDAY: {resp}')
    elif mode == 'auto':
        print('Autonomous mode - FRIDAY running in background.')
        input('Press enter to stop...')
        scheduler.stop()
    elif mode == 'stats':
        print_stats()
    else:
        print('Invalid mode. Use: voice/cli/auto/stats')
        print_stats()

