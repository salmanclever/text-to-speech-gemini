from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import datetime
import aiofiles # For async file operations if needed, though FileResponse handles sync opening

# Import utility modules
import text_utils
import gemini_tts

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- App Initialization ---
app = FastAPI(title="Persian TTS Backend")

# Configure CORS
origins = [
    "http://localhost:5173",  # Default Vite frontend port
    "http://localhost:3000",  # Common React dev port
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Ensure necessary directories exist ---
# Base directory for generated audio files (consistent with gemini_tts.py)
AUDIO_OUTPUT_DIR = gemini_tts.AUDIO_FILES_DIR
os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

# --- API Models (Pydantic models for request bodies) ---
from pydantic import BaseModel

class TTSRequest(BaseModel):
    text: str
    speaker_id: str # This will be the placeholder value like "fa-ir-male1-placeholder"

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "Persian TTS Backend is running!"}

@app.get("/api/speakers")
async def get_speakers():
    """Returns the list of available (placeholder) speakers."""
    return {"speakers": gemini_tts.list_available_speakers()}

@app.post("/api/tts")
async def text_to_speech_conversion(request: TTSRequest = Body(...)):
    """
    Converts text to speech.
    Receives text and speaker_id, processes it, and returns URLs to audio files.
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        raise HTTPException(status_code=400, detail="کلید API برای Gemini به درستی تنظیم نشده است.")

    # Validate speaker_id
    is_valid_speaker = False
    # Check if the provided speaker_id is one of the values in AVAILABLE_SPEAKERS
    if request.speaker_id in gemini_tts.AVAILABLE_SPEAKERS.values():
        is_valid_speaker = True

    if not is_valid_speaker:
        # Attempt to check if it's a key, though frontend should send value
        # This part is just for robustness if frontend sends key instead of value
        if request.speaker_id in gemini_tts.AVAILABLE_SPEAKERS.keys():
             # If it was a key, use the corresponding value
             request.speaker_id = gemini_tts.AVAILABLE_SPEAKERS[request.speaker_id]
             is_valid_speaker = True # Now it's valid (using the value)
        else:
            raise HTTPException(status_code=400, detail=f"شناسه گوینده نامعتبر است: {request.speaker_id}")


    if not request.text.strip():
        raise HTTPException(status_code=400, detail="متن ورودی نمی‌تواند خالی باشد.")

    chunks = text_utils.split_text_into_chunks(request.text)
    if not chunks:
        raise HTTPException(status_code=400, detail="پس از پردازش، متنی برای تبدیل وجود ندارد.")

    audio_file_urls = []
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    config_error = gemini_tts.configure_gemini(GEMINI_API_KEY)
    if config_error:
        # Log the detailed configuration error on the server
        print(f"API Configuration Error: {config_error}")
        # Provide a more generic error to the client
        raise HTTPException(status_code=500, detail="خطا در پیکربندی سرویس TTS.")


    for i, chunk in enumerate(chunks):
        output_filename_simple = f"output_{timestamp}_part_{i+1}.mp3"

        saved_filepath, error_message = gemini_tts.text_to_audio(
            api_key=GEMINI_API_KEY,
            text_prompt=chunk,
            speaker_id=request.speaker_id,
            output_filename=output_filename_simple
        )

        if error_message:
            print(f"Error converting chunk {i+1}: {error_message}")
            raise HTTPException(status_code=500, detail=f"خطا در تبدیل قطعه {i+1} به گفتار: {error_message[:100]}") # Truncate long API errors

        if saved_filepath:
            audio_file_urls.append(f"/audio/{output_filename_simple}")
        else: # Should be covered by error_message
            raise HTTPException(status_code=500, detail=f"خطای نامشخص در ذخیره فایل صوتی برای قطعه {i+1}.")

    if not audio_file_urls: # Should not be reached if previous checks are done, but as a safeguard
        raise HTTPException(status_code=500, detail="هیچ فایل صوتی تولید نشد.")

    return {"audio_urls": audio_file_urls, "message": f"{len(audio_file_urls)} قطعه صوتی با موفقیت تولید شد."}


@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Serves a generated audio file."""
    file_path = os.path.join(AUDIO_OUTPUT_DIR, filename)

    if ".." in filename or filename.startswith("/"):
        raise HTTPException(status_code=400, detail="نام فایل نامعتبر است.")

    if not os.path.exists(file_path):
        # Attempt to see if the file exists with a different case or slight variation (less critical)
        print(f"File not found at exact path: {file_path}")
        # Check case-insensitively (simple check, might not be robust for all FS)
        # For now, stick to exact match for security and simplicity.
        raise HTTPException(status_code=404, detail="فایل صوتی یافت نشد.")

    media_type = 'audio/mpeg'
    if filename.lower().endswith(".wav"):
        media_type = 'audio/wav'

    return FileResponse(path=file_path, media_type=media_type, filename=filename)


if __name__ == "__main__":
    import uvicorn
    # Print statements for server startup
    print(f"Attempting to start Uvicorn server...")
    print(f"Gemini API Key Loaded: {'Yes' if GEMINI_API_KEY and GEMINI_API_KEY != 'YOUR_API_KEY_HERE' else 'No or Placeholder'}")
    print(f"Audio files will be served from: {os.path.abspath(AUDIO_OUTPUT_DIR)}")

    # Check API key configuration at startup
    if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_API_KEY_HERE":
        config_error = gemini_tts.configure_gemini(GEMINI_API_KEY)
        if config_error:
            print(f"WARNING: Gemini API Key configuration failed at startup: {config_error}")
        else:
            print("Gemini API Key configured successfully at startup.")
    else:
        print("WARNING: Gemini API Key is not set or is a placeholder. TTS functionality will be limited/fail.")

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False) # reload=False for this check
