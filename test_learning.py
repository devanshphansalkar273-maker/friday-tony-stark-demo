from learning.logger import log_decision, init_db
from learning.metrics import show_stats

def main():
    print("AI System Started...")

    # Init if needed
    init_db()

    # Dummy decision (adapted to API)
    log_decision("RELIANCE", "BUY", 0.05, 0.75)

    print("Decision logged. Run `python test_learning.py stats` to see stats.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "stats":
        show_stats()
    else:
        main()

