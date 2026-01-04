import whisper
import tempfile
import soundfile as sf
import os

# Load model once at module level
model = whisper.load_model("base")

def transcribe_audio(audio_frames, sample_rate=48000):
    """
    audio_frames: list of numpy arrays from WebRTC
    """

    if not audio_frames:
        return ""

    audio = b"".join(audio_frames)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        filename = f.name
        sf.write(filename, audio, sample_rate)

    result = model.transcribe(filename)
    os.remove(filename)

    return result["text"].strip()
