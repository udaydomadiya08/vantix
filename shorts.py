import os
import time
import random
import json
import subprocess
import re
import requests
import shutil
import hashlib
import socket
import pickle
import threading
import numpy as np
import colorsys
import asyncio
from datetime import datetime
from functools import wraps
from io import BytesIO
from collections import Counter
from pathlib import Path

import torch
import torch.serialization
import nltk
import spacy
import ffmpeg
from gtts import gTTS
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont, ImageOps
from nltk.tokenize import sent_tokenize
from serpapi import GoogleSearch

# MoviePy Core
import moviepy.editor as mpe
from moviepy.editor import (
    VideoFileClip, concatenate_videoclips, AudioFileClip, 
    ColorClip, TextClip, CompositeVideoClip, ImageClip, 
    VideoClip, vfx
)
from moviepy.config import change_settings

# Parallelism
from parallel_helper import ParallelOrchestrator

# 🏛️ PROJECT ROOT SYNCHRONIZATION (v111.0)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

def layer_sfx_on_audio(base_audio_path, sfx_list):
    """👑 NEURAL SFX ORCHESTRATION (v56): Layer cinematic sounds on voiceover (WAV Standard)"""
    if not sfx_list: return base_audio_path
    
    try:
        base = AudioSegment.from_file(base_audio_path)
        
        for sfx_path, start_time in sfx_list:
            if not os.path.exists(sfx_path): continue
            
            sfx = AudioSegment.from_file(sfx_path)
            # Normalize SFX volume (ducking)
            sfx = sfx - 15 # Lower SFX volume so it doesn't drown voiceover
            
            # Position SFX at start_time (ms)
            position_ms = int(start_time * 1000)
            base = base.overlay(sfx, position=position_ms)
            
        # 💥 CINEMATIC MASTERING (v56): Export as WAV for 100% MoviePy stability
        output_path = base_audio_path.replace(".mp3", "_sfx.wav").replace(".wav", "_sfx_v2.wav")
        base.export(output_path, format="wav")
        return output_path
    except Exception as e:
        print(f"❌ SFX Layering failed: {e}")
        return base_audio_path

# === MoviePy & ImageMagick (INDUSTRIAL STABILIZATION) === #
def discover_imagemagick():
    """👑 VANTIX RENDERER: Autonomous ImageMagick Discovery"""
    candidates = [
        "/usr/bin/convert",
        "/usr/bin/magick",
        "/opt/homebrew/bin/magick",
        "/usr/local/bin/convert",
        "convert"
    ]
    for path in candidates:
        if os.path.exists(path) or shutil.which(path):
            print(f"🎬 [RENDERER] ImageMagick discovered at: {path}")
            return path
    print("⚠️ [RENDERER] ImageMagick not found. Subtitles may fail.")
    return "convert"

try:
    change_settings({"IMAGEMAGICK_BINARY": discover_imagemagick()})
except Exception as e:
    print(f"⚠️ [RENDERER] MoviePy configuration failed: {e}")

def perform_industrial_cleanup():
    """🧹 [SANITIZER]: Purge all temporary artifacts from previous production cycles."""
    temp_folders = ["video_creation", "audio", "pexels_images", "__pycache__"]
    for folder in temp_folders:
        path = os.path.join(PROJECT_ROOT, folder)
        if os.path.exists(path):
            print(f"🧹 [CLEANUP]: Purging {folder}...")
            shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path, exist_ok=True)

def prep_milestone_ffmpeg(input_path, output_path, duration, width=1080, height=1920):
    """
    🏎️ [WARP-PREP] Native FFmpeg Normalization (v122.24):
    Force-normalizes raw assets into perfectly calibrated blocks at native speed.
    Supports both Vertical (1080x1920) and Horizontal (1920x1080) output.
    """
    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height},setsar=1",
            "-t", str(duration + 0.3), # 🏎️ [HEADROOM]: Add 0.3s buffer to silence MoviePy EOF warnings
            "-r", "30",
            "-pix_fmt", "yuv420p",
            "-an", # Strip audio to prevent MoviePy muxing collisions
            output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"⚠️ FFmpeg Warp-Prep Failed: {e}")
        return False

# 💥 [ORPHAN PURGE]: Delete older video fragments (not the main outputs)
def purge_orphan_fragments():
    """🧹 [SANITIZER]: Flush orphan .mp4 / .mp3 / .wav fragments from synthesis root."""
    print("🧹 [CLEANUP]: Flushing orphan synthesis blocks...")
    for root, dirs, files in os.walk(PROJECT_ROOT):
        if "video_created" in root or "video_creation" in root: continue # Preserve active fragments
        for f in files:
            if f.endswith((".mp3", ".mp4", ".wav")):
                try: os.remove(os.path.join(root, f))
                except: pass

# --- GLOBAL STABILITY REGISTRY ---
import threading
VANTIX_RENDER_LOCK = threading.Lock()

def create_caption_clips(word_segments, resolution, include_avatar=True):
    """🖼️ [VANTIX CAPTIONS]: Generate high-retention cinematic text overlays."""
    from moviepy.editor import TextClip
    
    caption_clips = []
    width, height = resolution
    
    # 🎨 [STYLING]: Anton Regular for Bold Viral Impact
    font_pt = 140 if width > 1000 else 70
    color = "yellow"
    stroke_color = "black"
    stroke_width = 3
    
    for segment in word_segments:
        try:
            word = segment["word"].upper().strip()
            duration = segment["end"] - segment["start"]
            if duration <= 0: continue
            
            # 🎨 [STYLING]: Anton Regular with Iterative Fallback
            # Fonts to try in order of brand priority
            font_priorities = ["Anton-Regular", "Arial-Bold", "DejaVu-Sans-Bold", "Liberation-Sans-Bold"]
            
            txt = None
            for font_name in font_priorities:
                try:
                    with VANTIX_RENDER_LOCK: # 🔐 Prevent ImageMagick collision
                        txt = TextClip(
                            word,
                            font=font_name,
                            fontsize=font_pt,
                            color=color,
                            stroke_color=stroke_color,
                            stroke_width=stroke_width,
                            method="label",
                            size=(width * 0.8, None)
                        ).set_start(segment["start"]).set_duration(duration)
                    
                    # 💥 PRE-FLIGHT CHECK (v107.0): Verify frame AND mask integrity
                    _ = txt.get_frame(0)
                    if hasattr(txt, 'mask') and txt.mask is not None:
                        _ = txt.mask.get_frame(0)
                    
                    break # Success!
                except:
                    continue # Try next font
            
            if txt is None: continue # Skip if all fonts fail
                
            # Position at 70% height for vertical impact
            v_pos = height * 0.7 if not include_avatar else height * 0.5
            txt = txt.set_position(("center", v_pos))
            
            caption_clips.append(txt)
        except Exception as e:
            print(f"⚠️ Caption Error for '{segment.get('word')}': {e}")
            
    return caption_clips

import socket
# 🏛️ [VANTIX SYNC] socket.setdefaulttimeout(6000) removed to favor Global Sentinel (30s)

from googleapiclient.errors import HttpError
import pickle
import shutil
from pathlib import Path
import re  
from serpapi import GoogleSearch
import os
# 🛡️ [ENV-SANITIZATION]: Neutralizing auto-proxy injection for legacy SDKs
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)


import sys
sys.path.append(os.path.abspath('Wav2Lip'))

# Set environment variables so pydub can find ffmpeg and ffprobe

os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

# Optional: also explicitly set converter paths (may be ignored by some methods)
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"
AudioSegment.ffprobe = "/opt/homebrew/bin/ffprobe"

# 🎨 [INDUSTRIAL] Visual DNA (v103.1)
# Gemini/Cinematic AI Node Purged. Returning to Stock-Centric discovery.

# PACING_INTENSITY (1.0 = Standard, 0.5 = Slow/Cinematic, 2.0 = Fast/TikTok)
PACING_INTENSITY = 1.0

# CLIENT_SECRETS_FILE = "/Users/uday/Downloads/VIDEOYT/client_secret_.json"  # Path to your client secret
# SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
# API_SERVICE_NAME = "youtube"
# API_VERSION = "v3"

# === Initial Setup === #
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nlp = spacy.load("en_core_web_sm")

# === Global Layout & Rendering Settings (v59.1) ===
TARGET_RES = (1080, 1920) # Default Vertical
IS_HORIZONTAL = False

def set_orientation(horizontal=False):
    global TARGET_RES, IS_HORIZONTAL
    IS_HORIZONTAL = horizontal
    TARGET_RES = (1920, 1080) if horizontal else (1080, 1920)
    print(f"📐 [ENGINE] Orientation locked to: {'HORIZONTAL' if horizontal else 'VERTICAL'} ({TARGET_RES[0]}x{TARGET_RES[1]})")

# === API KEYS === #
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
SERP_API_KEY = os.environ.get("SERP_API_KEY", "")

# 💥 GLOBAL ASSET REGISTRY (v45.6): Hard Zero-Reuse Enforcement
GLOBAL_USED_URLS = set()


def retry_infinite(delay=5, max_delay=15, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            current_delay = delay
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    # Detect 429 Throttle in exception message or status code
                    is_throttle = "429" in str(e) or "Too Many Requests" in str(e)
                    
                    print(f"❌ '{func.__name__}' failed (Attempt {attempt}): {e}")
                    
                    wait_time = 15 if is_throttle else current_delay
                    if is_throttle:
                        print(f"🚦 [THROTTLE DETECTED] Backing off for {wait_time}s...")
                    else:
                        print(f"🔁 Retrying in {wait_time}s...")
                        
                    time.sleep(wait_time)
                    
                    # Exponential backoff for non-throttle errors
                    if not is_throttle:
                        current_delay = min(max_delay, current_delay * backoff_factor)
        return wrapper
    return decorator
# === AI Helper (Centralized Synthesis Engine v69.0) === #
from ai_helper import generate_ai_response, AIResponse

# Aliases for drop-in compatibility
def generate_groq_response(prompt, system_message="You are a cinematic assistant.", user_keys=None):
    return generate_ai_response(f"System: {system_message}\nUser: {prompt}", user_keys=user_keys)

def generate_gemini_response(prompt, system_message="You are a cinematic assistant.", user_keys=None):
    return generate_ai_response(f"System: {system_message}\nUser: {prompt}", user_keys=user_keys)

class GroqResponse:
    def __init__(self, text):
        self.text = text
# --- VANTIX CORE NEURAL PACING (v1.0) --- #
def get_scene_pacing_intent(sentence, user_keys=None):
    """
    🧠 SCRIPT INTENT ANALYZER (v47.2):
    Classifies a sentence as MONTAGE (descriptive/busy) or SUSTAINED (singular/majestic).
    """
    prompt = f"""Analyze this video script sentence and decide the visual intent:
    Script: "{sentence}"
    
    INTENT CATEGORIES:
    - MONTAGE: For environments with multiple objects, busy actions, or descriptive complexity.
    - SUSTAINED: For singular focus, steady movements, majestic scenery, or atmospheric stillness.
    
    Return ONLY a JSON formatted as follows:
    {{"intent": "MONTAGE" | "SUSTAINED", "justification": "<short reason>"}}
    """
    try:
        resp_obj = generate_groq_response(prompt, system_message="Return ONLY JSON valid object.", user_keys=user_keys)
        json_match = re.search(r'\{.*\}', resp_obj.text.strip(), re.DOTALL)
        if json_match:
            data = json.loads(json_match.group(0))
            intent = data.get("intent", "SUSTAINED").upper()
            print(f"🧠 [INTENT] Classified as {intent}: {data.get('justification')}")
            return intent
    except Exception as e:
        print(f"⚠️ Intent Analysis Fallback: {e}")
    return "SUSTAINED" # Default to cinematic stability

# Drop-in replacement for Gemini
generate_gemini_response = generate_groq_response

def get_word_level_transcription(audio_path, user_keys=None):
    """
    ⚡ UNIVERSAL TRANSCRIPTION ENGINE (v48.3):
    Cloud-First Groq Turbo (Direct REST) fallback to Local WhisperX.
    """
    import requests
    WHISPER_MODELS = ["whisper-large-v3-turbo", "whisper-large-v3"]
    groq_api_key = (user_keys or {}).get("groq") or os.environ.get("GROQ_API_KEY")

    if groq_api_key:
        for model in WHISPER_MODELS:
            try:
                print(f"⚡ [Groq REST] Transcribing with {model}...")
                url = "https://api.groq.com/openai/v1/audio/transcriptions"
                headers = {"Authorization": f"Bearer {groq_api_key}"}
                files = {
                    "file": (os.path.basename(audio_path), open(audio_path, "rb"), "audio/mpeg"),
                    "model": (None, model),
                    "response_format": (None, "verbose_json"),
                    "timestamp_granularities[]": (None, "word")
                }
                response = requests.post(url, headers=headers, files=files, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                word_segments = []
                # Case 1: Word-level timestamps supported (verbose_json)
                if "words" in data:
                    for w in data["words"]:
                        word_segments.append({
                            "word": w["word"],
                            "start": w["start"],
                            "end": w["end"]
                        })
                # Case 2: Segment-level only fallback
                elif "segments" in data:
                    for seg in data["segments"]:
                        words = seg.get("text", "").split()
                        if words:
                            per_word = (seg["end"] - seg["start"]) / len(words)
                            for i, word in enumerate(words):
                                word_segments.append({
                                    "word": word,
                                    "start": seg["start"] + (i * per_word),
                                    "end": seg["start"] + ((i+1) * per_word)
                                })
                
                if word_segments:
                    print(f"✅ [Groq REST] Success: {len(word_segments)} words captured.")
                    return word_segments
            except Exception as e:
                print(f"⚠️ Groq REST ({model}) failed: {e}")

    print(f"🚨 Cloud Exhausted. Engaging Local CPU Whisper Fail-Safe...")
    try:
        import whisperx
        device = "cpu"
        model = whisperx.load_model("tiny.en", device=device, compute_type="float32")
        result = model.transcribe(audio_path)
        align_model, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        aligned_result = whisperx.align(result["segments"], align_model, metadata, audio_path, device)
        return aligned_result["word_segments"]
    except Exception as e:
        print(f"❌ Transcription Failure: {e}")
    return []
from moviepy.editor import ImageClip, concatenate_videoclips

# Config
initial_vault = {
    "groq": os.environ.get("GROQ_API_KEY", ""),
    "openrouter": os.environ.get("OPENROUTER_API_KEY", ""),
    "pexels": os.environ.get("PEXELS_API_KEY", ""),
    "pixabay": os.environ.get("PIXABAY_API_KEY", "")
}

NUM_IMAGES = 21
VIDEO_DURATION = 5
PER_IMAGE_DURATION = VIDEO_DURATION / NUM_IMAGES
RESOLUTION = (1920, 1080)
TMP_DIR = "pexels_images"
OUTPUT_VIDEO = "outputcuts.mp4"

def is_near_resolution(size, target=(1920, 1080), tol=0.1):
    w, h = size
    tw, th = target
    return abs(w - tw)/tw <= tol and abs(h - th)/th <= tol

def clear_temp_folder(folder):
    if os.path.exists(folder):
        for f in os.listdir(folder):
            os.remove(os.path.join(folder, f))
    else:
        os.makedirs(folder)
import hashlib

def get_cache_folder_for_topic(topic):
    # Generate a simple hash folder name for topic (to avoid illegal characters in folder name)
    topic_hash = hashlib.md5(topic.encode('utf-8')).hexdigest()
    return os.path.join("pexels_cache", topic_hash)

def load_images_from_cache(cache_folder, count):
    if not os.path.exists(cache_folder):
        return []
    files = sorted([f for f in os.listdir(cache_folder) if f.endswith(".jpg")])
    if len(files) < count:
        return []
    return [os.path.join(cache_folder, f) for f in files[:count]]

def fetch_pexels_images(query, count):
    print("Fetching images from Pexels...")
    headers = {"Authorization": PEXELS_API_KEY}
    collected_urls = []
    page = 1

    while len(collected_urls) < count:
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=15&page={page}"
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            raise Exception(f"Pexels API Error: {response.status_code} - {response.text}")

        data = response.json()
        photos = data.get("photos", [])

        if not photos:
            break  # No more results

        for photo in photos:
            if len(collected_urls) >= count:
                break
            collected_urls.append(photo['src']['original'])

        page += 1

    if len(collected_urls) < count:
        print(f"Warning: Only {len(collected_urls)} images available from Pexels.")

    return collected_urls



def prepare_images(urls, folder, target_res):
    os.makedirs(folder, exist_ok=True)
    paths = []

    for i, url in enumerate(urls):
        try:
            print(f"Downloading image {i + 1}/{len(urls)}...")
            response = requests.get(url)
            img = Image.open(BytesIO(response.content)).convert("RGB")

            # Resize and crop to exactly target_res without black borders
            img = ImageOps.fit(img, target_res, Image.LANCZOS, centering=(0.5, 0.5))


            path = os.path.join(folder, f"img_{i:02d}.jpg")
            img.save(path, quality=95)
            paths.append(path)
        except Exception as e:
            print(f"Error processing image {i + 1}: {e}")
    
    return paths



from Wav2Lip.inference import parser, run_inference

sys.path.append('Wav2Lip')



def run_wav2lip_inference(
    checkpoint_path,
    face_video,
    audio_path,
    output_video,
    static=True,
    fps=24,
    wav2lip_batch_size=128,   # default value
    resize_factor=1,
    out_height=480
):
    args_list = [
        '--checkpoint_path', checkpoint_path,
        '--face', face_video,
        '--audio', audio_path,
        '--outfile', output_video,
        '--fps', str(fps),
        '--wav2lip_batch_size', str(wav2lip_batch_size),
        '--resize_factor', str(resize_factor),
        '--out_height', str(out_height),
    ]

    if static:
        args_list.append('--static')

    args = parser.parse_args(args_list)

    print("Starting Wav2Lip inference...")
    run_inference(args)
    print("Inference done!")



# Initialize JSON storage
def initialize_json():
    today = datetime.now().strftime("%Y-%m-%d")
    data = {"date": today, "count": UPLOAD_LIMIT}
    with open(JSON_FILE, "w") as f:
        json.dump(data, f)

# Load or reset upload status
def get_upload_status():
    if not os.path.exists(JSON_FILE):
        initialize_json()

    try:
        with open(JSON_FILE, "r") as f:
            data = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        print("⚠️ JSON file corrupted or empty. Reinitializing...")
        initialize_json()
        with open(JSON_FILE, "r") as f:
            data = json.load(f)

    today = datetime.now().strftime("%Y-%m-%d")

    if data["date"] != today:
        print("🔄 New day. Resetting count.")
        data = {"date": today, "count": UPLOAD_LIMIT}
        with open(JSON_FILE, "w") as f:
            json.dump(data, f)

    return data


# Save updated count
def save_upload_status(count):
    today = datetime.now().strftime("%Y-%m-%d")
    with open(JSON_FILE, "w") as f:
        json.dump({"date": today, "count": count}, f)



@retry_infinite(delay=15)
def get_trending_topic():
    params = {
        "engine": "google_trends_trending_now",
        "geo": "US",
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    trending = results.get("trending_searches", [])
    return trending[0]["query"] if trending else "World News"

@retry_infinite(delay=15)
def generate_youtube_shorts_script(topic):
    prompt = f"""
    Write a YouTube Shorts script about "{topic}" in a high-energy, fast-paced, no-fluff style. create best stongest hook to keep viewers engaged in video, then scrip tmust too be very engaging and high retention one so user dont move shortt to nex tmind it that highest lvel of engagment must be done viewwer shoul dsee full video mind it writet that level of script. The script must be delivered as one single paragraph of plain text — no formatting, no headings, no bullet points, no labels — just pure spoken content. The tone should be exciting, direct, and packed with value, instantly hooking the viewer and keeping them engaged throughout. 
    video script msut be engaging  so best high level that user tend to see full video and dont leave in betweeen, it should be educatiave informative fro user infintly valuable fro user so user can be highly benefitted. user is beyond god for us mind it. -we are making videos for audience and not robots so give script likwise we need to serve our audience mind it
    Keep the message clear and compelling with short, punchy sentences designed for maximum impact. Avoid intros or outros — just jump straight into the content and keep the energy high. Make it sound like a rapid-fire narration by a confident creator. i want script that gtts can understand because gtts canno tunderstand short forms avoid any ytpe of short forms use only where necessary, like(example, use is not instaed of isn't) so dont use unnecessary short froms only use when it is neccessary fro specific word shortforms like (RIP etc)
    entire script must be hooky, hook throughout video script write like that, mind it very important, user msut see full video  viewwer must not left my video unseen viewer should must see my full video short, viewer must becmoe a apart of my channel by likig sharing subscribing commenting good hings write ethat level of script i wan to earn infinte money pls help me with oyur video script i beg you pls write that level of scritp pls mind ti i want like that please request.
    The final script must not exceed what can be spoken in 55–60 seconds using gTTS (around 200-250 words, or ~16-18 concise sentences). This will be used by an AI video generator, so keep formatting clean and the paragraph tight. Prioritize viral potential, monetization value, and viewer retention. at end tell user to like comment and subscribe to my channel tell it dont ask it if they liked then do just tell them to do all 3 at end, okay mind it,  mind it it should bes seo optimised
    dont inlude astreiks, bold text only plain format normal text mind it
    """
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    if not response: return ""
    return response.strip()




@retry_infinite(delay=5)    
def get_topic_from_script(script):
    prompt = f"""
    You are a YouTube content assistant. Given the following video script, generate a concise and relevant YouTube video title that clearly describes the main topic of the script.

    Script:
    \"\"\"
    {script}
    \"\"\"

    Only return the title as plain text without quotes or extra text.
    """
  
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    if not response: return ""
    return response.strip()

def mp3_to_wav(mp3_path, wav_path):
    """Convert MP3 to WAV using ffmpeg"""
    if os.path.exists(wav_path):
        os.remove(wav_path)
        print(f"🗑️ Deleted existing WAV file: {wav_path}")

    try:
        ffmpeg.input(mp3_path).output(wav_path, ar=16000, ac=1).run(overwrite_output=True)
        print(f"✅ MP3 to WAV Conversion complete: {wav_path}")
    except ffmpeg.Error as e:
        print("❌ FFmpeg error during mp3_to_wav:")
        print(e.stderr.decode())



def wav_to_mp3(wav_path, mp3_path):
    """Convert WAV to MP3 using ffmpeg"""
    if os.path.exists(mp3_path):
        os.remove(mp3_path)
        print(f"🗑️ Deleted existing MP3 file: {mp3_path}")

    try:
        ffmpeg.input(wav_path).output(mp3_path, acodec='libmp3lame').run(overwrite_output=True)
        print(f"✅ WAV to MP3 Conversion complete: {mp3_path}")
    except ffmpeg.Error as e:
        print("❌ FFmpeg error during wav_to_mp3:")
        print(e.stderr.decode())


# === Extract Keywords with SpaCy === #
def extract_keywords(text):
    doc = nlp(text)
    return [token.text for token in doc if token.pos_ in ("NOUN", "PROPN", "ADJ")]

# === Visual Search Query Generation === #

@retry_infinite(delay=15)
def generate_visual_search_batch(sentences, user_topic, user_keys=None):
    """
    🏎️ [WARP-Discovery] Batch AI Query Node (v122.24):
    Processes multiple script segments in a single AI pass to kill serialized wait-times.
    """
    if not sentences: return {}
    
    full_script = os.environ.get("FORCE_SCRIPT", "")
    segments_payload = "\n".join([f"{i}: {s}" for i, s in enumerate(sentences)])
    
    prompt = f"""You are a high-speed cinematic researcher for Vantix.
    TASK: Generate 3 physical, high-quality visual search queries for EACH of the script segments listed below.
    
    FULL SCRIPT CONTEXT: "{full_script}"
    TOPIC: {user_topic}
    
    SEGMENTS:
    {segments_payload}
    
    STRICT MANDATES:
    1. For each segment index, resolve pronouns using the FULL SCRIPT. 
    2. Return ONLY a JSON object mapping the index (as string) to a list of 3 query strings.
    Example: {{"0": ["lunar map", "rocket controls", "space cabin"], "1": ["..."]}}"""

    all_results = {}
    try:
        resp_obj = generate_ai_response(prompt, user_keys=user_keys)
        text_resp = resp_obj.text.strip()
        
        json_pattern = re.compile(r'\{.*\}', re.DOTALL)
        match = json_pattern.search(text_resp)
        if match:
             try:
                  clean_json = match.group(0).replace("```json", "").replace("```", "").strip()
                  all_results = json.loads(clean_json)
             except: pass
             
    except Exception as e:
        print(f"⚠️ Batch Discovery AI Failed: {e}")
        
    return all_results

def generate_visual_search_queries(sentence, user_topic, user_keys=None):
    """👑 VANTIX SUBJECT LOCKDOWN (v50.5): Holistic Narrative Awareness"""
    # 💥 FULL SCRIPT CONTEXT (v50.5): Ensure search knows what 'it' refers to.
    full_script = os.environ.get("FORCE_SCRIPT", sentence)
    
    prompt = f"""You are a professional cinematic researcher.
    TASK: Generate 10 visual search queries for this part: "{sentence}"
    
    NARRATIVE CONTEXT (FULL SCRIPT): "{full_script}"
    
    STRICT MANDATES:
    1. Resolve all pronouns! If the sentence says 'it' or 'beside it', look at the NARRATIVE CONTEXT to see what 'it' is.
       - Example: If Context is 'Key on table', and sentence is 'beside it', query is 'beside silver key'.
    2. Every query MUST show the literal physical nouns from the narrative.
    3. Topic context: {user_topic}
    
    Return ONLY 10 queries in a JSON list of strings."""
    
    try:
        resp_obj = generate_ai_response(prompt, user_keys=user_keys)
        text_resp = resp_obj.text.strip()
        
        # 💥 ROBUST JSON EXTRACTION (v50.3)
        queries = []
        json_pattern = re.compile(r'\[.*\]', re.DOTALL)
        match = json_pattern.search(text_resp)
        if match:
             try:
                  clean_json = match.group(0).replace("```json", "").replace("```", "").strip()
                  queries = json.loads(clean_json)
             except: pass
        
        # 💥 TYPE HARDENING (v109.1): Flatten and stringify queries
        final_queries = []
        if isinstance(queries, list):
            for q in queries:
                if isinstance(q, list): final_queries.extend([str(item) for item in q])
                elif isinstance(q, dict): final_queries.append(str(q.get("query") or q.get("text") or str(q)))
                else: final_queries.append(str(q))
        else:
            final_queries = [str(queries)]
            
        return [q.strip() for q in final_queries if q.strip()][:10] if final_queries else [f"{sentence}"]
    except Exception as e:
        print(f"⚠️ Query Gen Fallback: {e}")
        return [f"{sentence}"]

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")
def identify_narrative_sfx(sentence, user_keys=None):
    """👑 VANTIX SFX ORCHESTRATION (v55): Identify sound-rich script markers"""
    prompt = f"""You are a foley artist. Identify 2-3 sound-rich physical nouns or actions in this sentence: "{sentence}"
    For each, provide a 1-word search query for a sound effect and its relative importance.
    
    Return a JSON list:
    [{{"word": "<the word in sentence>", "sfx_query": "<simple search query>", "volume_boost": <0 to 10>}}]
    
    Example: "A vintage silver key lies on a dusty wooden table."
    -> [{{"word": "key", "sfx_query": "metallic clink", "volume_boost": 5}}]
    """
    
    try:
        resp_obj = generate_ai_response(prompt, user_keys=user_keys)
        json_match = re.search(r'\[.*\]', resp_obj.text.strip(), re.DOTALL)
        if json_match:
             return json.loads(json_match.group(0))
    except Exception as e:
        print(f"⚠️ SFX Marker Fallback: {e}")
    return []

# ⚡ [ENGINE] Discovery Node: Pexels API (v1.1: Fail-Fast for Hybrid)
def search_pexels_videos(query, per_page=15, max_results=8, horizontal=False, user_keys=None, job_id=None, **kwargs):
    if job_id:
        import api.telemetry as telemetry
        telemetry.update_progress(job_id, f"Searching Pexels: {query}")
    """👑 Discovery Node: Pexels API"""
    api_key = (user_keys or {}).get("pexels") or os.environ.get("PEXELS_API_KEY")
    if not api_key:
        print("⚠️ [PEXELS] No API Key in vault. Skipping.")
        return []
        
    orientation = "landscape" if horizontal else "portrait"
    url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&orientation={orientation}"
    headers = {"Authorization": api_key}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 429:
             print("🚦 [PEXELS THROTTLE] Rate limit reached. Returning empty for failover...")
             return []
             
        response.raise_for_status()
        videos = response.json().get('videos', [])
        print(f"🎬 [Pexels] Discovery Found {len(videos)} videos for '{query}'")
        
        # 💥 RELEVANCE TAGGING (v1.0)
        suitable = []
        for v in videos:
             v["source"] = "pexels"
             # Normalize resolution data
             v["width"] = v.get("width")
             v["height"] = v.get("height")
             suitable.append(v)
             
        return suitable[:max_results]
    except Exception as e:
        print(f"⚠️ [PEXELS] Discovery Error: {e}")
        raise e

# ⚡ [ENGINE] Discovery Node: Pixabay API (v1.1: Fail-Fast for Hybrid)
def search_pixabay_videos(query, per_page=20, max_results=8, horizontal=False, user_keys=None, job_id=None, **kwargs):
    if job_id:
        import api.telemetry as telemetry
        telemetry.update_progress(job_id, f"Searching Pixabay: {query}")
    """👑 Discovery Node: Pixabay API"""
    api_key = (user_keys or {}).get("pixabay") or os.environ.get("PIXABAY_API_KEY")
    if not api_key:
        print("⚠️ [PIXABAY] No API Key in vault. Skipping.")
        return []
        
    url = 'https://pixabay.com/api/videos/'
    params = {'key': api_key, 'q': query, 'per_page': per_page}
    params["orientation"] = "horizontal" if horizontal else "vertical"
    
    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 429:
             print("🚦 [PIXABAY THROTTLE] Rate limit reached. Returning empty for failover...")
             return []
             
        response.raise_for_status()
        hits = response.json().get('hits', [])
        print(f"🎬 [Pixabay] Discovery Found {len(hits)} videos for '{query}'")
        
        suitable = []
        for hit in hits:
            videos = hit.get("videos", {})
            best = videos.get("large") or videos.get("medium") or videos.get("small")
            if best:
                hit["video_files"] = [{"link": best["url"]}]
                hit["width"] = best["width"]
                hit["height"] = best["height"]
                hit["source"] = "pixabay"
                suitable.append(hit)
        return suitable[:max_results]
    except Exception as e:
        print(f"⚠️ [PIXABAY] Discovery Error: {e}")
        raise e

@retry_infinite(delay=15)
def discover_global_sfx(query):
    """👑 VANTIX SFX ORCHESTRATION (v55): Dynamic Global SFX Discovery (No Hardcoding)"""
    print(f"🎵 [Global SFX] Searching for cinematic texture: '{query}'...")
    
    # Tier 1: Discover Freesound Pages via SERP
    params = {
        "q": f"site:freesound.org \"{query}\" .mp3",
        "api_key": SERP_API_KEY
    }
    
    # Tier 1: Discover High-Fidelity Leads via SERP
    params = {
        "q": f"(site:mixkit.co OR site:freesound.org) \"{query}\" .mp3",
        "api_key": SERP_API_KEY
    }
    
    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        organic = results.get("organic_results", [])
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        for result in organic[:5]: # Deep discovery
             page_url = result.get("link")
             if "mixkit.co" in page_url:
                  resp = requests.get(page_url, headers=headers, timeout=15)
                  if resp.status_code == 200:
                       match = re.search(r'https://assets.mixkit.co/[^"]*\.mp3', resp.text)
                       if match:
                            d_link = match.group(0)
                            print(f"✅ [SFX DISCOVERY] Found direct Mixkit asset: {d_link}")
                            return d_link
             elif "freesound.org" in page_url:
                  resp = requests.get(page_url, headers=headers, timeout=15)
                  if resp.status_code == 200:
                       match = re.search(r'https://freesound.org/data/previews/[^"]*\.mp3', resp.text)
                       if match:
                            d_link = match.group(0)
                            print(f"✅ [SFX DISCOVERY] Found direct Freesound asset: {d_link}")
                            return d_link
    except Exception as e:
        print(f"⚠️ Global SFX Discovery Error: {e}")
    
    return None
    
    return None

def download_sfx(sfx_url, query):
    """👑 VANTIX SFX ORCHESTRATION (v55): Download and cache SFX"""
    sfx_dir = "static/sfx"
    os.makedirs(sfx_dir, exist_ok=True)
    
    filename = f"{query.replace(' ', '_')}_{int(time.time())}.mp3"
    filepath = os.path.join(sfx_dir, filename)
    
    try:
        response = requests.get(sfx_url, stream=True)
        if response.status_code == 200:
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk: f.write(chunk)
            return filepath
    except Exception as e:
        print(f"❌ SFX Download failed: {e}")
    return None




@retry_infinite(delay=15)
def search_pexels_video(query, per_page=80, target_width=1080, target_height=1920, tolerance=200, max_clips=15, horizontal=False, api_key=None):
    page = 1
    # 🏛️ [VANTIX PERSISTENCE] Check In-Memory first, then fall back to Ledger
    active_key = api_key or PEXELS_API_KEY
    headers = {"Authorization": active_key}
    suitable_clips = []

    while True:
        params = {"query": query, "per_page": per_page, "page": page}
        # 📐 [ENGINE] Native Orientation Filter (v59.2)
        params["orientation"] = "landscape" if horizontal else "portrait"
        
        response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
        response.raise_for_status()
        results = response.json().get("videos", [])

        results = response.json().get("videos", [])
        if not results:
            print(f"❌ Pexels: No more results on page {page} for '{query}'")
            break

        print(f"🔎 Pexels Page {page}: Found {len(results)} videos for '{query}'")

        for i, clip in enumerate(results):
            # 💥 VISUAL RICHNESS (v31): Accept ANY high-quality video (720p+) and let resize_crop handle it
            best_file = None
            for file in clip["video_files"]:
                w = file.get("width", 0)
                h = file.get("height", 0)
                # Prefer 1080p if available
                if w >= 1080 or h >= 1080:
                    best_file = file
                    break
                # Fallback to 720p
                if w >= 720 or h >= 720:
                    best_file = file
            
            if best_file:
                print(f"✅ High-Quality video selected: {best_file.get('link')} ({best_file.get('width')}x{best_file.get('height')})")
                clip["video_files"] = [best_file]
                clip["width"] = best_file["width"]
                clip["height"] = best_file["height"]
                clip["source"] = "pexels"
                suitable_clips.append(clip)

            if len(suitable_clips) >= max_clips:
                print(f"🎯 Collected {max_clips} suitable clips. Stopping search.")
                return suitable_clips

        print(f"➡️ No enough clips yet, moving to page {page + 1}...")
        page += 1

    return suitable_clips




# === Search Pexels for a Query === #






# Replace with your actual Pixabay API key


@retry_infinite(delay=15)
def download_videos1(video_url, download_path):
    os.makedirs(os.path.dirname(download_path), exist_ok=True)
    try:
        print(f"📥 Downloading video from: {video_url}")
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        with open(download_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"✅ Downloaded: {download_path}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download video: {e}")




# === Find 1 Best Clip Per Search Term, avoiding duplicates === #

def extract_visual_keywords(text):
    """
    Extracts core visual keywords from a sentence by stripping common noise words.
    This helps in high-relevance asset searching.
    """
    import re
    # Common words that don't help in video search
    noise = set(['the', 'a', 'an', 'is', 'are', 'was', 'were', 'and', 'but', 'or', 'so', 'to', 'of', 'for', 'with', 'on', 'at', 'by', 'from', 'in', 'out', 'this', 'that', 'these', 'those', 'it', 'its', 'their', 'them', 'they', 'we', 'us', 'our', 'you', 'your', 'my', 'me', 'mine', 'shall', 'will', 'would', 'could', 'should', 'can', 'cant', 'may', 'might', 'must', 'been', 'being', 'having', 'about', 'however', 'therefore', 'moreover', 'nonetheless', 'additionally', 'secondly', 'thirdly', 'finally', 'then', 'now', 'here', 'there', 'some', 'any', 'none', 'all', 'every', 'each', 'either', 'neither', 'both', 'only', 'just', 'even', 'actually', 'really', 'very', 'quite', 'too', 'also', 'instead', 'rather', 'often', 'mostly', 'maybe', 'perhaps'])
    
    # Remove punctuation
    cleaned = re.sub(r'[^\w\s]', '', text.lower())
    words = cleaned.split()
    
    # Filter keywords (nouns, verbs, adjectives mostly)
    keywords = [w for w in words if w not in noise and len(w) > 2]
    
    if not keywords:
        return text # Fallback to original if nothing left
    
    # Return top 4 keywords for focused search
    return " ".join(keywords[:4])

# === Find 1 Best Clip Per Search Term, avoiding duplicates === #

def rank_candidates_with_ai(candidates, sentence, user_keys=None):
    """👑 VANTIX RELEVANCE SYNTHESIS (v1.0): Relative Ranking Engine Ratio"""
    if not candidates: return 0, None
    if len(candidates) == 1: return 10.0, candidates[0] # Single candidate is best by default

    print(f"🧠 [Intelligence] Synthesizing Narrative Relevance for {len(candidates)} candidates...")
    
    context = ""
    for idx, c in enumerate(candidates):
        tags = " ".join([t.get('title', '') for t in c.get('tags', [])]) if isinstance(c.get('tags'), list) else c.get('tags', '')
        context += f"Candidate {idx} Metadata: {tags}\n"
        
    prompt = f"""You are a Master Cinematic Researcher. Rank the Candidates by their PRECISE relevance to this Narrative: "{sentence}"
    
    METADATA CONTEXT:
    {context}

    RELEVANCE SYNTHESIS PROTOCOL:
    1. LITERAL ACCURACY: Does the candidate PRECISELY show the physical subject mentioned? (e.g. if 'key', does it show a 'key'?)
    2. TOPIC SYMMETRY: Does the visual match the broader topic and narrative context?
    
    Return a JSON:
    {{"best_index": <number>, "relevance_score": <0.0 to 10.0>, "justification": "<why it is the most narrative-accurate>"}}
    
    MANDATE: Assign high scores (9+) ONLY for literal subject matches. Reject generic vibes with low scores.
    """
    
    try:
        resp_obj = generate_ai_response(prompt, user_keys=user_keys)
        text_resp = resp_obj.text.strip()
        
        json_pattern = re.compile(r'\{.*\}', re.DOTALL)
        match = json_pattern.search(text_resp)
        if match:
             data = json.loads(match.group(0).replace("```json", "").replace("```", "").strip())
             score = float(data.get("relevance_score", 0))
             idx = int(data.get("best_index", -1))
             
             if 0 <= idx < len(candidates):
                  return score, candidates[idx]
    except Exception as e:
        print(f"⚠️ Synthesis Ranking Fallback: {e}")
    return 0, None

@retry_infinite(delay=15)
def find_one_video_clips(sentence, used_video_urls, user_topic, max_clips=1, horizontal=False, user_keys=None, job_id=None, pre_queries=None):
    if job_id:
        import api.telemetry as telemetry
        telemetry.update_progress(job_id, f"Searching for: {sentence[:30]}...")
    """👑 VANTIX DUAL-CORE DISCOVERY (v1.1): Hybrid Search Engine"""
    print(f"🔍 [DISCOVERY] Initiating Hybrid Search for: '{sentence}'")
    
    # 🏎️ [VELOCITY]: Use pre-calculated queries from the Batcher if available
    if pre_queries:
        precise_queries = pre_queries
    else:
        precise_queries = generate_visual_search_queries(sentence, user_topic, user_keys=user_keys)
    
    # 💥 TYPE HARDENING (v109.1): Ensure all queries are strings before comparison
    precise_queries = [str(q) for q in precise_queries if q]
    semantic_keyword = extract_visual_keywords(sentence)
    
    if semantic_keyword:
        if str(semantic_keyword).lower() not in [q.lower() for q in precise_queries]:
            precise_queries.append(str(semantic_keyword))

    def get_relevance_score(clip_text, sentence):
        if not clip_text: return 0.2
        stop_words = set(['the', 'is', 'are', 'was', 'were', 'and', 'but', 'or', 'a', 'an', 'in', 'on', 'at', 'with', 'know', 'how', 'why'])
        words_sentence = set([w for w in re.sub(r'[^\w\s]', '', sentence.lower()).split() if w not in stop_words and len(w) > 2])
        words_clip = set([w for w in re.sub(r'[^\w\s]', '', clip_text.lower()).split() if w not in stop_words])
        if not words_sentence: return 0.5
        overlap = words_sentence.intersection(words_clip)
        return len(overlap) / len(words_sentence)

    def process_pixels(query, limit):
        print(f"🔎 [Pexels] Stage: {query}")
        candidates = search_pexels_videos(query, max_results=limit*4, horizontal=horizontal, user_keys=user_keys, job_id=job_id)
        scored = []
        for clip in candidates:
            try:
                url = clip["video_files"][0]["link"]
                if url in used_video_urls or url in GLOBAL_USED_URLS: continue
                tags = " ".join([t.get('title', '') for t in clip.get('tags', [])])
                score = get_relevance_score(tags + " " + query, sentence)
                scored.append((score, clip))
            except: continue
        return sorted(scored, key=lambda x: x[0], reverse=True)[:limit]

    def process_pixabay(query, limit):
        print(f"🔎 [Pixabay] Stage: {query}")
        candidates = search_pixabay_videos(query, max_results=limit*4, horizontal=horizontal, user_keys=user_keys, job_id=job_id)
        scored = []
        for clip in candidates:
            try:
                url = clip["video_files"][0]["link"]
                if url in used_video_urls or url in GLOBAL_USED_URLS: continue
                tags = clip.get('tags', '')
                score = get_relevance_score(tags + " " + query, sentence)
                scored.append((score, clip))
            except: continue
        return sorted(scored, key=lambda x: x[0], reverse=True)[:limit]

    collected = []
    # 🏛️ ENGINE ROTATION: Priorities search engines based on available keys
    engines = []
    if (user_keys or {}).get("pexels") or os.environ.get("PEXELS_API_KEY"):
        engines.append(("Pexels", process_pixels))
    if (user_keys or {}).get("pixabay") or os.environ.get("PIXABAY_API_KEY"):
        engines.append(("Pixabay", process_pixabay))
        
    if not engines:
         print("❌ [DISCOVERY] Critical Failure: No visual keys in vault.")
         return []

    for query in precise_queries:
        for name, engine in engines:
            try:
                results = engine(query, max_clips)
                for score, clip in results:
                    collected.append(clip)
                    if len(collected) >= max_clips:
                         print(f"✅ [DISCOVERY] Successfully captured {len(collected)} assets via {name}.")
                         return collected
            except Exception as e:
                print(f"⚠️ [DISCOVERY] Engine {name} failed for query '{query}': {e}")
                continue # Try next engine or query
                
    return collected
def download_video(url, filename, retries=3):
    """📥 [VANTIX STABILITY]: Download and verify asset integrity."""
    for attempt in range(retries):
        try:
            print(f"📥 [DOWNLOADING]: {url} -> {filename} (Attempt {attempt+1})")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(filename, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # 💥 INTEGRITY CHECK (v103.6): Ensure file was actually written and has size
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                print(f"✅ [DOWNLOADED]: {filename} ({os.path.getsize(filename)} bytes)")
                return filename
            else:
                print(f"⚠️ [INTEGRITY ERROR]: {filename} is empty. Retrying...")
        except Exception as e:
            print(f"❌ [DOWNLOAD FAILED]: {e}")
            if attempt == retries - 1: raise e
            time.sleep(2)
    return filename



import random
import numpy as np
from moviepy.editor import VideoClip, CompositeVideoClip, TextClip, ColorClip, VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip

import colorsys

def create_gradient_frame(w, h, offset, direction, left_color, right_color):
    x = np.linspace(0, 1, w)
    y = np.linspace(0, 1, h)
    X, Y = np.meshgrid(x, y)

    if direction == "diagonal_tl_br":
        pos = (X + Y) / 2
        ratio = (pos + offset) % 1

    elif direction == "diagonal_br_tl":
        pos = (X + Y) / 2
        ratio = (1 - pos + offset) % 1

    else:
        ratio = np.full((h, w), offset)

    gradient = (1 - ratio[..., None]) * left_color + ratio[..., None] * right_color
    return gradient.astype(np.uint8)

def hsv_to_rgb_array(h, s, v):
    """Convert arrays of HSV to RGB arrays (values 0-1)"""
    rgb = np.array([colorsys.hsv_to_rgb(h_, s, v) for h_ in h.flatten()])  # (N,3)
    return rgb.reshape(h.shape + (3,))

def colorize_by_sentiment(word):
    """Return hex color based on word emotion/meaning."""
    word_lower = word.lower().strip(",.!?\"")
    colors = {
        "money": "#00FF00", "wealth": "#00FF00", "profit": "#00FF00", "rich": "#00FF00", "dollar": "#00FF00",
        "danger": "#FF0000", "dead": "#FF0000", "mistake": "#FF0000", "fail": "#FF0000", "scary": "#FF0000",
        "secret": "#FFD700", "hidden": "#FFD700", "rare": "#FFD700", "mystery": "#FFD700",
        "best": "#00BFFF", "smart": "#00BFFF", "tech": "#00BFFF", "future": "#00BFFF"
    }
    return colors.get(word_lower, None)

def random_bright_color():
    # Return bright HSV (random hue, full saturation & value)
    h = random.random()
    s = 1.0
    v = 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return np.array([r, g, b]) * 255

def create_word_gradient_clip(word, duration, font, fontsize, video_size):
    # Sentiment-based colorization for GOD-MODE
    word_color = "white"
    sentiment_color = colorize_by_sentiment(word)
    if sentiment_color:
        left_color = np.array(list(int(sentiment_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))
        right_color = left_color
    left_color = random_bright_color() if sentiment_color is None else np.array(list(int(sentiment_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)))
    right_color = left_color if sentiment_color else random_bright_color()
    direction = random.choice(["diagonal_tl_br", "diagonal_br_tl"])

    # 🛡️ [VANTIX FIX]: Create local text_mask to avoid Scope Errors
    text_mask = TextClip(
        word,
        font=font,
        fontsize=fontsize,
        color="white",
        method="label",
        size=video_size
    ).set_duration(duration)

    def make_frame(t):
        progress = (t / duration) % 1 if duration > 0 else 0
        offset = progress
        gradient = create_gradient_frame(video_size[0], video_size[1], offset, direction, left_color, right_color)
        mask_frame = text_mask.get_frame(t)
        colored_frame = (gradient * mask_frame[:, :, None]).astype(np.uint8)
        return colored_frame

    return VideoClip(make_frame, duration=duration).set_position("center").set_mask(text_mask.mask)


def create_word_by_word_subtitles(
    word_segments,
    video_size=(1080, 1920),
    font=os.path.join(PROJECT_ROOT, "Anton-Regular.ttf"),
    fontsize=110,
):
    from moviepy.editor import CompositeVideoClip
    from moviepy.video.fx.all import fadein, fadeout

    clips = []

    for word_info in word_segments:
        word = word_info["word"]
        start = word_info["start"]
        end = word_info["end"]
        duration = end - start

        grad_clip = create_word_gradient_clip(word, duration, font, fontsize, video_size)
        grad_clip = grad_clip.set_start(start).fx(fadein, 0.1).fx(fadeout, 0.1)
        clips.append(grad_clip)

    return CompositeVideoClip(clips, size=video_size)


nlp = spacy.load("en_core_web_sm")



def clean_text_to_match_timestamps(text, timestamps):
    doc = nlp(text)
    total_times = len(timestamps)

    # Filter words: ignore punctuation and "*"
    words = [token for token in doc if not token.is_punct and token.text != "*"]
    
    # If matched already
    if len(words) == total_times:
        return [{"word": token.text, "start": t["start"], "end": t["end"]} for token, t in zip(words, timestamps)]

    # If more words than timestamps
    if len(words) > total_times:
        # Remove stopwords first
        non_stop_words = [token for token in words if not token.is_stop]

        # If still too many, remove low-importance words
        if len(non_stop_words) > total_times:
            # Remove additional least important words (heuristic: short words, adverbs, etc.)
            important_pos = {"NOUN", "PROPN", "VERB", "ADJ"}
            important_words = [token for token in non_stop_words if token.pos_ in important_pos]

            # Truncate if still needed
            final_words = important_words[:total_times] if len(important_words) >= total_times else non_stop_words[:total_times]
        else:
            final_words = non_stop_words
    else:
        final_words = words

    # If fewer words than timestamps, trim timestamps
    if len(final_words) < total_times:
        timestamps = timestamps[:len(final_words)]

    # Final alignment
    return [{"word": token.text, "start": t["start"], "end": t["end"]} for token, t in zip(final_words, timestamps)]


def remove_stopwords_and_punctuation(text):
    doc = nlp(text)
    cleaned_words = [
        token.text for token in doc
        if not token.is_stop and not token.is_punct and token.text != "*"
    ]
    return " ".join(cleaned_words)

def update_character_count(text, filename="char_count.txt"):
    # Count characters in the input text
    current_count = len(text)
    
    try:
        # Try to read the previous total count from the file
        with open(filename, "r") as f:
            total_count = int(f.read())
    except FileNotFoundError:
        # If file doesn't exist, start with 0
        total_count = 0
    except ValueError:
        # If file content is invalid, reset to 0
        total_count = 0

    # Add current count to total
    total_count += current_count

    # Write updated total back to file
    with open(filename, "w") as f:
        f.write(str(total_count))

    print(f"Characters in this text: {current_count}")
    print(f"Total characters counted so far: {total_count}")


import base64
import base64
import requests

def generate_tts_audio(text, filename="output.mp3", voice_name="alloy", speaking_rate=1.0):
    """
    Generate high-fidelity neural audio using edge-tts (Direct) with FFPROBE integrity checks.
    """
    VOICE_MAP = {
        "alloy": "en-US-ChristopherNeural",   # Balanced
        "echo": "en-GB-RyanNeural",           # Soft/British-ish
        "fable": "en-GB-SoniaNeural",         # British Female
        "onyx": "en-US-GuyNeural",            # Deep/Authoritative
        "nova": "en-US-AriaNeural",           # Energetic
        "shimmer": "en-US-JennyNeural"        # Clear Female
    }
    voice_name = VOICE_MAP.get(voice_name, voice_name)
    
    print(f"🎙️ Generating Edge-TTS Neural voiceover for {filename} ({voice_name})...")
    try:
        if not text or not text.strip():
             text = "..." # Minimal content to avoid empty file errors

        import asyncio
        import edge_tts
        import os
        import subprocess
        import time
        
        async def run_edge_tts():
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(filename)
            
        asyncio.run(run_edge_tts())
        time.sleep(0.5) # 💥 FLUSH BUFFER (v36): Ensure OS has released file handle
        
        # 💥 FFPROBE VALIDATION (v36): Check if the file is ACTUALLY a valid media stream
        verify_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filename]
        try:
            res = subprocess.run(verify_cmd, capture_output=True, text=True, check=True)
            if float(res.stdout.strip()) > 0:
                print(f"✅ Edge-TTS Audio verified: {filename} ({os.path.getsize(filename)} bytes, {res.stdout.strip()}s)")
                return
            else:
                raise ValueError("Zero duration audio produced.")
        except:
            raise IOError("Media integrity check failed: Corrupted MP3 header.")

    except Exception as edge_e:
        print(f"⚠️ Edge-TTS failed or corrupted: {edge_e}")

    # Fallback to gTTS (Robotic but reliable offline)
    print(f"🔄 Fallback to gTTS for {filename}...")
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang='en')
        tts.save(filename)
        time.sleep(0.5)
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            print(f"✅ gTTS Audio saved to {filename}")
        else:
             print(f"❌ gTTS also failed to create valid file.")
    except Exception as fallback_e:
        print(f"❌ All TTS methods failed: {fallback_e}")

# Example usage:
# generate_tts_audio("Hello, this is a test!", "test.mp3")



from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip, vfx

from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    ImageClip
)



def apply_pattern_interrupt(clip):
    """Randomly inject a glitch or shake to reset attention."""
    if random.random() > 0.4:
        return clip
    interrupt_type = random.choice(["shake", "flash", "zoom_shock"])
    dur = clip.duration
    if interrupt_type == "shake":
        def move(t):
            return (random.randint(-10, 10), random.randint(-10, 10))
        return clip.set_position(move)
    elif interrupt_type == "flash":
        flash = ColorClip(size=clip.size, color=(255, 255, 255), duration=0.15).set_opacity(0.3)
        return CompositeVideoClip([clip, flash.set_start(random.uniform(0.1, max(0.1, dur-0.2)))])
    else:
        return clip.fx(vfx.speedx, 1.2).set_duration(dur)
# --- VANTIX NEURAL PACING (v46.1) --- #
# Intensity Dial: 1.0 (Viral/Fast) to 0.0 (Cinematic/Stable)
GLOBAL_PACING_INTENSITY = 1.0 

def apply_vantix_pacing(clip, is_hook=False, intent="SUSTAINED", intensity=None):
    """
    ⚡ NEURAL PACING ENGINE (v47.2):
    Dynamically scales clip duration based on intensity and SCRIPT INTENT.
    """
    if intensity is None: intensity = GLOBAL_PACING_INTENSITY
    dur = clip.duration
    
    # 💥 CONTEXTUAL OVERRIDE (v47.2): If the script intent is SUSTAINED, let the clip breathe
    if intent == "SUSTAINED":
        # At 0.0 intensity, keep full dur. At 1.0 intensity, cap at 3.5s (to prevent stagnant frames)
        sustained_max = 3.5 + (dur - 3.5) * (1.0 - PACING_INTENSITY)
        if dur > sustained_max:
            return clip.subclip(0, sustained_max)
        return clip

    # MONTAGE Mode: Use established intensity-scaling trimming
    if is_hook:
        target_dur = 0.8 + (dur - 0.8) * (1.0 - intensity)
    else:
        target_dur = 2.0 + (dur - 2.0) * (1.0 - intensity)
        
    if dur > target_dur:
        return clip.subclip(0, target_dur)
    return clip

def apply_ken_burns(clip, duration, zoom_step=0.04):
    if duration <= 0: return clip
    def zoom(t):
        return 1 + zoom_step * (t / duration)
    return clip.resize(zoom)

def draw_progress_bar(final_clip):
    """Add a sleek progress bar at the bottom of the video."""
    bar_height = 8
    video_w, video_h = final_clip.size
    def make_frame(t):
        bar_frame = np.zeros((bar_height, video_w, 3), dtype=np.uint8) + 50 # Dark gray
        progress_w = int((t / final_clip.duration) * video_w)
        if progress_w > 0:
            bar_frame[:, :progress_w] = [255, 69, 0] # OrangeRed
        return bar_frame
        
    bar = VideoClip(make_frame, duration=final_clip.duration).set_position(("center", "bottom"))
    # Force explicit size to prevent black screen inheritance issues
    return CompositeVideoClip([final_clip, bar], size=TARGET_RES)

def create_word_by_word_subtitles(word_segments, video_size=None, include_avatar=False):
    if video_size is None: video_size = TARGET_RES
    """
    VANTIX AVATAR SYNERGY ENGINE (v1.0):
    - Avatar-Aware Positioning: Shifts to Y=0.50 (Center) if avatar is present to avoid overlap.
    - Strictly One-Word Mode: Forced 1-word transitions for avatar segments.
    - Zero-Gap Pacing: Instant breaks on silence.
    - Hypersonic Fidelity: 0px gap, 12px buffer, Yellow/Green palette.
    """
    from moviepy.editor import TextClip, CompositeVideoClip
    
    # 🖋️ [VANTIX TYPOGRAPHY] (v2.0): Standardizing on Anton-Regular.ttf for brand across all nodes
    FONT = os.path.join(PROJECT_ROOT, "Anton-Regular.ttf")
    if not os.path.exists(FONT):
        # Fallback for systems without Anton in project root
        FONT = "DejaVuSans-Bold" if os.name != 'nt' else "Arial"
    # 🛡️ [RECURSION FIX]: Use the stable global caption engine
    from moviepy.editor import TextClip, CompositeVideoClip
    return create_caption_clips(word_segments, video_size, include_avatar)

def resize_crop(clip):
    if clip is None: return None
    # 📐 [ENGINE] Target Resolution is now dynamic (v59.1)
    t_w, t_h = TARGET_RES
    target_aspect = t_w / t_h
    actual_aspect = clip.w / clip.h
    
    # 💥 CRITICAL: Multi-stage scaling to ensure NO black bars
    if actual_aspect > target_aspect:
        # Source is wider than target
        clip = clip.resize(height=t_h)
        if clip.w < t_w: clip = clip.resize(width=t_w) 
        x_center = clip.w / 2
        return clip.crop(x1=max(0, x_center - t_w/2), x2=min(clip.w, x_center + t_w/2), y1=0, y2=t_h)
    else:
        # Source is narrower than target
        clip = clip.resize(width=t_w)
        if clip.h < t_h: clip = clip.resize(height=t_h)
        y_center = clip.h / 2
        return clip.crop(x1=0, x2=t_w, y1=max(0, y_center - t_h/2), y2=min(clip.h, y_center + t_h/2))

def technical_mastering(input_path, output_path):
    """👑 CINEMATIC MASTERING & PLAYABILITY (v56): Final H.264/AAC Mastering Pass"""
    print(f"🎬 [MASTERING] Executing Technical Finalizer for: {input_path}")
    
    # 💥 VANTIX STABILITY (v1.0): Raw FFmpeg mastery for 100% playability
    try:
        cmd = [
            'ffmpeg', '-y', 
            '-i', input_path,
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-movflags', '+faststart',
            output_path
        ]
        subprocess.run(cmd, check=True)
        print(f"✅ [MASTERED] Final production certified: {output_path}")
        return output_path
    except Exception as e:
        print(f"❌ Mastering Failed: {e}")
        return input_path

@retry_infinite(delay=15)
def create_scene(text, idx, used_video_urls, user_topic, max_clips=15, topic_pool=None, include_avatar=True, horizontal=False, user_keys=None, visual_source="pexels", intensity=None, voice_id="alloy", job_id=None, **kwargs):
    if job_id:
        import api.telemetry as telemetry
        telemetry.update_progress(job_id, f"Synthesizing Scene {idx+1}")
    print(f"\n🎬 Creating Scene {idx + 1} | Visual: {visual_source} | Voice: {voice_id} | Intensity: {intensity}")
    
    # 💥 VANTIX AUDIO DEFINITION (v1.0): Must happen BEFORE assembly
    audio_path = f"audio/scene_{idx}.mp3"
    try:
        generate_tts_audio(text, audio_path, voice_name=voice_id)
        update_character_count(text)
        
        # 💥 SEMANTIC SYNCHRONIZATION (v48.2): Transcribe BEFORE Assembly
        word_segments = get_word_level_transcription(audio_path, user_keys=user_keys)
        if not word_segments:
             print("⚠️ Transcription failed. Falling back to Time-Based Pacing.")
             word_segments = []

        # 💥 NEURAL SFX ORCHESTRATION (v55): Audio Fusion Pass
        sfx_markers = identify_narrative_sfx(text, user_keys=user_keys)
        if sfx_markers and word_segments:
             print(f"🎵 [SFX PHONICS] Identifying {len(sfx_markers)} narrative sound markers...")
             layering_list = []
             for marker in sfx_markers:
                  word_match = marker.get("word", "").lower()
                  # Find timestamp for this word
                  start_t = next((s["start"] for s in word_segments if word_match in s["word"].lower()), None)
                  if start_t is not None:
                       sfx_link = discover_global_sfx(marker["sfx_query"])
                       if sfx_link:
                            local_sfx = download_sfx(sfx_link, marker["sfx_query"])
                            if local_sfx:
                                 layering_list.append((local_sfx, start_t))
             
             if layering_list:
                  audio_path = layer_sfx_on_audio(audio_path, layering_list)
                  print(f"🎵 [SFX FUSION] Multi-dimensional audio mastered (WAV): {audio_path}")
        
        # 🛡️ [SOVEREIGN VERIFICATION]: Verify Audio Integrity before composing
        try:
            audio_clip = AudioFileClip(audio_path)
            audio_duration = audio_clip.duration
            # Burn-test: probe first 0.1s
            _ = audio_clip.get_frame(0)
        except Exception as ae:
            print(f"⚠️ [STABILITY] Narration node corrupted for Scene {idx}: {ae}. Using silence.")
            audio_clip = None
            audio_duration = 3.0
    except Exception as e:
        print(f"⚠️ Master Audio/SFX Error: {e}")
        # Final safety fallback for duration
        try:
             audio_duration = AudioFileClip(audio_path).duration
        except: audio_duration = 3.0
    
    # 💥 CONTEXT-DRIVEN PACING (v47.2): Analyze Script Intent
    pacing_intent = get_scene_pacing_intent(text, user_keys=user_keys)

    # --- PHASE 1: SEMANTIC MILESTONE EXTRACTION (v54: Cinematic Stabilization) ---
    raw_milestones = []
    if word_segments:
        current_buffer = []
        current_start = word_segments[0]["start"]
        
        for i, seg in enumerate(word_segments):
            word = seg["word"].strip().lower()
            doc = nlp(word)
            pos = doc[0].pos_ if len(doc) > 0 else "OTHER"
            current_buffer.append(word)
            
            if pos in ["NOUN", "PROPN", "VERB"] and len(word) > 2 or i == len(word_segments) - 1:
                raw_milestones.append({
                    "query": " ".join(current_buffer),
                    "start": current_start,
                    "end": seg["end"]
                })
                current_buffer = []
                if i < len(word_segments) - 1:
                    current_start = word_segments[i+1]["start"]

    # 💥 CINEMATIC STABILIZATION (v54): Cluster short milestones
    # Normal Pacing (0.5) -> 2.0s floor. High Pacing (1.0) -> 0.8s floor.
    if intensity is None:
        intensity = float(os.environ.get("PACING_INTENSITY", PACING_INTENSITY))
    else:
        intensity = float(intensity)
        
    min_floor = 2.5 * (1.1 - intensity) # Intensity 0.5 -> 1.5s, 1.0 -> 0.25s
    
    milestones = []
    if raw_milestones:
        temp_ms = raw_milestones[0]
        for next_ms in raw_milestones[1:]:
            cur_dur = temp_ms["end"] - temp_ms["start"]
            if cur_dur < min_floor:
                # Merge into existing
                temp_ms["query"] += " " + next_ms["query"]
                temp_ms["end"] = next_ms["end"]
            else:
                milestones.append(temp_ms)
                temp_ms = next_ms
        milestones.append(temp_ms) # Add final
            
    # --- PHASE 2: WORD-LOCKED ASSEMBLY ---
    total_collected = 0.0
    collected_clips = []
    new_used_urls = set()
    
    # 💥 PACING CONSTANTS (v48.2)
    DURATION_BUFFER = 0.5
    search_iteration = 0
    total_filled = idx * 3.0 # Approx offset for pacing logic
    
    if milestones:
        print(f"🧠 [VANTIX SYNC] Orchestrating {len(milestones)} Word-Locked Semantic Cuts (PARALLEL)...")
        
        # 🏎️ [WARP-Discovery] Pre-calculate all queries via Batch Node (v122.24)
        print(f"📡 [BATCH]: Pre-calculating visual search terms for {len(milestones)} milestones...")
        sentences_to_query = [m["query"] for m in milestones]
        batch_queries_raw = generate_visual_search_batch(sentences_to_query, user_topic, user_keys=user_keys)
        # Standardize indices for robust lookup
        batch_queries = {str(k): v for k, v in batch_queries_raw.items()}

        def process_milestone(i, ms):
            target_dur = ms["end"] - ms["start"]
            if target_dur <= 0: return None
            
            print(f"🎯 Milestone {i}: '{ms['query']}' | Duration: {target_dur:.2f}s")
            
            video_url = None
            raw_tmp_path = f"video_creation/raw_ms_{idx}_{i}.mp4"
            prepped_tmp_path = f"video_creation/ms_{idx}_{i}.mp4"
            
            # 🏎️ [WARP-Discovery]: Fetch pre-calculated queries with fallback indexing
            pre_queries = batch_queries.get(str(i)) or batch_queries.get(i) or batch_queries.get(int(i))
            
            # --- 📽️ INDUSTRIAL STOCK DISCOVERY (v110.0: Relentless Tiered Mode) ---
            # Tier 1: [PRECISE] Milestone Narrative Query
            pool = find_one_video_clips(ms["query"], used_video_urls | new_used_urls, user_topic, max_clips=1, horizontal=horizontal, user_keys=user_keys, job_id=job_id, pre_queries=pre_queries)
            
            # Tier 2: [SIMPLEX] Subject Deconstruction
            if not pool:
                simplex_query = extract_visual_keywords(ms["query"])
                print(f"📡 [RELENTLESS]: Milestone '{ms['query']}' failed. Trying Simplex: '{simplex_query}'")
                pool = find_one_video_clips(simplex_query, used_video_urls | new_used_urls, user_topic, max_clips=1, horizontal=horizontal, user_keys=user_keys)
            
            # Tier 3: [PILLAR] Narrative Heritage (The overarching topic)
            if not pool:
                print(f"📡 [RELENTLESS]: Simplex failed. Falling back to Topic Pillar: '{user_topic}'")
                pool = find_one_video_clips(user_topic, used_video_urls | new_used_urls, user_topic, max_clips=1, horizontal=horizontal, user_keys=user_keys)
            
            # Tier 4: [AESTHETIC] Dynamic Visual Harmony (Context-Aware Fallback)
            if not pool:
                aesthetic_queries = ["cinematic abstract textures", "dynamic light trails", "atmospheric motion graphics", "elegant cinematic b-roll"]
                if "tech" in user_topic.lower() or "future" in user_topic.lower():
                    aesthetic_queries = ["high tech digital motion", "cybernetic data stream", "futuristic neural network"]
                elif "space" in user_topic.lower() or "universe" in user_topic.lower():
                    aesthetic_queries = ["cinematic cosmic nebula", "starfield motion galactic", "planet aerial cinematic"]
                
                fallback_query = random.choice(aesthetic_queries)
                print(f"📡 [RELENTLESS]: Engaging Dynamic Aesthetic: '{fallback_query}'")
                pool = find_one_video_clips(fallback_query, used_video_urls | new_used_urls, user_topic, max_clips=1, horizontal=horizontal, user_keys=user_keys)
                
            # Tier 5: [ABSOLUTE] Generic High-Retention Visual (Failure is not an option)
            if not pool:
                emergency_safe = "cinematic nature 4k"
                print(f"📡 [RELENTLESS]: All tiers exhausted. Triggering Tier 5 Absolute: '{emergency_safe}'")
                pool = find_one_video_clips(emergency_safe, used_video_urls | new_used_urls, user_topic, max_clips=1, horizontal=horizontal, user_keys=user_keys)

            if not pool: 
                 print(f"❌ [ULTIMATE EXHAUSTION]: No visuals found for Milestone {i}.")
                 return {"is_placeholder": True, "dur": target_dur}

            try:
                # 💥 [VANTIX HARDENING]: Multi-layer structural verification
                if not pool[0].get("video_files"):
                    raise ValueError("Pexels response missing video_files payload.")
                
                video_url = pool[0]["video_files"][0]["link"]
                download_video(video_url, raw_tmp_path)
                
                # 🏎️ [WARP-PREP] Standardize Asset via C-speed FFmpeg (v122.24: Dynamic Resolution)
                success = prep_milestone_ffmpeg(raw_tmp_path, prepped_tmp_path, target_dur, width=TARGET_RES[0], height=TARGET_RES[1])
                
                if success:
                    # Clean up the raw file immediately to save disk I/O
                    try: os.remove(raw_tmp_path)
                    except: pass
                    return {"tmp_path": prepped_tmp_path, "url": video_url, "dur": target_dur, "is_placeholder": False, "prepped": True}
                else:
                    return {"tmp_path": raw_tmp_path, "url": video_url, "dur": target_dur, "is_placeholder": False, "prepped": False}
                    
            except Exception as e:
                print(f"❌ Milestone {i} Discovery/Prep Failed: {e}")
                return {"is_placeholder": True, "dur": target_dur}

        # Execute [Sovereign] Parallel Discovery (v122.24: Optimized 3-Worker Sync)
        orch = ParallelOrchestrator(max_workers=3)
        parallel_results = orch.parallel_map_indexed(process_milestone, milestones, task_name="Milestone")
        
        # Assemble in Sequence (v122.24: High-Velocity Feed)
        for i, (ms, res) in enumerate(zip(milestones, parallel_results)):
            # 🛡️ [SYNC]: Safely extract duration from result or milestone
            target_dur = res["dur"] if (res and "dur" in res) else ms["end"] - ms["start"]
            
            if res and not res.get("is_placeholder", False) and os.path.exists(res.get("tmp_path", "")):
                try:
                    # Load standardized asset
                    raw_clip = VideoFileClip(res["tmp_path"]).without_audio()
                    
                    # 💥 [VELOCITY]: If FFmpeg prepped the asset, skip MoviePy's slow resize/crop
                    if res.get("prepped", False):
                        clip = raw_clip
                    else:
                        clip = resize_crop(raw_clip).set_fps(30)
                    
                    # Apply sub-second cinematic effects
                    clip = apply_pattern_interrupt(apply_ken_burns(clip, target_dur))
                    clip = apply_vantix_pacing(clip, is_hook=(len(collected_clips)==0), intensity=intensity)
                    
                    # Force duration to match milestone exactly
                    clip = clip.set_duration(target_dur).set_start(total_collected)
                    
                    collected_clips.append(clip)
                    new_used_urls.add(res["url"])
                    total_collected += target_dur
                    print(f"✅ Milestone Loaded: {res['url']} ({target_dur:.2f}s)")
                except Exception as e:
                    print(f"⚠️ Failed to load or verify captured asset {res.get('tmp_path', 'unknown')}: {e}")
                    # 💥 [EMERGENCY PLACEHOLDER]
                    emergency_clip = ColorClip(size=(1080, 1920), color=(10, 10, 10), duration=target_dur).set_fps(30)
                    collected_clips.append(emergency_clip)
                    total_collected += target_dur
            else:
                # 💥 [EMERGENCY PLACEHOLDER]: Use captured loop index 'i' instead of .index() lookup
                print(f"🔄 [RELENTLESS]: Using emergency visual placeholder for milestone {i}.")
                emergency_clip = ColorClip(size=(1080, 1920), color=(10, 10, 10), duration=target_dur).set_fps(30)
                collected_clips.append(emergency_clip)
                total_collected += target_dur
    
    # --- PHASE 4: INDESTRUCTIBLE ASSEMBLY (v106.1) ---
    final_output = f"video_creation/scene_{idx}_final.mp4"
    if not collected_clips:
        print(f"⚠️ [RENDER FAILURE] No valid clips for Scene {idx}. Creating emergency placeholder.")
        from moviepy.editor import ColorClip
        placeholder = ColorClip(size=(1080, 1920), color=(0,0,0), duration=max(1.0, audio_duration)).set_fps(30)
        collected_clips.append(placeholder)

    try:
        from moviepy.editor import CompositeVideoClip
        
        # 🛡️ [STEP 1]: Background Stabilization (Nuclear Purification v108.0)
        res_clips = []
        for c in collected_clips:
            if c is not None and hasattr(c, "get_frame"):
                try:
                    # Verify frame producer and mask integrity
                    _ = c.get_frame(0)
                    if hasattr(c, 'mask') and c.mask is not None:
                        _ = c.mask.get_frame(0)
                    res_clips.append(c.resize((1080, 1920)).set_fps(30))
                except Exception as e:
                    print(f"⚠️ [STABILITY] Removing corrupted background clip: {e}")

        if not res_clips:
            raise ValueError("VANTIX CRITICAL: All background clips failed verification. Visual stream is empty.")

        # 🛡️ [STEP 2]: Initial Composite (Stable Chain Method)
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        try:
            # 🔗 Use 'chain' method to avoid complex composition maps that leak memory
            scene_comp = concatenate_videoclips(res_clips, method="chain")
            _ = scene_comp.get_frame(0) 
        except Exception as e:
            print(f"❌ Composite Stage 1 failed: {e}. Falling back to composition mode.")
            scene_comp = CompositeVideoClip(res_clips)

        # 🛡️ [STEP 3]: Audio-Visual Fusion
        try:
            if audio_clip is not None:
                scene_comp = scene_comp.set_audio(audio_clip)
            scene_comp = scene_comp.set_duration(audio_duration)
        except Exception as e:
            print(f"⚠️ Audio Fusion Warning: {e}")
            scene_comp = scene_comp.set_duration(audio_duration)

        # 🛡️ [STEP 4]: Caption Augmentation & Purification
        caption_clips = create_caption_clips(word_segments, (1080, 1920), include_avatar=include_avatar)
        
        # Final pass filter to catch internal MoviePy memory leaks
        pure_captions = []
        for cap in (caption_clips or []):
            if cap is not None and hasattr(cap, "get_frame"):
                try:
                    _ = cap.get_frame(0)
                    if hasattr(cap, 'mask') and cap.mask is not None:
                        _ = cap.mask.get_frame(0)
                    pure_captions.append(cap)
                except:
                    continue # Purge corrupted caption object
        
        if pure_captions:
            try:
                # Re-verify scene_comp before final merge
                _ = scene_comp.get_frame(0)
                scene_comp = CompositeVideoClip([scene_comp] + pure_captions)
                _ = scene_comp.get_frame(0)
            except Exception as e:
                print(f"⚠️ Caption Merge failed (likely mask collision): {e}. Proceeding without captions.")
                # Re-stabilize to background only
                scene_comp = concatenate_videoclips(res_clips, method="chain")

        # 🛡️ [STEP 5]: Final Immortal Rendering
        print(f"🏎️ [RENDER] Starting Industrial Pass for Scene {idx}...")
        with VANTIX_RENDER_LOCK: # 🔐 Sovereign Render Lock
            try:
                scene_comp.write_videofile(
                    final_output,
                    codec="libx264",
                    audio_codec="aac",
                    fps=30,
                    preset="ultrafast",
                    threads=2,
                    logger=None
                )
            except Exception as re:
                print(f"❌ [RENDER FAILURE] Scene {idx}: {re}. Retrying with simplified lock...")
                # 🛡️ [RETRY NODE]: If the first pass fails, we attempt one final stable render
                try:
                    scene_comp.write_videofile(
                        final_output,
                        codec="libx264",
                        audio_codec="aac",
                        fps=30,
                        preset="ultrafast",
                        threads=1, # Single thread for maximum OS-level safety
                        logger=None
                    )
                except Exception as final_e:
                    raise final_e
        
        # Immediate cleanup of memory handles
        scene_comp.close()
        for c in res_clips: c.close()
        for c in pure_captions: c.close()
        
        return final_output, new_used_urls
        
    except Exception as e:
        print(f"❌ [CRITICAL RENDER FAILURE] Scene {idx}: {e}")
        return None, []
        
        # 🧹 [SURGICAL CLEANUP]: Immediate purge of milestone artifacts
        print(f"🧹 [CLEANUP]: Purging Milestone fragments for Scene {idx}...")
        for res in parallel_results:
            if res and "tmp_path" in res: # I'll make sure to store tmp_path in res
                try: os.remove(res["tmp_path"])
                except: pass
        
        return final_output, new_used_urls
    except Exception as e:
        print(f"❌ [RENDER FAILURE] Scene {idx}: {e}")
        return None, []

    # --- PHASE 3: RESILIENCE & CONTINUITY ---
    if not collected_clips:
        print("⚠️ Semantic Sync Failed. Reverting to variety collection.")
        video_clips_data = find_one_video_clips(text, used_video_urls, user_topic, max_clips=max_clips, user_keys=user_keys)
        current_pool = list(video_clips_data)
        
        while total_collected < (audio_duration + DURATION_BUFFER) and search_iteration < 5:
            if not current_pool:
                 current_pool = find_one_video_clips(text, used_video_urls | new_used_urls, user_topic, user_keys=user_keys)
            if not current_pool: break
            
            for clip_data in list(current_pool):
                if total_collected >= (audio_duration + DURATION_BUFFER): break
                video_url = clip_data["video_files"][0]["link"]
                if video_url in used_video_urls or video_url in new_used_urls: continue
                
                tmp_path = f"video_creation/fb_{idx}_{len(collected_clips)}.mp4"
                try:
                    download_video(video_url, tmp_path)
                    raw_clip = VideoFileClip(tmp_path).without_audio()
                    clip = resize_crop(raw_clip).set_fps(30)
                    clip = apply_pattern_interrupt(apply_ken_burns(clip, 2.0))
                    collected_clips.append(clip)
                    new_used_urls.add(video_url)
                    total_collected += clip.duration
                except Exception as e:
                    print(f"❌ Fallback Error: {e}")
            search_iteration += 1
        
    # 4) ABSOLUTE VANTIX PACING (v1.0): Bridge gaps with EXCLUSIVELY literal variations.
    if total_collected < (audio_duration + DURATION_BUFFER):
        print(f"📡 Transitioning to Literal Milestone Expansion for Scene {idx + 1}...")
        
        # Generate Literal Variations of the current context using AI
        expansion_prompt = f"""We are creating a video for: '{text}'. 
        We need 3 more HIGHLY SPECIFIC, literal stock footage search queries that match this exact narrative context.
        STRICT RULES:
        1. NO abstract metaphors (e.g., no 'flowing light', no 'abstract motion').
        2. Must be strictly literal subjects mentioned in or implied by the script.
        3. Use only nouns and cinematic actions (e.g., 'golden crown sinking', 'close up of oceanic coral').
        
        Return ONLY a JSON list of strings."""
        
        novelty_queries = []
        try:
             resp_obj = generate_groq_response(expansion_prompt, system_message="Return ONLY JSON valid list.", user_keys=user_keys)
             json_match = re.search(r'\[.*\]', resp_obj.text, re.DOTALL)
             if json_match:
                  novelty_queries = json.loads(json_match.group(0))
        except:
             # Fallback to literal keywords if AI expansion fails
             novelty_queries = [text, user_topic]
        
        novelty_iteration = 0
        
        while total_collected < (audio_duration + DURATION_BUFFER) and novelty_iteration < len(novelty_queries):
            query = novelty_queries[novelty_iteration]
            print(f"📡 Recursive Discovery [{novelty_iteration+1}]: Searching for unique asset '{query}'...")
            
            novel_pool = find_one_video_clips(query, used_video_urls | new_used_urls, user_topic, max_clips=1, user_keys=user_keys)
            
            if novel_pool:
                video_url = novel_pool[0]["video_files"][0]["link"]
                tmp_path = f"video_creation/novel_{idx}_{novelty_iteration}.mp4"
                try:
                    download_video(video_url, tmp_path)
                    raw_clip = VideoFileClip(tmp_path).without_audio()
                    clip = resize_crop(raw_clip).set_fps(30)
                    clip = apply_pattern_interrupt(apply_ken_burns(clip, 2.0))
                    
                    collected_clips.append(clip)
                    new_used_urls.add(video_url)
                    GLOBAL_USED_URLS.add(video_url)
                    total_collected += clip.duration
                    print(f"✅ Bridge Asset Secured: {clip.duration:.2f}s | Registry Size: {len(GLOBAL_USED_URLS)}")
                except:
                    pass
            novelty_iteration += 1

    # Final Safety Fallback: If STILL under (impossible unless APIs 100% down), loop only as a last resort
    if total_collected < (audio_duration + DURATION_BUFFER) and collected_clips:
        print("⚠️ CRITICAL: Novelty exhausted. Using emergency loop (v32 legacy).")
        while total_collected < (audio_duration + DURATION_BUFFER):
             source_clip = collected_clips[-1]
             loop_clip = source_clip.copy().set_start(total_collected)
             collected_clips.append(loop_clip)
             total_collected += loop_clip.duration

    if not collected_clips:
        print("❌ CRITICAL: Total Visual Blackout. Rendering Cinematic Fallback (v32).")
        # Use a cinematic dark gray instead of pure black
        final_video = ColorClip(size=TARGET_RES, color=(30, 30, 30), duration=audio_duration)
    else:
        # 👑 VANTIX ASSEMBLY (v1.0): Reverting to "compose" as per user baseline
        final_video = concatenate_videoclips(collected_clips, method="compose")
        final_video = final_video.subclip(0, audio_duration)

    # 💥 VANTIX RESOLUTION LOCK: Force 1080x1920 regardless of input sources
    final_video = final_video.set_fps(30).set_duration(audio_duration)
    final_video = final_video.set_audio(AudioFileClip(audio_path))
    
    # 💥 BULLETPROOF BACKGROUND layer (v32): Dark gray anchor
    bg_base = ColorClip(size=TARGET_RES, color=(20, 20, 20)).set_duration(audio_duration)
    final_video = CompositeVideoClip([bg_base, final_video], size=TARGET_RES)

    subtitle_clips = []
    if word_segments:
        try:
             # Generate Clips using the pre-transcribed word_segments
             subtitle_clips = create_word_by_word_subtitles(word_segments, video_size=TARGET_RES, include_avatar=include_avatar)
        except Exception as e:
             print(f"⚠️ Subtitle generation error: {e}")

    if subtitle_clips:
        # 💥 CRITICAL: Explicitly set size and DURATION to prevent subtitle leakage (v101.16)
        final_video_clip = CompositeVideoClip([final_video] + subtitle_clips, size=TARGET_RES).set_duration(audio_duration)
    else:
        final_video_clip = final_video

    final_video_clip = draw_progress_bar(final_video_clip)
    return final_video_clip, list(new_used_urls)









from moviepy.editor import VideoFileClip, concatenate_videoclips

from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeAudioClip, AudioFileClip


from moviepy.editor import AudioFileClip, CompositeAudioClip, ImageClip, concatenate_videoclips

def create_fast_cut_clip_from_images(image_paths, total_duration=5, resolution=(1920,1080)):
    per_image_duration = total_duration / len(image_paths)
    tick_sound = AudioFileClip(os.path.join(PROJECT_ROOT, "analog-camera-shutter-96604_z7Dhy2kD.mp3")).volumex(0.1)
    clips = []

    for i, path in enumerate(image_paths):
        clip = ImageClip(path).set_duration(per_image_duration).fadein(0.1).fadeout(0.05).resize(resolution)
        tick_audio = tick_sound.subclip(0, min(0.17, tick_sound.duration))
        clip = clip.set_audio(tick_audio)
        clips.append(clip)

    fast_cut_clip = concatenate_videoclips(clips, method="chain")

 

    return fast_cut_clip
def create_video_from_script(script, user_topic):
    import tempfile
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
    from moviepy.audio.fx.all import audio_loop

    def save_clip_to_tempfile(clip, suffix="", pad_duration=1):
        clip = clip.set_fps(30)

        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=f"{suffix}.mp4").name
        padded_path = tempfile.NamedTemporaryFile(delete=False, suffix=f"{suffix}_padded.mp4").name

        # Save normal clip first
        from proglog import TqdmProgressBarLogger
        log = TqdmProgressBarLogger(print_messages=False)
        print("📊 [RENDER] Encoding Clip Segment...")
        clip.write_videofile(
            temp_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="ultrafast",
            threads=4,
            audio=True,
            logger=log
        )

        # Add freeze-frame padding of `pad_duration` seconds at the end
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-i", temp_path,
            "-vf", f"tpad=stop_mode=clone:stop_duration={pad_duration}",
            "-af", f"apad=pad_dur={pad_duration}",
            "-preset", "ultrafast",
            padded_path
        ]
        subprocess.run(ffmpeg_cmd, check=True)

        os.remove(temp_path)  # remove unpadded

        return padded_path

    from moviepy.editor import VideoFileClip

    def ffmpeg_chain_random_transitions(clip_paths, output_path, transition_duration=0.08):
        transitions = [
            "fade", "fadeblack", "fadewhite", "radial", "circleopen",
            "circleclose", "rectcrop", "distance", "slideleft", "slideright", "slideup", "slidedown"
        ]

        durations = []
        for p in clip_paths:
            clip = VideoFileClip(p)
            durations.append(clip.duration)
            clip.close()

        offsets = []
        accum = durations[0]
        for i in range(1, len(durations)):
            offset = accum - transition_duration
            offsets.append(offset)
            accum += durations[i] - transition_duration

        current_input = clip_paths[0]
        from tqdm import tqdm
        pbar = tqdm(total=len(clip_paths)-1, desc="🎞️ Applying Transitions", unit="xfade")

        for i in range(1, len(clip_paths)):
            next_input = clip_paths[i]
            offset = offsets[i - 1]
            transition_type = random.choice(transitions)

            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

            ffmpeg_cmd = [
                "ffmpeg", "-y",
                "-i", current_input,
                "-i", next_input,
                "-filter_complex",
                f"[0:v][1:v]xfade=transition={transition_type}:duration={transition_duration}:offset={offset}",
                "-preset", "ultrafast",
                "-crf", "23",
                temp_output
            ]

            print(f"🎞️ Transition {i}: '{transition_type}' at offset={offset:.2f}s")
            subprocess.run(ffmpeg_cmd, check=True)

            # Remove temp file if it’s not original input
            if current_input not in clip_paths:
                try:
                    os.remove(current_input)
                except:
                    pass

            current_input = temp_output
            pbar.update(1)
        pbar.close()

        # Final rename to output
        os.rename(current_input, output_path)


    # ---- [VANTIX BOLT HIGH-SPEED ENGINE] ----
    GLOBAL_USED_URLS.clear() 
    sentences = sent_tokenize(script)
    all_used_urls = set()
    output_dir = "video_created"
    os.makedirs(output_dir, exist_ok=True)

    print(f"🚀 [VANTIX BOLT] Launching Parallel Scene Synthesis ({len(sentences)} tasks)...")
    
    scene_tasks = []
    for i, sent in enumerate(sentences):
        scene_tasks.append((sent, i))

    def process_scene_bundle(task):
        s_text, s_idx = task
        # We call the globally available create_scene
        return create_scene(s_text, s_idx, all_used_urls, user_topic, **kwargs)

    # 🧶 [ORCHESTRATION]: Render all scenes in parallel
    orch = ParallelOrchestrator(max_workers=3)
    results = orch.parallel_map(process_scene_bundle, scene_tasks, task_name="Scene Atomic Render")

    scene_paths = []
    for res in results:
        if res and res[0]:
            scene_paths.append(res[0])
            all_used_urls.update(res[1])

    if not scene_paths:
        print("❌ [CRITICAL] No scenes rendered. Aborting.")
        return None, None

    # 🧶 [STITCHING]: Atomic FFmpeg Concat Demuxer (Industrial O(1))
    concat_list_path = os.path.join(output_dir, "concat_list.txt")
    with open(concat_list_path, "w") as f:
        for p in scene_paths:
            # Must use absolute paths for FFmpeg safety
            f.write(f"file '{os.path.abspath(p)}'\n")

    timestamp = datetime.now().strftime("%H%M%S")
    output_filename = f"video_{timestamp}.mp4"
    output_path = os.path.join(output_dir, output_filename)
    
    print("\n⚡ [ASSEMBLY] Executing Atomic Byte-Stream Stitch...")
    stitch_cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path,
        "-c", "copy", output_path
    ]
    subprocess.run(stitch_cmd, check=True)

    # 🧹 [SURGICAL CLEANUP]: Final purge of scene segments
    print("\n🧹 [CLEANUP]: Executing Final Master Cleanup...")
    for p in scene_paths:
        try: os.remove(p)
        except: pass
    try: os.remove(concat_list_path)
    except: pass

    # 🎙️ [AUDIO]: Background Music Mixing
    print(f"\n✅ [SUCCESS] Industrial Video Created in Record Time: {output_path}")
    return output_path, all_used_urls


# def generate_youtube_title(topic):
#     prompt = f"""
#     Create a highly clickable, viral YouTube video title for the topic: "{topic}".
#     Do not include any extra explanation or formatting. Just return the title only. it should be seo optimised mind it
#     """
#     response = gemini_model.generate_content(prompt)
#     return response.text.strip()

@retry_infinite(delay=15)
def generate_youtube_description(topic):
    prompt = f"""
    Write a compelling 21 sentences each in new line, YouTube video description for the topic: "{topic}".
    It should be keyword-rich and increase viewer interest.
    Do not include any formatting or labels like 'Description:'. Just return the description text only. it should be seo optimised mind it. include some like 8-10 seo optimised hastags also at end.
    write description first lines hooky so that user read and jut tendto click my video and want to watch full video write descriptrion like that and frist few lines nust be highest hooky attractive that user tend to click my video mind it write that lebel of firaast few lines of description and following whole decription like that and also seo optimised mind it create like this.
    """
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    return response.text.strip()

@retry_infinite(delay=15)
def generate_youtube_tags(topic):
    prompt = f"""
    Generate a list of 21 relevant, high-SEO YouTube tags (comma-separated) for the topic: "{topic}".
    Only return the tags in a list format separated by commas. Do not include extra explanation or formatting. it should be seo optimised mind it, just return list of tags comma separted thats it
    tags must be such that my video goes viral okay mind it best tags and relevent mind it bes tatgs seo optimised to make my video viral mind it okay
    """
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    tag_string = response.text.strip()
    tag_list = [tag.strip() for tag in tag_string.split(',')]
    return tag_list

import ast

@retry_infinite(delay=15)
def clean_tags_with_gemini(raw_tags):
    prompt = f"""
    You are an assistant that cleans and formats YouTube video tags.

    Here are the original tags:
    {', '.join(raw_tags)}

    Rules:
    - Remove duplicates.
    - Avoid overly long or repetitive phrases.
    - Limit the total character count to under 500 characters.
    - Respond ONLY with the cleaned tags list, comma-separated. Do not add any extra text any other than that in one line.
    """

    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    if not response: return []
    try:
        tag_string = response.strip()
        cleaned_tags = [tag.strip() for tag in tag_string.split(',') if tag.strip()]
        return cleaned_tags
    except Exception as e:
        print("❌ Error parsing Gemini response:", e)
        print("Raw response:", response)
        return []


@retry_infinite(delay=15)
def get_category_id_from_gemini(topic):
    prompt = f"""
    Given the YouTube video topic: "{topic}", return the most appropriate YouTube Category Name and ID from this list:

    1 - Film & Animation  
    2 - Autos & Vehicles  
    10 - Music  
    15 - Pets & Animals  
    17 - Sports  
    19 - Travel & Events  
    20 - Gaming  
    22 - People & Blogs  
    23 - Comedy  
    24 - Entertainment  
    25 - News & Politics  
    26 - Howto & Style  
    27 - Education  
    28 - Science & Technology  
    29 - Nonprofits & Activism  

    Only return the output in this format:
    Category Name: <name>  
    Category ID: <id>
    """


    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    return response.text


def extract_category_id(text):
    match = re.search(r'Category ID:\s*(\d+)', text)
    return int(match.group(1)) if match else 27  # Default to Education if not found






# --- Functions ---
# --- New Function to Generate Relevant Search Term ---
@retry_infinite(delay=15)
def generate_search_term(topic):
    prompt = f"Given the YouTube video topic '{topic}', suggest a short, relevant visual keyword or phrase for finding an image background. Limit to 3-5 words, no punctuation, just a plain image search phrase only one line and nothing else : keywords or phrase  just onloy that and nothing else mind it."
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    return response.text.strip()

@retry_infinite(delay=15)
def generate_title_from_topic1(topic):
    prompt = f"Create a catchy YouTube video thumbnail title for this topic: '{topic}'  one line title which seo optimised and nothing else okay i ahve to fed to my progrma so it should be clena and precise dont use symbols or icons or emojis, cerate catchy one, use punctuation marks properly and highly to emphasize, and it should have max upto 5 or 6 words not more that that"
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    return response.text.strip()

from PIL import Image

def resize_and_crop_to_1080x1920(img):
    target_width = 1080
    target_height = 1920
    target_ratio = target_width / target_height  # 1080 / 1920 = 0.5625

    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image is wider than target ratio
        # Resize by height, width will be larger than target_width
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        # Image is taller or equal ratio
        # Resize by width, height will be larger than target_height
        new_width = target_width
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Center crop
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    img = img.crop((left, top, right, bottom))
    return img



@retry_infinite(delay=15)
def search_pexels_image(query):
    url = "https://api.pexels.com/v1/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 10}
    resp = requests.get(url, headers=headers, params=params)
    photos = resp.json().get("photos", [])

    def is_aspect_ratio_close(photo):
        width, height = photo["width"], photo["height"]
        ratio = width / height
        return 1.7 < ratio < 1.9  # Close to 16:9

    # Try to find a 16:9 image
    for photo in photos:
        if is_aspect_ratio_close(photo):
            return photo["src"]["original"]

    # Fallback to first image if none are 16:9
    return photos[0]["src"]["original"] if photos else None

@retry_infinite(delay=15)
def search_google_image(query):
    params = {
        "engine": "google",
        "q": query,
        "tbm": "isch",
        "api_key": SERP_API_KEY,
        "num": 10  # get multiple images
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    images = results.get("images_results", [])

    def is_aspect_ratio_close(img_obj):
        try:
            url = img_obj["original"]
            img = download_image1(url)
            ratio = img.width / img.height
            # Check if ratio is approx 16:9 and size is decent
            if img.width >= 1080 and img.height >= 1920 and 1.7 < ratio < 1.9:
                return True, url
            else:
                return False, None
        except Exception:
            return False, None

    for img_obj in images:
        ok, url = is_aspect_ratio_close(img_obj)
        if ok:
            return url  # Return first good image URL

    # Fallback
    if images:
        return images[0]["original"]
    return None

@retry_infinite(delay=15)
def download_image1(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.content)).convert("RGB")


def get_dominant_color(img, resize_scale=150):
    """Resize image and get the most common RGB color."""
    small_img = img.resize((resize_scale, resize_scale))
    pixels = np.array(small_img).reshape(-1, 3)
    most_common = Counter(map(tuple, pixels)).most_common(1)[0][0]
    return most_common  # returns (R, G, B)

def invert_color(rgb):
    """Invert an RGB color."""
    return tuple(255 - v for v in rgb)


def get_readable_color(rgb_color):
    # Determine if black or white will be more readable on the given background color
    r, g, b = rgb_color
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (0, 0, 0) if luminance > 186 else (255, 255, 255)

def create_thumbnail(topic):
    print("🎯 Generating title...")
    title = generate_title_from_topic1(topic)
    print("📝 Title:", title)

    print("📥 Loading and resizing image...")
    # 🏛️ [VANTIX ASSET REGISTRY]: Use project-relative path or fail gracefully
    input_img_path = os.path.join(PROJECT_ROOT, "clara explains.png")
    if not os.path.exists(input_img_path):
         # Create a placeholder or use the topic image if available
         print("⚠️ Supplemental asset missing. Using stock backdrop...")
         img = Image.new("RGB", (1080, 1920), color=(30, 30, 30))
    else:
         img = Image.open(input_img_path).convert("RGB")
    
    img = resize_and_crop_to_1080x1920(img)

    print("🎨 Analyzing dominant color...")
    dominant_color = get_dominant_color(img)
    text_color = get_readable_color(dominant_color)
    border_color = get_readable_color(text_color)
    print(f"🎨 Dominant: {dominant_color}, Text: {text_color}, Border: {border_color}")

    print("🖋️ Adding title to image...")
    draw = ImageDraw.Draw(img)
    
    # 🖋️ [VANTIX TYPOGRAPHY] (v2.0)
    font_path = os.path.join(PROJECT_ROOT, "Anton-Regular.ttf")
    if not os.path.exists(font_path):
        # Industrial Fallback Loop
        fallbacks = ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", "Arial.ttf", "Impact.ttf"]
        for f in fallbacks:
            if os.path.exists(f) or shutil.which(f):
                font_path = f
                break
                
    try:
        font = ImageFont.truetype(font_path, 80)
    except:
        print("⚠️ [RENDERER] Final Font Fallback: Default")
        font = ImageFont.load_default()

    # Calculate text position
    bbox = draw.textbbox((0, 0), title, font=font)
    # 📐 [ENGINE] Dynamic Vertical Centering (v1.0)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    
    # Correct for target resolution: 1080 (W) x 1920 (H)
    x = (1080 - text_w) // 2
    y = 1920 - text_h - 150 # Shifted up for cinematic balance

    # Optional: Semi-transparent background box for better text visibility
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    padding = 40
    overlay_draw.rectangle(
        [x - padding, y - padding, x + text_w + padding, y + text_h + padding],
        fill=(0, 0, 0, 150)
    )
    img = Image.alpha_composite(img.convert("RGBA"), overlay)

    # Draw border (shadow effect)
    draw = ImageDraw.Draw(img)
    border_thickness = 4
    for dx in range(-border_thickness, border_thickness + 1):
        for dy in range(-border_thickness, border_thickness + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), title, font=font, fill=border_color)

    # Draw main title text
    draw.text((x, y), title, font=font, fill=text_color)

    # Save thumbnail
    out_path = "final_thumbnail.png"
    img.convert("RGB").save(out_path)
    print(f"✅ Thumbnail saved: {out_path}")


def trim_tags(tags, max_length=490):
    final_tags = []
    total_len = 0
    for tag in tags:
        if total_len + len(tag) + 2 <= max_length:
            final_tags.append(tag)
            total_len += len(tag) + 2  # +2 for comma and space
        else:
            break
    return final_tags

import googleapiclient.errors

# MAX_RETRIES = 10
# @retry_infinite(delay=15)
# def resumable_upload(request):
#     response = None
#     error = None
#     retry = 0

#     while response is None:
#         try:
#             print("Uploading...")
#             status, response = request.next_chunk()
#             if response:
#                 print(f"✅ Upload complete. Video ID: {response['id']}")
#                 return response
#         except (googleapiclient.errors.HttpError, IOError) as e:
#             error = e
#             retry += 1
#             if retry > MAX_RETRIES:
#                 print("❌ Upload failed after multiple retries.")
#                 return None
#             sleep_seconds = 2 ** retry
#             print(f"Unexpected error: {str(e)}")
#             print(f"🔁 Retrying in {sleep_seconds} seconds...")
#             time.sleep(sleep_seconds)

import logging


def sanitize_text(text, max_length=5000):
    """
    Clean and truncate text for YouTube metadata.
    - Replace multiple whitespace/newlines with single space.
    - Remove problematic control characters.
    - Truncate to max_length.
    """
    # Remove control characters except line breaks (optional)
    text = re.sub(r'[\x00-\x09\x0b-\x0c\x0e-\x1f\x7f]', '', text)
    
    # Normalize whitespace & newlines
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Truncate to max_length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text

def sanitize_tags(tags, max_tag_length=30):
    """
    Clean tags to be valid YouTube tags.
    - Remove empty strings.
    - Truncate tags that are too long.
    """
    clean_tags = []
    for tag in tags:
        tag = tag.strip()
        if not tag:
            continue
        if len(tag) > max_tag_length:
            tag = tag[:max_tag_length]
        clean_tags.append(tag)
    return clean_tags


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("upload.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

import google.auth.transport.requests


logger = logging.getLogger(__name__)


def generate_description_with_scene_links(base_description, scene_urls, feedback_link):
    description = sanitize_text(base_description)
    description = (
        f"{description}\n\n"
        f"📢 We'd love your feedback! Share your thoughts here 👉 {feedback_link}\n\n"
        "🎥 Scene Video Sources:\n"
    )

    for i, url in enumerate(scene_urls, 1):
        description += f"Scene {i} video: {url}\n"

    description += (
        "\nCinematic Technology | Cybernetic Dreams by Alex-Productions\n"
        "https://youtu.be/NDYRjTti5Bw\n"
        "Music promoted by https://onsound.eu/\n"
    )

    return description





# @retry_infinite(delay=15)
# def upload_video(file_path, topic):
  
#     feedback_link = "https://forms.gle/NLQ3gmdrsNU7DKev6"  # Replace with your actual form link
#     description=generate_youtube_description(topic)
    
#     description = sanitize_text(description)
#     description=generate_description_with_scene_links(description, feedback_link)
    
#     # Generate and clean tags
#     tags = trim_tags(generate_youtube_tags(topic))
#     final_tags = clean_tags_with_gemini(tags)
#     final_tags = sanitize_tags(final_tags)
#     # Category ID resolution
#     category_info = get_category_id_from_gemini(topic)
#     category_id = extract_category_id(category_info)

#     thumbnail_path=create_thumbnail(topic)  # Generate thumbnail before upload if needed

#     logger.info("📦 Preparing video upload...")
#     logger.info(f"🎬 Title: {topic}")
#     logger.info(f"📝 Description: {description}")
#     logger.info(f"🏷️ Tags: {final_tags}")
#     logger.info(f"📁 File: {file_path}")

#     request_body = {
#         "snippet": {
#             "title": topic,
#             "description": description,
#             "categoryId": str(category_id)
#         },
#         "status": {
#             "privacyStatus": "public"
#         }
#     }
    

#     if final_tags:
#         request_body["snippet"]["tags"] = final_tags
#     else:
#         logger.warning("⚠️ No tags provided, skipping tags field.")
#     import json
#     print(json.dumps(request_body, indent=2))
#     # Prepare media upload
#     try:
#         media = MediaFileUpload(file_path, chunksize=21*1024*1024, resumable=True, mimetype="video/mp4")
#     except Exception as e:
#         logger.error(f"❌ Error preparing video for upload: {e}")
#         return

#     try:
#         request = youtube.videos().insert(
#             part="snippet,status",
#             body=request_body,
#             media_body=media
#         )
#     except Exception as e:
#         logger.error(f"❌ Failed to initiate upload: {e}")
#         return

#     # Upload loop with retries
#     response = None
#     retry = 0
#     max_retries = 111111111  # reasonable max retries

#     while response is None:
#         try:
#             logger.info("🚀 Uploading...")
#             status, response = request.next_chunk()

#             if status:
#                 logger.info(f"📶 Upload progress: {int(status.progress() * 100)}%")

#             if response and 'id' in response:
#                 video_url = f"https://youtu.be/{response['id']}"
#                 logger.info(f"✅ Video uploaded successfully: {video_url}")
#                 break
#             else:
#                 logger.error("❌ Upload failed: No video ID returned.")
#                 return

#         except HttpError as e:
#             logger.warning(f"⚠️ HTTP Error {e.resp.status}: {e.content}")
#             if e.resp.status == 400:
#                 logger.error("❌ Bad Request. Check your metadata (title, description, tags, categoryId).")
#                 return
#             if e.resp.status not in [500, 502, 503, 504]:
#                 return

#         except (socket.timeout, TimeoutError, requests.exceptions.ReadTimeout) as e:
#             logger.warning(f"⏱️ Read timeout: {e}")

#         except (BrokenPipeError, ConnectionResetError, OSError) as e:
#             logger.warning(f"🔌 Connection error: {e}")

#         except Exception as e:
#             logger.error(f"❗ Unexpected error: {e}")
#             return

#         retry += 1
#         if retry > max_retries:
#             logger.error("❌ Upload failed after maximum retries.")
#             return

#         sleep_time = min(60, 2 ** retry)
#         logger.info(f"🔁 Retrying in {sleep_time:.2f} seconds (attempt {retry}/{max_retries})...")
#         time.sleep(sleep_time)

#     # Upload thumbnail
#     if thumbnail_path and response and 'id' in response:
#         try:
#             logger.info("🖼️ Uploading thumbnail...")
#             youtube.thumbnails().set(
#                 videoId=response["id"],
#                 media_body=MediaFileUpload(thumbnail_path)
#             ).execute()
#             logger.info("✅ Thumbnail uploaded successfully!")
#         except Exception as e:
#             logger.warning(f"❌ Thumbnail upload failed: {e}")




TOKEN_PATHS = [
    "/Users/uday/Downloads/VIDEOYT/token1.pickle",
    "/Users/uday/Downloads/VIDEOYT/token2.pickle",
    "/Users/uday/Downloads/VIDEOYT/token3.pickle",
    "/Users/uday/Downloads/VIDEOYT/token.pickle"
]

def build_youtube_client(token_path):
    with open(token_path, "rb") as token_file:
        credentials = pickle.load(token_file)
    return build("youtube", "v3", credentials=credentials)

def is_token_usable(youtube):
    try:
        channel_response = youtube.channels().list(part="contentDetails", mine=True).execute()
        return channel_response is not None
    except Exception as e:
        print(f"❌ Token not usable or quota exceeded: {e}")
        return False

def get_available_token():
    for path in TOKEN_PATHS:
        try:
            youtube = build_youtube_client(path)
            if is_token_usable(youtube):
                print(f"✅ Using token: {path}")
                return youtube, path
        except Exception as e:
            print(f"⚠️ Failed to load token: {path} — {e}")
    return None, None




# === MAIN DRIVER === #
if __name__ == "__main__":
        
    
    while True:

    # list_items = ["The Vision for Altcoin Season: Why You Shouldn't Overlook It!", "Exciting Predictions: Why This New AI Token Could Be Your Next 100X Opportunity!", "Essential Investment Strategies You Must Try This Week"
    # ]

    # for i in range(len(list_items)):
    #     user_topic = list_items[i]
    #     print(user_topic)

            
            # status = get_upload_status()
            # count = status["count"]

            # if count <= 0:
            #     print("✅ Upload limit reached for today.")
            #     break



        youtube, token_path = get_available_token()

        # Step 1: Get your channel ID - if you already know it, skip this step
        channel_response = youtube.channels().list(
            part="contentDetails",
            mine=True  # gets your own channel details
        ).execute()

        uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # Step 2: Retrieve all video titles from the uploads playlist
        video_titles = []
        next_page_token = None

        while True:
            playlist_response = youtube.playlistItems().list(
                part="snippet",
                playlistId=uploads_playlist_id,
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            for item in playlist_response['items']:
                video_titles.append(item['snippet']['title'])

            next_page_token = playlist_response.get('nextPageToken')
            if not next_page_token:
                break

        # Step 3: Save video titles to a text file and CSV file
        with open("/Users/uday/Downloads/VIDEOYT/used_topics.txt", "w", encoding="utf-8") as txt_file:
            for title in video_titles:
                txt_file.write(title + "\n")



        print(f"Retrieved and saved {len(video_titles)} video titles.")

        TOPIC_LOG_FILE = "used_topics.txt"

        @retry_infinite(delay=15)
        def generate_viral_wealth_topic():
            # prompt = (
            #     "Titles that create curiosity and enagagment and attractive that user tend to click highly"
            #     "1) Personal Finance & Investing 2)Health & Fitness 3) Tech Tutorials and Reviews 4) Tech and AI Innovations 5) Personal Development & Motivation 6) how to and facts are our target niches on which we will create videos\n\n"
            #     "generate a YouTube video title from above niches randomly that is:\n"
            #     "- catchy SEO-optimized with high click-through potential\n"
            #     "dont include i as title should be ggeneral but specific but not include me\n"
            #     "i want ot generate infinite wealth by using this title to create my video and post on yt to earn money"
            #     "- Strictly a single-line output (only the video title)\n\n"
            #     "dont include year, The output must be only the video title. Keep it human, and audience-focused."
            # )
            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Personal Finance and Investing niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):
          
            #     1. Passive Income & Wealth Building  
            #     2. Investing for Beginners  
            #     3. Stock Market & Equity Investing  
            #     4. Real Estate Investing  
            #     5. Cryptocurrency & Blockchain Investing  
            #     6. Budgeting & Saving Money  
            #     7. Tax Optimization & Smart Filing  
            #     8. Credit Score & Loan Management  
            #     9. Financial Planning & Goal Setting  
            #     10. Finance for Freelancers and Digital Creators  

            #     From  subcategories listed above, chose randomly one and give me:
            #     -title which is  such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by thsi title create that level of bes ttitle it should immediately make viewer to watch video mind it i want that level of title. mind it it should bes seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     -we are making videos for audience and not robots so give  a title likwise
            #     - dont include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that ehich peope are most searching for so video has highest potential of getiing viral, title must be specific not generic okay and aslo catcah attractice that user want to watch video and subscribe my channel mind it 
            #     - title msut be short not long one, max 50 characters, be precise consices and it should m,sut be engaging tiitle hooky title but short only and it must be valid title not an invalid one plas mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else don tuse bold text just plain format normal  text and nothing else.
                
            #     """
            # ]

            prompt = [
                """
                Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Tech & Gadgets niche, including AI Tools.

                I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

                1. AI Tools That Boost Productivity  
                2. Futuristic Gadgets & Smart Devices  
                3. Tech Reviews & Comparisons  
                4. Mobile & Laptop Innovations  
                5. Emerging Technologies & Trends  
                6. Software Tools & Chrome Extensions  
                7. Best Tech Under Budget (phones, gadgets etc.)  
                8. Automation & Workflow Tools  
                9. Daily Tech Life Hacks  
                10. Tech News & Quick Updates  

                From subcategories listed above, choose randomly one and give me:
                - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
                - 1 viral, curiosity-driven YouTube video title 
                - do not include me in the title it should be general but specific mind it
                - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
                - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
                Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
                """
            ]

            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Health & Fitness niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. Weight Loss & Fat Burning  
            #     2. Muscle Building & Home Workouts  
            #     3. Morning Routines for Energy & Focus  
            #     4. Fitness Challenges (7-day, 30-day, etc.)  
            #     5. Nutrition & Healthy Eating Hacks  
            #     6. Mental Health & Stress Relief Techniques  
            #     7. Sleep Hacks & Night Routines  
            #     8. Mobility, Flexibility & Posture Fixes  
            #     9. Biohacking & Recovery Tools  
            #     10. Fitness Tips for Busy People  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]

            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Make Money Online & Side Hustles niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. AI-Powered Side Hustles  
            #     2. Freelancing & Remote Work Platforms  
            #     3. Dropshipping & E-commerce  
            #     4. Affiliate Marketing Strategies  
            #     5. Print-on-Demand & Digital Products  
            #     6. Passive Income with Content Creation  
            #     7. Earning from YouTube, TikTok & Reels  
            #     8. Earning with ChatGPT & AI Automation  
            #     9. Selling Courses & Info Products  
            #     10. Best Work-from-Home Hacks  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]

            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Motivation & Self-Improvement niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. Morning Motivation & Daily Routines  
            #     2. Mindset Shifts for Success  
            #     3. Time Management & Productivity  
            #     4. Confidence Building & Overcoming Fear  
            #     5. Goal Setting & Life Planning  
            #     6. Habits of Successful People  
            #     7. Law of Attraction & Manifestation  
            #     8. Stoic Wisdom & Mental Toughness  
            #     9. Self-Discipline & Focus  
            #     10. Inspirational Stories & Life Lessons  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]

            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Relationships & Dating Advice niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. Dating Tips & First Impressions  
            #     2. Relationship Communication & Conflict Resolution  
            #     3. Online Dating & Dating Apps Strategies  
            #     4. Building Trust & Emotional Intimacy  
            #     5. Breakup Recovery & Moving On  
            #     6. Signs of Healthy vs Toxic Relationships  
            #     7. Attraction Psychology & Body Language  
            #     8. Long-Distance Relationships Advice  
            #     9. Marriage & Commitment Tips  
            #     10. Self-Love & Personal Growth in Relationships  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]

            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Health & Fitness niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. Home Workouts & Exercise Routines  
            #     2. Weight Loss Tips & Fat Burning  
            #     3. Nutrition & Healthy Eating  
            #     4. Mental Health & Stress Relief  
            #     5. Muscle Building & Strength Training  
            #     6. Yoga & Flexibility Exercises  
            #     7. Fitness Challenges & Transformation Stories  
            #     8. Supplements & Vitamins Guide  
            #     9. Sleep Improvement & Recovery  
            #     10. Health Myths & Facts Debunked  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]

            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Beauty & Fashion niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. Skincare Routines & Tips  
            #     2. Makeup Tutorials & Hacks  
            #     3. Fashion Trends & Styling Advice  
            #     4. Haircare & Hairstyles  
            #     5. Product Reviews & Recommendations  
            #     6. Sustainable & Ethical Fashion  
            #     7. Beauty Tools & Gadgets  
            #     8. Seasonal Fashion Lookbooks  
            #     9. DIY Beauty Remedies  
            #     10. Celebrity Style Inspirations  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]

            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Education & Learning niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. Study Tips & Productivity Hacks  
            #     2. Learning New Skills Fast  
            #     3. Exam Preparation Strategies  
            #     4. Language Learning Tips  
            #     5. Educational Technology & Tools  
            #     6. Science Experiments & Demonstrations  
            #     7. Math Tricks & Problem Solving  
            #     8. Career Advice & Job Skills  
            #     9. History & Fun Facts  
            #     10. Book Summaries & Reviews  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]

            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Travel & Adventure niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. Budget Travel Hacks  
            #     2. Hidden Travel Gems  
            #     3. Adventure Sports & Activities  
            #     4. Travel Gear Reviews  
            #     5. Cultural Experiences  
            #     6. Travel Vlogs & Stories  
            #     7. Travel Safety Tips  
            #     8. Eco-Friendly Travel  
            #     9. Food & Cuisine from Around the World  
            #     10. Solo Travel Guides  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]
            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Health & Fitness niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. Home Workout Routines  
            #     2. Nutrition & Diet Tips  
            #     3. Weight Loss Strategies  
            #     4. Mental Health & Wellness  
            #     5. Yoga & Meditation  
            #     6. Fitness Challenges  
            #     7. Supplements & Vitamins  
            #     8. Muscle Building Tips  
            #     9. Healthy Recipes  
            #     10. Injury Prevention & Recovery  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]

            # prompt = [
            #     """
            #     Act as a infinite wealth YouTube content creator and expert viral scriptwriter in the Beauty & Fashion niche.

            #     I want you to generate **highly engaging, viral video content ideas and titles** based on the following subcategories (ranked in descending order of profitability and audience interest):

            #     1. Skincare Routines & Tips  
            #     2. Makeup Tutorials  
            #     3. Fashion Trends & Hauls  
            #     4. Hair Care & Styling  
            #     5. Product Reviews & Recommendations  
            #     6. DIY Beauty Hacks  
            #     7. Sustainable Fashion  
            #     8. Men's Grooming Tips  
            #     9. Celebrity Style Inspiration  
            #     10. Seasonal Lookbooks  

            #     From subcategories listed above, choose randomly one and give me:
            #     - title which is such that user just clicks the video and want to see my video that much hooky catchy and attractive title, he tend to subscribe my video anyhow by this title create that level of best title it should immediately make viewer to watch video mind it i want that level of title. mind it it should be seo optimised
            #     - 1 viral, curiosity-driven YouTube video title 
            #     - do not include me in the title it should be general but specific mind it
            #     - title selected must be most trendy which is most trending on google search or whatever it must be that which people are most searching for so video has highest potential of getting viral
            #     - title must be short not long one, max 50 characters, be precise concise and it should must be engaging title hooky title but short only and it must be valid title not an invalid one please mind it, mind it
            #     Make title attention-grabbing, specific, and designed for high watch time and shares — ideal for platform YouTube, only return title plain text in one line and nothing else do not use bold text just plain format normal text and nothing else.
            #     """
            # ]


            # prompt = (

            #     "generate a YouTube video title on which i cerate video and upload on yt\n"
            #     "- catchy SEO-optimized with high click-through potential\n"
            #     "dont include i as title should be ggeneral but specific but not include me\n"
            #     "i want ot generate infinite wealth by using this title to create my video and post on yt to earn money"
            #     "- Strictly a single-line output (only the video title)\n\n"
            #     "dont include year, The output must be only the video title. Keep it human, and audience-focused."
            # )  
            # )


            # Load existing topics if file exists
            existing_topics = set()
            if os.path.exists(TOPIC_LOG_FILE):
                with open(TOPIC_LOG_FILE, 'r', encoding='utf-8') as file:
                    existing_topics = set(line.strip().lower() for line in file if line.strip())

            # Loop until a unique topic is generated
            while True:
                response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
                new_topic = response.text.strip()

                if new_topic.lower() not in existing_topics:
                    with open(TOPIC_LOG_FILE, 'a', encoding='utf-8') as file:
                        file.write(new_topic + '\n')
                    return new_topic
                    
                else:
                    print("Duplicate topic found, regenerating...")

        # Example usage
        user_topic = generate_viral_wealth_topic()
        print("💡 Unique Viral Topic:", user_topic)

        


        def delete_path(path):
            try:
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                elif path.is_file():
                    path.unlink()
                print(f"✅ Deleted: {path}")
            except Exception as e:
                print(f"❌ Error deleting {path}: {e}")

        # Cache directories
        cache_dirs = [
            Path.home() / "Library" / "Caches",
            Path("/Library/Caches"),
        ]

        # Log directories
        log_dirs = [
            Path.home() / "Library" / "Logs",
            Path("/Library/Logs")
        ]





        dirs_to_clean = cache_dirs + log_dirs 
        print("🧹 Cleaning up...")

        for d in dirs_to_clean:
            if d.exists():
                for item in d.iterdir():
                    delete_path(item)
            else:
                print(f"⚠️ Directory not found: {d}")

        print("✅ Done cleaning up!")


        output_path = "final_video/myfinal.mp4"  # replace with your actual output filename

        # Delete the file if it already exists
        if os.path.exists(output_path):
            os.remove(output_path)
            print(f"Previous file '{output_path}' deleted.")


        folder_path1 = "video_creation/"
        folder_path2 = "audio/"
        folder_path3 = "video_created/"

        # Function to delete files from a folder
        def delete_files_in_folder(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                

        # Delete files from both folders
        delete_files_in_folder(folder_path1)
        delete_files_in_folder(folder_path2)
        delete_files_in_folder(folder_path3)


        # !python3 -m pip uninstall torch torchvision torchaudio -y
        # !python3 -m pip uninstall torch torchvision torchaudio --user -y

        # !python3 -m pip install torch==2.0.1+cpu torchvision==0.15.2+cpu torchaudio==2.0.2+cpu --index-url https://download.pytorch.org/whl/cpu
        # !python3 -m pip install soundfile gradio
        # !pip uninstall numpy -y
        # !python3 -m pip install numpy==1.24.4

        # !python3 -m pip install openvoice-cli
        # !python3 -m pip install pydub
       
        script = generate_youtube_shorts_script(user_topic)
        print("\n📜 Generated Script:\n", script)
        output_dic, used_urls= create_video_from_script(script, user_topic)


        # print("🎬 How would you like to create your video?")
        # print("1. Based on a custom topic")
        # print("2. Based on a trending topic")
        # print("3. Using your own script")
        
        # choice = input("👉 Enter 1, 2, or 3: ").strip()

        # if choice == "1":
        #     user_topic = input("🎯 Enter your YouTube video topic: ").strip()
        #     script = generate_youtube_script(user_topic)
        #     print("\n📜 Generated Script:\n", script)
        #     create_video_from_script(script)

        # elif choice == "2":
        #     # Ensure get_trending_topic is defined or imported correctly
        #     try:
        #         user_topic = get_trending_topic()
        #         print(f"🔥 Trending Topic: {user_topic}")
        #         script = generate_youtube_script(user_topic)
        #         print("\n📜 Generated Script:\n", script)
        #         create_video_from_script(script)
        #     except NameError:
        #         print("⚠️ The 'get_trending_topic' function is not defined in this block. Skipping trending topic option.")


        # elif choice == "3":
        #     print("📝 Enter your script below. Press Enter twice to finish.")
        #     user_script_lines = []
        #     while True:
        #         line = input()
        #         if line.strip() == "":
        #             break
        #         user_script_lines.append(line)
        #     script = "\n".join(user_script_lines)
        #     print("\n📜 Using Your Script:\n", script)
        #     user_topic = get_topic_from_script(script)
        #     create_video_from_script(script)
        # else:
        #     print("❌ Invalid choice. Please run the program again and select 1, 2, or 3.")

        # 🛡️ [REDUNDANCY CLEANUP]: Neutralizing dangling NameErrors
        # final_video = concatenate_videoclips([clip.set_start(0) for clip in final_clips], method="chain")
        # output_temp = os.path.join(PROJECT_ROOT, "static/videos/temp_master.mp4")
        output_path = os.path.join(PROJECT_ROOT, "static/videos", f"vantix_{int(datetime.now().timestamp())}.mp4")

        # # Get a list of MP3 files in the folder
        # mp3_files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]


        # # Initialize an empty audio segment
        # combined = AudioSegment.empty()

        # # Concatenate all MP3 files
        # for file_name in mp3_files:
        #     file_path = os.path.join(folder_path, file_name)
        #     audio = AudioSegment.from_mp3(file_path)
        #     combined += audio

        # # Export the final merged MP3
        # combined.export(output_file, format="mp3")

        # === Step 1: Convert merged_audio.mp3 to WAV ===
        # mp3_path = '/Users/uday/Downloads/VIDEOYT/audio/merged_audio.mp3'
        # output_wav = '/Users/uday/Downloads/VIDEOYT/Wav2Lip/merged_audio.wav'
        # mp3_to_wav(mp3_path, output_wav)

   
        
        # python3 -m pip install -r /Users/uday/Downloads/VIDEOYT/Wav2Lip/requirements.txt
        # python3 -m pip uninstall torchvision -y
        # python3 -m pip uninstall batch-face -y # remove incorrect version if any
        # !python3 -m pip install batch-face==1.5.2  # latest stable batch-face version
        # !python3 -m pip install torchvision==0.15.1  # matches torch 2.7.0

        




        folder_path = "audio"
        combined = AudioSegment.empty()

        # Sort files by the numeric index in the filename
        def extract_scene_number(filename):
            match = re.search(r"scene_(\d+)\.mp3", filename)
            return int(match.group(1)) if match else float('inf')

        mp3_files = sorted(
            [f for f in os.listdir(folder_path) if f.endswith(".mp3")],
            key=extract_scene_number
        )

        for file_name in mp3_files:
            file_path = os.path.join(folder_path, file_name)

            if os.path.getsize(file_path) == 0:
                print(f"⚠️ Skipping empty file: {file_name}")
                continue

            try:
                audio = AudioSegment.from_mp3(file_path)
                combined += audio
            except Exception as e:
                print(f"❌ Could not decode {file_name}: {e}")
                continue

        # Export final merged MP3
        output_path1 = os.path.join(folder_path, "merged_audio.mp3")
        combined.export(output_path1, format="mp3")
        print(f"✅ Merged audio saved to: {output_path1}")



        # # === Step 1: Convert merged_audio.mp3 to WAV ===
        output_path1 = 'audio/merged_audio.mp3'
        output_wav = 'Wav2Lip/merged_audio.wav'
        mp3_to_wav(output_path1, output_wav)

        # from pydub import AudioSegment

        # def speed_up_wav(input_path, output_path, speed=1.5):
        #     sound = AudioSegment.from_wav(input_path)
        #     faster_sound = sound._spawn(sound.raw_data, overrides={
        #         "frame_rate": int(sound.frame_rate * speed)
        #     }).set_frame_rate(sound.frame_rate)
        #     faster_sound.export(output_path, format="wav")

        # # Example usage:
        # speed_up_wav(output_wav1, "faster.wav", speed=1.18)


        # # === Step 2: Run OpenVoice CLI with subprocess (not using !python) ===
        # input_wav = "faster1.wav"
        # output_wav = "/Users/uday/Downloads/VIDEOYT/Wav2Lip/merged_audio_final.wav"
        # openvoice_command = [
        #     "python3", "-m", "openvoice_cli", "single",
        #     "-i", output_wav1,
        #     "-r", input_wav,
        #     "-o", output_wav,
        #     "-d", "cpu"
        # ]

        # try:
        #     subprocess.run(openvoice_command, check=True)
        #     print(f"✅ OpenVoice processed: {output_wav}")
        # except subprocess.CalledProcessError as e:
        #     print("❌ OpenVoice CLI failed:")
        #     print(e)




        # Define all paths

        temp_result = "temp/result.avi"
        output_final = "video_created/output_with_audio.mp4"
        output_wav = os.path.join(PROJECT_ROOT, "Wav2Lip/merged_audio.wav")
        checkpoint_path = "checkpoints/wav2lip.pth"
        face_video = "Wav2Lip/output_video.mp4"
   

        run_wav2lip_inference(
            checkpoint_path="checkpoints/wav2lip.pth",
            face_video="Wav2Lip/output_video (4).mp4",
            audio_path="/Users/uday/Downloads/VIDEOYT/Wav2Lip/merged_audio.wav",
            output_video="video_created/output_with_audio1.mp4",
            static=True,
            fps=24,
            wav2lip_batch_size=256,
            resize_factor=4,
            out_height=360
        )



        # Step 2: Merge audio and video using FFmpeg
        print("🎵 Merging final video with audio...")
        subprocess.run([
            "ffmpeg", "-y",
            "-i", temp_result,
            "-i", output_wav,
            "-map", "0:v:0",
            "-map", "1:a:0",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "320k",         # Increased bitrate for better audio quality
            "-ar", "48000",         # Set sample rate to 48 kHz
            "-ac", "2",  
            "-shortest",
            output_final
        ])

        print(f"✅ Done! Final video with audio is saved to:\n{output_final}")



        


        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(PROJECT_ROOT, f"final_video/final_video_{timestamp}.mp4")






        command = [
            "ffmpeg", "-y",
            "-i", output_dic,        # Background video (with or without audio)
            "-i", output_final,   # Avatar video (with audio)
            "-filter_complex",
            """
            [1:v]scale=444:667[avatar];
            [0:v]scale=1080:1920[bg];
            [bg][avatar]overlay=W-w-10:H-h-10[outv];
            [0:a][1:a]amix=inputs=2:duration=first:dropout_transition=2[aout]
            """,
            "-map", "[outv]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",
            "-b:a", "192k",
            "-ar", "48000",
            "-ac", "2",
            "-shortest",
            output_file
        ]





        print("▶️ Generating video with avatar in bottom-right corner...")
        subprocess.run(command)
        print(f"✅ Final video saved to: {output_file}")



        def save_file_topic_mappings(mappings, filename):
            """
            Save mappings of output file paths and topic names to a text file.
            
            Each line will be:
            output_file_path | topic_name
            
            :param mappings: List of tuples [(file_path1, topic1), (file_path2, topic2), ...]
            :param filename: Text file to save mappings
            """
            with open(filename, 'a') as f:
                for file_path, topic in mappings:
                    f.write(f"{file_path} | {topic}\n")

        # Example usage:
        mappings = [
            (output_file, user_topic)
            
        ]

        save_file_topic_mappings(mappings, "/Users/uday/Downloads/VIDEOYT/file_topic_map.txt")


        # # Call your function
        # video_path, used_urls = create_video_from_script(script, user_topic)

        # If the video was created successfully, append to the permanent URL log file
        if output_file and used_urls:
            permanent_log_path = "all_video_used_urls.txt"  # Define your permanent log file

            with open(permanent_log_path, "a") as f:
                f.write(f"{os.path.basename(output_file)}\n")
                for url in sorted(used_urls):
                    f.write(url + "\n")
                f.write("\n")  # Blank line between entries

            print(f"📝 Appended used URLs to: {permanent_log_path}")
        else:
            print("❌ Could not create video or no URLs were used.")

        # count-=1

        # def get_urls_for_video(video_name, log_file="all_video_used_urls.txt"):
        #     urls = []
        #     with open(log_file, "r") as f:
        #         lines = f.readlines()

        #     collecting = False
        #     for line in lines:
        #         line = line.strip()
        #         if not line:
        #             collecting = False  # Stop when reaching a blank line
        #             continue
        #         if line == video_name:
        #             urls = []           # Clear in case video name appears multiple times
        #             collecting = True
        #             continue
        #         if collecting:
        #             urls.append(line)

        #     return urls


        # def generate_description_with_scene_links(base_description,feedback_link):
        #     description = sanitize_text(base_description)
        #     description = (
        #         f"{description}\n\n"
        #         f"📢 We'd love your feedback! Share your thoughts here 👉 {feedback_link}\n\n"
        #         "🎥 Scene Video Sources:\n"
        #     )
        #     urls= get_urls_for_video(output_file, log_file="all_video_used_urls.txt")
        #     for i, url in urls:
        #         description += f"Scene {i} video: {url}\n"

        #     description += (
        #         "\nCinematic Technology | Cybernetic Dreams by Alex-Productions\n"
        #         "https://youtu.be/NDYRjTti5Bw\n"
        #         "Music promoted by https://onsound.eu/\n"
        #     )

        #     return description

        # # Run the command
        # print("▶️ Merging video with avatar overlay and avatar audio...")
        # subprocess.run(command)
        # print(f"✅ Done! Final video saved to:\n{output_file}")
        

        # # Example Usage:
        # if output_file is not None:
        #     upload_video(output_file, user_topic)
        # else:
        #     print("Video creation failed.")

        # count -= 1
        # save_upload_status(count)
        # print(f"✅ Upload complete. Remaining uploads today: {count}")



