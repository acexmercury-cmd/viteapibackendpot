from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to Bodéwadmimwen ASR API"}

@app.post("/transcribe")
async def transcribe(file: UploadFile):
    # Placeholder for transcription logic using Whisper
    return {"message": "Transcription successful!"}

@app.post("/translate")
async def translate(text: str):
    # Placeholder for translation logic using Claude
    return {"message": "Translation successful!"}