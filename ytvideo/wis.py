import whisperx

audio_path = "voice.mp3"
device = "cpu"  # or "cuda" if you have GPU

# Load WhisperX model forcing float32 compute type
model = whisperx.load_model("tiny.en", device=device, compute_type="float32")

result = model.transcribe(audio_path)

align_model, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

aligned_result = whisperx.align(result["segments"], align_model, metadata, audio_path, device)

for word_info in aligned_result["word_segments"]:
    print(f"[{word_info['start']:.2f} - {word_info['end']:.2f}] {word_info['word']}")
