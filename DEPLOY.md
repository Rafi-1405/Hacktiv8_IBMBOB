# AutoSpec QA — PythonAnywhere Deployment Guide

The complete, current GitHub and PythonAnywhere setup is documented in the [README](README.md#deploy-on-pythonanywhere). Follow that guide for the supported Python version, virtual environment, WSGI configuration, API key setup, and update process.

Quick reminders:

- Set `GEMINI_API_KEY` in the PythonAnywhere Web tab's environment variables. Never commit the key.
- The app serves its own frontend and `/static` assets; a separate static-file mapping is not needed.
- After `git pull`, click **Reload** in the Web tab.
