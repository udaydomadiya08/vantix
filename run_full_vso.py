import os
import sys

# 🏛️ PROJECT ROOT SYNCHRONIZATION (v1.0)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
import omni_engine as main
import shorts
from parallel_helper import ParallelOrchestrator
import subprocess
from datetime import datetime
from moviepy.editor import concatenate_videoclips

# Use Ollama locally for absolute sovereignty
os.environ["USE_OLLAMA_FIRST"] = "true"
def run_full_vso(forced_script=None, forced_topic=None, forced_avatar=None, horizontal=False, user_keys=None, intensity=None, **kwargs):
    """👑 VANTIX BATCH FACTORY (v1.0): Integrated VSO Orchestrator"""
    print("🚀 INITIALIZING FULL VANTIX PRODUCTION...")
    shorts.set_orientation(horizontal) # 📐 [ENGINE] Set resolution before production
    shorts.GLOBAL_USED_URLS.clear() # 💥 HARD RESET (v45.6): Zero reuse within this run
    
    # Logic to determine script and topic
    if forced_script or forced_topic:
        script = forced_script
        topic = forced_topic or "Vantix Batch"
        include_avatar = forced_avatar if forced_avatar is not None else False
        choice = "FORCE"
    elif os.environ.get("FORCE_SCRIPT"):
        script = os.environ.get("FORCE_SCRIPT")
        topic = "Vantix Test"
        include_avatar = (os.environ.get("FORCE_AVATAR") == "y")
        print(f"🤖 Vantix Test Mode: Script length={len(script)} characters.")
        choice = "FORCE" 
    elif len(sys.argv) > 1:
        choice = sys.argv[1]
        topic = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "life on mars"
        print(f"🤖 Automation Mode: Choice={choice}, Topic={topic}")
        include_avatar = False 
    else:
        print("🎬 How would you like to create your video?")
        print("1. Enter a Topic (The Viral Critic AI will write the script)")
        print("2. Paste your own Script")
        print("3. Let AI Pick a Niche Topic (Cosmic, Future, Finance, etc.)")
        print("4. Let AI Search Trending Topics (Real-time Global Trends)")
        choice = input("👉 Enter 1, 2, 3, or 4: ").strip()
        
        topic = ""
        if choice == "1":
            topic = input("🎯 Enter your video topic: ").strip().lower()
        elif choice == "3":
            print("🤖 Engaging Niche-Specific Intelligence...")
            topic = main.get_niche_topic()
        elif choice == "4":
            print("🌐 Engaging Global-Trending Intelligence via SerpAPI...")
            topic = main.get_trending_topic()
            print(f"🔥 Trending Topic Found: {topic}")
        
        print("\n🎬 High-Retention Branding:")
        ans = input("👤 Include AI Avatar (Wav2Lip Lip-Sync)? (y/n): ").strip().lower()
        include_avatar = (ans == 'y')
        
        print("\n⚡ Neural Pacing Control (v46.1):")
        print("0.0 = Cinematic/Stable (3s+ cuts)")
        print("0.5 = Professional/Balanced (1.5s - 2.5s cuts)")
        print("1.0 = Viral/Hyper-Active (0.8s - 1.5s cuts)")
        try:
            p_val = input("📈 Enter Intensity (0.0 to 1.0) [Default 1.0]: ").strip()
            shorts.PACING_INTENSITY = float(p_val) if p_val else 1.0
        except:
            shorts.PACING_INTENSITY = 1.0
        
    avatar_sync_path = None
    if include_avatar:
        # Determine avatar image based on voice gender (default male)
        avatar_path = "static/avatars/male_avatar.png"
        if os.path.exists(avatar_path):
             print(f"✅ AI Avatar (Male) selected for Wav2Lip sync.")
        else:
             print("⚠️ Avatar image not found. Proceeding without.")
             include_avatar = False

    if choice in ["1", "3", "4"]:
        if not topic:
            topic = input("🎯 Enter your video topic: ").strip()
        print(f"🧠 Orchestrating Viral Critic Loop for: {topic}")
        script = main.generate_vantix_script(topic, user_keys=user_keys)

    elif choice == "2":
        topic = "Custom Script Entry"
        print("📝 Enter your script below. Press Enter twice to finish.")
        user_script_lines = []
        while True:
            try:
                line = input()
                if line.strip() == "":
                    break
                user_script_lines.append(line)
            except EOFError:
                break
            except KeyboardInterrupt:
                break
        script = "\n".join(user_script_lines)
    elif choice == "FORCE":
        if not script:
            print(f"🧠 [API] Orchestrating Viral Critic Loop for: {topic}")
            script = main.generate_vantix_script(topic, user_keys=user_keys)
    else:
        print("❌ Invalid choice. Exiting.")
        return
        
    print(f"\n✨ FULL SCRIPT TO BE PROCESSED:\n{script}\n")
    
    # 2. Get Voiceover & Visuals natively split into sentences/scenes
    print("🎙️ Generating Voiceover & Visuals...")
    
    import nltk
    from nltk.tokenize import sent_tokenize
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
        
    sentences = sent_tokenize(script)
    if not sentences:
        import re
        sentences = [s.strip() for s in re.split(r'[.!?]\s+', script) if s.strip()]
    
    print(f"🧠 Script Tokenized into {len(sentences)} scenes.")
    total_urls = set()
    
    # ⚡ LIGHTNING ASSEMBLY (v57): Eliminate Global Pool for Speed
    # We no longer pre-fetch 40 clips. We discover them JIT per scene.
    topic_pool = [] 
    
    final_clips = []
    clean_voiceover_files = []
    
    def process_scene(i, sentence):
        sentence = sentence.strip()
        if not sentence: return None
        print(f"🎬 [PARALLEL] Orchestrating Scene {i+1}/{len(sentences)}...")
        try:
            # Discover & Produce Scene
            scene_clip, scene_urls = shorts.create_scene(
                sentence, i, total_urls.copy(), topic, max_clips=5, topic_pool=topic_pool, 
                include_avatar=include_avatar, horizontal=horizontal, user_keys=user_keys, 
                intensity=intensity, visual_source=kwargs.get("visual_source", "pexels"), 
                voice_id=kwargs.get("voice_id", "alloy")
            )
            
            if scene_clip:
                audio_path = f"audio/scene_{i}.mp3"
                return {"clip": scene_clip, "urls": scene_urls or set(), "audio": audio_path if os.path.exists(audio_path) else None}
            return None
        except Exception as e:
            print(f"⚠️ Scene {i+1} Failed: {e}")
            return None

    # Execute Parallel Scene Production (Max workers 3 to respect Resource Boundaries)
    orch = ParallelOrchestrator(max_workers=3)
    parallel_results = orch.parallel_map_indexed(process_scene, sentences, task_name="Scene")
    
    # Assemble in Sequence
    for res in parallel_results:
        if res:
            final_clips.append(res["clip"])
            if res["urls"]:
                total_urls.update(res["urls"])
            if res["audio"]:
                clean_voiceover_files.append(res["audio"])
            
    # Concatenate Clean Voiceover for Wav2Lip
    master_voiceover = "audio/master_narration.mp3"
    avatar_sync_path = None
    if include_avatar and clean_voiceover_files:
        print("🎙️ Concatenating Clean Voiceover for AI Lip-Sync...")
        from moviepy.audio.AudioClip import concatenate_audioclips
        from moviepy.editor import AudioFileClip
        audio_clips = [AudioFileClip(f) for f in clean_voiceover_files]
        final_audio_conc = concatenate_audioclips(audio_clips)
        final_audio_conc.write_audiofile(master_voiceover, logger=None)
        for c in audio_clips: c.close()
        
        # Call Wav2Lip via create_avatar bridge
        print("🧠 Invoking Wav2Lip Inference (This may take a moment)...")
        try:
            from create_avatar import create_avatar_video
            avatar_sync_output = os.path.join(PROJECT_ROOT, "video_creation/avatar_synced.mp4")
            
            success = create_avatar_video(
                face_video_path=avatar_path,
                audio_path=master_voiceover,
                output_path=avatar_sync_output,
                static=True,
                batch_size=128,
                out_height=1080
            )
            if success:
                avatar_sync_path = avatar_sync_output
                print("✅ Wav2Lip Lip-Sync generated successfully.")
            else:
                print("⚠️ Wav2Lip failed. Falling back to no avatar.")
                include_avatar = False
        except Exception as e:
            print(f"⚠️ Wav2Lip Bridge error: {e}")
            include_avatar = False

    # 3. Assemble and Finalize
    if not final_clips:
        print("\n❌ ERROR: No scenes were successfully processed. Visual engine failed to produce content.")
        print("💡 Suggestion: Check terminal logs for API or resource failures.")
        return

    # method='chain' is much more stable in MoviePy 1.0.3 for sequential scene joining
    final_video = concatenate_videoclips(final_clips, method="chain")
    
    # ⚡ VANTIX BATCH NAMING: Use timestamp for non-test runs
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_temp = os.path.join(PROJECT_ROOT, "static/videos", f"temp_{ts}.mp4")
    output_path = os.path.join(PROJECT_ROOT, "static/videos", f"vantix_{ts}.mp4")
    
    # Export the main video first
    print("\n🎬 [PHASE 4/4] Starting Final Master Render...")
    # ⚡ LIGHTNING ASSEMBLY (v57/v58): 8-Thread Hardware Optimization
    final_video.write_videofile(
        output_temp, 
        fps=30, 
        codec="libx264", 
        audio_codec="aac", 
        temp_audiofile=os.path.join(PROJECT_ROOT, "temp_audio.m4a"), 
        remove_temp=True,
        threads=8,
        preset="ultrafast",
        logger=None
    )

    # Apply Mandatory AI Avatar Lip-Sync Overlay using raw ffmpeg
    if include_avatar and avatar_sync_path and os.path.exists(avatar_sync_path):
        print(f"👄 Applying AI Avatar Lip-Sync Overlay: {os.path.basename(avatar_sync_path)}...")
        
        ffmpeg_cmd = [
            "ffmpeg", "-y",
            "-i", output_temp,
            "-i", avatar_sync_path,
            "-filter_complex",
            "[1:v]scale=450:600[av];[0:v][av]overlay=W-w-10:H-h-10[outv]",
            "-map", "[outv]",
            "-map", "0:a", # Keep original mixed audio (Music + Voice)
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-c:a", "copy",
            output_path
        ]
        
        try:
            subprocess.run(ffmpeg_cmd, check=True)
            print("✅ AI Avatar Lip-Sync overlay applied successfully via ffmpeg.")
            os.remove(output_temp) # cleanup temp master
        except Exception as e:
            print(f"⚠️ Failed to apply avatar overlay via ffmpeg: {e}")
            os.rename(output_temp, output_path) # Fallback to master without avatar
    else:
        if include_avatar:
             print("⚠️ Skipping Avatar: Lip-sync generation failed or was invalid.")
        os.rename(output_temp, output_path)

    # 💥 CINEMATIC MASTERING (v56): Final Technical Finalizer for 100% Playability
    mastered_output = output_path.replace(".mp4", "_mastered.mp4")
    shorts.technical_mastering(output_path, mastered_output)
    
    # Final swap to ensure the main path is the mastered one
    if os.path.exists(mastered_output):
         os.rename(mastered_output, output_path)
    
    # Final cleanup (v43.1): Removed aggressive directory wipe to prevent race conditions.
    print("🧹 Production Cycle Complete.")
    print(f"\n👑 VANTIX FULL PRODUCTION READY: {output_path}")
    return output_path


if __name__ == "__main__":
    run_full_vso()
