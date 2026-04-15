



# === Imports === #
import os
import requests
import nltk
import spacy
from gtts import gTTS
from datetime import datetime
from nltk.tokenize import sent_tokenize
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip
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

import os

output_path = "/Users/uday/Downloads/VIDEOYT/final_video/myfinal.mp4"  # replace with your actual output filename

# Delete the file if it already exists
if os.path.exists(output_path):
    os.remove(output_path)
    print(f"Previous file '{output_path}' deleted.")


folder_path1 = "/Users/uday/Downloads/VIDEOYT/video_creation/"
folder_path2 = "/Users/uday/Downloads/VIDEOYT/audio/"
folder_path3 = "/Users/uday/Downloads/VIDEOYT/video_created/"

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


genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name='models/gemini-2.5-flash-preview-04-17-thinking')

# Get trending topic from Google Trends using SerpAPI



UPLOAD_LIMIT = 6
JSON_FILE = "/Users/uday/Downloads/VIDEOYT/UPLOAD_STATUS.json"

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
    write youtube script for {topic} in narrating style with intro and outro,, video should be engaging and valuable to viewers, focus on quality and engagement,  i want video to be viral and generate infinite money with it so make script that good. script must be in paragraph format(required dont forget it mind it) dont write in bold anything script should be in paragraph format against youtube script word plainly and nothing else in it as i have to fed it to my ai program so making it understand would be easy so just assign script plainly against youtube script word, script length must be accordding to needs as per topic but dont cerate scritp lenght which will last only for 1 minute script length must be longer than that so that it does nto create only 1 min video, script msut be creative mind it i need it okay.
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
        print(e.stderr.decode() if e.stderr else str(e))

import ffmpeg






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
def fallback_search_query(sentence):
    prompt = f"Give a short search query to find a stock video for: '{sentence}', just plainly text query not in bold, give 1  query search term only, and nothing else,  "
    response = gemini_model.generate_content(prompt)
    return [q.strip() for q in response.text.strip().split(",")]

# === Search Pexels for a Query === #
@retry_infinite(delay=5)
def search_pexels_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 10}
    response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("videos", [])
    return []


# === Find 1 Best Clip Per Search Term, avoiding duplicates === #
@retry_infinite(delay=5)
def find_three_video_clips(sentence, used_video_urls):
    print(f"🔍 Searching videos for: {sentence}")
    final_results = []
    queries = fallback_search_query(sentence)

    for query in queries:
        print(f"🔎 Searching for: {query}")
        found_clip = None

        # Try direct search
        clips = search_pexels_video(query)
        for clip in clips:
            video_url = clip["video_files"][0]["link"]
            if (abs(clip["width"] - 1920) <= 200 and abs(clip["height"] - 1080) <= 200 and
                video_url not in used_video_urls):
                found_clip = clip
                used_video_urls.add(video_url)
                break

        # If not found, try using extracted keywords from that query
        if not found_clip:
            keywords = extract_keywords(query)
            for keyword in keywords:
                clips = search_pexels_video(keyword)
                for clip in clips:
                    video_url = clip["video_files"][0]["link"]
                    if (abs(clip["width"] - 1920) <= 200 and abs(clip["height"] - 1080) <= 200 and
                        video_url not in used_video_urls):
                        found_clip = clip
                        used_video_urls.add(video_url)
                        break
                if found_clip:
                    break

        # Add the clip if one was found
        if found_clip:
            final_results.append(found_clip)

    return final_results  # List of up to 3 unique clips, one per query



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


from moviepy.editor import ColorClip

# def get_fallback_clip(duration=3, size=(1920, 1080), fps=24):
#     """Returns a black video clip of the given duration."""
#     return ColorClip(size=size, color=(0, 0, 0), duration=duration).set_fps(fps)

from moviepy.editor import ColorClip, AudioFileClip, concatenate_videoclips, VideoFileClip, vfx
import os

def create_scene(text, idx, used_video_urls):
    print(f"\n🎬 Creating Scene {idx + 1}")
    video_clips_data = find_three_video_clips(text, used_video_urls)

    audio_path = f"/Users/uday/Downloads/VIDEOYT/audio/scene_{idx}.mp3"
    
    try:
        audio_clip = generate_audio(text, audio_path)
        audio_duration = audio_clip.duration

        if audio_duration <= 0:
            print(f"⚠️ Audio duration is zero or less for scene {idx+1}. Skipping scene.")
            return None

        clips = []

        if video_clips_data:
            duration_per_clip = audio_duration / max(1, len(video_clips_data))  # Split evenly

            for i, clip_data in enumerate(video_clips_data):
                try:
                    video_url = clip_data['video_files'][0]['link']
                    video_path = f"/Users/uday/Downloads/VIDEOYT/video_creation/scene_{idx}_{i}.mp4"
                    download_video(video_url, video_path)

                    video_clip = VideoFileClip(video_path)

                    if video_clip.duration <= 0:
                        print(f"⚠️ Clip {i} has invalid duration. Skipping.")
                        continue

                    # Resize/crop to 1920x1080
                    target_aspect = 1920 / 1080
                    actual_aspect = video_clip.w / video_clip.h

                    if abs(actual_aspect - target_aspect) < 0.01:
                        video_clip = video_clip.resize((1920, 1080)).set_fps(24)
                    elif actual_aspect > target_aspect:
                        video_clip = video_clip.resize(height=1080)
                        x_center = video_clip.w / 2
                        video_clip = video_clip.crop(x1=x_center - 960, x2=x_center + 960, y1=0, y2=1080).set_fps(24)
                    else:
                        video_clip = video_clip.resize(width=1920)
                        y_center = video_clip.h / 2
                        video_clip = video_clip.crop(x1=0, x2=1920, y1=y_center - 540, y2=y_center + 540).set_fps(24)

                    # Adjust speed to fit allotted time
                    speed_factor = video_clip.duration / duration_per_clip
                    adjusted_clip = video_clip.fx(vfx.speedx, factor=speed_factor).set_duration(duration_per_clip)

                    clips.append(adjusted_clip)

                except Exception as e:
                    print(f"⚠️ Error with clip {i} in scene {idx+1}: {e}")
                    continue

        if not clips:
            print(f"❌ No usable clips for scene {idx+1}. Using black screen fallback.")
            black_clip = ColorClip(size=(1920, 1080), color=(0, 0, 0), duration=audio_duration).set_fps(24)
            black_clip = black_clip.set_audio(audio_clip)
            return black_clip

        # Combine clips and add audio
        final_scene = concatenate_videoclips(clips, method="chain").set_audio(audio_clip).set_duration(audio_duration)
        return final_scene

    except Exception as e:
        print(f"⚠️ Unexpected error in scene {idx+1}: {e}")
        return None



# import os
# import subprocess
# from datetime import datetime
# from nltk.tokenize import sent_tokenize

# def create_video_from_script(script):
#     global output_path
#     sentences = sent_tokenize(script)
#     scenes = []
#     used_video_urls = set()  # To keep track of all used videos across scenes

#     for idx, sentence in enumerate(sentences):
#         scene = create_scene(sentence, idx, used_video_urls)
#         if scene is not None:
#             scenes.append(scene)

#     if not scenes:
#         print("❌ No scenes could be created. Cannot generate final video.")
#         return

#     try:
#         final_video = concatenate_videoclips(scenes, method="compose")
#         output_path = f"/Users/uday/Downloads/VIDEOYT/static/videos/myfinal1.mp4"
#         final_video.write_videofile(output_path, codec="libx264", audio_codec="libmp3lame", fps=24, threads=8, verbose=0, preset="ultrafast", audio = False)
#         print(f"\n✅ Final video saved to: {output_path}")
#     except Exception as e:
#         print(f"❌ Error during final video concatenation or writing: {e}")


import os
import subprocess
from datetime import datetime
from nltk.tokenize import sent_tokenize

def create_video_from_script(script):
    global output_path
    sentences = sent_tokenize(script)
    used_video_urls = set()
    scene_file_paths = []

    output_dir = "/Users/uday/Downloads/VIDEOYT/video_created"
    os.makedirs(output_dir, exist_ok=True)

    # Disclaimer clip (assumed to have no audio or you want to keep audio)
    # disclaimer_path = "/Users/uday/Downloads/VIDEOYT/disclaimer_video.mp4"
    # if include_disclaimer:
    #     # Remove audio from disclaimer as well, to keep consistency if needed:
    #     disclaimer_noaudio = os.path.join(output_dir, "disclaimer_noaudio.mp4")
    #     subprocess.run([
    #         "ffmpeg", "-y", "-i", disclaimer_path,
    #         "-c:v", "copy", "-an", disclaimer_noaudio
    #     ], check=True)
    #     scene_file_paths.append(disclaimer_noaudio)
    # # else:
    #     scene_file_paths.append(disclaimer_path)

    # Process each sentence and create scene videos without audio
    for idx, sentence in enumerate(sentences):
        scene_clip = create_scene(sentence, idx, used_video_urls)
        if scene_clip is not None:
            scene_path = os.path.join(output_dir, f"scene_{idx}.mp4")
            scene_clip.write_videofile(scene_path, codec='libx264', fps=24, preset='ultrafast', threads=8)
            
            # Remove audio from saved scene video
            scene_noaudio_path = os.path.join(output_dir, f"scene_{idx}_noaudio.mp4")
            subprocess.run([
                "ffmpeg", "-y", "-i", scene_path,
                "-c:v", "copy",
                "-an",
                scene_noaudio_path
            ], check=True)
            scene_file_paths.append(scene_noaudio_path)

            # Optional: delete original scene with audio if you want to save space
            os.remove(scene_path)

    if not scene_file_paths:
        print("❌ No scenes could be created. Cannot generate final video.")
        return

    # Create video list file for ffmpeg concat
    video_list_path = os.path.join(output_dir, "video_list.txt")
    with open(video_list_path, "w") as f:
        for path in scene_file_paths:
            f.write(f"file '{path}'\n")

    # Concatenate silent scenes into one silent video
    output_path =  f"/Users/uday/Downloads/VIDEOYT/static/videos/myfinal1.mp4"
    ffmpeg_concat_cmd = [
        "ffmpeg",
        "-y",  # <--- this is the key addition to force overwrite
        "-f", "concat",
        "-safe", "0",
        "-i", video_list_path,
        "-c", "copy",
        output_path
    ]

    try:
        subprocess.run(ffmpeg_concat_cmd, check=True)
        print(f"✅ Concatenated silent main video created: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg failed to concatenate scenes: {e}")
        return


# def create_video_from_script(script, include_disclaimer=True):
#     global output_path
#     sentences = sent_tokenize(script)
#     used_video_urls = set()
#     scene_file_paths = []

#     output_dir = "/Users/uday/Downloads/VIDEOYT/video_created"
#     os.makedirs(output_dir, exist_ok=True)

#     # Final output path
#     output_path = os.path.join(output_dir, f"final_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

#     # Process each sentence into scenes
#     for idx, sentence in enumerate(sentences):
#         scene_clip = create_scene(sentence, idx, used_video_urls)
#         if scene_clip is not None:
#             scene_path = os.path.join(output_dir, f"scene_{idx}.mp4")
#             scene_clip.write_videofile(scene_path, codec='libx264', fps=24, preset='ultrafast', threads=4)
#             scene_file_paths.append(scene_path)

    # # Handle cases based on number of created scenes
    # if len(scene_file_paths) == 0:
    #     print("❌ No video scenes were created. Exiting.")
    #     return

    # elif len(scene_file_paths) == 1:
    #     # Rename the only scene to final output
    #     os.rename(scene_file_paths[0], output_path)
    #     print(f"✅ Only one scene available. Saved as: {output_path}")
    #     return

    # else:
    #     # Create video list file for FFmpeg concat
    #     video_list_path = os.path.join(output_dir, "video_list.txt")
    #     with open(video_list_path, "w") as f:
    #         for path in scene_file_paths:
    #             f.write(f"file '{path}'\n")

    #     # FFmpeg command to concatenate all scenes
    #     ffmpeg_cmd = [
    #         "ffmpeg",
    #         "-f", "concat",
    #         "-safe", "0",
    #         "-i", video_list_path,
    #         "-c:v", "libx264",
    #         "-c:a", "libmp3lame",
    #         "-b:a", "192k",
    #         output_path
    #     ]

    #     subprocess.run(ffmpeg_cmd, check=True)
    #     print(f"✅ Final video created at: {output_path}")



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
    Do not include any formatting or labels like 'Description:'. Just return the description text only. it should be seo optimised mind it
    """
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

@retry_infinite(delay=5)
def generate_youtube_tags(topic):
    prompt = f"""
    Generate a list of 21 relevant, high-SEO YouTube tags (comma-separated) for the topic: "{topic}".
    Only return the tags in a single line, separated by commas. Do not include extra explanation or formatting. it should be seo optimised mind it
    """
    response = gemini_model.generate_content(prompt)
    tag_string = response.text.strip()
    tag_list = [tag.strip() for tag in tag_string.split(',')]
    return tag_list

@retry_infinite(delay=5)
def clean_tags_with_gemini(raw_tags):
   

    prompt = f"""
    You are an assistant that cleans and formats YouTube video tags.

    Here are the original tags:
    {raw_tags}

    Rules:
    - Remove duplicates.
    - Avoid overly long or repetitive phrases.
    - Limit the total character count to under 500 characters.
    - Return them as a clean Python list of strings.

    Respond ONLY with the cleaned list of tags nothing else return only list of tags comma seperated
    """

    response = gemini_model.generate_content(prompt)
    try:
        # Use eval carefully; better with ast.literal_eval for safety
        cleaned_tags = eval(response.text.strip(), {"__builtins__": {}})
        return cleaned_tags
    except Exception as e:
        print("Error parsing Gemini response:", e)
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
    border_color = invert_color(dominant_color)
    print(f"🎨 Dominant: {dominant_color}, Inverted: {border_color}")

    print("🖋️ Adding title to image...")
    draw = ImageDraw.Draw(img)
    font_path = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"  # Change this path if needed
    font = ImageFont.truetype(font_path, 80)

    bbox = draw.textbbox((0, 0), title, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (1920 - text_w) // 2
    y = 1080 - text_h - 50

    # Draw shadow/border with inverted color
    # Draw thick border by looping over a range
    border_thickness = 8  # Increase for thicker border
    for dx in range(-border_thickness, border_thickness + 1):
        for dy in range(-border_thickness, border_thickness + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), title, font=font, fill=border_color)


    # Draw main text with dominant color
    draw.text((x, y), title, font=font, fill=dominant_color)

    out_path = "/Users/uday/Downloads/VIDEOYT/final_thumbnail.jpg"
    img.save(out_path)
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



# def upload_video(file_path, topic, thumbnail_path=None):
    

#     description = generate_youtube_description(topic)
#     tags1 = generate_youtube_tags(topic)
#     tags=trim_tags(tags1)
#     final_tags = clean_tags_with_gemini(tags)
#     category_info = get_category_id_from_gemini(topic)
#     id=extract_category_id(category_info)

#     create_thumbnail(topic)
 
 

#     print("Title:", topic)
#     print("Description:", description)
#     print("Tags:", tags)

#     request_body = {
#         "snippet": {
#             "categoryId": str(id),  # Education
#             "title": topic,
#             "description": description,
#             "tags": final_tags
            
    #     },
    #     "status": {
    #         "privacyStatus": "public",
  
           
    #     }
    # }
    # print(json.dumps(request_body, indent=2))
    # # media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    # # request = youtube.videos().insert(part="snippet,status", body=request_body, media_body=media)

    # # Upload with retry and progress tracking
    # response = None
    # while response is None:
    #     try:
    #         status, response = request.next_chunk()
    #         if status:
    #             print(f"Uploading: {int(status.progress() * 100)}%")
    #     except HttpError as e:
    #         print(f"HttpError: {e}")
           
    #         print("Retrying after error...")
    #         time.sleep(5)
    #     except Exception as e:
    #         print(f"Unexpected error: {e}")
    #         time.sleep(5)

    # print(f"✅ Video uploaded successfully! Video ID: {response['id']}")

    # thumbnail_path="/Users/uday/Downloads/VIDEOYT/final_thumbnail.jpg"

    # # ✅ Upload the thumbnail if provided
    # if thumbnail_path:
    #     print("Uploading thumbnail...")
    #     youtube.thumbnails().set(
    #         videoId=response["id"],
    #         media_body=MediaFileUpload(thumbnail_path)
    #     ).execute()
    #     print("✅ Thumbnail uploaded successfully!")





# === MAIN DRIVER === #
if __name__ == "__main__":
        
    
    # while True:
        
        # status = get_upload_status()
        # count = status["count"]

        # if count <= 0:
        #     print("✅ Upload limit reached for today.")
        #     break



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



        # print(f"Retrieved and saved {len(video_titles)} video titles.")

        # TOPIC_LOG_FILE = "/Users/uday/Downloads/VIDEOYT/used_topics.txt"

        # @retry_infinite(delay=5)
        # def generate_viral_wealth_topic():
        #     prompt = (
        #         "From the following top YouTube niches ranked by performance and CPM:\n"
        #         "1) Personal Finance & Investing, 2) Tech Reviews & Tutorials, 3) Health & Fitness, "
        #         "4) Make Money Online / Entrepreneurship, 5) Lifestyle, 6) Education & How-To, 7) Food —\n\n"
        #         "Randomly choose one niche from the list above and generate a YouTube video title that is:\n"
        #         "- catchy SEO-optimized with high click-through potential\n"
        #         "dont include i as title should be ggeneral but specifi but not include me\n"
        
        #         "- Strictly a single-line output (only the video title)\n\n"
        #         "dont include year, The output must be **only** the video title. Keep it human, and audience-focused."
        #     )

        #     # Load existing topics if file exists
        #     existing_topics = set()
        #     if os.path.exists(TOPIC_LOG_FILE):
        #         with open(TOPIC_LOG_FILE, 'r', encoding='utf-8') as file:
        #             existing_topics = set(line.strip().lower() for line in file if line.strip())

        #     # Loop until a unique topic is generated
        #     while True:
        #         response = gemini_model.generate_content(prompt)
        #         new_topic = response.text.strip()

        #         if new_topic.lower() not in existing_topics:
            
        #             return new_topic
        #         else:
        #             print("Duplicate topic found, regenerating...")

        # # Example usage
        # user_topic = generate_viral_wealth_topic()
        # print("💡 Unique Viral Topic:", user_topic)




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

  


    folder_path1 = "/Users/uday/Downloads/VIDEOYT/video_creation/"
    folder_path2 = "/Users/uday/Downloads/VIDEOYT/audio/"
    folder_path3 = "/Users/uday/Downloads/VIDEOYT/video_created/"

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

    # script = generate_youtube_script(user_topic)
    # print("\n📜 Generated Script:\n", script)
    # create_video_from_script(script)


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


    
    with open("input.txt", "r", encoding="utf-8") as f:
        script = f.read().strip()



    create_video_from_script(script)

    


    from pydub import AudioSegment
    import os
    import ffmpeg

    folder_path = "/Users/uday/Downloads/VIDEOYT/audio"
    combined = AudioSegment.empty()

    mp3_files = [f for f in os.listdir(folder_path) if f.endswith(".mp3")]

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
    mp3_path = '/Users/uday/Downloads/VIDEOYT/audio/merged_audio.mp3'
    output_wav = '/Users/uday/Downloads/VIDEOYT/Wav2Lip/merged_audio.wav'
    mp3_to_wav(mp3_path, output_wav)

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

    



    import os
    import subprocess

    # Define all paths
    inference_script = "/Users/uday/Downloads/VIDEOYT/Wav2Lip/inference.py"
    checkpoint_path = "checkpoints/wav2lip.pth"
    face_video ="/Users/uday/Downloads/VIDEOYT/Wav2Lip/output_video (4).mp4" 
    output_video_no_audio = "/Users/uday/Downloads/VIDEOYT/video_created/output.mp4"
    temp_result = "temp/result.avi"
    output_final = "/Users/uday/Downloads/VIDEOYT/video_created/output_with_audio.mp4"

    # Step 1: Run Wav2Lip inference
    print("▶️ Running Wav2Lip inference...")
    subprocess.run([
        "python3", inference_script,
        "--checkpoint_path", checkpoint_path,
        "--face", face_video,
        "--audio", output_wav,
        "--outfile", output_video_no_audio,
        
    
    ])


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
        "-b:a", "192k",
        "-shortest",
        output_final
    ])

    print(f"✅ Done! Final video with audio is saved to:\n{output_final}")

    import subprocess


    
    output_file = "/Users/uday/Downloads/VIDEOYT/static/videos/myfinal.mp4"
    output_path = f"/Users/uday/Downloads/VIDEOYT/static/videos/myfinal1.mp4"

    command = [
        "ffmpeg", "-y",
        "-i", output_path,     # Main video (input 0)
        "-i", output_final,    # Avatar video (input 1)
        "-filter_complex",
        "[1:v]scale=280:400[avatar];[0:v][avatar]overlay=10:H-h-10[outv]",
        "-map", "[outv]",
        "-map", "1:a?",        # Audio from the main video
        "-c:v", "libx264",
        "-preset", "ultrafast", 
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        "-shortest",
        output_file
    ]



    # Run the command
    print("▶️ Merging video with avatar overlay and avatar audio...")
    subprocess.run(command)
    print(f"✅ Done! Final video saved to:\n{output_file}")


    # # Run the command
    # print("▶️ Merging video with avatar overlay and avatar audio...")
    # subprocess.run(command)
    # print(f"✅ Done! Final video saved to:\n{output_file}")

    # import time

    # # Example Usage:
    # upload_video(output_file, user_topic, "/Users/uday/Downloads/VIDEOYT/final_thumbnail.jpg")

    # count -= 1
    # save_upload_status(count)
    # print(f"✅ Upload complete. Remaining uploads today: {count}")




