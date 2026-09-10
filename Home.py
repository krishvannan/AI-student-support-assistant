"""
CampusAI – Intelligent Student Support Assistant
Multipage Root Entrypoint.
"""

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Delegate to app.py navigation
from app import pg

if __name__ == "__main__" or True:
    pg.run()
