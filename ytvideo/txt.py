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
        generate_tts_audio(text, audio_path)
        update_character_count(text)
        audio_clip = AudioFileClip(audio_path)

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

        # Resize and crop to 1080x1920 (YouTube Shorts)
        target_aspect = 1080 / 1920
        actual_aspect = raw_clip.w / raw_clip.h

        if abs(actual_aspect - target_aspect) < 0.01:
            clip = raw_clip.resize((1080, 1920))
        elif actual_aspect > target_aspect:
            # Video is wider → crop width
            clip = raw_clip.resize(height=1920)
            x_center = clip.w / 2
            clip = clip.crop(x1=x_center - 540, x2=x_center + 540, y1=0, y2=1920)
        else:
            # Video is taller → crop height
            clip = raw_clip.resize(width=1080)
            y_center = clip.h / 2
            clip = clip.crop(x1=0, x2=1080, y1=y_center - 960, y2=y_center + 960)

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
        break  # Exit the loop after finding one suitable video
    else:
        # Close raw_clip if no break happens (no suitable video found)
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

            # Resize & crop to 1080x1920 (portrait for YouTube Shorts)
            target_aspect = 1080 / 1920
            actual_aspect = raw_clip.w / raw_clip.h

            if abs(actual_aspect - target_aspect) < 0.01:
                clip = raw_clip.resize((1080, 1920))
            elif actual_aspect > target_aspect:
                # Video is wider → crop width
                clip = raw_clip.resize(height=1920)
                x_center = clip.w / 2
                clip = clip.crop(x1=x_center - 540, x2=x_center + 540, y1=0, y2=1920)
            else:
                # Video is taller → crop height
                clip = raw_clip.resize(width=1080)
                y_center = clip.h / 2
                clip = clip.crop(x1=0, x2=1080, y1=y_center - 960, y2=y_center + 960)

            clip = clip.set_fps(30)
            collected_clips.append(clip)
            new_used_urls.append(video_url)
            total_collected += clip.duration
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
   

    # 4) Run WhisperX to get word-level timings
    try:
        import whisperx
        device = "cpu"
        model = whisperx.load_model("tiny.en", device=device, compute_type="float32")
        result = model.transcribe(audio_path)

        align_model, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
        aligned_result = whisperx.align(result["segments"], align_model, metadata, audio_path, device)

        word_segments = aligned_result["word_segments"]
        # text1=remove_stopwords_and_punctuation(text)
        # word_segments = clean_text_to_match_timestamps(text1, word_segments)
        subtitle = create_word_by_word_subtitles(word_segments, video_size=(1080, 1920))


    except Exception as e:
        print(f"❌ WhisperX failed: {e}")
        subtitle = None


    if subtitle:
        final_scene = CompositeVideoClip([final_video, subtitle])
    else:
        final_scene = final_video

    final_scene = final_scene.set_duration(audio_duration)
    return final_scene, new_used_urls



import random
from moviepy.editor import VideoFileClip, concatenate_videoclips

import random

def crossfade_out(clip, duration):
    def opacity(t):
        if t < clip.duration - duration:
            return 1
        else:
            return max(0, 1 - (t - (clip.duration - duration)) / duration)
    return clip.fl(lambda gf, t: gf(t) * opacity(t), apply_to=['mask'])

def crossfade_in(clip, duration):
    def opacity(t):
        if t < duration:
            return min(1, t / duration)
        else:
            return 1
    return clip.fl(lambda gf, t: gf(t) * opacity(t), apply_to=['mask'])



def fade_out_effect(clip, duration):
    return crossfade_out(clip, duration)

def fade_in_effect(clip, duration):
    return crossfade_in(clip, duration)

def zoom_out_effect(clip, duration):
    start = clip.duration - duration
    def zoom(t):
        t = max(start, min(t, clip.duration))  # Clamp t
        return max(0.1, 1 - 0.3 * ((t - start) / duration))
    return clip.resize(lambda t: zoom(t))

def zoom_in_effect(clip, duration):
    def zoom(t):
        t = max(0, min(t, duration))  # Clamp t
        return max(0.1, 0.7 + 0.3 * (t / duration))
    return clip.resize(lambda t: zoom(t))

def slide_fade_out(clip, duration, side='left'):
    w, h = clip.size
    def position(t):
        delta = min(max(t / duration, 0), 1)
        if side == 'left':
            return (-w * delta, 0)
        elif side == 'right':
            return (w * delta, 0)
        elif side == 'top':
            return (0, -h * delta)
        else:
            return (0, h * delta)
    return clip.set_position(position).fadeout(duration).set_duration(duration)

def slide_fade_in(clip, duration, side='right'):
    w, h = clip.size
    def position(t):
        delta = min(max(1 - (t / duration), 0), 1)
        if side == 'left':
            return (-w * delta, 0)
        elif side == 'right':
            return (w * delta, 0)
        elif side == 'top':
            return (0, -h * delta)
        else:
            return (0, h * delta)
    return clip.set_position(position).fadein(duration).set_duration(duration)

def rotate_out_effect(clip, duration):
    start = clip.duration - duration
    def rot(t):
        t = max(start, min(t, clip.duration))
        return 360 * ((t - start) / duration)
    return clip.rotate(rot)

def rotate_in_effect(clip, duration):
    def rot(t):
        t = max(0, min(t, duration))
        return -360 * (t / duration)
    return clip.rotate(rot)

# Random slide directions
def slide_out(clip, duration):
    side = random.choice(['left', 'right', 'top', 'bottom'])
    w, h = clip.size
    def position(t):
        delta = min(max(t / duration, 0), 1)
        if side == 'left':
            return (-w * delta, 0)
        elif side == 'right':
            return (w * delta, 0)
        elif side == 'top':
            return (0, -h * delta)
        else:
            return (0, h * delta)
    return clip.set_duration(duration).set_position(position)

def slide_in(clip, duration):
    side = random.choice(['left', 'right', 'top', 'bottom'])
    w, h = clip.size
    def position(t):
        delta = min(max(1 - (t / duration), 0), 1)
        if side == 'left':
            return (-w * delta, 0)
        elif side == 'right':
            return (w * delta, 0)
        elif side == 'top':
            return (0, -h * delta)
        else:
            return (0, h * delta)
    return clip.set_duration(duration).set_position(position)

def slide_fade_out_random(clip, duration):
    return slide_out(clip.fadeout(duration), duration)

def slide_fade_in_random(clip, duration):
    return slide_in(clip.fadein(duration), duration)

def zoom_fade_out(clip, duration):
    return clip.resize(lambda t: max(0.1, 1 - 0.3 * (t / duration))).crossfadeout(duration)

def zoom_fade_in(clip, duration):
    return clip.resize(lambda t: max(0.1, 0.7 + 0.3 * (t / duration))).crossfadein(duration)

def slide_fade_out_top(clip, duration):
    return clip.fx(slide_out, duration=duration, side='top').crossfadeout(duration)

def slide_fade_in_bottom(clip, duration):
    return clip.fx(slide_in, duration=duration, side='bottom').crossfadein(duration)

def rotate_fade_out(clip, duration):
    return clip.rotate(lambda t: 20 * (t / duration)).crossfadeout(duration)

def rotate_fade_in(clip, duration):
    return clip.rotate(lambda t: -20 + 20 * (t / duration)).crossfadein(duration)

# Safe split transition function
def split_transition(clip1, clip2, transition_duration=2, effect_out=None, effect_in=None):
    half = transition_duration / 2
    half = min(half, clip1.duration / 2, clip2.duration / 2)  # Ensure safe timing
    c1 = effect_out(clip1, half)
    c2 = effect_in(clip2, half)
    return concatenate_videoclips([c1, c2], method="compose")

from moviepy.editor import VideoFileClip, concatenate_videoclips
import random

# Assuming your existing effect functions (fade_out_effect, zoom_out_effect, etc.)
# and your `transitions` list are defined elsewhere in your code as provided.

def split_transition(clip1, clip2, transition_duration=2, effect_out_func=None, effect_in_func=None):
    """
    Applies an outgoing effect to clip1 and an incoming effect to clip2,
    then combines them with a crossfade for a seamless transition.

    Args:
        clip1 (VideoFileClip): The first video clip.
        clip2 (VideoFileClip): The second video clip.
        transition_duration (int/float): The duration of the transition in seconds.
        effect_out_func (function, optional): The function to apply as an outgoing effect on clip1.
        effect_in_func (function, optional): The function to apply as an incoming effect on clip2.

    Returns:
        VideoFileClip: A single clip representing clip1 transitioning into clip2.
    """
    # Ensure transition duration is safe and doesn't exceed half of either clip's duration.
    # This prevents errors if clips are shorter than the desired transition.
    t_dur = min(transition_duration, clip1.duration / 2, clip2.duration / 2)
    if t_dur < 0.1:  # Use a small epsilon for a noticeable transition
        print(f"⚠️ Transition duration too short or clips too short for effective transition. Concatenating without crossfade.")
        return concatenate_videoclips([clip1, clip2], method="compose")

    # Apply the "out" effect to clip1 *before* the crossfade.
    # Your effect functions should be designed to modify the clip's behavior over its own duration.
    if effect_out_func:
        clip1_fx = effect_out_func(clip1, t_dur)
    else:
        clip1_fx = clip1

    # Apply the "in" effect to clip2 *before* the crossfade.
    if effect_in_func:
        clip2_fx = effect_in_func(clip2, t_dur)
    else:
        clip2_fx = clip2

    # Use MoviePy's crossfade to blend the end of the first clip with the beginning of the second.
    # The `+` operator with `crossfadeout` and `crossfadein` automatically handles the overlap.
    return clip1_fx.crossfadeout(t_dur) + clip2_fx.crossfadein(t_dur)
# List of transitions to pick randomly (pairs of out/in effects)

transitions = [
    (fade_out_effect, fade_in_effect),
    (slide_fade_out_random,slide_fade_in_random),
    (zoom_out_effect, zoom_in_effect),
    (crossfade_out, crossfade_in),
    (rotate_out_effect, rotate_in_effect),
    (zoom_fade_out,zoom_fade_in),
    (slide_fade_out,slide_fade_in),
    (rotate_fade_out,rotate_fade_in)
]


# Main function to apply random transitions on clip list:

# def make_video_with_random_transitions(clips, transition_duration=2):
#     final_clips = []
#     for i in range(len(clips)-1):
#         clip1 = clips[i]
#         clip2 = clips[i+1]
#         effect_out, effect_in = random.choice(transitions)
#         transitioned = split_transition(clip1, clip2, transition_duration, effect_out, effect_in)
#         final_clips.append(transitioned)
#     # The last clip does not have transition after it, add separately if needed
#     if len(clips) > 0:
#         final_clips.append(clips[-1])
    
    # Concatenate all results (these are already concatenated pairs)
    # We have overlapping pairs, so combine carefully by removing duplicates:
    # Because split_transition returns clip1+clip2 concatenated,
    # consecutive calls overlap clips, so let's just concatenate the first one fully
    # and then append the last clip without transition
    
    # Or, better approach: build full final video by chaining transitions manually:
    
    # Instead of multiple pairs, do a chain:
    
def chain_transitions(clips, transition_duration=2):
    current = clips[0]
    for i in range(1, len(clips)):
        effect_out, effect_in = random.choice(transitions)
        current = split_transition(current, clips[i], transition_duration, effect_out, effect_in)
    return current

# Usage:
# final_video = concatenate_with_random_transitions(your_clip_list, transition_duration=1)




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
def create_video_from_script(script, user_topic):
    import os
    import subprocess
    import uuid
    from nltk.tokenize import sent_tokenize
    from moviepy.editor import (
        VideoFileClip, concatenate_videoclips,
        AudioFileClip, CompositeAudioClip
    )
    from moviepy.audio.fx.all import audio_loop
    from datetime import datetime

    sentences = sent_tokenize(script)
    used_video_urls = set()
    scene_clips = []
    all_used_urls = set()

    output_dir = "video_created"
    os.makedirs(output_dir, exist_ok=True)

    print(f"🎞️ Total scenes to generate: {len(sentences)}")

    # === Generate scenes ===
    for idx, sentence in enumerate(sentences):
        print(f"\n🔹 Processing Scene {idx + 1}/{len(sentences)}: {sentence}")
        scene_clip, scene_urls = create_scene(sentence, idx, used_video_urls, user_topic)

        if scene_clip is None:
            print(f"⚠️ Skipping Scene {idx + 1} (No clip returned)")
            continue

        if not hasattr(scene_clip, 'duration'):
            print(f"⚠️ Invalid clip (missing duration) at index {idx}. Skipping.")
            continue

        scene_clips.append(scene_clip)
        all_used_urls.update(scene_urls)

    print("\n✅ All used URLs:", all_used_urls)

    if not scene_clips:
        print("❌ No valid scenes generated. Cannot proceed with final video.")
        return None, None

    # === Concatenate valid video clips ===

    try:
        final_clip = chain_transitions(scene_clips, transition_duration=1)
    except Exception as e:
        print(f"❌ Failed to concatenate clips: {e}")
        return None, None

    # === Add background music ===
    try:
        bg_music_raw = AudioFileClip("/Users/uday/Downloads/VIDEOYT/Cybernetic Dreams.mp3").volumex(0.08)
        bg_music_looped = audio_loop(bg_music_raw, duration=final_clip.duration).set_start(0)

        if final_clip.audio:
            final_audio = CompositeAudioClip([final_clip.audio.set_duration(final_clip.duration), bg_music_looped])
        else:
            final_audio = bg_music_looped

        final_clip = final_clip.set_audio(final_audio)
    except Exception as e:
        print(f"⚠️ Background music could not be applied: {e}")

    # === Output final video ===
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"video_{timestamp}.mp4"
    output_path = f"/Users/uday/Downloads/VIDEOYT/video_created/{output_filename}"


    try:
        final_clip.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="libmp3lame",
            fps=30,
            preset="ultrafast",
            threads=8,
            audio=True,
            logger="bar"
        )
        print(f"\n✅ Final video created at: {output_path}")
        return output_path, all_used_urls

    except Exception as e:
        print(f"❌ Failed to render final video: {e}")
        return None, None