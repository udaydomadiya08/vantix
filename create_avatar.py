#!/usr/bin/env python3
"""
Simple Avatar Video Creator using Wav2Lip

This script creates an avatar video by syncing a face video with an audio file.

Usage:
    python create_avatar.py --face <face_video.mp4> --audio <audio.mp3> --output <output.mp4>

Example:
    python create_avatar.py --face input_face.mp4 --audio voiceover.mp3 --output avatar_result.mp4
"""

import os
import sys
import argparse
import subprocess
from datetime import datetime

# Add Wav2Lip to path
sys.path.append(os.path.abspath('Wav2Lip'))

from Wav2Lip.inference import parser as wav2lip_parser, run_inference


def mp3_to_wav(mp3_path, wav_path, denoise=False):
    """Convert MP3 to WAV using ffmpeg, optionally applying denoising"""
    if os.path.exists(wav_path):
        os.remove(wav_path)
        print(f"🗑️  Deleted existing WAV file: {wav_path}")
    
    try:
        import ffmpeg
        stream = ffmpeg.input(mp3_path)
        
        if denoise:
            print("🔊 Applying afftdn denoising (-20dB)...")
            stream = stream.filter('afftdn', nr=20)
            
        stream.output(wav_path, ar=16000, ac=1).run(overwrite_output=True, quiet=True)
        print(f"✅ MP3 to WAV conversion complete: {wav_path}")
        return True
    except Exception as e:
        print(f"❌ FFmpeg error during conversion: {e}")
        return False


def create_avatar_video(face_video_path, audio_path, output_path, 
                       checkpoint="checkpoints/wav2lip.pth",
                       static=False, fps=None, batch_size=128, 
                       resize_factor=1, out_height=720, denoise=False):
    """
    Create an avatar video by syncing face video with audio
    
    Args:
        face_video_path: Path to the input face video (e.g., .mp4)
        audio_path: Path to the audio file (supports .mp3, .wav)
        output_path: Path where the output avatar video will be saved
        checkpoint: Path to Wav2Lip model checkpoint
        static: Use static mode (True) or dynamic (False)
        fps: Frames per second for output video (default: None, auto-detects from input)
        batch_size: Batch size for processing
        resize_factor: Factor to resize input video
        out_height: Output video height
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    # Validate inputs
    if not os.path.exists(face_video_path):
        print(f"❌ Face video not found: {face_video_path}")
        return False
    
    # Auto-detect FPS if not explicitly provided or if it's the default placeholder
    if fps is None or fps == 25:
        try:
            import cv2
            cap = cv2.VideoCapture(face_video_path)
            detected_fps = cap.get(cv2.CAP_PROP_FPS)
            cap.release()
            if detected_fps > 0:
                print(f"📹 Detected input video FPS: {detected_fps}")
                fps = detected_fps
            else:
                print("⚠️ Could not detect FPS, defaulting to 25")
                fps = 25
        except Exception as e:
            print(f"⚠️ FPS detection failed: {e}, defaulting to 25")
            fps = 25
    
    if not os.path.exists(audio_path):
        print(f"❌ Audio file not found: {audio_path}")
        return False
    
    if not os.path.exists(checkpoint):
        print(f"❌ Checkpoint not found: {checkpoint}")
        print(f"   Please download wav2lip.pth or wav2lip_gan.pth to checkpoints/")
        return False
    
    # Convert audio to WAV if it's MP3
    audio_ext = os.path.splitext(audio_path)[1].lower()
    if audio_ext == '.mp3':
        temp_wav = "temp_audio_for_avatar.wav"
        print(f"🔄 Converting MP3 to WAV {'with denoising' if denoise else ''}...")
        if not mp3_to_wav(audio_path, temp_wav, denoise=denoise):
            return False
        final_audio_path = temp_wav
    elif audio_ext == '.wav':
        final_audio_path = audio_path
    else:
        print(f"❌ Unsupported audio format: {audio_ext}")
        print(f"   Supported formats: .mp3, .wav")
        return False
    
    # Prepare Wav2Lip arguments
    args_list = [
        '--checkpoint_path', checkpoint,
        '--face', face_video_path,
        '--audio', final_audio_path,
        '--outfile', output_path,
        '--fps', str(fps),
        '--wav2lip_batch_size', str(batch_size),
        '--resize_factor', str(resize_factor),
        '--out_height', str(out_height),
    ]
    
    if static:
        args_list.append('--static')
    
    args = wav2lip_parser.parse_args(args_list)
    
    # Run Wav2Lip inference
    print("\n🎬 Starting Wav2Lip avatar generation...")
    print(f"   Face video: {face_video_path}")
    print(f"   Audio: {audio_path}")
    print(f"   Output: {output_path}")
    print(f"   Mode: {'Static' if static else 'Dynamic'}")
    
    try:
        run_inference(args)
        print(f"\n✅ Avatar video created successfully!")
        print(f"   Saved to: {output_path}")
        
        # Clean up temp WAV if created
        if audio_ext == '.mp3' and os.path.exists(temp_wav):
            os.remove(temp_wav)
            print(f"🗑️  Cleaned up temporary WAV file")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during avatar generation: {e}")
        return False


def main():
    """Command-line interface"""
    parser = argparse.ArgumentParser(
        description="Create avatar video by syncing face video with audio using Wav2Lip",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python create_avatar.py --face my_face.mp4 --audio speech.mp3 --output result.mp4
  
  # With custom settings
  python create_avatar.py --face face.mp4 --audio voice.wav --output avatar.mp4 --fps 30 --batch-size 256
  
  # Using GAN checkpoint for better quality
  python create_avatar.py --face face.mp4 --audio audio.mp3 --output out.mp4 --checkpoint checkpoints/wav2lip_gan.pth
        """
    )
    
    parser.add_argument('--face', '-f', required=True,
                       help='Path to input face video (e.g., video.mp4)')
    
    parser.add_argument('--audio', '-a', required=True,
                       help='Path to input audio file (.mp3 or .wav)')
    
    parser.add_argument('--output', '-o', default=None,
                       help='Base name/path for output video (timestamp will be appended)')
    
    parser.add_argument('--checkpoint', '-c', default='checkpoints/wav2lip.pth',
                       help='Path to Wav2Lip checkpoint (default: checkpoints/wav2lip.pth)')
    
    parser.add_argument('--static', action='store_true', default=False,
                       help='Use static mode for images (default: False, uses dynamic mode for videos)')
    
    parser.add_argument('--dynamic', action='store_true',
                       help='Use dynamic mode instead of static')
    
    parser.add_argument('--fps', type=int, default=None,
                       help='Output video FPS (default: Auto-detect from input)')
    
    parser.add_argument('--batch-size', type=int, default=128,
                       help='Batch size for processing (default: 128)')
    
    parser.add_argument('--resize-factor', type=int, default=1,
                       help='Resize factor for input video (default: 1)')
    
    parser.add_argument('--out-height', type=int, default=2160,
                       help='Output video height (default: 2160 for 4K)')
    
    parser.add_argument('--denoise', action='store_true', default=False,
                       help='Denoise audio using afftdn filter (-20dB) (default: False)')
    
    args = parser.parse_args()
    

    static_mode = args.static
    
    # Generate output filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if args.output:
        base_name, ext = os.path.splitext(args.output)
        if not ext:
            ext = ".mp4"
        output_filename = f"{base_name}_{timestamp}{ext}"
    else:
        output_filename = f"avatar_output_{timestamp}.mp4"
        
    print(f"📝 Output will be saved to: {output_filename}")
    
    # Create output directory if needed
    output_dir = os.path.dirname(output_filename)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # Create avatar video
    success = create_avatar_video(
        face_video_path=args.face,
        audio_path=args.audio,
        output_path=output_filename,
        checkpoint=args.checkpoint,
        static=static_mode,
        fps=args.fps,
        batch_size=args.batch_size,
        resize_factor=args.resize_factor,
        out_height=1080,  # Default to 2K
        denoise=args.denoise
    )
    
    if success:
        print("\n🎉 Done!")
        sys.exit(0)
    else:
        print("\n❌ Failed to create avatar video")
        sys.exit(1)


if __name__ == "__main__":
    main()
