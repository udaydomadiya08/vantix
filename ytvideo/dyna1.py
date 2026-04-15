import os
import sys
import subprocess
import requests
import json
import time
import google.generativeai as genai
from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    CompositeAudioClip,
    ImageClip,
)
from moviepy.video.fx.all import fadein, fadeout, crop, speedx
from gtts import gTTS

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

PEXELS_API_KEY = os.getenv(
    "PEXELS_API_KEY", "DGhCtAB83klpCIv5yq5kMIb2zun7q67IvHJysvW4lInb0WVXaQF2xLMu"
)
GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY", "AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw"
)

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(
    model_name="models/gemini-2.0-flash"
)

# ─── VIDEO SCRIPT TEMPLATE ─────────────────────────────────────────────────────

VIDEO_SCRIPT_TEMPLATE = """
import os
import sys
import requests
from moviepy.editor import (
    VideoFileClip,
    concatenate_videoclips,
    TextClip,
    CompositeVideoClip,
    AudioFileClip,
    CompositeAudioClip,
    ImageClip,
)
from moviepy.video.fx.all import fadein, fadeout, crop, speedx
from gtts import gTTS

PEXELS_API_KEY = "{pexels_api_key}"

def parse_resolution(res_str):
    res_str = res_str.lower().strip()
    aspect_ratio = 16 / 9
    if "x" in res_str:
        try:
            width, height = map(int, res_str.split("x"))
            return width, height
        except:
            pass
    elif res_str.endswith("p"):
        try:
            height = int(res_str[:-1])
            width = int(height * aspect_ratio)
            return width, height
        except:
            pass
    else:
        try:
            height = int(res_str)
            width = int(height * aspect_ratio)
            return width, height
        except:
            pass
    return 854, 480

def fetch_pexels_videos(search_term, max_results=3, target_height=480):
    url = "https://api.pexels.com/videos/search?query=" + search_term + "&per_page=" + str(max_results)
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
    os.makedirs(folder, exist_ok=True)
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
        return crop(
            clip,
            x1=x_center - target_width / 2,
            x2=x_center + target_width / 2,
            y1=0,
            y2=target_height
        )
    else:
        clip = clip.resize(width=target_width)
        y_center = clip.h / 2
        return crop(
            clip,
            x1=0,
            x2=target_width,
            y1=y_center - target_height / 2,
            y2=y_center + target_height / 2
        )

def create_video(
    script_lines,
    output_path="{output_path}",
    font="{font}",
    font_color="{font_color}",
    font_bold={font_bold},
    font_italic={font_italic},
    transition="{transition}",
    transition_duration={transition_duration},
    duration={duration},
    resolution="{resolution}",
    text_position="{text_position}",
    text_size={text_size},
    fps={fps},
    num_clips={num_clips},
    with_audio={with_audio},
    background_music="{background_music}",
    audio_volume={audio_volume},
    voiceover_text="{voiceover_text}",
    watermark_path="{watermark_path}"
):
    tmp_dir = "temp_clips"
    os.makedirs(tmp_dir, exist_ok=True)
    target_width, target_height = parse_resolution(resolution)
    clips = []

    bg_music = None
    if background_music and os.path.isfile(background_music):
        bg_music = AudioFileClip(background_music).volumex(audio_volume)

    for i, sentence in enumerate(script_lines[:num_clips]):
        videos = fetch_pexels_videos(sentence, max_results=1, target_height=target_height)
        if not videos:
            print(f"No videos found for: {{sentence}}")
            continue

        video_url = videos[0]
        video_path = download_video(video_url, tmp_dir, i)
        raw_clip = VideoFileClip(video_path).subclip(0, duration)
        clip = resize_and_crop(raw_clip, target_width, target_height)

        if transition == "fade":
            clip = fadein(clip, transition_duration).fx(fadeout, transition_duration)

        if with_audio:
            text_to_speak = voiceover_text if voiceover_text.strip() else sentence
            tts = gTTS(text=text_to_speak, lang="en")
            audio_mp3 = os.path.join(tmp_dir, f"audio_{{i}}.mp3")
            tts.save(audio_mp3)

            if not os.path.isfile(audio_mp3) or os.path.getsize(audio_mp3) == 0:
                raise Exception(f"TTS failed, {{audio_mp3}} is empty.")

            audio_clip = AudioFileClip(audio_mp3)
            if clip.duration > audio_clip.duration:
                clip = clip.subclip(0, audio_clip.duration)
            elif clip.duration < audio_clip.duration:
                speed_factor = clip.duration / audio_clip.duration
                clip = speedx(clip, speed_factor)
            audio_clip = audio_clip.subclip(0, clip.duration)

            if bg_music:
                bg_segment = bg_music.subclip(0, clip.duration)
                final_audio = CompositeAudioClip([bg_segment, audio_clip])
            else:
                final_audio = audio_clip
        else:
            final_audio = None

        style = font
        if font_bold and font_italic:
            style += "-BoldItalic"
        elif font_bold:
            style += "-Bold"
        elif font_italic:
            style += "-Italic"

        txt_clip = TextClip(
            sentence,
            fontsize=text_size,
            font=style,
            color=font_color,
            method="caption",
            size=(int(target_width * 0.8), None)
        ).set_duration(clip.duration).set_pos(text_position)

        if final_audio:
            comp = CompositeVideoClip([clip, txt_clip]).set_audio(final_audio).set_fps(fps)
        else:
            comp = CompositeVideoClip([clip, txt_clip]).set_fps(fps)

        if watermark_path and os.path.isfile(watermark_path):
            watermark = (
                ImageClip(watermark_path)
                .set_duration(comp.duration)
                .resize(width=int(target_width * 0.2))
                .set_pos(("right", "bottom"))
                .set_opacity(0.6)
            )
            comp = CompositeVideoClip([comp, watermark])

        clips.append(comp)

    if not clips:
        print("No clips created, exiting.")
        sys.exit(1)

    final_clip = concatenate_videoclips(clips, method="compose")
    final_clip.write_videofile(
        output_path,
        fps=fps,
        audio=True,
        codec="libx264",
        audio_codec="libmp3lame"
    )

if __name__ == "__main__":
    user_input = input("Describe your video requirements:\n").strip()
    # Dummy script lines for test
    create_video([user_input])
"""

# ─── SUPPORT FUNCTIONS ─────────────────────────────────────────────────────────

def call_gemini_api(error_msg, script_code):
    if not gemini_model:
        print("⚠️ Gemini model not available → returning original script.")
        return script_code

    prompt = (
        f"Fix the following Python script errors:\n\n"
        f"Error:\n{error_msg}\n\n"
        f"Code:\n{script_code}\n\n"
        "Return only the corrected Python code, no extra text."
    )
    response = gemini_model.generate_content(prompt)
    fixed = response.text.strip()

    if fixed.startswith("```"):
        lines = fixed.splitlines()
        if lines[0].startswith("```"):
            lines.pop(0)
        if lines and lines[-1].strip() == "```":
            lines.pop(-1)
        fixed = "\n".join(lines).strip()

    return fixed

def run_script_with_retry(script_code, script_path="generated_video_script.py"):
    with open(script_path, "w") as f:
        f.write(script_code)

    for attempt in range(3):
        try:
            print(f"Running generated script (attempt {attempt+1})…")
            subprocess.run(["python3", script_path], check=True, capture_output=True, text=True)
            print("Script ran successfully.")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Script failed with error:\n{e.stderr}")
            fixed_code = call_gemini_api(e.stderr, script_code)
            if fixed_code and fixed_code != script_code:
                print("Gemini fixed the script. Retrying…")
                script_code = fixed_code
                with open(script_path, "w") as f:
                    f.write(script_code)
            else:
                print("No fixes returned by Gemini or same code, aborting.")
                break
    return False

# ─── MAIN DYNAMIC GENERATOR ─────────────────────────────────────────────────────

def generate_video_code(
    user_query,
    text_overlay,
    voiceover_text,
    output_path="output_video.mp4",
    font="Arial",
    font_color="white",
    font_bold=False,
    font_italic=False,
    transition="fade",
    transition_duration=1,
    duration=4,
    resolution="480p",
    text_position="bottom",
    text_size=40,
    fps=24,
    num_clips=3,
    with_audio=True,
    background_music="",
    audio_volume=0.2,
    watermark_path=""
):
    # Use json.dumps to safely encode strings for embedding in Python source code
    safe_query = json.dumps(user_query)
    safe_text_overlay = json.dumps(text_overlay)
    safe_voiceover = json.dumps(voiceover_text if voiceover_text else "")

    code = VIDEO_SCRIPT_TEMPLATE.format(
        pexels_api_key=PEXELS_API_KEY,
        user_query=safe_query,
        text_overlay=safe_text_overlay,
        voiceover_text=safe_voiceover,
        output_path=output_path,
        font=font,
        font_color=font_color,
        font_bold=str(font_bold),
        font_italic=str(font_italic),
        transition=transition,
        transition_duration=transition_duration,
        duration=duration,
        resolution=resolution,
        text_position=text_position,
        text_size=text_size,
        fps=fps,
        num_clips=num_clips,
        with_audio=str(with_audio),
        background_music=background_music,
        audio_volume=audio_volume,
        watermark_path=watermark_path
    )
    return code

# ─── USAGE EXAMPLE ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Welcome! Enter your video query and options.")
    user_query = input("Search query for videos: ").strip()
    text_overlay = input("Text overlay on video: ").strip()
    voiceover_text = input("Voiceover text (optional, leave empty for no voiceover): ").strip()

    script_code = generate_video_code(
        user_query=user_query,
        text_overlay=text_overlay,
        voiceover_text=voiceover_text,
        output_path="output_video.mp4",
        font="Arial",
        font_color="white",
        font_bold=False,
        font_italic=False,
        transition="fade",
        transition_duration=1,
        duration=4,
        resolution="480p",
        text_position="bottom",
        text_size=40,
        fps=24,
        num_clips=3,
        with_audio=bool(voiceover_text),
        background_music="",
        audio_volume=0.2,
        watermark_path=""
    )

    success = run_script_with_retry(script_code)
    if success:
        print("🎉 Video created successfully: output_video.mp4")
    else:
        print("❌ Video creation failed after retries.")

