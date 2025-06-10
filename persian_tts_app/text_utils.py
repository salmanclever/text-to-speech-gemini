import re

# Define a maximum character limit for TTS chunks.
# This is an assumption; actual Gemini API limits should be verified.
# The user mentioned "maximum token limit". We're using a character limit as a proxy.
MAX_CHUNK_LENGTH = 3000 # Characters

def split_text_into_chunks(text: str, max_length: int = MAX_CHUNK_LENGTH) -> list[str]:
    """
    Splits a long text into smaller chunks suitable for TTS processing.
    Attempts to split at sentence endings ('.', '؟', '!') or paragraph breaks.

    Args:
        text (str): The input Persian text.
        max_length (int): The maximum character length for each chunk.

    Returns:
        list[str]: A list of text chunks.
    """
    chunks = []
    current_chunk = ""

    # Split by common sentence terminators in Persian, also considering newlines.
    # The regex looks for '.', '؟', '!', or newline characters.
    # It uses a lookbehind `(?<=...)` to keep the delimiter at the end of the chunk.
    sentences = re.split(r'(?<=[.؟!\n])\s*', text.strip())

    # Filter out any empty strings that might result from multiple newlines
    sentences = [s for s in sentences if s.strip()]

    if not sentences: # Handle case where text has no delimiters (e.g., a very long single sentence)
        if len(text) > max_length:
            # Fallback: split by length if no natural breaks and text is too long
            for i in range(0, len(text), max_length):
                chunks.append(text[i:i+max_length])
            return chunks
        else:
            return [text] if text.strip() else []


    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # If a single sentence is already too long, split it hard.
        if len(sentence) > max_length:
            if current_chunk: # Add the pending chunk before processing the very long sentence
                chunks.append(current_chunk)
                current_chunk = ""
            # If a sentence itself is longer than max_length, we need to split it further.
            # This part will split the long sentence by max_length.
            for i in range(0, len(sentence), max_length):
                chunks.append(sentence[i:i+max_length])
            # Reset current_chunk as the long sentence has been fully processed.
            current_chunk = ""
            continue # Move to the next sentence

        if len(current_chunk) + len(sentence) + 1 <= max_length: # +1 for potential space
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
        else:
            if current_chunk: # Add the completed chunk
                chunks.append(current_chunk)
            current_chunk = sentence # Start a new chunk with the current sentence

    if current_chunk: # Add the last remaining chunk
        chunks.append(current_chunk)

    return chunks

if __name__ == '__main__':
    print("Testing text_utils.py...")

    test_text_short = "سلام دنیا. این یک آزمایش است."
    chunks_short = split_text_into_chunks(test_text_short, 50)
    print(f"Short text: '{test_text_short}' -> Chunks: {chunks_short}")
    # Expected: ['سلام دنیا.', 'این یک آزمایش است.'] (or similar depending on exact split logic with spaces)

    test_text_long = "این یک متن طولانی است. هدف از این متن، آزمایش تابع تقسیم کننده می‌باشد. آیا به درستی کار می‌کند؟ باید ببینیم. امیدوارم که همه چیز خوب پیش برود! این بخش دیگری از متن است. و این هم بخش آخر."
    chunks_long = split_text_into_chunks(test_text_long, 60)
    print(f"Long text (limit 60): -> Chunks: {chunks_long}")
    # Expected: Multiple chunks, split at punctuation.

    test_text_very_long_sentence = "اینیکجمله‌یبسیارطولانیاستکههیچنقطعهویرگولیایاپایانخطینداردوبرایهمینبایدبهصورتمستقیمبراساسطولتقسیمشودتامطمئنشویمکهاینحالتهمپشتیبانیمیشود"
    chunks_very_long_sentence = split_text_into_chunks(test_text_very_long_sentence, 50)
    print(f"Very long sentence (limit 50): -> Chunks: {chunks_very_long_sentence}")
    # Expected: ['اینیکجمله‌یبسیارطولانیاستکههیچنقطعهویرگولیایاپایانخطی', 'نداردوبرایهمینبایدبهصورتمستقیمبراساسطولتقسیمشودتامطم', 'ئنشویمکهاینحالتهمپشتیبانیمیشود']

    test_text_with_newlines = "خط اول.\nخط دوم با یک سوال؟\nخط سوم!"
    chunks_newlines = split_text_into_chunks(test_text_with_newlines, 30)
    print(f"Text with newlines (limit 30): -> Chunks: {chunks_newlines}")
    # Expected: ['خط اول.', 'خط دوم با یک سوال؟', 'خط سوم!']

    test_text_no_delimiters_long = "abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz" # 52 chars
    chunks_no_delimiters_long = split_text_into_chunks(test_text_no_delimiters_long, 20)
    print(f"Long text no delimiters (limit 20): -> Chunks {chunks_no_delimiters_long}")
    # Expected: ['abcdefghijklmnopqrst', 'uvwxyzabcdefghijklmn', 'opqrstuvwxyz']

    test_text_empty = ""
    chunks_empty = split_text_into_chunks(test_text_empty)
    print(f"Empty text: -> Chunks: {chunks_empty}") # Expected: []

    test_text_whitespace = "   \n   "
    chunks_whitespace = split_text_into_chunks(test_text_whitespace)
    print(f"Whitespace text: -> Chunks: {chunks_whitespace}") # Expected: []

    # Test where a single sentence is longer than max_length
    single_long_sentence = "این یک جمله خیلی خیلی خیلی خیلی خیلی طولانی است که از حد مجاز بیشتر است و باید شکسته شود." # length > 50
    chunks_single_long = split_text_into_chunks(single_long_sentence, 50)
    print(f"Single long sentence (limit 50): -> Chunks: {chunks_single_long}")
    # Expected: Sentence split into parts e.g. ["این یک جمله خیلی خیلی خیلی خیلی خیلی طولانی است", "که از حد مجاز بیشتر است و باید شکسته شود."]
    # OR hard split: ["این یک جمله خیلی خیلی خیلی خیلی خیلی طولانی است که", " از حد مجاز بیشتر است و باید شکسته شود."]

    # Test with a real Persian example that caused issues before
    persian_example = "این یک متن نمونه است. این متن شامل چندین جمله است که باید به درستی تقسیم شوند. آیا تقسیمات به درستی انجام می‌شوند؟ باید تست کنیم."
    # Max length should be chosen such that it forces splits.
    chunks_persian_example = split_text_into_chunks(persian_example, max_length=50)
    print(f"Persian example (limit 50): -> Chunks: {chunks_persian_example}")
