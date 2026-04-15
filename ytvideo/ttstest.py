# test_coqui.py
from TTS.api import TTS

# Use VITS for great quality & speed
tts = TTS(model_name="tts_models/en/multi-dataset/tortoise-v2", progress_bar=True, gpu=False)
tts.tts_to_file(text="Hello! This is a test using Coqui TTS VITS model.", file_path="output.wav")
