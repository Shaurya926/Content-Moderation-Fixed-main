"""
server/app.py — OpenEnv required entry point.

openenv validate expects this file at server/app.py.
This file re-exports the same FastAPI app from root app.py
so both HF Spaces (root app.py) and openenv validate (server/app.py) work.
"""

import sys
import os

# Add root to path so we can import from root app.py
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, main  # noqa: F401 — re-export for openenv

def main():
    import uvicorn
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
