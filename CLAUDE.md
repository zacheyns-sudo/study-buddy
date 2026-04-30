# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the App

```bash
# Install dependencies (use a virtualenv)
pip install -r requirements.txt

# Set the required API key
export ANTHROPIC_API_KEY=your_key_here

# Run locally (defaults to port 5557)
python app.py

# Production (as deployed via Procfile)
gunicorn app:app
```

The app serves `index.html` from the repo root at `/` and exposes three API routes.

## Architecture

This is a two-file app:

**`app.py`** — Flask backend. Handles file parsing, prompt construction, and streaming AI responses. Three routes:
- `POST /api/upload` — accepts a file (docx/pdf/pptx/xlsx), extracts text into a list of paragraphs, truncates to `MAX_CHARS` (60,000), returns `{paragraphs, truncated, char_count}`
- `POST /api/review` — takes `{paragraphs, mode, rubric?, context?}`, streams NDJSON back. Each line is either a comment object or a final `{"type":"summary"}` line.
- `POST /api/chat` — takes `{paragraphs?, history, message}`. First message embeds the full document with `cache_control: ephemeral`; subsequent messages use the history array directly (document already cached).

**`index.html`** — Single-file SPA (HTML + embedded CSS + vanilla JS). No build step. All state lives in `localStorage` under the key `sb_v1`. The UI has two screens: upload and review. The review screen is a two-panel layout (document left, feedback right).

## Key Patterns

**Streaming**: Both `/api/review` and `/api/chat` use Flask `stream_with_context` + Anthropic's `.text_stream`. The frontend reads these as SSE-style streams via `ReadableStream`. Review responses are NDJSON — the client splits on `\n` and `JSON.parse`s each line. Chat responses are raw text streamed directly into the bubble element.

**Prompt caching**: The system prompts in `_review_stream` and `_chat_stream` use `cache_control: {type: "ephemeral"}` on the system message. The chat route also caches the document on the first user turn — the client sends `paragraphs` only on the first message; follow-ups send `history` only.

**Two modes**: `supervisor` (mentoring tone, `overall_grade: null`) and `grading` (formal assessment, letter grade). Mode is toggled in the UI and sent with each `/api/review` call. The system prompt is swapped entirely — `SUPERVISOR_PROMPT` vs `GRADING_PROMPT`.

**Document numbering**: `numbered_doc()` wraps every paragraph as `[0] text`, `[1] text`, etc. The AI is instructed to reference these indices in `paragraph_index`. The frontend uses these indices to cross-link comment cards to paragraphs.

**Paragraph truncation**: `chunk_paragraphs()` hard-stops at 60,000 chars. If truncated, the frontend shows a banner. The truncation is applied at upload time — the trimmed list is what gets stored in the JS `currentParagraphs` variable and sent to all subsequent API calls.

## Model

All three routes use `claude-sonnet-4-6`. To change the model, update the `model=` parameter in `_review_stream()` and `_chat_stream()` in `app.py`.
