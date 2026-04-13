"""
Intelligence engine for trading decisions.
"""
from friday.intelligence.strategy import register

def register_all_intelligence(mcp):
    register(mcp)

