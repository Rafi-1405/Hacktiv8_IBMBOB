"""
wsgi.py — PythonAnywhere WSGI entry point
=========================================
PythonAnywhere's web-hosting layer is WSGI-based.
FastAPI is an ASGI application, so we use `a2wsgi` to wrap it.

How PythonAnywhere finds this file
-----------------------------------
In the Web tab → WSGI configuration file, point to this file.
The module-level name `application` is the standard WSGI callable.

Environment variables
----------------------
Set GEMINI_API_KEY in the Web tab → Environment variables section.
Do NOT hard-code secrets here.
"""

import os
import sys
from pathlib import Path

# ── Make sure our project directory is on the Python path ──────────────────
# PythonAnywhere runs wsgi.py from an arbitrary CWD; we need imports to work.
PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# ── Load .env if it exists (local dev convenience; ignored on PythonAnywhere
# since env vars are set in the Web tab).
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_DIR / ".env")
except ImportError:
    pass  # python-dotenv not installed — env vars come from the system

# ── Import the FastAPI app ──────────────────────────────────────────────────
from main import app  # noqa: E402  (import after sys.path manipulation)

# ── Wrap the ASGI app as a WSGI callable ───────────────────────────────────
# a2wsgi bridges ASGI → WSGI so PythonAnywhere can call `application(environ, start_response)`.
from a2wsgi import ASGIMiddleware  # noqa: E402

application = ASGIMiddleware(app)
