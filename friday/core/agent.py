from friday.llm.local_llm import generate_response
from friday.core.router import route_command
from friday.memory.memory import memory
from friday.system.actions import open_app, close_app, shutdown, restart, execute_shell
from friday.system.files import create_file, delete_file, move_file, search_files
# web tools are registered via MCP, not imported here
from friday.intelligence.strategy import get_best_stock
from friday.learning.learning import learning
from friday.autonomous.scheduler import scheduler
from friday.voice.output import speak
from friday.automation.gui import take_screenshot, type_text, move_mouse, click_current_pos, get_mouse_pos
import friday.autonomous.scheduler

class StarkAgent:
    def __init__(self):
        self.llm = generate_response
        self.memory = memory
        self.learning = learning

    def execute_tool(self, module_str: str, text: str) -> str:
        """Execute tool based on route."""
        if module_str == 'system.actions':
            if 'open' in text.lower():
                app = text.split('open ')[-1].strip('.')
                return open_app(app)
            elif 'close' in text.lower():
                app = text.split('close ')[-1].strip('.')
                return close_app(app)
            elif 'shutdown' in text.lower():
                return shutdown()
            elif 'restart' in text.lower():
                return restart()
            elif 'shell' in text.lower() or 'cmd' in text.lower():
                cmd = text.split('shell ')[-1] if 'shell ' in text.lower() else text.split('cmd ')[-1]
                return execute_shell(cmd)
        elif module_str == 'system.files':
            # Parse simple commands
            if 'create file' in text.lower():
                parts = text.lower().split('create file ')[1].split(' with ')
                path = parts[0]
                content = parts[1] if len(parts) > 1 else ''
                return create_file(path, content)
            elif 'delete file' in text.lower():
                path = text.lower().split('delete file ')[1]
                return delete_file(path)
        elif module_str == 'memory':
            if 'remember' in text.lower():
                key, value = text.split('remember ')[1].split(':', 1)
                self.memory.remember(key.strip(), value.strip())
                return 'Remembered.'
            elif 'recall' in text.lower():
                key = text.lower().split('recall ')[1]
                return self.memory.recall(key)
        elif module_str == 'intelligence':
            best = get_best_stock()
            self.learning.track_usage('stock_check')
            return f"Boss, best stock: {best['symbol']}, conf {best['combined_conf']:.1f}%"
        elif module_str == 'learning':
            self.learning.improve()
            return "Learning updated."
        elif module_str == 'automation':
            scheduler.start()
            return "Automation started."
        elif module_str == 'automation.gui':
            if 'screenshot' in text.lower() or 'capture' in text.lower():
                return take_screenshot()
            elif 'type' in text.lower() or 'write' in text.lower():
                content = text.split('type ')[-1] if 'type ' in text.lower() else text.split('write ')[-1]
                return type_text(content)
            elif 'click' in text.lower():
                return click_current_pos()
            elif 'mouse' in text.lower() or 'cursor' in text.lower():
                if 'move' in text.lower():
                    # Parse "move mouse to 100 200"
                    parts = text.lower().split('move mouse to ')[-1].split()
                    try:
                        x, y = int(parts[0]), int(parts[1])
                        return move_mouse(x, y)
                    except:
                        return "Failed to parse coordinates."
                return get_mouse_pos()
        return 'Tool executed.'

    def process_input(self, text: str) -> str:
        # Memory
        mem = self.memory.recall(text)
        context = self.memory.get_context()

        # Route
        route = route_command(text)
        if route != 'llm':
            result = self.execute_tool(route, text)
            self.learning.track_usage(route)
            self.memory.remember('last_action', route)
            return result

        # LLM
        prompt = f"FRIDAY context: {context}\nUser: {text}\nYou are FRIDAY, Tony Stark's AI. Keep responses concise, helpful, witty."
        response = self.llm(prompt)
        self.memory.remember('conversation', text + ' -> ' + response)
        return response

    def run_voice_loop(self):
        from friday.voice.input import listen
        import signal
        import sys

        def signal_handler(sig, frame):
            print('\nFRIDAY standing by.')
            sys.exit(0)
        signal.signal(signal.SIGINT, signal_handler)

        print('FRIDAY online. Say "friday" to wake or Ctrl+C to stop.')
        while True:
            text = listen()
            if 'friday' in text.lower():
                resp = self.process_input(text)
                speak(resp)
