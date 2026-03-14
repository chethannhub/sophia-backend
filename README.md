# Sophia Backend

Flask backend for news retrieval, summarization, chat, and text-to-speech.

## What This Service Does

- Fetches and aggregates news from multiple providers
- Generates summaries from selected article IDs
- Supports chat sessions over selected articles
- Generates audio narration from selected article IDs

## Tech Stack

- Python 3.9+
- Flask + Flask-CORS
- LangChain + Chroma + sentence-transformers
- Gunicorn (production server)
- Piper TTS + pydub for audio generation

## Project Structure

- `app.py`: Flask API entrypoint
- `News_api/`: Core business logic (news, summarization, chat, TTS)
- `text/`: Cached/generated text data
- `summarized/audio/`: Generated audio files
- `chats/`: Chat history storage
- `db/`: Local vector store data
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container build definition

## Prerequisites

- Python 3.9 or newer
- `ffmpeg` installed and available in PATH
- Optional: Docker (for containerized run)

## Environment Variables

Create `.env` in the project root (or copy from `example.env`) and set:

```env
NEWS_API_KEY=your-newsapi-key
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-custom-search-engine-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

Notes:
- `NEWS_API_KEY` is used for daily news endpoints.
- Google API values are used by the configured search and Google-related integrations in `News_api/`.
- Keep secrets out of source control.

## Local Run (Recommended)

1. Create and activate a virtual environment.
2. Install dependencies.
3. Start Flask app.

```bash
python -m venv .venv
# Windows PowerShell:
. .venv/Scripts/Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Default app URL:

- `http://localhost:5001`

## Run With Gunicorn

```bash
gunicorn --bind 0.0.0.0:8080 --workers 2 --timeout 120 app:app
```

## Docker Run

Build and run:

```bash
docker build -t sophia-backend:local .
docker run --rm -p 8080:8080 --env-file .env sophia-backend:local
```

App URL (Docker):

- `http://localhost:8080`

## API Endpoints

- `GET /get_preview`
  - Query: `url`
- `GET|POST /get_daily_news`
  - Params/JSON: `query_news`, `query_edge`
- `GET|POST /summarize`
  - Params/JSON: `urls` (comma-separated IDs)
- `GET|POST /chat`
  - Params/JSON: `urls` (comma-separated IDs)
- `GET|POST /continue_chat`
  - Params/JSON: `chat_id`, `text`
- `GET|POST /get_audio`
  - Params/JSON: `urls` (comma-separated IDs)

## Notes on Data Directories

This project writes local runtime data to:

- `text/`
- `summarized/audio/`
- `chats/`
- `db/`

For production, use persistent storage instead of container-local filesystem paths.

## Removed Deployment Path

Google Cloud deployment scripts/manifests and GCP-specific deployment docs have been removed from this repository.

## Troubleshooting

- If audio generation fails, verify `ffmpeg` installation.
- If startup fails on dependency build, upgrade `pip` and retry.
- If endpoints return provider errors, verify API keys in `.env`.
