import google.generativeai as genai
import os

AVAILABLE_SPEAKERS = {
    "فارسی - مرد ۱": "fa-ir-male1-placeholder",
    "فارسی - زن ۱": "fa-ir-female1-placeholder",
    "پیش‌فرض": "default-placeholder"
}
TTS_MODEL_NAME = "models/text-to-speech"

def configure_gemini(api_key):
    try:
        genai.configure(api_key=api_key)
        # print("Gemini API key configured.") # Less verbose
    except Exception as e:
        # print(f"Error configuring Gemini API: {e}") # Let the caller handle logging detailed errors
        return f"خطا در پیکربندی Gemini API: {e}"
    return None

def list_available_speakers():
    return AVAILABLE_SPEAKERS

def text_to_audio(api_key, text_prompt, speaker_id, output_filepath):
    """
    Converts text to audio using Gemini API and saves it to a file.

    Returns:
        tuple: (str: output_filepath, None: error_message) on success,
               (None: output_filepath, str: error_message) on failure.
    """
    if not api_key:
        return None, "کلید API برای Gemini ارائه نشده است."

    # Configure Gemini API (idempotent, but returns error message if fails)
    config_error = configure_gemini(api_key)
    if config_error:
        return None, config_error

    try:
        # print(f"Requesting TTS for: '{text_prompt[:50]}...' with speaker: {speaker_id}")

        model = genai.GenerativeModel(TTS_MODEL_NAME)
        # This is the part that needs actual knowledge of the TTS API structure for voice selection.
        # Assuming the speaker_id might be part of a voice configuration object or a direct parameter.
        # For now, the placeholder speaker_id will likely cause an error with the real API.
        response = model.generate_content(
            text_prompt
            # generation_config=genai.types.GenerationConfig(
            # voice_name=speaker_id # This is a guess for how speaker ID might be passed
            # )
            # Or, the API might require specific formatting in the prompt or a different method.
        )

        # Check for audio content in the response
        # The exact attribute name for audio content needs to be verified from SDK documentation.
        # Common patterns: response.audio_content, response.audio, response.result.audio
        # For now, using a hypothetical 'audio_content' attribute.
        if hasattr(response, 'audio_content') and response.audio_content:
            with open(output_filepath, 'wb') as f:
                f.write(response.audio_content) # audio_content should be bytes
            # print(f"Audio content saved to {output_filepath}")
            return output_filepath, None
        else:
            # If no audio_content, try to find an error message in the response
            error_detail = "پاسخ API فاقد محتوای صوتی بود."
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                 # Check for block_reason or other error indicators
                if hasattr(response.prompt_feedback, 'block_reason_message') and response.prompt_feedback.block_reason_message:
                    error_detail += f" دلیل انسداد: {response.prompt_feedback.block_reason_message}"
                elif hasattr(response.prompt_feedback, 'block_reason') and response.prompt_feedback.block_reason:
                     error_detail += f" دلیل انسداد: {response.prompt_feedback.block_reason}"


            # Fallback for other errors or unexpected responses
            # print(f"SIMULATING: Audio content would be saved to {output_filepath} if API call was real.")
            # print(f"SIMULATING: Response object received: {type(response)}, attributes: {dir(response)}")
            # Try to see if there's any text part in the response for debugging
            # try:
            #     print(f"SIMULATING: Response text part (if any): {response.text}")
            # except Exception:
            #     pass

            # For now, if it's not audio_content, assume it's an error or unexpected response.
            # The actual error reporting from Gemini API might be different.
            # This part will need refinement based on real API responses.

            # Create a dummy file to allow workflow to continue during simulation if no real API key
            # This simulation should only happen if API_KEY is a known dummy or placeholder
            if "YOUR_API_KEY_HERE" in api_key or "DUMMY_KEY" in api_key or not api_key: # Basic check
                print(f"SIMULATION: Creating dummy audio file at {output_filepath} due to dummy/missing API key.")
                with open(output_filepath, 'w') as f:
                    f.write("This is a dummy audio file content (simulated).")
                return output_filepath, None # Simulate success for dummy key

            return None, f"خطا از Gemini API: {error_detail}"

    except genai.types.BlockedPromptException as e:
        return None, f"درخواست توسط Gemini مسدود شد: {e}"
    except genai.types.StopCandidateException as e:
        return None, f"تولید محتوا توسط Gemini متوقف شد: {e}"
    except Exception as e:
        # import traceback
        # traceback.print_exc() # For debugging
        # More general error, could be network, invalid API key format, etc.
        return None, f"خطا در ارتباط با Gemini API: {e}"


if __name__ == '__main__':
    print("Testing gemini_tts.py with error return...")
    # Setup for testing (as before, condensed)
    # Attempt to load from .env for standalone testing
    from dotenv import load_dotenv
    if os.path.exists(".env"): # Look in current dir
        load_dotenv(".env")
    elif os.path.exists("../.env"): # Look in parent if script is in a subdir like persian_tts_app
        load_dotenv("../.env")

    api_key_to_test = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE") # Test with actual key from .env if present

    # Create test_output directory if it doesn't exist
    if not os.path.exists("test_output"):
        os.makedirs("test_output")

    output_file = "test_output/test_audio_err.mp3"
    speakers = list_available_speakers()
    speaker = speakers.get("پیش‌فرض", "default-placeholder")

    # Test 1: Valid (simulated) call or real call if key is valid
    print(f"\nTest 1: Attempting TTS with key: ...{api_key_to_test[-4:] if len(api_key_to_test) > 4 else api_key_to_test}")
    fpath, err = text_to_audio(api_key_to_test, "سلام، این یک آزمایش است.", speaker, output_file)
    if err:
        print(f"Test 1 Error: {err}")
    else:
        print(f"Test 1 Success: Audio at {fpath}")
        if os.path.exists(fpath):
            print(f"File {fpath} created.")
        else:
            print(f"File {fpath} NOT created (unexpected).")


    # Test 2: Invalid API key (empty string)
    print("\nTest 2: No API Key (empty string)")
    fpath_no_key, err_no_key = text_to_audio("", "سلام", speaker, "test_output/no_key_test.mp3")
    if err_no_key:
        print(f"Test 2 Error (expected): {err_no_key}")
    else:
        print(f"Test 2 Success (unexpected for no key): {fpath_no_key}")

    # Test 3: Invalid Speaker ID (if API reaches that point)
    # This depends on having a valid API key to get past initial checks.
    if api_key_to_test and api_key_to_test != "YOUR_API_KEY_HERE" and not ("DUMMY_KEY" in api_key_to_test):
        print("\nTest 3: Invalid Speaker ID (with potentially valid key)")
        invalid_speaker = "invalid-speaker-id" # This ID is not in AVAILABLE_SPEAKERS
        # The current text_to_audio doesn't validate speaker_id against AVAILABLE_SPEAKERS
        # but the API itself would likely reject an unknown/unsupported speaker ID/voice name.
        fpath_inv_spk, err_inv_spk = text_to_audio(api_key_to_test, "تست گوینده نامعتبر", invalid_speaker, "test_output/invalid_speaker_test.mp3")
        if err_inv_spk:
            print(f"Test 3 Error (expected for invalid speaker, or API key error if key is bad): {err_inv_spk}")
        else:
            print(f"Test 3 Success (unexpected for invalid speaker): {fpath_inv_spk}")
    else:
        print("\nTest 3: Invalid Speaker ID - Skipped (real API key not available or is placeholder)")
