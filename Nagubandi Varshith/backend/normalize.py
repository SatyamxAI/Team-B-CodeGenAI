import re

def normalize_ocr_text(text: str) -> str:
    """
    Cleans common OCR mistakes before sending to LLM.
    This does NOT try to fix logic — only characters.
    """

    # Remove clearly invalid symbols
    text = re.sub(r"[@¢§°]", "", text)

    # Fix common OCR numeric corruption
    text = re.sub(r"(\d)[oO]", r"\1", text)   # 10O -> 100
    text = re.sub(r"[lI](\d)", r"1\1", text)  # l0 -> 10

    # Normalize spacing around operators
    text = re.sub(r"\s*=\s*", " = ", text)
    text = re.sub(r"\s*\+\s*", " + ", text)
    text = re.sub(r"\s*-\s*", " - ", text)
    text = re.sub(r"\s*/\s*", " / ", text)

    # Collapse excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()
