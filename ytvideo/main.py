import socket
socket.setdefaulttimeout(6000)

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
gemini_model = genai.GenerativeModel(model_name='models/gemini-2.5-flash-preview-05-20')

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
    write youtube script for {topic} in narrating style without intro and outro, be concise and precise straight to the point only content of topic nothing else , dont use bold text to emphasize or any mark like **, i just want plain normal format , it should have just script and nothing else mind it, video should be engaging and valuable to viewers, focus on quality and engagement,  i want video to be viral and generate infinite money with it so make script that good. script must be in paragraph format(required dont forget it mind it) dont write in bold anything script should be in paragraph format against youtube script word plainly and nothing else in it as i have to fed it to my ai program so making it understand would be easy so just assign script plainly against youtube script word,  script length msut be of max 2 minute only or max 21 sentences only and not more than this criteria, script msut be creative and engaging mind it i need it okay.
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



from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    ImageClip
)

from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    ImageClip
)

def create_scene(text, idx, used_video_urls, user_topic):
    print(f"\n🎬 Creating Scene {idx + 1}")

    # 1) Fetch up to 15 candidate clips
    video_clips_data = find_one_video_clips(text, used_video_urls, user_topic, max_clips=15)
    if not video_clips_data:
        print("❌ No clips found.")
        return None, []

    # 2) Generate TTS audio for this sentence
    try:
        audio_path = f"audio/scene_{idx}.mp3"
        audio_clip = generate_audio(text, audio_path)
        audio_duration = audio_clip.duration
    except Exception as e:
        print(f"❌ Audio generation failed: {e}")
        return None, []

    new_used_urls = []
    final_video = None

    # 3a) Attempt to find a single video ≥ audio_duration
    for clip_data in video_clips_data:
        video_url = clip_data["video_files"][0]["link"]
        if video_url in used_video_urls:
            continue

        tmp_path = f"video_creation/scene_{idx}_temp.mp4"
        if clip_data.get("source", "unknown") == "pixabay":
            download_videos1(video_url, tmp_path)
        else:
            download_video(video_url, tmp_path)

        raw_clip = VideoFileClip(tmp_path).without_audio()

        if raw_clip.duration >= audio_duration:
            # Resize & crop to 1920×1080
            target_aspect = 1920 / 1080
            actual_aspect = raw_clip.w / raw_clip.h
            if abs(actual_aspect - target_aspect) < 0.01:
                clip = raw_clip.resize((1920, 1080))
            elif actual_aspect > target_aspect:
                clip = raw_clip.resize(height=1080)
                x_center = clip.w / 2
                clip = clip.crop(x1=x_center - 960, x2=x_center + 960, y1=0, y2=1080)
            else:
                clip = raw_clip.resize(width=1920)
                y_center = clip.h / 2
                clip = clip.crop(x1=0, x2=1920, y1=y_center - 540, y2=y_center + 540)

            # Subclip exactly to the audio_duration
            final_video = (
                clip
                .subclip(0, audio_duration)
                .set_fps(30)
                .set_duration(audio_duration)
            )

            used_video_urls.add(video_url)
            new_used_urls.append(video_url)
            raw_clip.close()
            break
        else:
            raw_clip.close()

    # 3b) If no single clip is long enough, concatenate shorter clips
    if final_video is None:
        collected_clips = []
        total_collected = 0.0

        for clip_data in video_clips_data:
            video_url = clip_data["video_files"][0]["link"]
            if video_url in used_video_urls:
                continue

            tmp_path = f"video_creation/scene_{idx}_{len(collected_clips)}.mp4"
            if clip_data.get("source", "unknown") == "pixabay":
                download_videos1(video_url, tmp_path)
            else:
                download_video(video_url, tmp_path)

            raw_clip = VideoFileClip(tmp_path).without_audio()

            # Resize & crop to 1920×1080
            target_aspect = 1920 / 1080
            actual_aspect = raw_clip.w / raw_clip.h
            if abs(actual_aspect - target_aspect) < 0.01:
                piece = raw_clip.resize((1920, 1080))
            elif actual_aspect > target_aspect:
                piece = raw_clip.resize(height=1080)
                x_center = piece.w / 2
                piece = piece.crop(x1=x_center - 960, x2=x_center + 960, y1=0, y2=1080)
            else:
                piece = raw_clip.resize(width=1920)
                y_center = piece.h / 2
                piece = piece.crop(x1=0, x2=1920, y1=y_center - 540, y2=y_center + 540)

            piece = piece.set_fps(30)
            collected_clips.append(piece)
            new_used_urls.append(video_url)
            total_collected += piece.duration
            raw_clip.close()

            if total_collected >= audio_duration:
                break

        if not collected_clips:
            print("❌ All clip processing failed.")
            return None, []

        # Concatenate all collected pieces
        interim = concatenate_videoclips(collected_clips, method="compose")

        if interim.duration >= audio_duration:
            # Too long → subclip & force exact duration
            final_video = (
                interim
                .subclip(0, audio_duration)
                .set_fps(30)
                .set_duration(audio_duration)
            )
        else:
            # Too short → freeze-frame the last frame
            current_dur = interim.duration
            freeze_needed = audio_duration - current_dur

            last_frame_img = interim.get_frame(current_dur - 1e-3)  # a pixel just before the end
            freeze_clip = (
                ImageClip(last_frame_img)
                .set_duration(freeze_needed)
                .set_fps(30)
                .set_size(interim.size)
            )

            final_video = concatenate_videoclips([interim, freeze_clip], method="compose")\
                .set_duration(audio_duration)\
                .set_fps(30)

        for u in new_used_urls:
            used_video_urls.add(u)

    # 4) Overlay subtitles and attach the audio
    subtitle = (
        TextClip(
            text,
            fontsize=60,
            color="white",
            font="Arial-Bold",
            size=final_video.size,
            method="caption"
        )
        .set_position(("center", "bottom"))
        .set_duration(audio_duration)
        .fadein(1)
    )

    final_scene = CompositeVideoClip([final_video, subtitle])
    final_scene = final_scene.set_duration(audio_duration).set_audio(audio_clip)

    return final_scene, new_used_urls








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
    import os
    import subprocess
    import uuid
    from nltk.tokenize import sent_tokenize
    from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, CompositeAudioClip
    from moviepy.audio.fx.all import audio_loop

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






# --- Functions ---
# --- New Function to Generate Relevant Search Term ---
@retry_infinite(delay=5)
def generate_search_term(topic):
    prompt = f"Given the YouTube video topic '{topic}', suggest a short, relevant visual keyword or phrase for finding an image background. Limit to 3-5 words, no punctuation, just a plain image search phrase only one line and nothing else : keywords or phrase  just onloy that and nothing else mind it."
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

@retry_infinite(delay=5)
def generate_title_from_topic1(topic):
    prompt = f"Create a catchy YouTube video thumbnail title for this topic: '{topic}'  one line title which seo optimised and nothing else okay i ahve to fed to my progrma so it should be clena and precise dont use symbols or icons or emojis, cerate catchy one, use punctuation marks properly and highly to emphasize, and it should have max upto 5 or 6 words not more that that"
    response = gemini_model.generate_content(prompt)
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

def get_chunk_size(file_path):
    file_size = os.path.getsize(file_path)  # size in bytes
    mb = 1024 * 1024
    
    if file_size < 50 * mb:
        return 50*mb
    elif file_size < 200 * mb:
        return 100*mb
    else:
        return 400*mb


@retry_infinite(delay=5)
def upload_video(file_path, topic, thumbnail_path):
    
    feedback_link = "https://forms.gle/NLQ3gmdrsNU7DKev6"  # Replace with your actual form link
    description=generate_youtube_description(topic)
    
    description = sanitize_text(description)
    description=generate_description_with_scene_links(description, feedback_link)
    
    # Generate and clean tags
    tags = trim_tags(generate_youtube_tags(topic))
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



        from googleapiclient.discovery import build
        from googleapiclient.http import HttpRequest
        import pickle
        with open("/Users/uday/Downloads/VIDEOYT/token.pickle", "rb") as token_file:
            credentials = pickle.load(token_file)

        youtube = build("youtube", "v3", credentials=credentials)





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



        # print(f"Retrieved and saved {len(video_titles)} video titles.")

        TOPIC_LOG_FILE = "used_topics.txt"

        @retry_infinite(delay=5)
        def generate_viral_wealth_topic():
            prompt = (
            
                "1) Personal Finance & Investing 2)Health & Fitness 3) Tech Tutorials and Reviews 4) Tech and AI Innovations 5) Personal Development & Motivation 6) how to and facts are our target niches on which we will create videos\n\n"
                "generate a YouTube video title from above niches randomly that is:\n"
                "- catchy SEO-optimized with high click-through potential\n"
                "dont include i as title should be ggeneral but specific but not include me\n"
                "i want ot generate infinite wealth by using this title to create my video and post on yt to earn money"
                "- Strictly a single-line output (only the video title)\n\n"
                "dont include year, The output must be only the video title. Keep it human, and audience-focused."
            )

            # prompt = (

            #     "generate a YouTube video title on which i cerate video and upload on yt\n"
            #     "- catchy SEO-optimized with high click-through potential\n"
            #     "dont include i as title should be ggeneral but specific but not include me\n"
            #     "i want ot generate infinite wealth by using this title to create my video and post on yt to earn money"
            #     "- Strictly a single-line output (only the video title)\n\n"
            #     "dont include year, The output must be only the video title. Keep it human, and audience-focused."
            # )


            # Load existing topics if file exists
            existing_topics = set()
            if os.path.exists(TOPIC_LOG_FILE):
                with open(TOPIC_LOG_FILE, 'r', encoding='utf-8') as file:
                    existing_topics = set(line.strip().lower() for line in file if line.strip())

            # Loop until a unique topic is generated
            while True:
                response = gemini_model.generate_content(prompt)
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
        user_topic="my car"
        script = generate_youtube_script(user_topic)
        print("\n📜 Generated Script:\n", script)
        output_path, used_urls= create_video_from_script(script, user_topic)


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
        output_path = os.path.join(folder_path, "merged_audio.mp3")
        combined.export(output_path, format="mp3")
        print(f"✅ Merged audio saved to: {output_path}")



        # === Step 1: Convert merged_audio.mp3 to WAV ===
        mp3_path = 'audio/merged_audio.mp3'
        output_wav = 'Wav2Lip/merged_audio.wav'
        mp3_to_wav(mp3_path, output_wav)


        import os
        import subprocess

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

        import subprocess


        output_path= "video_created/final_video_01.mp4"
    
        from datetime import datetime

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


        def generate_description_with_scene_links(base_description,feedback_link):
            description = sanitize_text(base_description)
            description = (
                f"{description}\n\n"
                f"📢 We'd love your feedback! Share your thoughts here 👉 {feedback_link}\n\n"
                "🎥 Scene Video Sources:\n"
            )
            urls= get_urls_for_video(video_path, log_file="all_video_used_urls.txt")
            for i, url in urls:
                description += f"Scene {i} video: {url}\n"

            description += (
                "\nCinematic Technology | Cybernetic Dreams by Alex-Productions\n"
                "https://youtu.be/NDYRjTti5Bw\n"
                "Music promoted by https://onsound.eu/\n"
            )

            return description
        
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
        remove_video_entry(video_path)


        

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
        

        # Example Usage:
        success = upload_video(video_path, user_topic, "/Users/uday/Downloads/VIDEOYT/final_thumbnail.jpg")
        mapping_file = '/Users/uday/Downloads/VIDEOYT/file_topic_map.txt'
        if success:
            try:
                os.remove(video_path)
                remove_video_entry(video_path)
                remove_mapping_entry(video_path, mapping_file)
                print(f"Deleted: {video_path}")
                count -= 1
                save_upload_status(count)
                print(f"✅ Upload complete. Remaining uploads today: {count}")

            except Exception as e:
                print(f"Failed to delete {video_path}: {e}")

       

 




