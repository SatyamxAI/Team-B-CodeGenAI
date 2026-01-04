import requests
import json

OLLAMA_URL = "http://localhost:11434/api/generate"

def generate_response(prompt, model="llama3", stream=True):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }

    response = requests.post(
        OLLAMA_URL,
        json=payload,
        stream=stream,
        timeout=120
    )

    if not stream:
        return response.json()["response"]

    def stream_generator():
        for line in response.iter_lines():
            if not line:
                continue
            try:
                data = json.loads(line.decode("utf-8"))
                yield data.get("response", "")
            except json.JSONDecodeError:
                continue

    return stream_generator()

def generate_title(text, model="llama3"):
    """
    Generate a short chat title from user input.
    """
    prompt = (
        "Generate a very short title (max 5 words) for this message.\n"
        "Do NOT use quotes.\n"
        "Do NOT add punctuation.\n\n"
        f"Message: {text}\nTitle:"
    )

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=60
    )

    title = response.json()["response"].strip()
    return title[:40]
