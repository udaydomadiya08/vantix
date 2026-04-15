


import whisperx

audio_path = "/Users/uday/Downloads/VIDEOYT/voice.mp3"  # Replace with your actual audio path

device = "cpu"
model = whisperx.load_model("tiny.en", device=device, compute_type="float32")

# Transcribe audio
result = model.transcribe(audio_path)

# Load alignment model
align_model, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

# Align to get word-level timestamps
aligned_result = whisperx.align(result["segments"], align_model, metadata, audio_path, device)

# Extract word segments
word_segments = aligned_result["word_segments"]

# Print word-level timestamp data
for i, word in enumerate(word_segments):
    print(f"{i+1:02d}. '{word['word']}' — Start: {word['start']:.2f}s, End: {word['end']:.2f}s")

