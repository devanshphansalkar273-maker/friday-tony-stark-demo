"""
System Control Tools
Provides safe system operations.
"""

import logging
import subprocess
import time
from pathlib import Path
from typing import Optional


logger = logging.getLogger(__name__)


def get_system_info() -> dict:
    """Get system information."""
    try:
        import platform
        import psutil
        
        return {
            "os": platform.system(),
            "platform": platform.platform(),
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent
        }
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return {}


def execute_command(command: str, timeout: int = 10) -> str:
    """
    Execute shell command safely.
    
    Args:
        command: Command to execute
        timeout: Timeout in seconds
        
    Returns:
        Command output
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout if result.returncode == 0 else result.stderr
    except subprocess.TimeoutExpired:
        return f"Command timed out after {timeout}s"
    except Exception as e:
        logger.error(f"Error executing command: {e}")
        return str(e)


def get_disk_usage(path: str = ".") -> dict:
    """Get disk usage information."""
    try:
        import shutil
        usage = shutil.disk_usage(path)
        return {
            "total": usage.total,
            "used": usage.used,
            "free": usage.free,
            "percent": (usage.used / usage.total) * 100
        }
    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        return {}


def get_time() -> str:
    """Get current time."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def wait(seconds: float) -> str:
    """Wait for specified seconds."""
    time.sleep(seconds)
    return f"Waited {seconds} seconds"
