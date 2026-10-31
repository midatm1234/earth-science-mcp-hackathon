import sys
from pathlib import Path

# Make server.py and science.py importable as top-level modules for this server's tests.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
