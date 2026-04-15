from ai_helper import generate_ai_response
import groq

# 🛡️ [NUCLEAR NEUTRALIZATION]: Legacy Proxies Fix (v1.0)
_original_groq_init = groq.Groq.__init__
def _patched_groq_init(self, *args, **kwargs):
    kwargs.pop("proxies", None)
    _original_groq_init(self, *args, **kwargs)
groq.Groq.__init__ = _patched_groq_init

import socket
socket.setdefaulttimeout(6000)

# === Imports === #
import os
os.environ["USE_OLLAMA_FIRST"] = "true"
import requests
import nltk
import spacy
from gtts import gTTS
from datetime import datetime
from nltk.tokenize import sent_tokenize
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, ColorClip, ImageClip, CompositeVideoClip, CompositeAudioClip, TextClip, vfx
from moviepy.audio.AudioClip import concatenate_audioclips
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import ffmpeg
import subprocess
from pydub import AudioSegment
import time
from functools import wraps
import json

from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO

from collections import Counter
import numpy as np



from googleapiclient.errors import HttpError
import pickle
import shutil
from pathlib import Path
import re  
from serpapi import GoogleSearch
import feedparser
import random

import sys
sys.path.append(os.path.abspath('Wav2Lip'))

# Set environment variables so pydub can find ffmpeg and ffprobe

os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

# Optional: also explicitly set converter paths (may be ignored by some methods)
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"
AudioSegment.ffprobe = "/opt/homebrew/bin/ffprobe"

# CLIENT_SECRETS_FILE = "/Users/uday/Downloads/VIDEOYT/client_secret_.json"  # Path to your client secret
# SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
# API_SERVICE_NAME = "youtube"
# API_VERSION = "v3"

# === Initial Setup === #
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nlp = spacy.load("en_core_web_sm")

# === API KEYS === #
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")
SERP_API_KEY = os.environ.get("SERP_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")



genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name='models/gemini-2.5-flash-preview-05-20')

# Get trending topic from Google Trends using SerpAPI



UPLOAD_LIMIT = 100
JSON_FILE = "UPLOAD_STATUS.json"



# Config (Environment Synchronized)
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

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

def retry_infinite(delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while True:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    print(f"❌ function failed (Attempt {attempt}): {e}")
                    print(f"🔁 Retrying in {delay} seconds...")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry_infinite(delay=5)
def get_trending_topic():
    """Tries SerpAPI for trends, falls back to free Google News RSS if needed."""
    print("📈 Searching for global trends...")
    
    # Primary: SerpAPI (High Precision)
    if SERP_API_KEY and SERP_API_KEY != "YOUR_SERPAPI_KEY":
        try:
            params = {
                "engine": "google_trends_trending_now",
                "geo": "US",
                "api_key": SERP_API_KEY
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            trending = results.get("trending_searches", [])
            if trending:
                return trending[0]["query"]
        except Exception as e:
            print(f"⚠️ SerpAPI Trending failed: {e}. Switching to Keyless Fallback...")

    # Fallback: Google News RSS (Free & Unlimited)
    return get_free_trending_topic()

def get_free_trending_topic():
    """Returns a trending headline from Google News RSS feed (Keyless)."""
    print("🌐 Engaging Keyless Stability: Fetching Trends via Google News RSS...")
    try:
        rss_url = "https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
        feed = feedparser.parse(rss_url)
        if feed.entries:
            # Pick a random entry from top 10 to ensure variety across runs
            entry = random.choice(feed.entries[:10])
            # Strip the source from title (usually at the end like "- CNN")
            topic = entry.title.rsplit('-', 1)[0].strip()
            return topic
    except Exception as e:
        print(f"⚠️ Keyless Trends failed: {e}")
    
    return "The future of Artificial Intelligence" # Ultimate Hardcoded Fallback

def get_niche_topic():
    """Returns a high-impact viral topic from a selected set of successful niches."""
    import random
    niches = {
        "Cosmic Mysteries": [
            "What happens if you fall into a white hole?",
            "The terrifying truth about the Great Attractor",
            "Why we might be the only life in the multiverse",
            "The rogue planet heading straight for our solar system"
        ],
        "Hidden History": [
            "The forbidden city found under the Giza pyramids",
            "The 2,000 year old battery that actually works",
            "The secret mission to find the Ark of the Covenant",
            "What the Vatican is hiding in its secret archives"
        ],
        "AI & Future": [
            "The day AI becomes smarter than all of humanity",
            "How we will live in a world without work",
            "The bio-hack that will let humans live for 200 years",
            "Why the first AI child will be born by 2030"
        ],
        "Elite Finance": [
            "The secret meeting where the world's wealth is decided",
            "How the 1% use debt to never pay taxes",
            "The coming collapse of the traditional banking system",
            "Why gold is being quietly hoarded by central banks"
        ]
    }
    category = random.choice(list(niches.keys()))
    topic = random.choice(niches[category])
    print(f"🤖 AI Niche Selection: [{category}] - {topic}")
    return topic

@retry_infinite(delay=5)
def generate_youtube_script(topic):
    prompt = f"""
    Write a high-retention YouTube script for the topic: "{topic}".
    
    STRUCTURE:
    1. THE HOOK (First 3-5 seconds): Start with a shocking fact, a direct question, or a high-stakes'curiosity gap'. Grab attention IMMEDIATELY.
    2. THE STORY: Don't just list facts. Build a narrative. Pose a problem, then lead towards the solution.
    3. RETENTION TRIGGERS: Use phrases like "Wait until you see what happens next" or "But here's the part nobody tells you".
    
    GUIDELINES:
    - NO intro like "Hey guys" or "Welcome back".
    - NO outro or call to action.
    - Style: Narrating, concise, precise, straight to the point.
    - Format: PLAIN PARAGRAPH format against the word 'youtube script'. 
    - No bold text (**), no lists, no marks.
    - Length: Max 2 minutes (approx 15-20 impactful sentences).
    - Goal: I want this to go viral. Make it creative, valuable, and irresistible to stop watching.
    """
    response = generate_ai_response(prompt)
    full_text = response.text.strip()

    # Extract only the part after the phrase 'youtube script'
    if 'youtube script' in full_text.lower():
        # Find the first occurrence regardless of casing
        index = full_text.lower().index('youtube script')
        script = full_text[index + len('youtube script'):].strip()
        # Remove any leading colon or punctuation often added by LLMs
        script = re.sub(r'^[ :\-]+', '', script)
        return script
    else:
        return full_text  # fallback if 'youtube script' not found

@retry_infinite(delay=5)    
def generate_viral_title(script, user_keys=None):
    prompt = f"""
    Based on this video script, generate 5 high-CTR (Click-Through Rate) YouTube titles.
    Use psychological triggers like: 
    - Curiosity ("The Truth About...")
    - Scarcity ("Never Do This...")
    - Numbers ("7 Secrets To...")
    - Hyperbole ("Unbelievable", "Insane", "Changed Everything")
    
    Choose the absolute BEST, most clickable one and return ONLY that title.
    
    Script:
    \"\"\"
    {script}
    \"\"\"
    
    Only return the title text, no quotes.
    """
    response = generate_ai_response(prompt, user_keys=user_keys)
    return response.text.strip().replace('"', '')

@retry_infinite(delay=5)    
def get_topic_from_script(script, user_keys=None):
    # Keeping this for internal use or as a fallback
    prompt = f"""
    Generate a concise topic name (2-4 words) for this script.
    
    Script: {script[:500]}...
    """
    response = generate_ai_response(prompt, user_keys=user_keys)
    if hasattr(response, 'text'):
        return response.text.strip().replace('"', '')
    return str(response).strip().replace('"', '')

@retry_infinite(delay=5)
def clean_script_noise(text):
    import re
    # Remove markers like [Hook], (Scene 1), etc. ONLY if they exist
    # But as per user request, we are moving towards "Direct" output.
    # We will only remove bolding and clean whitespace to stay as close to raw as possible.
    text = text.replace('*', '')
    
    # Normalize whitespace
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def generate_vantix_script(topic, user_keys=None):
    # Pass 1: Initial Viral Draft
    draft_prompt = f"""
    Write a high-intensity, viral YouTube script for: "{topic}".
    Use a shocking hook, curiosity gaps, and a fast-paced narrative arc.
    
    LIMIT: The script must be optimized for a 60-second YouTube Short. 
    Aim for approximately 140-160 words total.
    
    STRICT REQUIREMENT: Return ONLY the raw spoken words in a clean, continuous paragraph. 
    NO introductory text, NO scene labels, NO [Hook] tags, NO stage directions, NO headers. 
    Just start with the first word of the script.
    """
    draft_obj = generate_ai_response(draft_prompt, user_keys=user_keys)
    draft = draft_obj.text if hasattr(draft_obj, 'text') else str(draft_obj)
    draft = clean_script_noise(draft)
    
    # Pass 2: The Viral Critic (Self-Correction)
    critique_prompt = f"""
    You are the 'Viral Critic'. Analyze this script for:
    1. Hook Strength: Is it shocking enough in the first 3 seconds?
    2. Dopamine Pacing: Are there enough pattern interrupts in the text?
    3. Retention: Is there a reason to stay until the very end?
    
    Script:
    {draft}
    
    STRICT REQUIREMENT: Return ONLY the improved version of the spoken script as a pure, continuous paragraph.
    Absolutely NO feedback, NO analysis, NO [tags], NO headers, NO conversational filler.
    """
    critique_obj = generate_ai_response(critique_prompt, user_keys=user_keys)
    critique = critique_obj.text if hasattr(critique_obj, 'text') else str(critique_obj)
    
    # Pass 3: Final Infinity Edition
    final_prompt = f"""
    Rewrite the original script incorporating the Viral Critic's improvements.
    Ensure every sentence is punchy, high-stakes, and impossible to click away from.
    
    LENGTH CONSTRAINT: The final script MUST be between 140 and 160 words to fit within 60 seconds of high-fidelity narration.
    
    Original:
    {draft}
    
    Improvements to integrate:
    {critique}
    
    STRICT REQUIREMENT: Return ONLY the final spoken script in one solid paragraph.
    NO [labels], NO "Narrator:", NO intros, NO outros, NO meta-text.
    STRICTLY ONLY the words that will be spoken on camera.
    """
    final_obj = generate_ai_response(final_prompt, user_keys=user_keys)
    final_text = final_obj.text if hasattr(final_obj, 'text') else str(final_obj)
    return clean_script_noise(final_text)

@retry_infinite(delay=5)
def generate_youtube_script(topic, user_keys=None):
    return generate_vantix_script(topic, user_keys=user_keys)

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

@retry_infinite(delay=5)
def generate_visual_search_queries(sentence, user_topic, user_keys=None):
    prompt = f"""You are a stock footage search expert. Given a script sentence and topic, generate exactly 3 search queries for finding relevant background video clips on Pexels/Pixabay.

RULES:
1. Think about what REAL VIDEO FOOTAGE exists on stock sites — concrete, filmable scenes
2. Each query must be 2-4 words, simple and specific
3. Query 1 = most directly related to the sentence content
4. Query 2 = related to the visual mood/setting of the sentence
5. Query 3 = broader topic-level visual that still fits
6. NEVER use abstract concepts — stock sites have footage of REAL things, not ideas
7. Prefer: people, places, objects, nature, actions, technology in use

GOOD examples: "scientist in lab", "city traffic night", "person using phone", "ocean waves sunset"
BAD examples: "artificial intelligence", "economic growth", "political tension", "innovation"

Topic: {user_topic}
Sentence: {sentence}

Return ONLY 3 queries, one per line, no numbering, no quotes, no extra text."""
    response = generate_ai_response(prompt, user_keys=user_keys)
    queries = [q.strip() for q in response.text.strip().split("\n") if q.strip()]
    return queries[:3] if queries else [user_topic]

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY", "")

@retry_infinite(delay=5)
def identify_visual_beats_ollama(sentence, user_topic):
    """
    Identify essential visual transitions in a sentence using local Ollama.
    STRICTLY NEEDS-BASED: Only identify a new beat if the subject matter changes.
    Returns: List of dicts [{"text": "...", "queries": [...]}]
    """
    url = "http://localhost:11434/api/generate"
    prompt = f"""Analyze this script segment and identify every single semantic transition point to keep the video FAST-PACED and ENGAGING.

Topic: {user_topic}
Segment: {sentence}

STRICT GUIDELINES:
1. Identify a new visual beat EVERY TIME a new key term, entity, or distinct action is mentioned.
2. Aim for a high cut frequency: ideally one cut every 2-4 seconds of speech.
3. Each beat must have a specific 'text' part and highly relevant search 'queries'.
4. Together, the segment texts must EXACTLY equal the full segment: "{sentence}"
5. If the segment is long, you MUST provide at least 3-6 distinct beats.

Return ONLY valid JSON:
[
  {{"text": "sub-phrase 1", "queries": ["query A", "query B"]}},
  ...
]"""
    
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.7  # Higher temperature for more creative/frequent segmentation
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            result = response.json()
            segments = json.loads(result['response'])
            if isinstance(segments, list) and len(segments) > 0:
                # No more hardcoded middle-splitting. Trusting the semantic prompt.
                for seg in segments:
                    if 'text' not in seg: seg['text'] = sentence
                    if 'queries' not in seg: seg['queries'] = [user_topic]
                return segments
    except Exception as e:
        print(f"⚠️ Ollama beat identification failed: {e}")
    
    return [{"text": sentence, "queries": [user_topic]}]

@retry_infinite(delay=5)
def search_pixabay_videos(query, per_page=200, max_results=15):  # lowered per_page for quicker tests
    url = 'https://pixabay.com/api/videos/'
    page = 1
    found_clips = []

    while len(found_clips) < max_results:
        params = {'key': API_KEY, 'q': query, 'per_page': per_page, 'page': page}
        response = requests.get(url, params=params)

        if response.status_code != 200:
            print(f"❌ Pixabay Error: {response.status_code} - {response.text}")
            break

        results = response.json().get('hits', [])
        if not results:
            print(f"❌ Pixabay: No more results on page {page} for '{query}'")
            break

        print(f"🔎 Pixabay Page {page}: Found {len(results)} videos for '{query}'")

        for i, clip in enumerate(results):
            videos = clip.get("videos", {})
            for quality_key, quality in videos.items():
                width = quality.get("width", 0)
                height = quality.get("height", 0)
                video_url = quality.get("url", "NO_URL")

                if abs(width - 1920) <= 200 and abs(height - 1080) <= 200:
                    clip["video_files"] = [quality]
                    clip["width"] = width
                    clip["height"] = height
                    clip["source"] = "pixabay"

                    if video_url not in [c["video_files"][0]["url"] for c in found_clips]:
                        found_clips.append(clip)

                    break  # Exit inner loop once 1 quality match is found

        page += 1

    return found_clips




@retry_infinite(delay=5)
def search_pexels_video(query, per_page=80, target_width=1920, target_height=1080, tolerance=200, max_clips=15):
    page = 1
    headers = {"Authorization": PEXELS_API_KEY}
    suitable_clips = []

    while True:
        params = {"query": query, "per_page": per_page, "page": page}
        response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)

        if response.status_code != 200:
            print(f"❌ Pexels Error: {response.status_code} - {response.text}")
            return suitable_clips

        results = response.json().get("videos", [])
        if not results:
            print(f"❌ Pexels: No more results on page {page} for '{query}'")
            break

        print(f"🔎 Pexels Page {page}: Found {len(results)} videos for '{query}'")

        if page == 1:
            print("Sample raw results for inspection:")
            print(json.dumps(results[:2], indent=2))

        for i, clip in enumerate(results):
            for file in clip["video_files"]:
                width = file.get("width", 0)
                height = file.get("height", 0)
                video_url = file.get("link", "NO_URL")

                print(f"Candidate {i}: URL={video_url}, Resolution={width}x{height}")

                if abs(width - target_width) <= tolerance and abs(height - target_height) <= tolerance:
                    print(f"✅ Suitable video found at {video_url} with resolution {width}x{height}")

                    clip["video_files"] = [file]
                    clip["width"] = width
                    clip["height"] = height
                    clip["source"] = "pexels"

                    suitable_clips.append(clip)
                    break  # No need to check other file resolutions for this clip

            if len(suitable_clips) >= max_clips:
                print(f"🎯 Collected {max_clips} suitable clips. Stopping search.")
                return suitable_clips

        print(f"➡️ No enough clips yet, moving to page {page + 1}...")
        page += 1

    return suitable_clips




# === Search Pexels for a Query === #






# Replace with your actual Pixabay API key


@retry_infinite(delay=5)
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

@retry_infinite(delay=5)
def find_one_video_clips(sentence, used_video_urls, user_topic, max_clips=15):
    print(f"🔍 Searching multiple clips for: {sentence}")
    queries = generate_visual_search_queries(sentence, user_topic)

    def is_valid(clip_url, width, height):
        return (
            abs(width - 1920) <= 200 and
            abs(height - 1080) <= 200 and
            clip_url not in used_video_urls
        )

    def process_pexels(query):
        print(f"🔎 [Pexels] Query: {query}")
        results = []
        for clip in search_pexels_video(query):
            video_url = clip["video_files"][0]["link"]
            if is_valid(video_url, clip["width"], clip["height"]):
                clip["source"] = "pexels"
                results.append(clip)
                if len(results) >= max_clips:
                    break
        return results

    def process_pixabay(query):
        print(f"🔎 [Pixabay] Query: {query}")
        results = []
        for clip in search_pixabay_videos(query, per_page=200):
            try:
                video = clip["videos"]["medium"]
                video_url = video["url"]
                if is_valid(video_url, video["width"], video["height"]):
                    results.append({
                        "video_files": [{"link": video_url}],
                        "width": video["width"],
                        "height": video["height"],
                        "source": "pixabay"
                    })
                    if len(results) >= max_clips:
                        break
            except KeyError:
                continue
        return results

    collected = []

    for query in queries:
        collected += process_pexels(query)
        if len(collected) >= max_clips:
            return collected[:max_clips]

        collected += process_pixabay(query)
        if len(collected) >= max_clips:
            return collected[:max_clips]

        # Try keywords from query if not enough
        keywords = extract_keywords(query)
        for keyword in keywords:
            collected += process_pexels(keyword)
            if len(collected) >= max_clips:
                return collected[:max_clips]

            collected += process_pixabay(keyword)
            if len(collected) >= max_clips:
                return collected[:max_clips]

    print("❌ Not enough suitable clips found.")
    return collected[:max_clips]







    
 # List of up to 3 unique clips, one per query



# === Download Video === #
@retry_infinite(delay=5)
def download_video(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename

# === Generate Audio === #
@retry_infinite(delay=5)
def generate_audio(text, filename):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return AudioFileClip(filename)



def create_scene(sentence_text, idx, used_video_urls, user_topic):
    print(f"\n🎬 Creating Smart Scene {idx + 1}")

    # 1) Identify visual beats strictly as needed using Ollama
    beats = identify_visual_beats_ollama(sentence_text, user_topic)
    
    all_new_urls = []
    segment_clips = []
    segment_audios = []

    for b_idx, beat in enumerate(beats):
        beat_text = beat["text"].strip()
        if not beat_text: continue
        
        print(f"  󰄱 Visual Beat {b_idx+1}: {beat_text}")
        
        # 2) Generate TTS for this beat to get exact duration
        try:
            temp_audio_path = f"audio/scene_{idx}_beat_{b_idx}.mp3"
            seg_audio = generate_audio(beat_text, temp_audio_path)
            seg_duration = seg_audio.duration
            segment_audios.append(seg_audio)
        except Exception as e:
            print(f"  ❌ Beat audio failed: {e}")
            continue

        # 3) Find video for this specific beat
        queries = beat.get("queries", [user_topic])
        found_clip = None
        
        candidate_clips = []
        for q in queries:
            print(f"    🔍 Searching for: {q}")
            pexels_res = search_pexels_video(q, max_clips=5)
            for clip in pexels_res:
                video_url = clip["video_files"][0].get("link") or clip["video_files"][0].get("url")
                if video_url and video_url not in used_video_urls:
                    clip["source"] = "pexels"
                    candidate_clips.append(clip)
                    break
            if candidate_clips: break
            
            pixabay_res = search_pixabay_videos(q, max_results=5)
            for clip in pixabay_res:
                video_url = clip["video_files"][0].get("link") or clip["video_files"][0].get("url")
                if video_url and video_url not in used_video_urls:
                    clip["source"] = "pixabay"
                    candidate_clips.append(clip)
                    break
            if candidate_clips: break

        if not candidate_clips:
            print(f"    ⚠️ No specific clip found, using topic fallback.")
            fallback_res = search_pexels_video(user_topic, max_clips=10)
            for clip in fallback_res:
                v_url = clip["video_files"][0].get("link") or clip["video_files"][0].get("url")
                if v_url and v_url not in used_video_urls:
                    candidate_clips = [clip]
                    break

        for clip_data in candidate_clips:
            video_url = clip_data["video_files"][0].get("link") or clip_data["video_files"][0].get("url")
            if not video_url: continue
            
            tmp_path = f"video_creation/scene_{idx}_beat_{b_idx}_temp.mp4"
            if clip_data.get("source") == "pixabay":
                download_videos1(video_url, tmp_path)
            else:
                download_video(video_url, tmp_path)
            
            try:
                raw_clip = VideoFileClip(tmp_path).without_audio()
                
                # Loop or trim to match beat duration
                if raw_clip.duration < seg_duration:
                    n_loops = int(np.ceil(seg_duration / raw_clip.duration))
                    raw_clip = vfx.loop(raw_clip, n=n_loops)
                
                clip = raw_clip.subclip(0, seg_duration)
                
                # Standardize resolution 1920x1080
                target_aspect = 1920 / 1080
                actual_aspect = clip.w / clip.h
                if abs(actual_aspect - target_aspect) < 0.01:
                    clip = clip.resize((1920, 1080))
                elif actual_aspect > target_aspect:
                    clip = clip.resize(height=1080)
                    x_center = clip.w / 2
                    clip = clip.crop(x1=x_center - 960, x2=x_center + 960, y1=0, y2=1080)
                else:
                    clip = clip.resize(width=1920)
                    y_center = clip.h / 2
                    clip = clip.crop(x1=0, x2=1920, y1=y_center - 540, y2=y_center + 540)
                
                found_clip = clip.set_position("center").set_fps(30)
                all_new_urls.append(video_url)
                used_video_urls.add(video_url)
                raw_clip.close()
                break
            except Exception as e:
                print(f"    ❌ Beat processing failed: {e}")
                continue
            
        if found_clip:
            segment_clips.append(found_clip)
        else:
            print(f"    ⚠️ Using placeholder for beat")
            segment_clips.append(ColorClip(size=(1920, 1080), color=(30, 30, 30)).set_duration(seg_duration).set_fps(30))

    if not segment_clips:
        return None, []

    # 4) Stitch visual beats
    final_video = concatenate_videoclips(segment_clips, method="compose")
    
    # Generate combined scene audio
    final_audio = concatenate_audioclips(segment_audios)
    final_audio_path = f"audio/scene_{idx}.mp3"
    final_audio.write_audiofile(final_audio_path, fps=44100, logger=None)
    
    # 5) Build Final Scene with Subtitles
    subtitle = (
        TextClip(
            sentence_text,
            fontsize=60,
            color="white",
            font="Arial-Bold",
            size=(1920, 1080),
            method="caption"
        )
        .set_position(("center", "bottom"))
        .set_duration(final_audio.duration)
        .fadein(0.5)
    )
    
    final_scene = CompositeVideoClip([final_video, subtitle])
    final_scene = final_scene.set_audio(AudioFileClip(final_audio_path))

    return final_scene, all_new_urls

def create_fast_cut_clip_from_images(image_paths, total_duration=5, resolution=(1920,1080)):
    per_image_duration = total_duration / len(image_paths)
    tick_sound = AudioFileClip("/Users/uday/Downloads/VIDEOYT/analog-camera-shutter-96604_z7Dhy2kD.mp3").volumex(0.1)
    clips = []

    for i, path in enumerate(image_paths):
        clip = ImageClip(path).set_duration(per_image_duration).fadein(0.1).fadeout(0.05).resize(resolution)
        tick_audio = tick_sound.subclip(0, min(0.17, tick_sound.duration))
        clip = clip.set_audio(tick_audio)
        clips.append(clip)

    fast_cut_clip = concatenate_videoclips(clips, method="compose")

 

    return fast_cut_clip


def create_video_from_script(script, user_topic, include_disclaimer=True):
    import uuid
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
    from moviepy.audio.fx.all import audio_loop

    # Split on periods and semicolons for better granularity
    initial_sentences = sent_tokenize(script)
    sentences = []
    for s in initial_sentences:
        # Split on semicolons for better granularity
        parts = [p.strip() for p in s.split(";") if p.strip()]
        for p in parts:
            # If a part is very long (>30 words), split it once at the nearest comma to help the AI
            # But keep it mostly semantic.
            if len(p.split()) > 30 and "," in p:
                comma_parts = [cp.strip() for cp in p.split(",", 1) if cp.strip()]
                sentences.extend(comma_parts)
            else:
                sentences.append(p)
    
    used_video_urls = set()
    scene_clips = []

    output_dir = "video_created"
    os.makedirs(output_dir, exist_ok=True)

    # Add disclaimer video if available
    disclaimer_path = "/Users/uday/Downloads/VIDEOYT/disclaimer_video.mp4"
    if include_disclaimer and os.path.exists(disclaimer_path):
        disclaimer_clip = VideoFileClip(disclaimer_path).without_audio()
        scene_clips.append(disclaimer_clip)
    elif include_disclaimer:
        print(f"⚠️ Disclaimer video not found at: {disclaimer_path}. Skipping disclaimer.")

    # After disclaimer, add the 5-second fast cut video from Pexels images
    cache_folder = get_cache_folder_for_topic(user_topic)
    images = load_images_from_cache(cache_folder, NUM_IMAGES)

    if not images:
        print("No sufficient cached images, fetching from Pexels...")
        clear_temp_folder(cache_folder)
        urls = fetch_pexels_images(user_topic, 21)
        images = prepare_images(urls, cache_folder, RESOLUTION)

    fast_cut_clip = create_fast_cut_clip_from_images(images, total_duration=5, resolution=RESOLUTION)
    scene_clips.append(fast_cut_clip)

    # Process scripted sentences into clips
    all_used_urls = set()
    for idx, sentence in enumerate(sentences):
        scene_clip, scene_urls = create_scene(sentence, idx, used_video_urls, user_topic)
        if scene_clip is not None:
            scene_clips.append(scene_clip)
        all_used_urls.update(scene_urls)

    print("All used URLs:", all_used_urls)

    if not scene_clips:
        print("❌ No scenes could be created. Cannot generate final video.")
        return None, None

    # Check for valid clips
    for i, clip in enumerate(scene_clips):
        if not hasattr(clip, 'duration'):
            print(f"❌ Invalid clip at index {i}: {clip}")
            return None, None

    # Concatenate all video clips
    final_clip = concatenate_videoclips(scene_clips, method="compose")

    # Background music
    bg_music_raw = AudioFileClip("/Users/uday/Downloads/VIDEOYT/Cybernetic Dreams.mp3").volumex(0.03)
    bg_music_looped = audio_loop(bg_music_raw, duration=final_clip.duration).set_start(5)

    # Mix with existing audio
    if final_clip.audio:
        final_audio = CompositeAudioClip([final_clip.audio.set_duration(final_clip.duration), bg_music_looped])
    else:
        final_audio = bg_music_looped

    final_clip = final_clip.set_audio(final_audio)

    # Temporary paths
    temp_video_path = os.path.join(output_dir, f"temp_video_{uuid.uuid4()}.mp4")
    temp_audio_path = os.path.join(output_dir, f"temp_audio_{uuid.uuid4()}.mp3")
    output_path = os.path.join(output_dir, "final_video_01.mp4")

    # Export video without audio
    final_clip.without_audio().write_videofile(
        temp_video_path,
        codec="libx264",
        fps=30,
        preset="ultrafast",
        threads=8,
        audio=False
    )

    # Export audio
    final_audio.write_audiofile(temp_audio_path, fps=44100)

    # Combine video and audio using FFmpeg
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",
        "-i", temp_video_path,
        "-i", temp_audio_path,
        "-c:v", "copy",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]

    print("🔧 Running FFmpeg to mux video and audio...")
    subprocess.run(ffmpeg_cmd, check=True)
    print(f"✅ Final video created at: {output_path}")

    # Optionally cleanup temp files
    os.remove(temp_video_path)
    os.remove(temp_audio_path)

    return output_path, all_used_urls







# @retry_infinite(delay=5)
# def generate_youtube_title(topic):
#     prompt = f"""
#     Create a highly clickable, viral YouTube video title for the topic: "{topic}".
#     Do not include any extra explanation or formatting. Just return the title only. it should be seo optimised mind it
#     """
#     response = generate_ai_response(prompt)
#     return response.text.strip()

@retry_infinite(delay=5)
def generate_youtube_description(topic, script):
    prompt = f"""
    Write a 3-part YouTube description for: "{topic}".
    1. THE HOOK: A compelling summary that makes people want to watch.
    2. VALUE POINTS: Use bullet points (plain text) to highlight 3-5 key takeaways from the script.
    3. SEO OPTIMIZATION: Naturally include high-volume keywords related to the topic.
    
    Include 10 viral hashtags at the end.
    Script context: {script[:300]}...
    
    Return the description content only. No labels like 'Description:'.
    """
    response = generate_ai_response(prompt)
    return response.text.strip()

@retry_infinite(delay=5)
def generate_youtube_tags(topic, script):
    prompt = f"""
    Generate 30 high-relevance YouTube tags for the topic: "{topic}".
    Include:
    - Specific keywords (e.g., specific names, entities)
    - Broad keywords (e.g., "technology", "news")
    - Trending descriptors (e.g., "2026", "new")
    
    Return ONLY a comma-separated list of tags. No explanation.
    Script context: {script[:300]}...
    """
    response = generate_ai_response(prompt)
    tag_string = response.text.strip()
    tag_list = [tag.strip() for tag in tag_string.split(',')]
    return tag_list

import ast

@retry_infinite(delay=5)
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

    response = generate_ai_response(prompt)
    try:
        tag_string = response.text.strip()
        cleaned_tags = [tag.strip() for tag in tag_string.split(',') if tag.strip()]
        return cleaned_tags
    except Exception as e:
        print("❌ Error parsing Gemini response:", e)
        print("Raw response:", response.text)
        return []


@retry_infinite(delay=5)
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


    response = generate_ai_response(prompt)
    return response.text


def extract_category_id(text):
    match = re.search(r'Category ID:\s*(\d+)', text)
    return int(match.group(1)) if match else 27  # Default to Education if not found






# --- Functions ---
# --- New Function to Generate Relevant Search Term ---
@retry_infinite(delay=5)
def generate_search_term(topic):
    prompt = f"Given the YouTube video topic '{topic}', suggest a short, relevant visual keyword or phrase for finding an image background. Limit to 3-5 words, no punctuation, just a plain image search phrase only one line and nothing else : keywords or phrase  just onloy that and nothing else mind it."
    response = generate_ai_response(prompt)
    return response.text.strip()

@retry_infinite(delay=5)
def generate_title_from_topic1(topic):
    prompt = f"Create a catchy YouTube video thumbnail title for this topic: '{topic}'  one line title which seo optimised and nothing else okay i ahve to fed to my progrma so it should be clena and precise dont use symbols or icons or emojis, cerate catchy one, use punctuation marks properly and highly to emphasize, and it should have max upto 5 or 6 words not more that that"
    response = generate_ai_response(prompt)
    return response.text.strip()

def resize_and_crop_to_1920x1080(img):
    target_ratio = 1920 / 1080
    img_ratio = img.width / img.height

    if img_ratio > target_ratio:
        # Image is too wide
        new_height = 1080
        new_width = int(1080 * img_ratio)
    else:
        # Image is too tall or exact fit
        new_width = 1920
        new_height = int(1920 / img_ratio)

    img = img.resize((new_width, new_height), Image.LANCZOS)

    # Crop center
    left = (img.width - 1920) // 2
    top = (img.height - 1080) // 2
    right = left + 1920
    bottom = top + 1080

    return img.crop((left, top, right, bottom))

@retry_infinite(delay=5)
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

@retry_infinite(delay=5)
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
            if img.width >= 1280 and img.height >= 720 and 1.7 < ratio < 1.9:
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

@retry_infinite(delay=5)
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

def get_readable_color(bg_color):
    """Return black or white text color based on background luminance."""
    r, g, b = bg_color
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return (255, 255, 255) if luminance < 0.5 else (0, 0, 0)

def create_thumbnail(topic):
    print("🎯 Generating title...")
    title = generate_title_from_topic1(topic)
    print("📝 Title:", title)

    print("🔎 Getting search phrase for image...")
    search_term = generate_search_term(topic)
    print("🔍 Searching image for:", search_term)

    print("🌄 Searching for background image...")
    bg_url = search_pexels_image(search_term) or search_google_image(search_term)
    if not bg_url:
        raise ValueError("❌ No image found for topic.")
    print("📷 Image URL:", bg_url)

    print("📥 Downloading image...")
    img = download_image1(bg_url)
    img = resize_and_crop_to_1920x1080(img)

    print("🎨 Analyzing dominant color...")
    dominant_color = get_dominant_color(img)
    text_color = get_readable_color(dominant_color)
    border_color = get_readable_color(text_color)
    print(f"🎨 Dominant: {dominant_color}, Text: {text_color}, Border: {border_color}")

    print("🖋️ Adding title to image...")
    draw = ImageDraw.Draw(img)
    font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"  # Adjust for Windows/Linux if needed
    font = ImageFont.truetype(font_path, 80)

    bbox = draw.textbbox((0, 0), title, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (1920 - text_w) // 2
    y = 1080 - text_h - 50

    # Optional: Draw semi-transparent box behind text to improve contrast
    # overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    # overlay_draw = ImageDraw.Draw(overlay)
    # padding = 40
    # overlay_draw.rectangle(
    #     [x - padding, y - padding, x + text_w + padding, y + text_h + padding],
    #     fill=(0, 0, 0, 150)  # Semi-transparent black background
    # )
    # img = Image.alpha_composite(img.convert("RGBA"), overlay)

    # Draw border
    draw = ImageDraw.Draw(img)
    border_thickness = 4
    for dx in range(-border_thickness, border_thickness + 1):
        for dy in range(-border_thickness, border_thickness + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), title, font=font, fill=border_color)

    # Draw main text
    draw.text((x, y), title, font=font, fill=text_color)

    # Save final image
    out_path = f"final_thumbnail.png"
    print("💾 Saving to:", out_path)

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
# @retry_infinite(delay=5)
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

import random
import google.auth.transport.requests


logger = logging.getLogger(__name__)



def get_chunk_size(file_path):
    file_size = os.path.getsize(file_path)  # size in bytes
    mb = 1024 * 1024
    
    if file_size < 50 * mb:
        return 50*mb
    elif file_size < 200 * mb:
        return 100*mb
    else:
        return 400*mb


def save_file_topic_mappings(mappings, filename):
    """
    Save mappings of output file paths and topic names to a text file.
    Each line will be: output_file_path | topic_name
    """
    with open(filename, 'a') as f:
        for file_path, topic in mappings:
            f.write(f"{file_path} | {topic}\n")


def get_urls_for_video(video_name, log_file="all_video_used_urls.txt"):
    urls = []
    if not os.path.exists(log_file):
        return urls
    with open(log_file, "r") as f:
        lines = f.readlines()

    collecting = False
    for line in lines:
        line = line.strip()
        if not line:
            collecting = False
            continue
        if line == os.path.basename(video_name):
            urls = []
            collecting = True
            continue
        if collecting:
            urls.append(line)
    return urls


def generate_description_with_scene_links(base_description, feedback_link, video_path):
    description = sanitize_text(base_description)
    description = (
        f"{description}\n\n"
        f"📢 We'd love your feedback! Share your thoughts here 👉 {feedback_link}\n\n"
        "🎥 Scene Video Sources:\n"
    )
    urls = get_urls_for_video(video_path, log_file="all_video_used_urls.txt")
    for i, url in enumerate(urls, 1):
        description += f"Scene {i} video: {url}\n"

    description += (
        "\nCinematic Technology | Cybernetic Dreams by Alex-Productions\n"
        "https://youtu.be/NDYRjTti5Bw\n"
        "Music promoted by https://onsound.eu/\n"
    )
    return description


def remove_video_entry(video_name, log_file="all_video_used_urls.txt"):
    if not os.path.exists(log_file):
        return
    with open(log_file, "r") as f:
        lines = f.readlines()

    new_lines = []
    skip = False
    target_name = os.path.basename(video_name)

    for line in lines:
        if line.strip() == target_name:
            skip = True
            continue
        if skip:
            if line.strip() == "":
                skip = False
            continue
        new_lines.append(line)

    with open(log_file, "w") as f:
        f.writelines(new_lines)

    print(f"✅ Entry for '{target_name}' removed from {log_file}")


@retry_infinite(delay=5)
def upload_video(file_path, topic, script, thumbnail_path):
    
    feedback_link = "https://forms.gle/NLQ3gmdrsNU7DKev6"  # Replace with your actual form link
    viral_title = generate_viral_title(script)
    description = generate_youtube_description(topic, script)
    pinned_comment = generate_pinned_comment(topic, script)
    
    print(f"🔥 VIRAL PINNED COMMENT GENERATED:\n{pinned_comment}\n")
    
    description = sanitize_text(description)
    description = generate_description_with_scene_links(description, feedback_link, file_path)
    
    # Generate and clean tags
    tags = trim_tags(generate_youtube_tags(topic, script))
    final_tags = clean_tags_with_gemini(tags)
    final_tags = sanitize_tags(final_tags)
    # Category ID resolution
    category_info = get_category_id_from_gemini(topic)
    category_id = extract_category_id(category_info)

    create_thumbnail(topic)  # Generate thumbnail before upload if needed
    chunk_size = get_chunk_size(file_path)
    logger.info("📦 Preparing video upload...")
    logger.info(f"🎬 Title: {topic}")
    logger.info(f"📝 Description: {description}")
    logger.info(f"🏷️ Tags: {final_tags}")
    logger.info(f"📁 File: {file_path}")

    request_body = {
        "snippet": {
            "title": viral_title,
            "description": description,
            "categoryId": str(category_id)
        },
        "status": {
            "privacyStatus": "public"
        }
    }
    

    if final_tags:
        request_body["snippet"]["tags"] = final_tags
    else:
        logger.warning("⚠️ No tags provided, skipping tags field.")
    print(json.dumps(request_body, indent=2))
    # Prepare media upload
    try:
        media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    except Exception as e:
        logger.error(f"❌ Error preparing video for upload: {e}")
        return

    try:
        request = youtube.videos().insert(
            part="snippet,status",
            body=request_body,
            media_body=media
        )
    except Exception as e:
        logger.error(f"❌ Failed to initiate upload: {e}")
        return

    # Upload loop with retries
    response = None
    retry = 0
    max_retries = 111111111  # reasonable max retries

    while response is None:
        try:
            logger.info("🚀 Uploading...")
            status, response = request.next_chunk()

            if status:
                logger.info(f"📶 Upload progress: {int(status.progress() * 100)}%")

            if response and 'id' in response:
                video_url = f"https://youtu.be/{response['id']}"
                logger.info(f"✅ Video uploaded successfully: {video_url}")
                return True
            else: 
                logger.error("❌ Upload failed: No video ID returned.")
                return False

        except HttpError as e:
            logger.warning(f"⚠️ HTTP Error {e.resp.status}: {e.content}")
            if e.resp.status == 400:
                logger.error("❌ Bad Request. Check your metadata (title, description, tags, categoryId).")
                return False
            if e.resp.status not in [500, 502, 503, 504]:
                return False

        except (socket.timeout, TimeoutError, requests.exceptions.ReadTimeout) as e:
            logger.warning(f"⏱️ Read timeout: {e}")

        except (BrokenPipeError, ConnectionResetError, OSError) as e:
            logger.warning(f"🔌 Connection error: {e}")

        except Exception as e:
            logger.error(f"❗ Unexpected error: {e}")
            return False

        retry += 1
        if retry > max_retries:
            logger.error("❌ Upload failed after maximum retries.")
            return False

        sleep_time = min(60, 2 ** retry)
        logger.info(f"🔁 Retrying in {sleep_time:.2f} seconds (attempt {retry}/{max_retries})...")
        time.sleep(sleep_time)

    # Upload thumbnail
    if thumbnail_path:
        try:
            logger.info("🖼️ Uploading thumbnail...")
            youtube.thumbnails().set(
                videoId=response["id"],
                media_body=MediaFileUpload(thumbnail_path)
            ).execute()
            logger.info("✅ Thumbnail uploaded successfully!")
        except Exception as e:
            logger.warning(f"❌ Thumbnail upload failed: {e}")



def remove_mapping_entry(video_path, mapping_file="file_topic_map.txt"):
    with open(mapping_file, "r") as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        if not line.strip().startswith(video_path):  # Skip the line matching the video
            new_lines.append(line)

    with open(mapping_file, "w") as f:
        f.writelines(new_lines)

    print(f"✅ Mapping entry for '{video_path}' removed from {mapping_file}")


# === MAIN DRIVER === #
if __name__ == "__main__":
        
    
    while True:
        
        status = get_upload_status()
        count = status["count"]

        if count <= 0:
            print("✅ Upload limit reached for today.")
            break



        # from googleapiclient.discovery import build
        # from googleapiclient.http import HttpRequest
        # import pickle
        # with open("/Users/uday/Downloads/VIDEOYT/token.pickle", "rb") as token_file:
        #     credentials = pickle.load(token_file)

        # youtube = build("youtube", "v3", credentials=credentials)





        # # Step 1: Get your channel ID - if you already know it, skip this step
        # channel_response = youtube.channels().list(
        #     part="contentDetails",
        #     mine=True  # gets your own channel details
        # ).execute()

        # uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        # # Step 2: Retrieve all video titles from the uploads playlist
        # video_titles = []
        # next_page_token = None

        # while True:
        #     playlist_response = youtube.playlistItems().list(
        #         part="snippet",
        #         playlistId=uploads_playlist_id,
        #         maxResults=50,
        #         pageToken=next_page_token
        #     ).execute()

        #     for item in playlist_response['items']:
        #         video_titles.append(item['snippet']['title'])

        #     next_page_token = playlist_response.get('nextPageToken')
        #     if not next_page_token:
        #         break

        # # Step 3: Save video titles to a text file and CSV file
        # with open("/Users/uday/Downloads/VIDEOYT/used_topics.txt", "w", encoding="utf-8") as txt_file:
        #     for title in video_titles:
        #         txt_file.write(title + "\n")



        # # print(f"Retrieved and saved {len(video_titles)} video titles.")

        # TOPIC_LOG_FILE = "used_topics.txt"

        # @retry_infinite(delay=5)
        # def generate_viral_wealth_topic():
        #     prompt = (
            
        #         "1) Personal Finance & Investing 2)Health & Fitness 3) Tech Tutorials and Reviews 4) Tech and AI Innovations 5) Personal Development & Motivation 6) how to and facts are our target niches on which we will create videos\n\n"
        #         "generate a YouTube video title from above niches randomly that is:\n"
        #         "- catchy SEO-optimized with high click-through potential\n"
        #         "dont include i as title should be ggeneral but specific but not include me\n"
        #         "i want ot generate infinite wealth by using this title to create my video and post on yt to earn money"
        #         "- Strictly a single-line output (only the video title)\n\n"
        #         "dont include year, The output must be only the video title. Keep it human, and audience-focused."
        #     )

        #     # prompt = (

        #     #     "generate a YouTube video title on which i cerate video and upload on yt\n"
        #     #     "- catchy SEO-optimized with high click-through potential\n"
        #     #     "dont include i as title should be ggeneral but specific but not include me\n"
        #     #     "i want ot generate infinite wealth by using this title to create my video and post on yt to earn money"
        #     #     "- Strictly a single-line output (only the video title)\n\n"
        #     #     "dont include year, The output must be only the video title. Keep it human, and audience-focused."
        #     # )


        #     # Load existing topics if file exists
        #     existing_topics = set()
        #     if os.path.exists(TOPIC_LOG_FILE):
        #         with open(TOPIC_LOG_FILE, 'r', encoding='utf-8') as file:
        #             existing_topics = set(line.strip().lower() for line in file if line.strip())

        #     # Loop until a unique topic is generated
        #     while True:
        #         response = generate_ai_response(prompt)
        #         new_topic = response.text.strip()

        #         if new_topic.lower() not in existing_topics:
        #             with open(TOPIC_LOG_FILE, 'a', encoding='utf-8') as file:
        #                 file.write(new_topic + '\n')
        #             return new_topic
                    
        #         else:
        #             print("Duplicate topic found, regenerating...")

        # # Example usage
        # user_topic = generate_viral_wealth_topic()
        # print("💡 Unique Viral Topic:", user_topic)

        


        print("🧹 Cleaning up project-specific temp files...")

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
        # user_topic="my car"
        # script = generate_youtube_script(user_topic)
        # print("\n📜 Generated Script:\n", script)
        # output_path, used_urls = create_video_from_script(script, user_topic)


        print("🎬 How would you like to create your video?")
        print("1. Based on a custom topic")
        print("2. Based on a trending topic")
        print("3. Using your own script")
        
        choice = input("👉 Enter 1, 2, or 3: ").strip()

        if choice == "1":
            user_topic = input("🎯 Enter your YouTube video topic: ").strip()
            script = generate_youtube_script(user_topic)
            viral_title = generate_viral_title(script)
            print(f"🔥 Viral Title: {viral_title}")
            output_path_created, used_urls = create_video_from_script(script, user_topic)
            print("\n📜 Generated Script:\n", script)

        elif choice == "2":
            # Ensure get_trending_topic is defined or imported correctly
            try:
                user_topic = get_trending_topic()
                print(f"🔥 Trending Topic: {user_topic}")
                script = generate_youtube_script(user_topic)
                viral_title = generate_viral_title(script)
                print(f"🔥 Viral Title: {viral_title}")
                output_path_created, used_urls = create_video_from_script(script, user_topic)
                print("\n📜 Generated Script:\n", script)
            except NameError:
                print("⚠️ The 'get_trending_topic' function is not defined in this block. Skipping trending topic option.")


        elif choice == "3":
            print("📝 Enter your script below. Press Enter twice to finish.")
            user_script_lines = []
            while True:
                line = input()
                if line.strip() == "":
                    break
                user_script_lines.append(line)
            script = "\n".join(user_script_lines)
            user_topic = get_topic_from_script(script)
            output_path_created, used_urls = create_video_from_script(script, user_topic)
            print("\n📜 Using Your Script:\n", script)
        else:
            print("❌ Invalid choice. Please run the program again and select 1, 2, or 3.")



        # # Folder containing MP3 files
        # folder_path = "/Users/uday/Downloads/VIDEOYT/audio/"
        # output_file = "/Users/uday/Downloads/VIDEOYT/audio/merged_audio.mp3"

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

        # # === Step 1: Convert merged_audio.mp3 to WAV ===
        # mp3_path = '/Users/uday/Downloads/VIDEOYT/audio/merged_audio.mp3'
        # output_wav = '/Users/uday/Downloads/VIDEOYT/Wav2Lip/merged_audio.wav'
        # mp3_to_wav(mp3_path, output_wav)

        # # === Step 2: Run OpenVoice CLI with subprocess (not using !python) ===
        # input_wav = "/Users/uday/Downloads/VIDEOYT/Wav2Lip/input.wav"
        # output_wav = "/Users/uday/Downloads/VIDEOYT/Wav2Lip/merged_audio_final.wav"
        # openvoice_command = [
        #     "python3", "-m", "openvoice_cli", "single",
        #     "-i", wav_path,
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

        # final_mp3 = "/Users/uday/Downloads/VIDEOYT/audio/merged_audio_final.mp3"
        # wav_to_mp3(output_wav, final_mp3) # === Step 3: Convert final WAV to MP3 ===
        
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
        output_path = os.path.join(folder_path, "merged_audio.mp3")
        combined.export(output_path, format="mp3")
        print(f"✅ Merged audio saved to: {output_path}")



        # === Step 1: Convert merged_audio.mp3 to WAV ===
        mp3_path = 'audio/merged_audio.mp3'
        output_wav = 'Wav2Lip/merged_audio.wav'
        mp3_to_wav(mp3_path, output_wav)



        # Define all paths

        temp_result = "temp/result.avi"
        output_final = "video_created/output_with_audio.mp4"

        checkpoint_path = "checkpoints/wav2lip.pth"
        face_video = "Wav2Lip/output_video (4).mp4"
        audio_path = "Wav2Lip/merged_audio.wav"
        output_video = "video_created/output_with_audio.mp4"

        run_wav2lip_inference(
            checkpoint_path="checkpoints/wav2lip.pth",
            face_video="Wav2Lip/output_video (4).mp4",
            audio_path="Wav2Lip/merged_audio.wav",
            output_video="video_created/output_with_audio.mp4",
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



        output_path= "video_created/final_video_01.mp4"
    

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_path = f"final_video/video_{timestamp}.mp4"


    

        command = [
            "ffmpeg", "-y",
            "-i", output_path,       # Main background video
            "-i", output_final,      # Avatar video with audio
            "-filter_complex",
            """
            [1:v]scale=280:400,setpts=PTS+10/TB[avatar];
            [0:v][avatar]overlay=10:H-h-10:enable='gte(t,10)'[outv];
            [1:a]adelay=10000|10000[a1];
            [0:a][a1]amix=inputs=2:duration=first:dropout_transition=2[aout]
            """,
            "-map", "[outv]",
            "-map", "[aout]",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "aac",  # or "libmp3lame"
            "-b:a", "320k",         # Increased bitrate for better audio quality
            "-ar", "48000",         # Set sample rate to 48 kHz
            "-ac", "2",  
            "-shortest",
            video_path
        ]

        # Run the command
        print("▶️ Merging video with avatar overlay and avatar audio...")
        subprocess.run(command)
        print(f"✅ Done! Final video saved to:\n{video_path}")


        # Example usage:
        mappings = [
            (video_path, user_topic)
          
        ]

        
        save_file_topic_mappings(mappings, "/Users/uday/Downloads/VIDEOYT/file_topic_map.txt")


        if video_path and used_urls:
            permanent_log_path = "all_video_used_urls.txt"  # Define your permanent log file

            with open(permanent_log_path, "a") as f:
                f.write(f"{os.path.basename(video_path)}\n")
                for url in sorted(used_urls):
                    f.write(url + "\n")
                f.write("\n")  # Blank line between entries

            print(f"📝 Appended used URLs to: {permanent_log_path}")
        else:
            print("❌ Could not create video or no URLs were used.")




        
        remove_video_entry(video_path)


        

        # Note: remove_video_entry function is already defined above at line 2007
        

        # Example Usage:
        # success = upload_video(video_path, user_topic, "/Users/uday/Downloads/VIDEOYT/final_thumbnail.jpg")
        # mapping_file = '/Users/uday/Downloads/VIDEOYT/file_topic_map.txt'
        # if success:
        #     try:
        #         os.remove(video_path)
        #         remove_video_entry(video_path)
        #         remove_mapping_entry(video_path, mapping_file)
        #         print(f"Deleted: {video_path}")
        #         count -= 1
        #         save_upload_status(count)
        #         print(f"✅ Upload complete. Remaining uploads today: {count}")

        #     except Exception as e:
        #         print(f"Failed to delete {video_path}: {e}")

       

 




