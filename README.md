# AutoSpec QA

**AutoSpec QA** is an intelligent, automated BDD test case generator that transforms raw user stories, PRD excerpts, or casual problem statements into structured Gherkin test suites using the Google Gemini API.

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
├── main.py            # FastAPI backend + Gemini integration
├── index.html         # Single-page frontend (served by FastAPI)
├── static/            # Optional static assets (CSS overrides, images)
├── requirements.txt   # Python dependencies
├── .env.example       # Environment variable template
└── README.md          # This file
```

---

## 🚀 Setup & Installation

Follow the instructions for your operating system.

---

### 🪟 Windows

#### Prerequisites

1. **Python 3.11 or later** — Download from [python.org](https://www.python.org/downloads/).  
   During installation check **"Add Python to PATH"**.

2. Verify Python is available:
   ```powershell
   python --version
   # Expected output: Python 3.11.x  (or newer)
   ```

3. Verify pip is available:
   ```powershell
   pip --version
   ```

#### Step 1 — Navigate to the project folder

```powershell
cd "C:\path\to\autospec-qa"
```

#### Step 2 — Create a virtual environment

```powershell
python -m venv .venv
```

#### Step 3 — Activate the virtual environment

```powershell
.venv\Scripts\activate
```

You will see `(.venv)` prepended to your prompt.

#### Step 4 — Install dependencies

```powershell
pip install -r requirements.txt
```

#### Step 5 — Configure the API key

```powershell
Copy-Item .env.example .env
```

Open `.env` in Notepad (or any editor) and replace the placeholder with your real key:

```
GEMINI_API_KEY=your_real_key_here
```

> **Where to get a key:** Visit [Google AI Studio](https://aistudio.google.com/), click **Get API Key**, and create a new key.

#### Step 6 — Start the server

```powershell
uvicorn main:app --reload
```

#### Step 7 — Open the app

Open your browser and go to:

```
http://127.0.0.1:8000
```

#### Stopping the server

Press `Ctrl + C` in the terminal.

#### Deactivating the virtual environment

```powershell
deactivate
```

---

### 🍎 macOS

#### Prerequisites

1. **Python 3.11 or later** — The recommended way is via [Homebrew](https://brew.sh/):
   ```bash
   brew install python@3.11
   ```
   Or download the macOS installer from [python.org](https://www.python.org/downloads/).

2. Verify Python is available:
   ```bash
   python3 --version
   # Expected output: Python 3.11.x  (or newer)
   ```

3. Verify pip is available:
   ```bash
   pip3 --version
   ```

#### Step 1 — Navigate to the project folder

```bash
cd /path/to/autospec-qa
```

#### Step 2 — Create a virtual environment

```bash
python3 -m venv .venv
```

#### Step 3 — Activate the virtual environment

```bash
source .venv/bin/activate
```

You will see `(.venv)` prepended to your prompt.

#### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

#### Step 5 — Configure the API key

```bash
cp .env.example .env
```

Open `.env` in any text editor and replace the placeholder with your real key:

```
GEMINI_API_KEY=AIzaSy...your_real_key_here
```

> **Where to get a key:** Visit [Google AI Studio](https://aistudio.google.com/), click **Get API Key**, and create a new key.

#### Step 6 — Start the server

```bash
uvicorn main:app --reload
```

#### Step 7 — Open the app

Open your browser and go to:

```
http://127.0.0.1:8000
```

#### Stopping the server

Press `Ctrl + C` in the terminal.

#### Deactivating the virtual environment

```bash
deactivate
```

---

## 🔌 API Reference

### `POST /generate`

Generates a structured Gherkin test suite from the supplied requirement text.

**Request body** (`application/json`):

```json
{
  "input_text": "As a user, I want to reset my password via email..."
}
```

**Validation rules:**
- `input_text` must be between 10 and 8 000 characters (whitespace stripped).

**Success response** (`200 OK`):

```json
{
  "gherkin": "Feature: Password Reset via Email\n...",
  "token_count": 512
}
```

**Error responses:**

| Status | Meaning |
|---|---|
| `422 Unprocessable Entity` | Input validation failure or AI safety filter rejection |
| `502 Bad Gateway` | Gemini API returned an unexpected error (after 3 retries) |
| `503 Service Unavailable` | `GEMINI_API_KEY` is not configured on the server |

### `GET /health`

Liveness probe — returns `{"status": "ok", "api_key_configured": true/false}`.

---

## 🎨 Gherkin Output Format

```gherkin
Feature: <descriptive name>
# <one-line feature summary>

## POSITIVE FUNCTIONAL & FLOW

Scenario: <happy-path scenario>
  Given ...
  When  ...
  Then  ...

## NEGATIVE & INPUT VALIDATION

Scenario: <validation failure scenario>
  ...

## EDGE CASES, ACCESSIBILITY & UI STATE

Scenario: Keyboard navigation through the form
  Given a user is navigating with a keyboard only
  When they press Tab to move through form fields
  Then each field receives a visible focus indicator
  And the focus order follows a logical reading sequence
```

---

## 🖥️ UI Features Guide

### Collapseable cards
Every time you generate test cases, a new card is added to the right panel with a one-sentence title derived from your input. Click the card header (or press Enter/Space when focused) to expand or collapse the Gherkin output.

### Pinning
Click the **Pin** button inside an expanded card to pin it to the top of the list. Pinned cards are highlighted with a gold border and a filled pin icon. Click **Pinned** again to unpin.

### Deleting
Click the **Delete** button inside a card. A confirmation dialog will appear before the card is removed.

### Reordering
Drag any card by the ⠿ grip icon on the left of its header to reorder it in the list.

### Clear all
Use the **Clear all** button in the top header bar to delete every result at once.

### localStorage persistence
All results (including their expanded/collapsed state and pin status) are automatically saved to `localStorage` under the key `autospec-qa-results-v2`. They survive page refreshes and browser restarts until you clear browser data or click **Clear all**.

---

## ⚙️ Configuration

| Environment variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Google Generative AI API key |

The Gemini model used is **`gemini-3.8-flash`** with temperature `0.3` for deterministic, structured output.  
To switch models, edit the `model` argument in [`main.py`](main.py) inside the `generate_test_cases` function.

---

## 🔒 Security Notes

- All user input is validated server-side (length limits, null-byte removal) before being sent to the API.
- The Gemini API key is never exposed to the browser.
- CORS is currently set to `allow_origins=["*"]` for local development. **Restrict this to your domain in production.**

---

## 🐛 Troubleshooting

| Problem | Solution |
|---|---|
| `uvicorn: command not found` | Ensure the virtual environment is activated and `pip install -r requirements.txt` has been run |
| `GEMINI_API_KEY is not set` warning | Check that `.env` exists (not just `.env.example`) and contains a valid key |
| `503 UNAVAILABLE` from Gemini | The free-tier key is rate-limited; the server will retry 3× automatically. Wait a moment and try again |
| `404 NOT_FOUND` model error | The model name is outdated — update `model=` in `main.py` to the model available to your key |
| Port 8000 already in use | Run on a different port: `uvicorn main:app --reload --port 8001` and open `http://127.0.0.1:8001` |
| `python-dotenv could not parse` | Ensure `.env` uses `#` for comments, not `//` |

---

## 📋 Dependencies

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
google-genai>=2.0.0
python-dotenv>=1.0.0
pydantic>=2.0.0
```

---

## 📄 License

MIT — free to use, modify, and distribute.
