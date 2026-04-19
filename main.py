import os
import tempfile
import anthropic
import whisper
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Bodéwadmimwen ASR API")

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allow all origins for now — lock this down to your Lovable URL in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Load Whisper model once at startup ───────────────────────────────────────
# "base" is fastest and smallest — swap for "small" or "medium" for better accuracy
MODEL_SIZE = os.getenv("WHISPER_MODEL", "base")
print(f"Loading Whisper model: {MODEL_SIZE}")
model = whisper.load_model(MODEL_SIZE)
print("Whisper model loaded.")

# ── Anthropic client for translation ─────────────────────────────────────────
anthropic_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_SIZE}


@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    Accept an audio file, run Whisper on it, return the transcript.
    Whisper supports: mp3, mp4, wav, webm, ogg, m4a, flac
    """
    # Save upload to a temp file (Whisper needs a file path)
    suffix = _get_suffix(audio.filename or "audio.webm")
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        contents = await audio.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        result = model.transcribe(tmp_path)
        text = result.get("text", "").strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")
    finally:
        os.unlink(tmp_path)

    return {"text": text}


class TranslateRequest(BaseModel):
    text: str


@app.post("/translate")
def translate(body: TranslateRequest):
    """
    Accept Bodéwadmimwen text, return an approximate English translation via Claude.
    Always marked as AI-assisted — not community-validated.
    """
    if not body.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Translation service not configured.")

    try:
        message = anthropic_client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "You are assisting with language preservation for Bodéwadmimwen (Potawatomi), "
                        "a critically endangered Indigenous language. "
                        "Translate the following Bodéwadmimwen text to English as accurately as possible. "
                        "If you are uncertain, provide your best attempt and note the uncertainty. "
                        "Return only the translation, nothing else.\n\n"
                        f"Bodéwadmimwen text: {body.text}"
                    ),
                }
            ],
        )
        translation = message.content[0].text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

    return {"translation": translation}


def _get_suffix(filename: str) -> str:
    ext = os.path.splitext(filename)[-1].lower()
    allowed = {".mp3", ".mp4", ".wav", ".webm", ".ogg", ".m4a", ".flac"}
    return ext if ext in allowed else ".webm"