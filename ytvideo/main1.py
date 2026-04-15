


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
from pydub import AudioSegment
import os

# === Initial Setup === #
nltk.download("punkt")
nltk.download("punkt_tab")
nltk.download("stopwords")
nlp = spacy.load("en_core_web_sm")

# === API KEYS === #
PEXELS_API_KEY = "DGhCtAB83klpCIv5yq5kMIb2zun7q67IvHJysvW4lInb0WVXaQF2xLMu"
SERP_API_KEY = "7f55bbfeff700d39fe9ee306af78102a69cf43267987037a77c5b111cbc48e98"
GEMINI_API_KEY = "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw"

os.environ["PATH"] += os.pathsep + "/opt/homebrew/bin"

# Optional: also explicitly set converter paths (may be ignored by some methods)
AudioSegment.converter = "/opt/homebrew/bin/ffmpeg"
AudioSegment.ffprobe = "/opt/homebrew/bin/ffprobe"

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
import google.generativeai as genai
# Get trending topic from Google Trends using SerpAPI
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

def generate_youtube_script(topic):
    prompt = f"""
    write youtube script for {topic} in narrating style with intro and outro, i want video to be viral and generate infinite money with it so make script that good. script must be in paragraph format(required dont forget it mind it) dont write in bold anything script should be in paragraph format against youtube script word plainly and nothing else in it as i have to fed it to my ai program so making it understand would be easy so just assign script plainly against youtube script word, script should have 2 sentences, i need it okay.
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


# === Extract Keywords with SpaCy === #
def extract_keywords(text):
    doc = nlp(text)
    return [token.text for token in doc if token.pos_ in ("NOUN", "PROPN", "ADJ")]

# === Fallback Search Queries (3) === #

def fallback_search_query(sentence, usr_topic):
    prompt = f"Give a short search query to find a stock video for: '{sentence}', just plainly text query not in bold, give 3 queries comma separated and queries search terms must relate to topic so that video clips are used which are relevent to topic pls kindly create search terms which are related to topic and current part dont get offshore, user topic is {user_topic}"
    response = gemini_model.generate_content(prompt)
    return [q.strip() for q in response.text.strip().split(",")]

# === Search Pexels for a Query === #
def search_pexels_video(query):
    headers = {"Authorization": PEXELS_API_KEY}
    params = {"query": query, "per_page": 10}
    response = requests.get("https://api.pexels.com/videos/search", headers=headers, params=params)
    if response.status_code == 200:
        return response.json().get("videos", [])
    return []


# === Find 1 Best Clip Per Search Term, avoiding duplicates === #
def find_three_video_clips(sentence, used_video_urls):
    print(f"🔍 Searching videos for: {sentence}")
    final_results = []
    queries = fallback_search_query(sentence, user_topic)

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
def download_video(url, filename):
    response = requests.get(url, stream=True)
    with open(filename, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    return filename

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


# === Generate Audio === #
def generate_audio(text, filename):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    return AudioFileClip(filename)

# === Create Scene from Sentence === #
def create_scene(text, idx, used_video_urls):
    print(f"\n🎬 Creating Scene {idx + 1}")
    video_clips_data = find_three_video_clips(text, used_video_urls)

    if not video_clips_data:
        print("❌ No clips found.")
        return None

    try:
        audio_clip = generate_audio(text, f"/Users/uday/Downloads/VIDEOYT/audio/scene_{idx}.mp3")
        audio_duration = audio_clip.duration

        if audio_duration <= 0:
            print(f"⚠️ Audio duration is zero or less for scene {idx+1}. Skipping scene.")
            return None

        duration_per_clip = audio_duration / max(1, len(video_clips_data)) # Avoid division by zero if somehow video_clips_data is empty after check

        clips = []
        for i, clip_data in enumerate(video_clips_data):
            try:
                video_url = clip_data['video_files'][0]['link']
                video_path = f"/Users/uday/Downloads/VIDEOYT/video_creation/scene_{idx}_{i}.mp4"
                download_video(video_url, video_path)

                video_clip = VideoFileClip(video_path)

                if video_clip.duration <= 0:
                    print(f"⚠️ Downloaded video clip {i} has zero or less duration for scene {idx+1}. Skipping this clip.")
                    continue

                # Resize while maintaining aspect ratio and then crop or pad
                target_aspect_ratio = 1920 / 1080
                clip_aspect_ratio = video_clip.w / video_clip.h

                if abs(clip_aspect_ratio - target_aspect_ratio) < 0.01: # Close to target aspect ratio
                     video_clip = video_clip.resize((1920, 1080))
                elif clip_aspect_ratio > target_aspect_ratio: # Wider than target
                    video_clip = video_clip.resize(height=1080)
                    # Center crop horizontally
                    x_center = video_clip.w / 2
                    video_clip = video_clip.crop(x1=x_center - 960, x2=x_center + 960, y1=0, y2=1080)
                else: # Taller than target
                    video_clip = video_clip.resize(width=1920)
                    # Center crop vertically
                    y_center = video_clip.h / 2
                    video_clip = video_clip.crop(x1=0, x2=1920, y1=y_center - 540, y2=y_center + 540)


                video_clip = video_clip.subclip(0, min(duration_per_clip, video_clip.duration))
                clips.append(video_clip)

            except Exception as e:
                print(f"⚠️ Error processing video clip {i} for scene {idx+1}: {e}. Skipping this clip.")
                continue # Continue to the next video clip if one fails

        if not clips:
            print(f"❌ No valid video clips were processed for scene {idx+1}. Skipping scene.")
            # Clean up the audio file if no video clips were added
            if os.path.exists(audio_clip):
                os.remove(audio_clip)
            return None

        # Concatenate valid video clips and set audio
        combined_clip = concatenate_videoclips(clips, method="compose").set_audio(audio_clip).set_duration(audio_duration)
        return combined_clip

    except Exception as e:
        print(f"⚠️ An unexpected error occurred while creating scene {idx+1}: {e}. Skipping scene.")
        return None


def create_video_from_script(script):
    global output_path
    sentences = sent_tokenize(script)
    scenes = []
    used_video_urls = set()  # To keep track of all used videos across scenes

    for idx, sentence in enumerate(sentences):
        scene = create_scene(sentence, idx, used_video_urls)
        if scene is not None:
            scenes.append(scene)

    if not scenes:
        print("❌ No scenes could be created. Cannot generate final video.")
        return

    try:
        final_video = concatenate_videoclips(scenes, method="compose")
        output_path = f"/Users/uday/Downloads/VIDEOYT/final_video_01.mp4"
        final_video.write_videofile(output_path, codec="libx264", audio_codec="libmp3lame", fps=24, threads=8, verbose=0, preset="ultrafast", audio = False)
        print(f"\n✅ Final video saved to: {output_path}")
    except Exception as e:
        print(f"❌ Error during final video concatenation or writing: {e}")


# === MAIN DRIVER === #
if __name__ == "__main__":
    print("🎬 How would you like to create your video?")
    print("1. Based on a custom topic")
    print("2. Based on a trending topic")
    print("3. Using your own script")
    choice = input("👉 Enter 1, 2, or 3: ").strip()

    if choice == "1":
        user_topic = input("🎯 Enter your YouTube video topic: ").strip()
        script = generate_youtube_script(user_topic)
        print("\n📜 Generated Script:\n", script)
        create_video_from_script(script)

    elif choice == "2":
        # Ensure get_trending_topic is defined or imported correctly
        try:
            user_topic = get_trending_topic()
            print(f"🔥 Trending Topic: {user_topic}")
            script = generate_youtube_script(user_topic)
            print("\n📜 Generated Script:\n", script)
            create_video_from_script(script)
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
        user_topic = "\n".join(user_script_lines)
        print("\n📜 Using Your Script:\n", user_topic)
        create_video_from_script(user_topic)

    else:
        print("❌ Invalid choice. Please run the program again and select 1, 2, or 3.")

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


    import os
    import subprocess

    # Define all paths
    inference_script = "/Users/uday/Downloads/VIDEOYT/Wav2Lip/inference.py"
    checkpoint_path = "checkpoints/wav2lip_gan.pth"
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


    
    output_file = "/Users/uday/Downloads/VIDEOYT/final_video/myfinal.mp4"
    output_path = f"/Users/uday/Downloads/VIDEOYT/final_video_01.mp4"

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




