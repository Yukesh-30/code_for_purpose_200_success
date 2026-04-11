"""
Pytest configuration — sets up the Python path so app imports work.
"""
import sys
import os

# Add backend root to path so `from app.xxx import yyy` works
sys.path.insert(0, os.path.dirname(__file__))
