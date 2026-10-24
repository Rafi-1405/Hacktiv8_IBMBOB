"""
AutoSpec QA — FastAPI Backend
Transforms user stories / casual problem statements into structured BDD Gherkin
test cases via the Google Gemini API.

Usage:
    uvicorn main:app --reload
"""

import os
import re
import time
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from google import genai
from google.genai import types as genai_types
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

load_dotenv()  # reads .env for GEMINI_API_KEY

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger(__name__)

# Configure the Gemini client once at startup
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY is not set — API calls will fail at runtime.")

# google-genai v2: client is instantiated per-request (stateless, thread-safe)
# We create a module-level client when the key is present.
_client: genai.Client | None = (
    genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None
)

app = FastAPI(
    title="AutoSpec QA",
    description="Automated BDD Gherkin Test Case Generator powered by Gemini",
    version="1.0.0",
)

# Allow the HTML front-end to call this server from any origin during dev.
# Lock this down to a specific domain in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Serve static assets (CSS overrides, any extra files placed in /static)
_static_path = Path(__file__).parent / "static"
if _static_path.exists():
    app.mount("/static", StaticFiles(directory=str(_static_path)), name="static")


# ---------------------------------------------------------------------------
# Prompt engineering
# ---------------------------------------------------------------------------

SYSTEM_INSTRUCTION = """
You are AutoSpec QA, an expert BDD test case engineer with deep knowledge of
Gherkin syntax, WCAG 2.1 accessibility standards, UX engineering, and software
quality assurance best practices.

YOUR SOLE JOB is to read the user-supplied requirement (which may be a formal
User Story, a PRD excerpt, or a casual pain-point description) and return
ONLY a structured Gherkin test suite — no conversational text, no explanations,
no markdown fences outside the output.

OUTPUT RULES (STRICT):
1. Begin with:      Feature: <short descriptive name>
2. Then a one-line:  # <concise feature description>
3. Divide scenarios into exactly THREE labelled sections:
   ## POSITIVE FUNCTIONAL & FLOW
   ## NEGATIVE & INPUT VALIDATION
   ## EDGE CASES, ACCESSIBILITY & UI STATE
4. Each section must contain at least 2 Scenario blocks.
5. Every Scenario uses only: Scenario, Given, When, Then, And, But.
6. Infer missing technical detail from the input:
   - If accessibility is mentioned → add WCAG 2.1 AA scenarios (keyboard nav,
     screen-reader labels, colour contrast, touch targets ≥ 44 × 44 px).
   - If a form is implied → add required-field, max-length, and XSS/injection
     boundary scenarios.
   - If a flow is implied → add happy-path and error-path with clear states.
7. Use present-tense, active voice in step text.
8. Do NOT add numbering to Scenario names beyond what is in the output.
9. Do NOT wrap the output in ```gherkin fences.
10. Do NOT add any text before "Feature:" or after the last scenario step.
""".strip()


def build_user_prompt(raw_input: str) -> str:
    """Wrap the sanitised user input in a structured prompt."""
    return (
        "Transform the following requirement into a complete BDD Gherkin "
        "test suite following all system rules exactly:\n\n"
        f"--- REQUIREMENT START ---\n{raw_input}\n--- REQUIREMENT END ---"
    )


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class GenerateRequest(BaseModel):
    """Payload sent by the browser."""

    input_text: str

    @field_validator("input_text")
    @classmethod
    def validate_input(cls, v: str) -> str:
        # Strip surrounding whitespace
        v = v.strip()
        if not v:
            raise ValueError("Input text must not be empty.")
        if len(v) < 10:
            raise ValueError("Input text is too short to derive meaningful test cases.")
        if len(v) > 8000:
            raise ValueError("Input text exceeds the 8 000-character limit.")
        # Basic sanitisation: remove null bytes
        v = v.replace("\x00", "")
        return v


class GenerateResponse(BaseModel):
    """Payload returned to the browser."""

    gherkin: str
    token_count: int | None = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def serve_ui():
    """Serve the single-page front-end."""
    html_path = Path(__file__).parent / "index.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="index.html not found.")
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.post("/generate", response_model=GenerateResponse)
async def generate_test_cases(payload: GenerateRequest):
    """
    Accept a user story / requirement, call Gemini, and return structured Gherkin.
    """
    logger.info("Generate request received (%d chars)", len(payload.input_text))

    if not _client:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key is not configured on the server.",
        )

    # Retry up to 3 times with exponential back-off for transient 503 errors
    # (common on free-tier keys during traffic spikes).
    _MAX_RETRIES = 3
    _RETRY_DELAYS = [3, 7, 15]   # seconds between attempts
    last_exc: Exception | None = None

    for attempt in range(_MAX_RETRIES):
        try:
            # google-genai v2 API: client.models.generate_content()
            response = _client.models.generate_content(
                model="gemini-3.8-flash",
                contents=build_user_prompt(payload.input_text),
                config=genai_types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.3,    # lower = more deterministic / structured
                    max_output_tokens=4096,
                ),
            )
            last_exc = None
            break   # success — exit retry loop
        except Exception as exc:
            err_str = str(exc)
            # Safety-filter rejection is permanent — never retry
            if "SAFETY" in err_str.upper() or "blocked" in err_str.lower():
                logger.warning("Prompt blocked by Gemini safety filters: %s", exc)
                raise HTTPException(
                    status_code=422,
                    detail="The input was blocked by the AI safety filter. Please rephrase.",
                ) from exc
            # 503 / 429 are transient — retry with back-off
            is_transient = "503" in err_str or "429" in err_str or "UNAVAILABLE" in err_str.upper()
            if is_transient and attempt < _MAX_RETRIES - 1:
                delay = _RETRY_DELAYS[attempt]
                logger.warning(
                    "Transient Gemini error (attempt %d/%d), retrying in %ds: %s",
                    attempt + 1, _MAX_RETRIES, delay, exc,
                )
                time.sleep(delay)
                last_exc = exc
                continue
            # Non-transient or final attempt
            last_exc = exc
            break

    if last_exc is not None:
        logger.error("Gemini API error after %d attempts: %s", _MAX_RETRIES, last_exc)
        raise HTTPException(
            status_code=502,
            detail=f"AI service error: {last_exc}",
        ) from last_exc

    gherkin_text = (response.text or "").strip()

    # Guard: if the model still returned fenced markdown, strip the fences
    gherkin_text = re.sub(r"^```[a-z]*\n?", "", gherkin_text, flags=re.MULTILINE)
    gherkin_text = re.sub(r"\n?```$", "", gherkin_text, flags=re.MULTILINE)
    gherkin_text = gherkin_text.strip()

    # Attempt to read usage metadata (not always present)
    token_count: int | None = None
    try:
        token_count = response.usage_metadata.total_token_count
    except AttributeError:
        pass

    logger.info("Generation successful — %d output chars", len(gherkin_text))
    return GenerateResponse(gherkin=gherkin_text, token_count=token_count)


@app.get("/health")
async def health():
    """Liveness probe — returns 200 when the server is running."""
    return {"status": "ok", "api_key_configured": bool(_client)}
