# AutoSpec QA

**AutoSpec QA** is an intelligent, automated BDD test case generator that transforms raw user stories, PRD excerpts, or casual problem statements into structured Gherkin test suites using the Google Gemini API.

Live demo: deployed on [PythonAnywhere](https://www.pythonanywhere.com/)

---

## ✨ Features

| Feature | Detail |
|---|---|
| Flexible input | Accepts formal user stories, PRDs, and informal pain-point descriptions |
| Requirement enrichment | LLM automatically derives WCAG, UX, and edge-condition scenarios |
| Structured Gherkin output | Three labelled categories: Positive & Flow · Negative & Validation · Edge / A11y / UI State |
| Collapseable output cards | Each result shown as a card with a one-sentence title; click to expand/collapse |
| Pin / Delete / Reorder | Pin important results to the top; delete unwanted ones; drag cards to reorder |
| localStorage persistence | All generated results survive page refreshes automatically |
| Syntax highlighting | Per-keyword colour coding (Given/When/Then/And/But) |
| One-click copy | Clipboard API with execCommand fallback per card |
| Dark / light mode | Respects OS preference; persisted to localStorage |
| WCAG 2.1 AA UI | Skip link, aria labels, keyboard navigation, 44 × 44 px touch targets |
| Keyboard shortcut | `Ctrl/Cmd + Enter` triggers generation from the textarea |
| Retry on transient errors | Auto-retries Gemini 503/429 up to 3× with back-off |

---

## 🗂 Project Structure

```
autospec-qa/
├── main.py            # FastAPI app — routes, Gemini API client, prompt engine
├── wsgi.py            # WSGI entry point for PythonAnywhere (wraps FastAPI via a2wsgi)
├── index.html         # Single-page frontend (served by FastAPI at GET /)
├── static/            # Optional static assets
├── requirements.txt   # Pinned Python dependencies
├── .env.example       # Environment variable template (no real secrets)
├── .gitignore         # Ignored files (.venv, .env, __pycache__)
└── README.md          # This file
```

---

## 🚀 Local Development Setup

### Prerequisites

- Python 3.11 or later
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Windows

```powershell
cd autospec-qa

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
Copy-Item .env.example .env
# Open .env and set: GEMINI_API_KEY=your_key_here

# Run
uvicorn main:app --reload
# Open http://127.0.0.1:8000
```

### macOS / Linux

```bash
cd autospec-qa

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Open .env and set: GEMINI_API_KEY=your_key_here

# Run
uvicorn main:app --reload
# Open http://127.0.0.1:8000
```

---

## ☁️ Deploying to PythonAnywhere

PythonAnywhere hosts Python web apps via WSGI. FastAPI is an ASGI framework, so the project includes [`wsgi.py`](wsgi.py) which wraps the FastAPI app using `a2wsgi` so PythonAnywhere can serve it.

**Your app will be available at:** `https://<your-username>.pythonanywhere.com`

---

### Step 1 — Create a PythonAnywhere account

Go to [pythonanywhere.com](https://www.pythonanywhere.com/) and sign up for a free account.
Free accounts get one web app at `https://<username>.pythonanywhere.com`.

---

### Step 2 — Upload project files

You need to get all project files onto PythonAnywhere. There are two ways:

#### Option A — Upload via the Files tab (easiest)

1. Log in → click the **Files** tab.
2. Navigate to (or create) the folder `/home/<username>/autospec-qa/`.
3. Upload each file one at a time using the **Upload a file** button:
   - `main.py`
   - `wsgi.py`
   - `index.html`
   - `requirements.txt`
   - `.env.example`

#### Option B — Clone from GitHub via Bash Console

1. Go to the **Consoles** tab → **Bash**.
2. Run:

```bash
git clone https://github.com/Rafi-1405/Hacktiv8_IBMBOB.git autospec-qa
```

This downloads all files directly into `/home/<username>/autospec-qa/`.

---

### Step 3 — Open a Bash Console

1. Click the **Consoles** tab.
2. Click **Bash** to open a terminal.
3. Navigate to your project:

```bash
cd ~/autospec-qa
```

---

### Step 4 — Create a virtual environment

PythonAnywhere free accounts support Python 3.10. Create a virtualenv named `venv` in your home directory:

```bash
mkvirtualenv --python=/usr/bin/python3.10 autospec-qa-venv
```

This creates the virtualenv at:
```
/home/<username>/.virtualenvs/autospec-qa-venv/
```

If `mkvirtualenv` is not available, use:

```bash
python3.10 -m venv /home/<username>/.virtualenvs/autospec-qa-venv
```

---

### Step 5 — Install dependencies

With the virtualenv active (it should activate automatically after `mkvirtualenv`), run:

```bash
workon autospec-qa-venv    # activate if not already active

cd ~/autospec-qa
pip install -r requirements.txt
```

Verify the install:

```bash
pip show fastapi a2wsgi google-genai
```

You should see version numbers for all three packages.

---

### Step 6 — Configure the Web App

1. Click the **Web** tab in the PythonAnywhere dashboard.
2. Click **Add a new web app**.
3. When asked to choose a framework, select **Manual configuration**.
4. Select **Python 3.10**.
5. Click **Next** until the web app is created.

---

### Step 7 — Set the WSGI configuration file

Still in the **Web** tab:

1. Find the **WSGI configuration file** section.
   It shows a path like `/var/www/<username>_pythonanywhere_com_wsgi.py`.
2. Click on that path to open the file editor.
3. **Delete all existing content** and replace it with:

```python
import sys
import os

# ── Add your project directory to the path ──────────────────────────────────
path = '/home/<username>/autospec-qa'   # <-- replace <username> with yours
if path not in sys.path:
    sys.path.insert(0, path)

# ── Set environment variables ────────────────────────────────────────────────
# Alternatively, set these in the Web tab → Environment variables section below.
os.environ.setdefault('GEMINI_API_KEY', 'your_gemini_api_key_here')

# ── Import the WSGI application ──────────────────────────────────────────────
from wsgi import application  # noqa
```

> **Important:** Replace `<username>` with your actual PythonAnywhere username on the `path` line.
> **Security:** Do not hard-code the real API key here — use the Environment Variables section in Step 8 instead, then remove the `os.environ.setdefault` line.

4. Click **Save**.

---

### Step 8 — Set the environment variable

Still in the **Web** tab, scroll down to the **Environment variables** section:

1. Click **Add a new variable**.
2. Set:
   - **Name:** `GEMINI_API_KEY`
   - **Value:** your real Gemini API key (starts with `AIza...`)
3. Click the checkmark to save.

Now go back to the WSGI file and remove the `os.environ.setdefault` line you added in Step 7 — the variable is now set securely by PythonAnywhere.

---

### Step 9 — Set the virtualenv path

In the **Web** tab, find the **Virtualenv** section:

1. Enter the full path to your virtualenv:
   ```
   /home/<username>/.virtualenvs/autospec-qa-venv
   ```
   Replace `<username>` with your PythonAnywhere username.
2. Click the checkmark to save.

---

### Step 10 — Reload the web app

At the top of the **Web** tab, click the big green **Reload** button.

Wait a few seconds, then open your app in a browser:

```
https://<username>.pythonanywhere.com
```

If the app loads correctly, deployment is complete. ✅

---

### Step 11 — Check logs if something goes wrong

In the **Web** tab, scroll down to the **Log files** section. There are three logs:

| Log | What it shows |
|---|---|
| **Error log** | Python tracebacks and import errors — check this first |
| **Server log** | Raw WSGI server output |
| **Access log** | Every HTTP request/response |

Click any log path to open the live tail view.

**Common errors:**

| Error in log | Fix |
|---|---|
| `ModuleNotFoundError: No module named 'fastapi'` | virtualenv path is wrong, or `pip install -r requirements.txt` was not run |
| `ModuleNotFoundError: No module named 'a2wsgi'` | Run `pip install a2wsgi==1.10.10` inside the virtualenv |
| `ModuleNotFoundError: No module named 'main'` | `path` in the WSGI file does not point to the correct project directory |
| `GEMINI_API_KEY is not set` | Environment variable not saved in the Web tab |
| `404 NOT_FOUND` model error | Edit `model=` in `main.py` to match the model available to your key |
| App loads but shows blank page | Check the browser console; the `index.html` path may be wrong |

---

### WSGI configuration reference

| Setting | Value |
|---|---|
| **WSGI file** | `/var/www/<username>_pythonanywhere_com_wsgi.py` |
| **Callable** | `application` (imported from `wsgi.py`) |
| **Project directory** | `/home/<username>/autospec-qa` |
| **Virtualenv path** | `/home/<username>/.virtualenvs/autospec-qa-venv` |
| **Python version** | `3.10` (PythonAnywhere free tier) |

---

### How the WSGI bridge works

```
Browser
  └─► PythonAnywhere WSGI server
        └─► /var/www/..._wsgi.py   (sets sys.path, imports application)
              └─► wsgi.py           (a2wsgi.ASGIMiddleware wraps FastAPI)
                    └─► main.py     (FastAPI app — routes, Gemini client)
                          └─► index.html  (served at GET /)
```

FastAPI is an ASGI framework. PythonAnywhere speaks WSGI. `a2wsgi.ASGIMiddleware` sits between them, translating WSGI `environ` / `start_response` calls into ASGI scope/receive/send calls.

---

### Updating the app on PythonAnywhere

After making local changes:

**Via GitHub (if using Option B):**

```bash
# In PythonAnywhere Bash console
cd ~/autospec-qa
git pull origin main
```

Then click **Reload** in the Web tab.

**Via manual file upload:**

Re-upload the changed files through the Files tab, then click **Reload** in the Web tab.

---

## 🔌 API Reference

### `POST /generate`

Generates a structured Gherkin test suite.

**Request body:**
```json
{ "input_text": "As a user, I want to reset my password via email..." }
```

**Success response (`200 OK`):**
```json
{ "gherkin": "Feature: Password Reset via Email\n...", "token_count": 512 }
```

**Error codes:**

| Status | Meaning |
|---|---|
| `422` | Input validation failure or AI safety filter rejection |
| `502` | Gemini API error after 3 retries |
| `503` | `GEMINI_API_KEY` not configured |

### `GET /health`

Returns `{"status": "ok", "api_key_configured": true/false}`.

---

## ⚙️ Configuration

| Variable | Required | Where to set |
|---|---|---|
| `GEMINI_API_KEY` | ✅ Yes | PythonAnywhere Web tab → Environment Variables (production); `.env` file (local dev) |

The Gemini model used is **`gemini-3.8-flash`** (temperature `0.3`).
To switch models, edit the `model=` argument in [`main.py`](main.py).

---

## 📋 Dependencies

```
fastapi==0.162.0
uvicorn[standard]==0.54.0
google-genai==2.33.0
python-dotenv==1.2.4
pydantic==2.14.1
a2wsgi==1.10.10
```

---

## 🔒 Security Notes

- The Gemini API key is **never** exposed to the browser.
- Set `GEMINI_API_KEY` only in the PythonAnywhere Web tab → Environment Variables. Never commit it to git.
- CORS is set to `allow_origins=["*"]` for development. Restrict it to your PythonAnywhere domain in `main.py` for production:
  ```python
  allow_origins=["https://<username>.pythonanywhere.com"]
  ```

---

## 🖥️ UI Features

| Action | How |
|---|---|
| Generate | Paste requirement → click **Generate Test Cases** (or `Ctrl+Enter`) |
| Collapse / Expand | Click any card header |
| Copy Gherkin | Click **Copy** inside an expanded card |
| Pin to top | Click **Pin** — card gets a gold border and moves to the top |
| Delete | Click **Delete** → confirm dialog |
| Reorder | Drag the ⠿ grip icon on the card header |
| Clear all | Click **Clear all** in the top header bar |
| Dark / light mode | Click the moon/sun icon in the header |

All results persist in browser `localStorage` (key: `autospec-qa-results-v2`).

---

## 📄 License

MIT — free to use, modify, and distribute.
