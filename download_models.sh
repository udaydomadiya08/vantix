#!/bin/bash
# 🏛️ VANTIX MODEL SYNC (v1.0)
# This script downloads the heavy Wav2Lip checkpoint for production.

mkdir -p checkpoints

echo "🛰️ DOWNLOADING WAV2LIP CHECKPOINT (416MB)..."
# Using a reliable public mirror for the Wav2Lip v1 checkpoint
curl -L -o checkpoints/wav2lip.pth "https://www.dropbox.com/s/76p8i9dypb6x412/wav2lip.pth?dl=1"

echo "✅ CHECKPOINT SYNCHRONIZED."
