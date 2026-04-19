# Bodéwadmimwen ASR — FastAPI Backend

Speech recognition and translation API for the Bodéwadmimwen (Potawatomi) language preservation tool.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/transcribe` | Upload audio → transcript (Whisper) |
| POST | `/translate` | Bodéwadmimwen text → English (Claude API) |

## Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
3. Select this repo
4. Add environment variables (see below)
5. Railway builds and deploys automatically
6. Copy the generated URL → paste into Lovable as `VITE_API_URL`

## Environment Variables

Set these in Railway's dashboard under your project → Variables:

| Variable | Value |
|----------|-------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key (for translation) |
| `WHISPER_MODEL` | `base` (default) — or `small`, `medium` for better accuracy |

## Local Development

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

API will be at `http://localhost:8000`