def build_prompt(chat_history):
    system_instruction = (
        "You are a coding assistant.\n"
        "When you write code, ALWAYS format it using Markdown code blocks.\n"
        "Example:\n"
        "```python\n"
        "print('Hello')\n"
        "```\n"
        "Explain clearly outside code blocks.\n\n"
    )

    prompt = system_instruction

    for msg in chat_history:
        role = msg["role"].upper()
        content = msg["content"]
        prompt += f"{role}: {content}\n"

    prompt += "ASSISTANT:"
    return prompt

def build_image_debug_prompt(ocr_text):
    return f"""
You are an expert software engineer.You are highly talented at debugging code snippets that have been extracted from images using OCR
The following code was extracted from an IMAGE of source code.
OCR may contain mistakes in spacing, symbols, or numbers.

Your job is to:
- Reconstruct the code as it was most likely written
- Understand what the code is doing
- Identify any bugs or errors
- Explain the issue clearly
- Provide corrected code if needed

Do NOT mention OCR.
Do NOT mention extraction errors.
Act as if you are reading the original source code.

CODE FROM IMAGE:
----------------
{ocr_text}
----------------

Respond in this structure:

1. What the code does
2. Bug or issue (if any)
3. Corrected code
"""