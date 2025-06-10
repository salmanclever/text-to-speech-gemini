import google.generativeai as genai
import os

# This should be defined by the Gemini API documentation for Persian.
# Using placeholders for now.
AVAILABLE_SPEAKERS = {
    "فارسی - مرد ۱": "fa-ir-male1-placeholder",
    "فارسی - زن ۱": "fa-ir-female1-placeholder",
    "پیش‌فرض": "default-placeholder"
}
TTS_MODEL_NAME = "models/text-to-speech" # Or other appropriate TTS model from Gemini

# Directory where generated audio files will be saved, relative to this script's location (or main.py)
# It's better to pass this as an argument or configure it globally if main.py is in a different loc.
# For now, assume main.py and this file are in the same directory.
AUDIO_FILES_DIR = "generated_audio"
# os.makedirs(AUDIO_FILES_DIR, exist_ok=True) # Ensure dir exists, main.py will handle this

def configure_gemini(api_key):
    """Configures the Gemini API key. Returns None on success, error message string on failure."""
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        return f"خطا در پیکربندی Gemini API: {e}"
    return None

def list_available_speakers():
    """Returns a dictionary of available speakers."""
    return AVAILABLE_SPEAKERS

def text_to_audio(api_key, text_prompt, speaker_id, output_filename):
    """
    Converts text to audio using Gemini API and saves it to a file in AUDIO_FILES_DIR.

    Args:
        api_key (str): The Gemini API key.
        text_prompt (str): The text to convert.
        speaker_id (str): The identifier for the desired speaker/voice.
        output_filename (str): The simple filename (e.g., "audio_part_1.mp3")
                               to save the audio file. It will be placed in AUDIO_FILES_DIR.

    Returns:
        tuple: (str: full_output_filepath, None: error_message) on success,
               (None: full_output_filepath, str: error_message) on failure.
    """
    if not api_key:
        return None, "کلید API برای Gemini ارائه نشده است."

    config_error = configure_gemini(api_key)
    if config_error:
        return None, config_error

    # Construct full path for saving the audio file
    # Ensure AUDIO_FILES_DIR exists (caller should ideally ensure this)
    os.makedirs(AUDIO_FILES_DIR, exist_ok=True)
    full_output_filepath = os.path.join(AUDIO_FILES_DIR, output_filename)

    try:
        model = genai.GenerativeModel(TTS_MODEL_NAME)
        # The method for specifying voice/speaker needs to be confirmed from Gemini docs
        response = model.generate_content(
            text_prompt
            # Example of how voice might be specified (this is a guess):
            # generation_config=genai.types.GenerationConfig(custom_voice={'speaker_id': speaker_id})
        )

        if hasattr(response, 'audio_content') and response.audio_content:
            with open(full_output_filepath, 'wb') as f:
                f.write(response.audio_content)
            return full_output_filepath, None
        else:
            error_detail = "پاسخ API فاقد محتوای صوتی بود."
            if hasattr(response, 'prompt_feedback'):
                 if hasattr(response.prompt_feedback, 'block_reason_message') and response.prompt_feedback.block_reason_message:
                    error_detail += f" دلیل انسداد: {response.prompt_feedback.block_reason_message}"
                 elif hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                     error_detail += f" دلیل انسداد: {response.prompt_feedback.block_reason}"

            # Simulation for dummy key (as in previous version)
            if "YOUR_API_KEY_HERE" in api_key or "DUMMY_KEY" in api_key:
                print(f"SIMULATION (gemini_tts.py): Creating dummy audio file at {full_output_filepath} due to dummy API key.")
                with open(full_output_filepath, 'w') as f:
                    f.write("This is a dummy audio file content (simulated).")
                return full_output_filepath, None

            return None, f"خطا از Gemini API: {error_detail}"

    except genai.types.BlockedPromptException as e: # Corrected alias usage from previous version
        return None, f"درخواست توسط Gemini مسدود شد: {e}"
    except genai.types.StopCandidateException as e: # Corrected alias usage
        return None, f"تولید محتوا توسط Gemini متوقف شد: {e}"
    except Exception as e:
        # import traceback; traceback.print_exc() # For debugging
        return None, f"خطا در ارتباط با Gemini API: {e}"
