# Memory Upgrade TODO

1. ✅ Update pyproject.toml with chromadb and sentence-transformers deps
2. ✅ Update friday/config.py with MEMORY_DB_PATH
3. ✅ Create friday/memory/__init__.py (register)\n4. ✅ Create friday/memory/store.py (ChromaDB store + remember tool)\n5. ✅ Create friday/memory/retrieve.py (semantic search)\n6. ✅ Create friday/memory/summarize.py (MCP summarize prompt)
7. ✅ Update server.py to register memory module\n8. ✅ Update friday/prompts/__init__.py to register memory prompts
9. ✅ Update friday/tools/__init__.py to register memory tools
10. ✅ Update agent_friday.py: Enhance SYSTEM_PROMPT to use memory_recall
11. Run `uv sync` to install deps
12. Test integration

