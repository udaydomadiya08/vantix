
import os
import subprocess
import requests
import json
import time
import google.generativeai as genai
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy.video.fx.all import fadein, fadeout, crop

PEXELS_API_KEY = "DGhCtAB83klpCIv5yq5kMIb2zun7q67IvHJysvW4lInb0WVXaQF2xLMu"
GEMINI_API_KEY = "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(model_name='models/gemini-2.5-flash-preview-04-17-thinking')

VIDEO_SCRIPT_TEMPLATE = '''
import os
import sys
import requests
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
from moviepy.video.fx.all import fadein, fadeout, crop

PEXELS_API_KEY = "DGhCtAB83klpCIv5yq5kMIb2zun7q67IvHJysvW4lInb0WVXaQF2xLMu"

def parse_resolution(res_str):
    res_str = res_str.lower().strip()
    aspect_ratio = 16 / 9
    if "x" in res_str:
        try:
            width, height = map(int, res_str.split("x"))
            return width, height
        except Exception:
            pass
    elif res_str.endswith("p"):
        try:
            height = int(res_str[:-1])
            width = int(height * aspect_ratio)
            return width, height
        except Exception:
            pass
    else:
        try:
            height = int(res_str)
            width = int(height * aspect_ratio)
            return width, height
        except Exception:
            pass
    return 854, 480

def fetch_pexels_videos(search_term, max_results=3, target_height=480):
    url = f"https://api.pexels.com/videos/search?query={{search_term}}&per_page={{max_results}}"
    headers = {{"Authorization": PEXELS_API_KEY}}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    data = response.json()
    videos = []
    for vid in data.get("videos", []):
        for file in vid.get("video_files", []):
            if abs(file.get("height", 0) - target_height) <= 100:
                videos.append(file["link"])
                break
    return videos

def download_video(url, folder, idx):
    local_path = os.path.join(folder, f"clip_{{idx}}.mp4")
    if os.path.exists(local_path):
        return local_path
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(local_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    return local_path

def resize_and_crop(clip, target_width, target_height):
    target_aspect = target_width / target_height
    actual_aspect = clip.w / clip.h
    if abs(actual_aspect - target_aspect) < 0.01:
        return clip.resize((target_width, target_height))
    elif actual_aspect > target_aspect:
        clip = clip.resize(height=target_height)
        x_center = clip.w / 2
        return crop(clip, x1=x_center - target_width / 2, x2=x_center + target_width / 2, y1=0, y2=target_height)
    else:
        clip = clip.resize(width=target_width)
        y_center = clip.h / 2
        return crop(clip, x1=0, x2=target_width, y1=y_center - target_height / 2, y2=y_center + target_height / 2)

from moviepy.editor import AudioFileClip
from gtts import gTTS
from moviepy.video.fx import all as vfx

def create_video(
    script_lines, output_path="{output_path}", font="{font}",
    transition="{transition}", duration=3, resolution="{resolution}",
    text_position="{text_position}", text_size=40, fps=30, num_clips=3, with_audio={with_audio}
):
    tmp_dir = "temp_clips"
    os.makedirs(tmp_dir, exist_ok=True)

    target_width, target_height = parse_resolution(resolution)
    clips = []

    for i, sentence in enumerate(script_lines[:num_clips]):
        videos = fetch_pexels_videos(sentence, max_results=1, target_height=target_height)
        if not videos:
            print(f"No videos found for sentence: {{sentence}}")
            continue

        video_path = download_video(videos[0], tmp_dir, i)
        raw_clip = VideoFileClip(video_path).subclip(0, duration)
        clip = resize_and_crop(raw_clip, target_width, target_height)

        if transition == "fade":
            clip = fadein(clip, 1).fx(fadeout, 1)

        if with_audio:
            tts = gTTS(sentence, lang="en")
            audio_path = os.path.join(tmp_dir, f"audio_{{i}}.mp3")
            tts.save(audio_path)  # Save audio before checking

            if os.path.getsize(audio_path) == 0:
                raise Exception(f"TTS failed, {{audio_path}} is empty.")

            audio_clip = AudioFileClip(audio_path)

            # Match clip duration to audio
            if clip.duration > audio_clip.duration:
                # Cut clip to match audio duration
                clip = clip.subclip(0, audio_clip.duration)
            elif clip.duration < audio_clip.duration:
                # Slow down clip to match audio duration
                speed_factor = clip.duration / audio_clip.duration
                clip = clip.fx(vfx.speedx, speed_factor)

            # Final match for safety
            audio_clip = audio_clip.subclip(0, clip.duration)
        else:
            audio_clip = None




        txt_clip = TextClip(
            sentence,
            fontsize=text_size,
            font=font,
            color='white',
            method='caption',
            size=(int(target_width * 0.8), None)
        ).set_duration(clip.duration).set_pos(text_position)

        if audio_clip:
            composite = CompositeVideoClip([clip, txt_clip]).set_audio(audio_clip).set_fps(fps)
        else:
            composite = CompositeVideoClip([clip, txt_clip]).set_fps(fps)

        clips.append(composite)


    if not clips:
        print("No clips created, exiting.")
        sys.exit(1)

    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(
        output_path,
        fps=fps,
        audio=True,
        codec="libx264",            # video codec (recommended)
        audio_codec="libmp3lame"        # audio codec (recommended)
   
    )



if __name__ == "__main__":
    user_input = "{user_query}"
    duration = {duration}
    font = "{font}"
    resolution = "{resolution}"
    text_position = "{text_position}"
    text_size = {text_size}
    fps = {fps}
    num_clips = {num_clips}
    transition = "{transition}"
    output_path = "{output_path}"
    with_audio={with_audio!r}


    try:
        import google.generativeai as genai
        genai.configure(api_key="{gemini_api_key}")
        gemini_model = genai.GenerativeModel(model_name='models/gemini-2.5-flash-preview-04-17-thinking')
    except Exception:
        gemini_model = None

    if "\\n" in user_input or len(user_input.split()) > 15:
        script_text = user_input
    else:
        if gemini_model:
            prompt = f"Write a short video script about: {{user_input}}\\nUse 3-5 short and catchy lines, only plain text script, no visuals or bold text."
            response = gemini_model.generate_content(prompt)
            script_text = response.text.strip()
        else:
            print("Error: Gemini model not available and no script provided.")
            sys.exit(1)

    script_lines = [line.strip() for line in script_text.split("\\n") if line.strip()]
    clip_duration = max(duration // max(len(script_lines), 1), 1)

    create_video(
        script_lines=script_lines,
        output_path=output_path,
        font=font,
        transition=transition,
        duration=clip_duration,
        resolution=resolution,
        text_position=text_position,
        text_size=text_size,
        fps=fps,
        num_clips=num_clips,
        with_audio=with_audio
    )
'''



import subprocess
import time
import json
import os

# Assume gemini_model is configured globally or inside main guard as before

def call_gemini_api(error_msg, script_code):
    if not gemini_model:
        print("⚠️ Gemini model not available for fixing errors.")
        return script_code
    prompt = f"Fix the following Python script errors:\n\nError:\n{error_msg}\n\nCode:\n{script_code}\n\nReturn only the corrected Python code without extra text."
    response = gemini_model.generate_content(prompt)
    fixed_code = response.text.strip()

    # Strip markdown triple backticks if present
    if fixed_code.startswith("```"):
        lines = fixed_code.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        fixed_code = "\n".join(lines).strip()

    return fixed_code


def run_script_with_retry(script_code, script_path="generated_video_script.py"):
    with open(script_path, "w") as f:
        f.write(script_code)
    for attempt in range(3):
        try:
            print(f"Running script, attempt {attempt + 1}...")
            subprocess.run(["python3", script_path], check=True, capture_output=True, text=True)
            print("✅ Video generated successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Attempt {attempt + 1} failed:\n{e.stderr}")
            print("Calling Gemini API to fix the script...")
            script_code = call_gemini_api(e.stderr, script_code)
            with open(script_path, "w") as f:
                f.write(script_code)
            time.sleep(1)
    print("❌ All retries failed.")
    return False


def parse_video_requirements(user_input):
    if not gemini_model:
        print("⚠️ Gemini model not available to parse video requirements.")
        return None

    prompt = f"""
From the following user description, extract a JSON object with:
- "query": string
- "text_overlay": string
- "font": string
- "transition": string
- "resolution": "480p", "720p", or "1080p"
- "duration": integer (in seconds, default 3)
- "num_clips": integer (1–5, default 3)
- "text_position": "top", "center", or "bottom"
- "text_size": integer (default 40)
- "fps": integer (default 30)
- "with_audio": boolean (true if audio narration is wanted, false otherwise, default true)

Text:
\"\"\"{user_input}\"\"\"

Return only JSON.
"""

    response = gemini_model.generate_content(prompt)
    text = response.text.strip()
    if text.startswith("```"):
        # Remove markdown code fences if present
        lines = text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        print("⚠️ Failed to parse JSON:", text)
        return None


def generate_video(
    user_query,
    text_overlay="",
    font="Arial",
    transition="fade",
    resolution="480p",
    duration=3,
    num_clips=3,
    text_position="center",
    text_size=40,
    fps=30,
    output_path="output_video.mp4",
    with_audio=True
):
    script_code = VIDEO_SCRIPT_TEMPLATE.format(
        user_query=user_query.replace('"', '\\"'),
        text_overlay=text_overlay.replace('"', '\\"'),
        font=font,
        transition=transition,
        resolution=resolution,
        duration=duration,
        num_clips=num_clips,
        text_position=text_position,
        text_size=text_size,
        fps=fps,
        output_path=output_path,
        with_audio=with_audio,   # Pass boolean as string "True" or "False"
        gemini_api_key=GEMINI_API_KEY
    )

    success = run_script_with_retry(script_code)
    return output_path if success else None


if __name__ == "__main__":
    user_input = input("Describe your video requirements:\n")
    params = parse_video_requirements(user_input) or {}

    video_file = generate_video(
        user_query=params.get("query", "nature"),
        text_overlay=params.get("text_overlay", ""),
        font=params.get("font", "Arial"),
        transition=params.get("transition", "fade"),
        resolution=params.get("resolution", "480p"),
        duration=params.get("duration", 3),
        num_clips=params.get("num_clips", 3),
        text_position=params.get("text_position", "center"),
        text_size=params.get("text_size", 40),
        fps=params.get("fps", 30),
        with_audio=params.get("with_audio", True),  # <-- Here, set from params, default True
    )
    if video_file:
        print(f"🎉 Video created successfully: {video_file}")
    else:
        print("Failed to generate video.")


