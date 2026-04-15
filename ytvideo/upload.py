import os
import socket
socket.setdefaulttimeout(600000)

# === Imports === #
import os
import requests
import nltk
import spacy
from gtts import gTTS
from datetime import datetime
from nltk.tokenize import sent_tokenize
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, ColorClip
import google.generativeai as genai
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
import ffmpeg
import os
import subprocess
from pydub import AudioSegment
import time
from functools import wraps
import google.generativeai as genai
import json
import os
import time
from datetime import datetime
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
import os

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

from collections import Counter
import numpy as np

import time

import subprocess
import os
import subprocess
from pydub import AudioSegment
import os
from googleapiclient.http import MediaFileUpload
import json

from googleapiclient.errors import HttpError
import pickle
from googleapiclient.discovery import build
import os
import shutil
from pathlib import Path
import re  
import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import google.generativeai as genai
from serpapi import GoogleSearch

import sys
import os
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
PEXELS_API_KEY = "DGhCtAB83klpCIv5yq5kMIb2zun7q67IvHJysvW4lInb0WVXaQF2xLMu"
SERP_API_KEY = "7f55bbfeff700d39fe9ee306af78102a69cf43267987037a77c5b111cbc48e98"
GEMINI_API_KEY = "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw"



genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name='models/gemini-2.0-flash-lite')

# Get trending topic from Google Trends using SerpAPI

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

UPLOAD_LIMIT = 100
JSON_FILE = "UPLOAD_STATUS.json"


import requests
from PIL import Image, ImageOps
from io import BytesIO
import os
from moviepy.editor import ImageClip, concatenate_videoclips

# Config
PEXELS_API_KEY = "DGhCtAB83klpCIv5yq5kMIb2zun7q67IvHJysvW4lInb0WVXaQF2xLMu" # Replace with your Pexels API key

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

import sys
sys.path.append('Wav2Lip')




import os
import time
import random
import json
from datetime import datetime
from pathlib import Path

class GeminiResponse:
    def __init__(self, text):
        self.text = text

FAILED_KEYS_FILE = "disabled_keys.json"

def load_disabled_keys():
    if not os.path.exists(FAILED_KEYS_FILE):
        return set()

    with open(FAILED_KEYS_FILE, "r") as f:
        data = json.load(f)
    today = datetime.now().strftime("%Y-%m-%d")
    return set(data.get(today, []))

def save_disabled_key(api_key):
    today = datetime.now().strftime("%Y-%m-%d")
    data = {}

    if os.path.exists(FAILED_KEYS_FILE):
        with open(FAILED_KEYS_FILE, "r") as f:
            data = json.load(f)

    if today not in data:
        data[today] = []

    if api_key not in data[today]:
        data[today].append(api_key)

    with open(FAILED_KEYS_FILE, "w") as f:
        json.dump(data, f, indent=2)

@retry_infinite(delay=5)
def generate_gemini_response(prompt, model_name=None, max_retries=5, wait_seconds=5):
    import google.generativeai as genai

    api_keys = [
        "AIzaSyA2Hj5phmEsqXBWqIGbZxQXxAzv129Zw1E",
        "AIzaSyDwTEr-7c2kP7doddq93aG9CpRmiz0Bv44",
        "AIzaSyAvsg_Oky2NJpD3uNnqMHF4xQJRBK3V9RY",
        "AIzaSyArpDip4G3DK3MiiN_mwE6CHpgDRtQD9TU",
        "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw",
        "AIzaSyCL46bkyk5tvCZNJCsAA3VSf-NC-g7BU3o"
    ]

    model_names = [
        "gemini-2.5-flash-preview-05-20",
        "gemini-2.5-pro-preview-05-06"
    ]

    disabled_keys_today = load_disabled_keys()

    for attempt in range(max_retries):
        available_keys = [k for k in api_keys if k not in disabled_keys_today]
        if not available_keys:
            raise RuntimeError("❌ All Gemini API keys are disabled for today.")

        key = random.choice(available_keys)
        model = model_name or random.choice(model_names)

        try:
            genai.configure(api_key=key)
            gemini = genai.GenerativeModel(model)
            print(f"✅ Success with model: {model}, key: {key[-6:]}")

            response = gemini.generate_content(prompt)
            return GeminiResponse(response.text.strip())

        except Exception as e:
            print(f"❌ Failed with key {key[-6:]} (Attempt {attempt + 1}): {e}")
            save_disabled_key(key)
            disabled_keys_today.add(key)
            time.sleep(wait_seconds)

    raise RuntimeError("❌ All Gemini API attempts failed.")





from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

api_keys = [
    "AIzaSyA2Hj5phmEsqXBWqIGbZxQXxAzv129Zw1E",
    "AIzaSyDwTEr-7c2kP7doddq93aG9CpRmiz0Bv44",
    "AIzaSyAvsg_Oky2NJpD3uNnqMHF4xQJRBK3V9RY",
    "AIzaSyArpDip4G3DK3MiiN_mwE6CHpgDRtQD9TU",
    "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw",
    "AIzaSyCL46bkyk5tvCZNJCsAA3VSf-NC-g7BU3o",
    "AIzaSyBFZS7DX_wDWvWjln22G3zN2XjORuMJV5o",
    "AIzaSyDiFNqDfLPHbK4JzciGHKvD9JijTqxIbtE"
]

# ✅ Utility: Resize image to 1080x1920 while keeping aspect ratio
def resize_to_1080x1920_stretch(image: Image.Image) -> Image.Image:
    target_size = (1920, 1080)
    return image.resize(target_size, Image.LANCZOS)  # Stretch to exact size

# ✅ Main function
def generate_thumbnail_with_multiple_keys(topic: str = "{topic}"):
    prompt = (
        f"Create a highly attractive and clickable YouTube thumbnail for a video titled '{topic}'. "
        "The thumbnail should have vibrant colors, bold and readable text, text as title on image, "
        "an expressive human face showing excitement or surprise, "
        "and relevant high-quality imagery that visually represents the topic clearly. "
        "Include dynamic backgrounds, subtle 3D effects, and modern design elements to grab attention. "
        "Make sure the thumbnail looks professional, clean, and irresistible to click. "
        "Thumbnail must be horizontal, ratio 16:9, 1920 width and 1080 height mind it."
    )

    response = None

    for key in api_keys:
        try:
            print(f"🔁 Trying API key ending with: {key[-6:]}")
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            break
        except Exception as e:
            print(f"❌ Failed with key ending in {key[-6:]}: {e}")
            continue

    if not response:
        print("❌ All API keys failed.")
        return None

    for part in response.candidates[0].content.parts:
        if part.text:
            print("Text:", part.text)
        elif part.inline_data:
            data = part.inline_data.data

            print("Raw data type:", type(data))
            print("Raw data preview:", data[:50])

            if isinstance(data, str):
                try:
                    image_data = base64.b64decode(data)
                except Exception as e:
                    print("Base64 decode error:", e)
                    image_data = None
            elif isinstance(data, (bytes, bytearray)):
                image_data = data
            else:
                print("Unknown data type in inline_data.data")
                image_data = None

            if image_data:
                try:
                    image = Image.open(BytesIO(image_data))
                    image = resize_to_1080x1920_stretch(image) # ✅ Resize to 1080x1920
                    thumbnail_path = 'resized_thumbnail_1080x1920.png'
                    image.save(thumbnail_path)
                    return thumbnail_path  # Return path for upload
                except Exception as e:
                    print("Error opening or resizing image:", e)
                    return None
            else:
                print("No valid image data found")
                return None





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



@retry_infinite(delay=5)
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

@retry_infinite(delay=5)
def generate_youtube_script(topic):
    prompt = f"""
    write youtube script for {topic} in narrating style without intro and outro, be concise and precise straight to the point only content of topic nothing else, dont use bold text to emphasize or any mark like **, i just want plain normal format , it should have just script and nothing else mind it, script   video should be engaging and valuable to viewers, focus on quality and engagement,  i want video to be viral and generate infinite money with it so make script that good. script must be in paragraph format(required dont forget it mind it) dont write in bold anything script should be in paragraph format against youtube script word plainly and nothing else in it as i have to fed it to my ai program so making it understand would be easy so just assign script plainly against youtube script word,  script length msut be of max 1 minute only or max 10-15 sentences only and not more than this criteria, script msut be creative and engaging mind it i need it okay.
    """
    response = gemini_model.generate_content(prompt)
    full_text = response.text.strip()

    # Extract only the part after the phrase 'youtube script'
    if 'youtube script' in full_text.lower():
        # Find the first occurrence regardless of casing
        index = full_text.lower().index('youtube script')
        script = full_text[index + len('youtube script'):].strip()
        return script
    else:
        return full_text  # fallback if 'youtube script' not found

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
  
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

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

# === Fallback Search Queries (3) === #

@retry_infinite(delay=5)
def fallback_search_query(sentence, user_topic):
    prompt = f"Give a short search query to find a stock video for: '{sentence}', just plainly text query not in bold, give 1  query search term only, and nothing else,  must relate to topic so that video clips are used which are relevent to topic pls kindly create search terms which are related to topic and current part dont get offshore, user topic is {user_topic}"
    response = gemini_model.generate_content(prompt)
    return [q.strip() for q in response.text.strip().split(",")]

API_KEY = '50331047-e9be991568dc6ca136acd003b'  # Replace with your actual Pixabay API key

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



import requests

import requests
import json
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



import requests



import requests
# Replace with your actual Pixabay API key

import os

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
    queries = fallback_search_query(sentence, user_topic)  # Single query expected in your case

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




from moviepy.editor import VideoFileClip, concatenate_videoclips, ColorClip, vfx
@retry_infinite(delay=5)
def create_scene(text, idx, used_video_urls, user_topic):
    print(f"\n🎬 Creating Scene {idx + 1}")
    
    video_clips_data = find_one_video_clips(text, used_video_urls, user_topic, max_clips=15)

    if not video_clips_data:
        print("❌ No clips found.")
        return None, []

    try:
        audio_path = f"audio/scene_{idx}.mp3"
        audio_clip = generate_audio(text, audio_path)
        audio_duration = audio_clip.duration
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        return None, []

    clips = []
    global new_used_urls
    new_used_urls = []
    
    for i, clip_data in enumerate(video_clips_data):
        try:
            video_url = clip_data["video_files"][0]["link"]
            if video_url in used_video_urls:
                continue

            source = clip_data.get("source", "unknown")
            video_path = f"video_creation/scene_{idx}_{i}.mp4"

            if source == "pixabay":
                download_videos1(video_url, video_path)
            else:
                download_video(video_url, video_path)

            clip = VideoFileClip(video_path).without_audio()

            # Resize and crop
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

            clips.append(clip.set_fps(30))
            new_used_urls.append(video_url)

            if sum(c.duration for c in clips) >= audio_duration:
                break

        except Exception as e:
            print(f"⚠️ Error processing {clip_data.get('video_files')[0]['link']}: {e}")
            continue

    if not clips:
        print("❌ All clip processing failed.")
        return None, []

    # Concatenate and match audio length
    final_video = concatenate_videoclips(clips, method="compose")
    if final_video.duration > audio_duration:
        final_video = final_video.subclip(0, audio_duration)
    else:
        speed_factor = final_video.duration / audio_duration
        final_video = final_video.fx(vfx.speedx, factor=speed_factor).set_duration(audio_duration)

    used_video_urls.update(new_used_urls)

    from moviepy.editor import TextClip, CompositeVideoClip
    subtitle = (
        TextClip(text, fontsize=60, color="white", font="Arial-Bold", size=final_video.size, method="caption")
        .set_position(("center", "bottom"))
        .set_duration(audio_duration)
        .fadein(1)
    )

    final_clip = CompositeVideoClip([final_video, subtitle])
    final_clip = final_clip.set_duration(audio_duration).set_audio(audio_clip)

    return final_clip, new_used_urls







import subprocess



import os
import subprocess
from datetime import datetime
from nltk.tokenize import sent_tokenize
from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

from moviepy.editor import VideoFileClip, concatenate_videoclips, CompositeAudioClip, AudioFileClip


from moviepy.editor import AudioFileClip, CompositeAudioClip, ImageClip, concatenate_videoclips

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
    from nltk.tokenize import sent_tokenize
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip

    sentences = sent_tokenize(script)
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
    scene_clips.append(fast_cut_clip)  # mute if you want silent here, or keep audio by removing .without_audio()

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
    output_path = os.path.join(output_dir, "final_video_01.mp4")

    # Background music
    from moviepy.audio.fx.all import audio_loop
    # Background music
    bg_music_raw = AudioFileClip("/Users/uday/Downloads/VIDEOYT/Cybernetic Dreams.mp3").volumex(0.03)
    bg_music_looped = audio_loop(bg_music_raw, duration=final_clip.duration).set_start(5)

    # Mix with existing audio (tick sounds, etc.)
    if final_clip.audio:
        final_audio = CompositeAudioClip([final_clip.audio.set_duration(final_clip.duration), bg_music_looped])
    else:
        final_audio = bg_music_looped


    final_clip = final_clip.set_audio(final_audio)

    # Write final video
    final_clip.write_videofile(
        output_path,
        codec="libx264",            # Video codec
        audio_codec="libmp3lame",   # Ensures .mp3-compatible audio encoding
        fps=30,
        audio=True,
        preset="ultrafast",
        threads=8
    )

    print(f"✅ Final video created at: {output_path}")

    # Return output_path and all_used_urls for use elsewhere
    return output_path







# @retry_infinite(delay=5)
# def generate_youtube_title(topic):
#     prompt = f"""
#     Create a highly clickable, viral YouTube video title for the topic: "{topic}".
#     Do not include any extra explanation or formatting. Just return the title only. it should be seo optimised mind it
#     """
#     response = gemini_model.generate_content(prompt)
#     return response.text.strip()

@retry_infinite(delay=5)
def generate_youtube_description(topic):
    prompt = f"""
    Write a compelling 21 sentences each in new line, YouTube video description for the topic: "{topic}".
    It should be keyword-rich and increase viewer interest.
    Do not include any formatting or labels like 'Description:'. Just return the description text only. it should be seo optimised mind it. include some like 8-10 seo optimised hastags also at end.
    """
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

@retry_infinite(delay=5)
def generate_youtube_tags(topic):
    prompt = f"""
    Generate a list of 21 relevant, high-SEO YouTube tags (comma-separated) for the topic: "{topic}".
    Only return the tags in a list format separated by commas. Do not include extra explanation or formatting. it should be seo optimised mind it, just return list of tags comma separted thats it
    """
    response = gemini_model.generate_content(prompt)
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

    response = gemini_model.generate_content(prompt)
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


    response = gemini_model.generate_content(prompt)
    return response.text


def extract_category_id(text):
    match = re.search(r'Category ID:\s*(\d+)', text)
    return int(match.group(1)) if match else 27  # Default to Education if not found








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

import time
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

import re

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
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

import json
import time
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import random
import time
import socket
import logging
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import requests

logger = logging.getLogger(__name__)

import random
import time
import socket
import requests
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


import os
from googleapiclient.http import MediaFileUpload

# def get_chunk_size(file_path):
#     file_size = os.path.getsize(file_path)  # size in bytes
#     mb = 1024 * 1024
    
#     if file_size < 50 * mb:
#         return 50*mb
#     elif file_size < 200 * mb:
#         return 100*mb
#     else:
#         return 400*mb
from googleapiclient.http import MediaFileUpload


import os
import pickle
from googleapiclient.discovery import build

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

def load_video_topic_mappings(filepath):
    """
    Loads video path and topic mappings from a text file.
    Format per line: /path/to/video.mp4 | Topic
    Returns: List of tuples (video_path, topic)
    """
    mappings = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' not in line:
                continue
            video_path, topic = map(str.strip, line.split('|', 1))
            mappings.append((video_path, topic))
    return mappings

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



def get_urls_for_video(video_name, log_file="all_video_used_urls.txt"):
    urls = []
    with open(log_file, "r") as f:
        lines = f.readlines()

    collecting = False
    for line in lines:
        line = line.strip()
        if not line:
            collecting = False  # Stop when reaching a blank line
            continue
        if line == video_name:
            urls = []           # Clear in case video name appears multiple times
            collecting = True
            continue
        if collecting:
            urls.append(line)

    return urls





def remove_video_entry(video_name, log_file="all_video_used_urls.txt"):
    with open(log_file, "r") as f:
        lines = f.readlines()

    new_lines = []
    skip = False

    for line in lines:
        if line.strip() == video_name:
            skip = True  # Start skipping this entry
            continue
        if skip:
            if line.strip() == "":  # End of this entry
                skip = False
            continue
        new_lines.append(line)

    with open(log_file, "w") as f:
        f.writelines(new_lines)

    print(f"✅ Entry for '{video_name}' removed from {log_file}")

# import google.generativeai as genai

# # Set your Gemini API key
# genai.configure(api_key="AIzaSyA2Hj5phmEsqXBWqIGbZxQXxAzv129Zw1E")

def generate_title_with_hashtags(topic: str) -> str:
    prompt = (
        f"Generate 3–5 trending, viral, SEO-optimized hashtags relevant to the topic: \"{topic}\" "
        f"in the personal finance and investing niche. Output only hashtags in one line, no explanation.  mind it it should bes seo optimised"
    )
    
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")

    hashtags = response.text.strip().replace("\n", " ")
    final = f"{topic} {hashtags}"

    # Truncate safely to max 90 chars without cutting words
    if len(final) > 80:
        truncated = final[:80]
        # Cut back to last space to avoid breaking a word/hashtag
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]
        return truncated
    return final




def generate_description_with_scene_links(base_description, feedback_link, video_path):
    description = sanitize_text(base_description)
    description += f"\n\n📢 We'd love your feedback! Share your thoughts here 👉 {feedback_link}\n\n"

    # Try to load scene video URLs
    urls = get_urls_for_video(video_path, log_file="all_video_used_urls.txt")

    # Only add scene video sources if URLs are found
    if urls:
        description += "🎥 Scene Video Sources:\n"
        for i, url in urls:
            description += f"Scene {i} video: {url}\n"

    # Add music credit
    description += (
        "\nCinematic Technology | Cybernetic Dreams by Alex-Productions\n"
        "https://youtu.be/NDYRjTti5Bw\n"
        "Music promoted by https://onsound.eu/\n"
    )

    return description




@retry_infinite(delay=5)
def upload_video(file_path, topic):

    thumbnail_path= generate_thumbnail_with_multiple_keys(topic)
    
    feedback_link = "https://forms.gle/NLQ3gmdrsNU7DKev6"  # Replace with your actual form link
    description=generate_youtube_description(topic)
    

    description=generate_description_with_scene_links(description, feedback_link)
    
    # Generate and clean tags
    tags = trim_tags(generate_youtube_tags(topic))
    final_tags = clean_tags_with_gemini(tags)
    final_tags = sanitize_tags(final_tags)
    # Category ID resolution
    category_info = get_category_id_from_gemini(topic)
    category_id = extract_category_id(category_info)


    logger.info("📦 Preparing video upload...")
    logger.info(f"🎬 Title: {topic}")
    logger.info(f"📝 Description: {description}")
    logger.info(f"🏷️ Tags: {final_tags}")
    logger.info(f"📁 File: {file_path}")

    request_body = {
        "snippet": {
            "title": topic,
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
    import json
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

                if thumbnail_path:
                    try:
                        logger.info("🖼️ Uploading thumbnail...")
                        youtube.thumbnails().set(
                            videoId=response["id"],
                            media_body=MediaFileUpload(thumbnail_path, mimetype='image/png')
                        ).execute()
                        logger.info("✅ Thumbnail uploaded successfully!")
                    except Exception as e:
                        logger.warning(f"❌ Thumbnail upload failed: {e}")


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


def load_video_topic_mappings(filepath):
    """
    Loads video path and topic mappings from a text file.
    Format per line: /path/to/video.mp4 | Topic
    Returns: List of tuples (video_path, topic)
    """
    mappings = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if '|' not in line:
                continue
            video_path, topic = map(str.strip, line.split('|', 1))
            mappings.append((video_path, topic))
    return mappings

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

if __name__ == "__main__":

    import os
    import time

    mapping_file = '/Users/uday/Downloads/VIDEOYT/file_topic_map.txt'

    while True:
        status = get_upload_status()
        count = status["count"]

        if count <= 0:
            print("✅ Upload limit reached for today.")
            break

        mappings = load_video_topic_mappings(mapping_file)

        if not mappings:
            print("⚠️ Mapping file is empty. Sleeping for 5 minutes...")
            time.sleep(300)
            continue

        for video_path, topic in mappings:
            if count <= 0:
                print("✅ Daily upload quota reached. Stopping.")
                break

            youtube, token_path = get_available_token()
            if not youtube:
                print("❌ All tokens failed or have reached the limit.")
                break

            if not os.path.exists(video_path):
                print(f"❌ Video file not found: {video_path}")
                continue  # Don't sleep, just skip to next video

            print(f"\n📤 Uploading Video: {video_path}")
            print(f"📝 Topic: {topic}")

            success = upload_video(video_path, topic)

            if success:
                try:
                    os.remove(video_path)
                    remove_video_entry(video_path)
                    remove_mapping_entry(video_path, mapping_file)
                    print(f"🗑️ Deleted: {video_path}")
                    count -= 1
                    save_upload_status(count)
                    print(f"✅ Upload complete. Remaining uploads today: {count}")
                except Exception as e:
                    print(f"⚠️ Failed to delete {video_path}: {e}")

        print("⏳ Sleeping 5 minute before checking mapping file again...")
        time.sleep(300)

