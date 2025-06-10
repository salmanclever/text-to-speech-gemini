import re

MAX_CHUNK_LENGTH = 3000 # Characters

def split_text_into_chunks(text: str, max_length: int = MAX_CHUNK_LENGTH) -> list[str]:
    """
    Splits a long text into smaller chunks suitable for TTS processing.
    Attempts to split at sentence endings ('.', '؟', '!') or paragraph breaks.
    """
    chunks = []
    current_chunk = ""
    sentences = re.split(r'(?<=[.؟!\n])\s*', text.strip())
    sentences = [s for s in sentences if s.strip()]

    if not sentences:
        if len(text) > max_length:
            for i in range(0, len(text), max_length):
                chunks.append(text[i:i+max_length])
            return chunks
        else:
            return [text] if text.strip() else []

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        if len(sentence) > max_length:
            # If current_chunk has content, add it before processing the long sentence
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = "" # Reset for next iteration
            # Split the long sentence itself
            for i in range(0, len(sentence), max_length):
                chunks.append(sentence[i:i+max_length])
            continue

        if len(current_chunk) + len(sentence) + 1 <= max_length:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
