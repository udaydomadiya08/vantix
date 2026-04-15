
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
    url = f"https://api.pexels.com/videos/search?query={search_term}&per_page={max_results}"
    headers = {"Authorization": PEXELS_API_KEY}
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
    local_path = os.path.join(folder, f"clip_{idx}.mp4")
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
    script_lines, output_path="output_video.mp4", font="",
    transition="", duration=3, resolution="720p",
    text_position="center", text_size=40, fps=30, num_clips=3, with_audio=True
):
    tmp_dir = "temp_clips"
    os.makedirs(tmp_dir, exist_ok=True)

    target_width, target_height = parse_resolution(resolution)
    clips = []

    for i, sentence in enumerate(script_lines[:num_clips]):
        videos = fetch_pexels_videos(sentence, max_results=1, target_height=target_height)
        if not videos:
            print(f"No videos found for sentence: {sentence}")
            continue

        video_path = download_video(videos[0], tmp_dir, i)
        raw_clip = VideoFileClip(video_path).subclip(0, duration)
        clip = resize_and_crop(raw_clip, target_width, target_height)

        if transition == "fade":
            clip = fadein(clip, 1).fx(fadeout, 1)

        if with_audio:
            tts = gTTS(sentence, lang="en")
            audio_path = os.path.join(tmp_dir, f"audio_{i}.mp3")
            tts.save(audio_path)  # Save audio before checking

            if os.path.getsize(audio_path) == 0:
                raise Exception(f"TTS failed, {audio_path} is empty.")

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
    user_input = "intro video on cropkart business brand"
    duration = 5
    font = ""
    resolution = "720p"
    text_position = "center"
    text_size = 40
    fps = 30
    num_clips = 3
    transition = ""
    output_path = "output_video.mp4"
    with_audio=True


    try:
        import google.generativeai as genai
        genai.configure(api_key="AIzaSyBRzQCetzqXL9aQDcQw8T2C0rnzRxIYTTw")
        gemini_model = genai.GenerativeModel(model_name='models/gemini-2.5-flash-preview-04-17-thinking')
    except Exception:
        gemini_model = None

    if "\n" in user_input or len(user_input.split()) > 15:
        script_text = user_input
    else:
        if gemini_model:
            prompt = f"Write a short video script about: {user_input}\nUse 3-5 short and catchy lines, only plain text script, no visuals or bold text."
            response = gemini_model.generate_content(prompt)
            script_text = response.text.strip()
        else:
            print("Error: Gemini model not available and no script provided.")
            sys.exit(1)

    script_lines = [line.strip() for line in script_text.split("\n") if line.strip()]
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
