import sys
import os
from pathlib import Path

def get_resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller (EXE).
    
    PyInstaller creates a temp folder and stores path in _MEIPASS.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # If not bundled, use the project root (assuming this file is in core/utils/)
        # Project root is 2 levels up from core/utils/resource_helper.py
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    return os.path.join(base_path, relative_path)
