"""
Memory Management System
Handles short-term conversation context and long-term persistent memory.
"""

import json
import logging
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """Single memory entry."""
    id: Optional[int] = None
    content: str = ""
    category: str = "general"
    timestamp: str = ""
    relevance_score: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp == "":
            self.timestamp = datetime.now().isoformat()
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class ShortTermMemory:
    """
    Conversation context and immediate working memory.
    Stores current conversation state.
    """

    def __init__(self, max_turns: int = 20):
        """
        Initialize ShortTermMemory.
        
        Args:
            max_turns: Maximum number of conversation turns to keep
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.max_turns = max_turns
        
        # Conversation history
        self.conversation: List[Dict[str, str]] = []
        
        # Current context
        self.context: Dict[str, Any] = {}
        
        # Current task info
        self.current_task: Optional[str] = None
        self.task_progress: Dict[str, Any] = {}

    def add_message(self, role: str, content: str) -> None:
        """
        Add message to conversation.
        
        Args:
            role: "user" or "assistant"
            content: Message content
        """
        self.conversation.append({"role": role, "content": content})
        
        # Keep only last N turns
        if len(self.conversation) > self.max_turns * 2:
            self.conversation = self.conversation[-self.max_turns * 2:]
        
        self.logger.debug(f"Added message: {role}: {content[:50]}...")

    def get_conversation(self) -> List[Dict[str, str]]:
        """Get full conversation history."""
        return self.conversation

    def get_last_n_turns(self, n: int) -> List[Dict[str, str]]:
        """
        Get last N conversation turns.
        
        Args:
            n: Number of turns
            
        Returns:
            Last N turns
        """
        return self.conversation[-n * 2:]

    def set_context(self, key: str, value: Any) -> None:
        """
        Set context variable.
        
        Args:
            key: Variable name
            value: Variable value
        """
        self.context[key] = value
        self.logger.debug(f"Set context: {key}")

    def get_context(self, key: Optional[str] = None) -> Any:
        """
        Get context variable(s).
        
        Args:
            key: Specific key (if None, return all)
            
        Returns:
            Context value or all context
        """
        if key:
            return self.context.get(key)
        return self.context

    def start_task(self, task: str) -> None:
        """Start tracking a task."""
        self.current_task = task
        self.task_progress = {"started_at": datetime.now().isoformat()}
        self.logger.info(f"Task started: {task}")

    def update_task_progress(self, **kwargs) -> None:
        """Update task progress."""
        self.task_progress.update(kwargs)

    def end_task(self, result: str) -> None:
        """End task tracking."""
        if self.current_task:
            self.task_progress["completed_at"] = datetime.now().isoformat()
            self.task_progress["result"] = result
            self.logger.info(f"Task completed: {self.current_task}")
        self.current_task = None

    def clear(self) -> None:
        """Clear all short-term memory."""
        self.conversation.clear()
        self.context.clear()
        self.current_task = None
        self.task_progress.clear()
        self.logger.info("Short-term memory cleared")

    def to_dict(self) -> Dict[str, Any]:
        """Get memory as dictionary."""
        return {
            "conversation": self.conversation,
            "context": self.context,
            "current_task": self.current_task,
            "task_progress": self.task_progress
        }


class LongTermMemory:
    """
    Persistent memory using SQLite.
    Stores facts, preferences, and past interactions.
    """

    def __init__(self, db_path: str = "friday/memory/long_term.db"):
        """
        Initialize LongTermMemory.
        
        Args:
            db_path: Path to SQLite database
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self._init_db()

    def _init_db(self) -> None:
        """Initialize database schema."""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Memory table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY,
                    content TEXT NOT NULL,
                    category TEXT,
                    timestamp TEXT,
                    relevance_score REAL,
                    metadata TEXT,
                    access_count INTEGER DEFAULT 0,
                    last_accessed TEXT
                )
            """)
            
            # User preferences
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS preferences (
                    id INTEGER PRIMARY KEY,
                    key TEXT UNIQUE,
                    value TEXT,
                    timestamp TEXT
                )
            """)
            
            # Past tasks/interactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY,
                    task TEXT,
                    input TEXT,
                    output TEXT,
                    success BOOLEAN,
                    timestamp TEXT,
                    duration REAL,
                    notes TEXT
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON memories(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)")
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Database initialized: {self.db_path}")
        
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")

    def store(self, entry: MemoryEntry) -> int:
        """
        Store memory entry.
        
        Args:
            entry: MemoryEntry to store
            
        Returns:
            ID of stored entry
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            metadata_json = json.dumps(entry.metadata)
            
            cursor.execute("""
                INSERT INTO memories (content, category, timestamp, relevance_score, metadata)
                VALUES (?, ?, ?, ?, ?)
            """, (entry.content, entry.category, entry.timestamp, entry.relevance_score, metadata_json))
            
            entry_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Stored memory: {entry_id}")
            return entry_id
        
        except Exception as e:
            self.logger.error(f"Error storing memory: {e}")
            return -1

    def recall(self, query: str, category: Optional[str] = None, limit: int = 5) -> List[MemoryEntry]:
        """
        Recall memories matching query.
        
        Args:
            query: Search query
            category: Filter by category
            limit: Maximum results
            
        Returns:
            List of matching memories
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Simple search in content
            if category:
                cursor.execute("""
                    SELECT id, content, category, timestamp, relevance_score, metadata
                    FROM memories
                    WHERE category = ? AND content LIKE ?
                    ORDER BY relevance_score DESC, timestamp DESC
                    LIMIT ?
                """, (category, f"%{query}%", limit))
            else:
                cursor.execute("""
                    SELECT id, content, category, timestamp, relevance_score, metadata
                    FROM memories
                    WHERE content LIKE ?
                    ORDER BY relevance_score DESC, timestamp DESC
                    LIMIT ?
                """, (f"%{query}%", limit))
            
            results = []
            for row in cursor.fetchall():
                entry = MemoryEntry(
                    id=row[0],
                    content=row[1],
                    category=row[2],
                    timestamp=row[3],
                    relevance_score=row[4],
                    metadata=json.loads(row[5] or "{}")
                )
                results.append(entry)
                
                # Update access count
                cursor.execute("""
                    UPDATE memories
                    SET access_count = access_count + 1, last_accessed = ?
                    WHERE id = ?
                """, (datetime.now().isoformat(), entry.id))
            
            conn.commit()
            conn.close()
            
            return results
        
        except Exception as e:
            self.logger.error(f"Error recalling memories: {e}")
            return []

    def set_preference(self, key: str, value: Any) -> None:
        """
        Store user preference.
        
        Args:
            key: Preference key
            value: Preference value
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            value_str = json.dumps(value) if not isinstance(value, str) else value
            
            cursor.execute("""
                INSERT OR REPLACE INTO preferences (key, value, timestamp)
                VALUES (?, ?, ?)
            """, (key, value_str, datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Set preference: {key}")
        
        except Exception as e:
            self.logger.error(f"Error setting preference: {e}")

    def get_preference(self, key: str, default: Any = None) -> Any:
        """
        Get user preference.
        
        Args:
            key: Preference key
            default: Default value if not found
            
        Returns:
            Preference value
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                try:
                    return json.loads(row[0])
                except:
                    return row[0]
            
            return default
        
        except Exception as e:
            self.logger.error(f"Error getting preference: {e}")
            return default

    def store_interaction(
        self,
        task: str,
        input_data: str,
        output_data: str,
        success: bool,
        duration: float,
        notes: Optional[str] = None
    ) -> None:
        """
        Store interaction/task record.
        
        Args:
            task: Task name
            input_data: Task input
            output_data: Task output
            success: Whether successful
            duration: Execution time
            notes: Additional notes
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO interactions (task, input, output, success, timestamp, duration, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (task, input_data, output_data, success, datetime.now().isoformat(), duration, notes))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Stored interaction: {task}")
        
        except Exception as e:
            self.logger.error(f"Error storing interaction: {e}")

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Statistics dictionary
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            # Count memories
            cursor.execute("SELECT COUNT(*) FROM memories")
            total_memories = cursor.fetchone()[0]
            
            # Count interactions
            cursor.execute("SELECT COUNT(*), SUM(success) FROM interactions")
            total_interactions, successful = cursor.fetchone()
            successful = successful or 0
            
            # Average duration
            cursor.execute("SELECT AVG(duration) FROM interactions WHERE success = 1")
            avg_duration = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "total_memories": total_memories,
                "total_interactions": total_interactions,
                "successful_interactions": successful,
                "average_duration": avg_duration,
                "success_rate": successful / total_interactions if total_interactions > 0 else 0
            }
        
        except Exception as e:
            self.logger.error(f"Error getting statistics: {e}")
            return {}

    def clear_old_memories(self, days: int = 30) -> int:
        """
        Clear memories older than N days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of deleted entries
        """
        try:
            from datetime import timedelta
            
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM memories WHERE timestamp < ?", (cutoff_date,))
            deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Deleted {deleted} old memories")
            return deleted
        
        except Exception as e:
            self.logger.error(f"Error clearing old memories: {e}")
            return 0


class MemoryManager:
    """
    Unified memory management combining short and long-term memory.
    """

    def __init__(self, db_path: str = "friday/memory/long_term.db"):
        """
        Initialize MemoryManager.
        
        Args:
            db_path: Path to long-term memory database
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(db_path=db_path)

    def remember(
        self,
        content: str,
        category: str = "general",
        relevance: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Store something in long-term memory.
        
        Args:
            content: What to remember
            category: Memory category
            relevance: Relevance score
            metadata: Additional metadata
        """
        entry = MemoryEntry(
            content=content,
            category=category,
            relevance_score=relevance,
            metadata=metadata or {}
        )
        
        self.long_term.store(entry)

    def recall(self, query: str, category: Optional[str] = None) -> List[str]:
        """
        Retrieve relevant memories.
        
        Args:
            query: What to search for
            category: Category filter
            
        Returns:
            List of relevant memories
        """
        entries = self.long_term.recall(query, category=category)
        return [e.content for e in entries]

    def save_to_long_term(self, key: str, value: Any, category: str = "context") -> None:
        """
        Move context from short-term to long-term memory.
        
        Args:
            key: Memory key
            value: Memory value
            category: Memory category
        """
        content = f"{key}: {json.dumps(value) if not isinstance(value, str) else value}"
        self.remember(content, category=category)

    def get_summary(self) -> Dict[str, Any]:
        """Get memory summary."""
        return {
            "short_term": self.short_term.to_dict(),
            "long_term_stats": self.long_term.get_statistics()
        }
