

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
import moviepy.editor
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx

import os

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

from collections import Counter
import numpy as np

import time
import socket
# socket.setdefaulttimeout(6000) # 🏛️ [VANTIX SYNC] Neutralized
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
def generate_gemini_response(prompt, model_name=None, max_retries=7, wait_seconds=5):
    import google.generativeai as genai

    api_keys = [
        "AIzaSyA2Hj5phmEsqXBWqIGbZxQXxAzv129Zw1E",
        "AIzaSyDwTEr-7c2kP7doddq93aG9CpRmiz0Bv44",
        "AIzaSyAvsg_Oky2NJpD3uNnqMHF4xQJRBK3V9RY",
        "AIzaSyArpDip4G3DK3MiiN_mwE6CHpgDRtQD9TU",
        "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw",
        "AIzaSyCL46bkyk5tvCZNJCsAA3VSf-NC-g7BU3o",
        "AIzaSyD4Pv1UiLc7fsA7InuOvhhWxVkMgGAO8dI",
        "AIzaSyCeBdgElggdHYaHnf4N3z0RlPeROZ5LzEU"
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


# Get trending topic from Google Trends using SerpAPI



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
    return response.text.strip()




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
    prompt = f"Give a short search query to find a stock video for: '{sentence}', just plainly text query not in bold, give 1  query search term only, and nothing else,  must relate to topic so that video clips are used which are relevent to topic pls kindly create search query which is related to topic and current part dont get offshore, user topic is {user_topic}, search query msut be such tthat it wil be most probable available or found in stock video clips website like pexels or pixabay, search query must be erlatable to sentence and user topic not just random thing okay mind it iam very serious about it"
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    return [q.strip() for q in response.text.strip().split(",")]

API_KEY = '50331047-e9be991568dc6ca136acd003b'  # Replace with your actual Pixabay API key

@retry_infinite(delay=5)
def search_pixabay_videos(query, per_page=200, max_results=3):  # lowered per_page for quicker tests
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
def search_pexels_video(query, per_page=80, target_width=1080, target_height=1920, tolerance=200, max_clips=1):
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
def find_one_video_clips(sentence, used_video_urls, user_topic, max_clips=1):
    print(f"🔍 Searching multiple clips for: {sentence}")
    queries = fallback_search_query(sentence, user_topic)  # Single query expected in your case

    def is_valid(clip_url, width, height):
        return (
            abs(width - 1080) <= 200 and
            abs(height - 1920) <= 200 and
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

        # collected += process_pixabay(query)
        # if len(collected) >= max_clips:
        #     return collected[:max_clips]

        # Try keywords from query if not enough
        keywords = extract_keywords(query)
        for keyword in keywords:
            collected += process_pexels(keyword)
            if len(collected) >= max_clips:
                return collected[:max_clips]

            # collected += process_pixabay(keyword)
            # if len(collected) >= max_clips:
            #     return collected[:max_clips]

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



from moviepy.editor import TextClip, CompositeVideoClip
from moviepy.video.fx.all import fadein, fadeout, resize

import numpy as np
import random
from moviepy.editor import VideoClip, CompositeVideoClip, TextClip
from moviepy.video.fx.all import fadein, fadeout, resize
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
    import colorsys
    rgb = np.array([colorsys.hsv_to_rgb(h_, s, v) for h_ in h.flatten()])  # (N,3)
    return rgb.reshape(h.shape + (3,))

def random_bright_color():
    # Return bright HSV (random hue, full saturation & value)
    h = random.random()
    s = 1.0
    v = 1.0
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return np.array([r, g, b]) * 255

def create_word_gradient_clip(word, duration, font, fontsize, video_size):
    text_clip = TextClip(word, fontsize=fontsize, font=font, color="white", method="label")

    text_mask = text_clip.to_mask()
    w, h = text_mask.size

    left_color = random_bright_color()
    right_color = random_bright_color()
    direction = random.choice(["diagonal_tl_br", "diagonal_br_tl"])

    def make_frame(t):
        progress = (t / duration) % 1
        offset = progress
        gradient = create_gradient_frame(w, h, offset, direction, left_color, right_color)
        mask_frame = text_mask.get_frame(t)
        colored_frame = (gradient * mask_frame[:, :, None]).astype(np.uint8)
        return colored_frame

    return VideoClip(make_frame, duration=duration).set_position("center").set_mask(text_mask)


def create_word_by_word_subtitles(
    word_segments,
    video_size=(1080, 1920),
    font="/Users/uday/Downloads/VIDEOYT/Anton-Regular.ttf",
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


import spacy
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


import os
import base64
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def generate_tts_audio(text, filename="output.mp3", json_key_path="my-project-tts-461911-dbd39de52028.json",
                       voice_name="en-US-Studio-O", speaking_rate=1.4):
    # Set env var for credentials
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key_path
    
    # Load credentials and refresh token
    credentials = service_account.Credentials.from_service_account_file(
        json_key_path,
        scopes=["https://www.googleapis.com/auth/cloud-platform"]
    )
    credentials.refresh(Request())
    access_token = credentials.token

    # API endpoint & headers
    url = "https://texttospeech.googleapis.com/v1/text:synthesize"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # JSON payload
    payload = {
        "input": {
            "text": text
        },
        "voice": {
            "languageCode": "en-US",
            "name": voice_name
        },
        "audioConfig": {
            "audioEncoding": "MP3",
            "speakingRate": speaking_rate
        }
    }

    # Send POST request
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        audio_content = response.json()["audioContent"]
        with open(filename, "wb") as out:
            out.write(base64.b64decode(audio_content))
        print(f"✅ Audio saved to {filename}")
    else:
        print(f"❌ Error {response.status_code}: {response.text}")

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

from moviepy.editor import (
    VideoFileClip, concatenate_videoclips, CompositeVideoClip, AudioFileClip, ImageClip
)
@retry_infinite(delay=5)
def create_scene(text, idx, used_video_urls, user_topic):
    print(f"\n🎬 Creating Scene {idx + 1}")

    # 1) Fetch candidate clips
    video_clips_data = find_one_video_clips(text, used_video_urls, user_topic, max_clips=15)
    if not video_clips_data:
        print("❌ No clips found.")
        return None, []

    # 2) Generate TTS audio for this sentence
    try:
        audio_path = f"audio/scene_{idx}.mp3"
        generate_tts_audio(text, audio_path)
        update_character_count(text)
        audio_clip = AudioFileClip(audio_path)
        audio_duration = audio_clip.duration
        audio_clip.close()
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        return None, []

    new_used_urls = set()
    final_video = None

    # Function to resize & crop video to 1080x1920 portrait
    def resize_crop(clip):
        target_aspect = 1080 / 1920
        actual_aspect = clip.w / clip.h
        if abs(actual_aspect - target_aspect) < 0.01:
            return clip.resize((1080, 1920))
        elif actual_aspect > target_aspect:
            # Wider → crop width
            clip = clip.resize(height=1920)
            x_center = clip.w / 2
            return clip.crop(x1=x_center - 540, x2=x_center + 540, y1=0, y2=1920)
        else:
            # Taller → crop height
            clip = clip.resize(width=1080)
            y_center = clip.h / 2
            return clip.crop(x1=0, x2=1080, y1=y_center - 960, y2=y_center + 960)

    # 3a) Try to find a single clip long enough for the audio
    for clip_data in video_clips_data:
        video_url = clip_data["video_files"][0]["link"]
        if video_url in used_video_urls or video_url in new_used_urls:
            continue

        tmp_path = f"video_creation/scene_{idx}_temp.mp4"
        try:
            if clip_data.get("source", "unknown") == "pixabay":
                download_videos1(video_url, tmp_path)
            else:
                download_video(video_url, tmp_path)

            raw_clip = VideoFileClip(tmp_path).without_audio()
            clip = resize_crop(raw_clip)

            # Subclip to exact audio duration, set fps and duration explicitly
            final_video = clip.subclip(0, min(audio_duration, clip.duration)) \
                              .set_fps(30) \
                              .set_duration(audio_duration)

            raw_clip.close()
            new_used_urls.add(video_url)
            break
        except Exception as e:
            print(f"❌ Failed processing clip {video_url}: {e}")
            try:
                raw_clip.close()
            except:
                pass
            continue
    else:
        # 3b) No single clip long enough, concatenate multiple shorter clips
        collected_clips = []
        total_collected = 0.0

        for clip_data in video_clips_data:
            video_url = clip_data["video_files"][0]["link"]
            if video_url in used_video_urls or video_url in new_used_urls:
                continue

            tmp_path = f"video_creation/scene_{idx}_{len(collected_clips)}.mp4"
            try:
                if clip_data.get("source", "unknown") == "pixabay":
                    download_videos1(video_url, tmp_path)
                else:
                    download_video(video_url, tmp_path)

                raw_clip = VideoFileClip(tmp_path).without_audio()
                clip = resize_crop(raw_clip).set_fps(30)
                collected_clips.append(clip)
                new_used_urls.add(video_url)
                total_collected += clip.duration
                raw_clip.close()
            except Exception as e:
                print(f"❌ Failed processing clip {video_url}: {e}")
                try:
                    raw_clip.close()
                except:
                    pass
                continue

            if total_collected >= audio_duration:
                break

        if not collected_clips:
            print("❌ All clip processing failed.")
            return None, []

        interim = concatenate_videoclips(collected_clips, method="compose")

        if interim.duration >= audio_duration:
            final_video = interim.subclip(0, audio_duration).set_fps(30).set_duration(audio_duration)
        else:
            # Freeze last frame to pad duration
            current_dur = interim.duration
            freeze_needed = audio_duration - current_dur
            last_frame_img = interim.get_frame(current_dur - 1e-3)
            freeze_clip = ImageClip(last_frame_img).set_duration(freeze_needed).set_fps(30).set_size(interim.size)
            final_video = concatenate_videoclips([interim, freeze_clip], method="compose") \
                          .set_duration(audio_duration).set_fps(30)

    # 4) Generate word-level subtitles using WhisperX if available
    subtitle = None
    try:
        import whisperx
        device = "cpu"
        model = whisperx.load_model("tiny.en", device=device, compute_type="float32")
        result = model.transcribe(audio_path)
        align_model, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        aligned_result = whisperx.align(result["segments"], align_model, metadata, audio_path, device)
        word_segments = aligned_result["word_segments"]
        subtitle = create_word_by_word_subtitles(word_segments, video_size=(1080, 1920))
    except Exception as e:
        print(f"❌ WhisperX subtitle generation failed: {e}")

    # 5) Compose final scene with subtitles if any
    if subtitle:
        final_scene = CompositeVideoClip([final_video, subtitle])
    else:
        final_scene = final_video

    final_scene = final_scene.set_duration(audio_duration)

    # Add new used urls to the global set
    used_video_urls.update(new_used_urls)

    return final_scene, list(new_used_urls)







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
def create_video_from_script(script, user_topic):
    import os
    import subprocess
    import tempfile
    from nltk.tokenize import sent_tokenize
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
    from moviepy.audio.fx.all import audio_loop
    from datetime import datetime

    def save_clip_to_tempfile(clip, suffix="", pad_duration=1):
        clip = clip.set_fps(30)

        temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=f"{suffix}.mp4").name
        padded_path = tempfile.NamedTemporaryFile(delete=False, suffix=f"{suffix}_padded.mp4").name

        # Save normal clip first
        clip.write_videofile(
            temp_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="ultrafast",
            threads=8,
            audio=True,
            logger=None
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

    import random
    import tempfile
    import subprocess
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

        # Final rename to output
        os.rename(current_input, output_path)


    # ---- Main logic starts ----
    sentences = sent_tokenize(script)
    used_video_urls = set()
    scene_clips = []
    all_used_urls = set()

    output_dir = "video_created"
    os.makedirs(output_dir, exist_ok=True)

    print(f"🎞️ Total scenes to generate: {len(sentences)}")
 
    for idx, sentence in enumerate(sentences):
        print(f"\n🔹 Processing Scene {idx + 1}/{len(sentences)}: {sentence}")
        scene_clip, scene_urls = create_scene(sentence, idx, used_video_urls, user_topic)

        if scene_clip is None or not hasattr(scene_clip, 'duration'):
            print(f"⚠️ Skipping Scene {idx + 1} due to invalid clip.")
            continue

        scene_clips.append(scene_clip)
        all_used_urls.update(scene_urls)

    print("\n✅ All used URLs:", all_used_urls)

    if not scene_clips:
        print("❌ No valid scenes generated. Cannot proceed.")
        return None, None

    # Resize and set fps consistently
    scene_clips = [clip.resize((1080, 1920)).set_fps(30) for clip in scene_clips]

    try:
        # Add padding to each clip before transitions
        transition_duration = 0.05
        temp_files = [
            save_clip_to_tempfile(c, suffix=f"_scene{i}", pad_duration=transition_duration)
            for i, c in enumerate(scene_clips)
        ]

        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

        # Apply transitions with the padded clips
        ffmpeg_chain_random_transitions(temp_files, output_temp, transition_duration)

        final_clip = VideoFileClip(output_temp)

        for f in temp_files:
            try:
                os.remove(f)
            except:
                pass

    except Exception as e:
        print(f"❌ Failed to apply transitions: {e}")
        return None, None

    # Add background music
    try:
        bg_music_raw = AudioFileClip("/Users/uday/Downloads/VIDEOYT/Cybernetic Dreams.mp3").volumex(0.08)
        bg_music_looped = audio_loop(bg_music_raw, duration=final_clip.duration).set_start(0)

        if final_clip.audio:
            final_audio = CompositeAudioClip([
                final_clip.audio.set_duration(final_clip.duration),
                bg_music_looped
            ])
        else:
            final_audio = bg_music_looped

        final_clip = final_clip.set_audio(final_audio)

    except Exception as e:
        print(f"⚠️ Background music could not be applied: {e}")

    # Export final video
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_filename = f"video_{timestamp}.mp4"
        output_path = os.path.join(output_dir, output_filename)

        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            preset="ultrafast",
            threads=8
        )
        print(f"\n✅ Final video created at: {output_path}")
        return output_path, all_used_urls

    except Exception as e:
        print(f"❌ Final export failed: {e}")
        return None, None


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
    write description first lines hooky so that user read and jut tendto click my video and want to watch full video write descriptrion like that and frist few lines nust be highest hooky attractive that user tend to click my video mind it write that lebel of firaast few lines of description and following whole decription like that and also seo optimised mind it create like this.
    """
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    return response.text.strip()

@retry_infinite(delay=5)
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

    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
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


    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    return response.text


def extract_category_id(text):
    match = re.search(r'Category ID:\s*(\d+)', text)
    return int(match.group(1)) if match else 27  # Default to Education if not found






# --- Functions ---
# --- New Function to Generate Relevant Search Term ---
@retry_infinite(delay=5)
def generate_search_term(topic):
    prompt = f"Given the YouTube video topic '{topic}', suggest a short, relevant visual keyword or phrase for finding an image background. Limit to 3-5 words, no punctuation, just a plain image search phrase only one line and nothing else : keywords or phrase  just onloy that and nothing else mind it."
    response = generate_gemini_response(prompt, model_name="gemini-2.5-flash-preview-05-20")
    return response.text.strip()

@retry_infinite(delay=5)
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

from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

def get_readable_color(rgb_color):
    # Determine if black or white will be more readable on the given background color
    r, g, b = rgb_color
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (0, 0, 0) if luminance > 186 else (255, 255, 255)
from PIL import Image, ImageDraw, ImageFont
import os

def create_thumbnail(topic):
    print("🎯 Generating title...")
    title = generate_title_from_topic1(topic)
    print("📝 Title:", title)

    print("📥 Loading and resizing image...")
    input_img_path = "/Users/uday/Downloads/VIDEOYT/clara explains.png"
    img = Image.open(input_img_path).convert("RGB")
    img = resize_and_crop_to_1080x1920(img)

    print("🎨 Analyzing dominant color...")
    dominant_color = get_dominant_color(img)
    text_color = get_readable_color(dominant_color)
    border_color = get_readable_color(text_color)
    print(f"🎨 Dominant: {dominant_color}, Text: {text_color}, Border: {border_color}")

    print("🖋️ Adding title to image...")
    draw = ImageDraw.Draw(img)
    
    # Ensure font path exists or use a fallback
    font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font not found at {font_path}")
    font = ImageFont.truetype(font_path, 80)

    # Calculate text position
    bbox = draw.textbbox((0, 0), title, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (1920 - text_w) // 2
    y = 1080 - text_h - 50

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





# @retry_infinite(delay=5)
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

        @retry_infinite(delay=5)
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

        import os

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

        # === Step 1: Convert merged_audio.mp3 to WAV ===
        # mp3_path = '/Users/uday/Downloads/VIDEOYT/audio/merged_audio.mp3'
        # output_wav = '/Users/uday/Downloads/VIDEOYT/Wav2Lip/merged_audio.wav'
        # mp3_to_wav(mp3_path, output_wav)

   
        
        # python3 -m pip install -r /Users/uday/Downloads/VIDEOYT/Wav2Lip/requirements.txt
        # python3 -m pip uninstall torchvision -y
        # python3 -m pip uninstall batch-face -y # remove incorrect version if any
        # !python3 -m pip install batch-face==1.5.2  # latest stable batch-face version
        # !python3 -m pip install torchvision==0.15.1  # matches torch 2.7.0

        


        from pydub import AudioSegment
        import os
        import ffmpeg

        from pydub import AudioSegment
        import os
        import re

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



        import os
        import subprocess

        # Define all paths

        temp_result = "temp/result.avi"
        output_final = "video_created/output_with_audio.mp4"
        output_wav="/Users/uday/Downloads/VIDEOYT/Wav2Lip/merged_audio.wav"
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

        import subprocess


        

        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"/Users/uday/Downloads/VIDEOYT/final_video/final_video_{timestamp}.mp4"




        import subprocess

        import subprocess

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



