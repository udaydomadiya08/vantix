

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
    dont inlude astreiks bold text only plain format normal text mind it
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

