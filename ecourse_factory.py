import os
import shutil
import json
import re
from datetime import datetime
import run_full_vso
import main
import shorts
from ai_helper import generate_ai_response
import api.telemetry as telemetry # 🏛️ [TELEMETRY] Global Heartbeat Hook

def generate_course_outline(topic, user_keys=None):
    """🎓 VANTIX Academy (v1.0): Generate organic course hierarchy"""
    print(f"🧠 [OUTLINE] Orchestrating organic course structure for: {topic}")
    prompt = f"""
    Create a comprehensive and structured video course outline for: "{topic}".
    The course must be high-value, educational, and cinematic.
    
    Structure it exactly like this (plain text):
    Chapter [Number]: [Chapter Title]
    - Lesson [Number]: [Lesson Title]
    
    Chapter [Number]: [Chapter Title]
    - Lesson [Number]: [Lesson Title]
    
    Be flexible. If the topic is complex, add more chapters/lessons. If simple, keep it tight.
    No strict bounding. Provide exactly what is needed for a masterpiece.
    """
    try:
        response = generate_ai_response(prompt, user_keys=user_keys)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Outline Generation Failed: {e}")
        return ""

# ... existing parse_outline ...

def generate_lesson_script(topic, chapter_title, lesson_title, user_keys=None):
    """🎓 VANTIX Academy (v1.0): Generate High-Retention Lesson Script"""
    print(f"🎙️ [SCRIPT] Synthesizing Viral Narrative for Lesson: {lesson_title}")
    
    # We use a specialized educational prompt for courses
    prompt = f"""
    Write a 60-90 second educational video script.
    Course: {topic}
    Chapter: {chapter_title}
    Lesson: {lesson_title}
    
    CRITICAL:
    1. Start with a massive hook related to this LESSON.
    2. Deliver dense, high-value information. 
    3. Paragraph format only. No labels, no bold.
    4. Focus on deep understanding + immediate practical value.
    """
    try:
        # Use centralized intelligence with custom educational prompt
        response = generate_ai_response(prompt, user_keys=user_keys)
        return response.text.strip()
    except Exception as e:
        print(f"❌ Script Generation Failed for {lesson_title}: {e}")
        return ""

def run_ecourse_factory(topic, horizontal=False, include_avatar=False, user_keys=None, job_id=None, output_dir=None, **kwargs):
    if job_id: telemetry.update_progress(job_id, "Drafting Academy Outline")
    """🚀 VANTIX Academy (v1.0): Master Orchestration Loop"""
    print(f"🏗️ [FACTORY] Initializing Vantix Academy Production: {topic}")
    
    # 🛡️ [PATH SENTINEL] Ensure output_dir exists
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # ... (rest of resolution and avatar print)
    print(f"📐 [LAYOUT] Resolution: {'Horizontal (16:9)' if horizontal else 'Vertical (9:16)'}")
    print(f"👤 [AVATAR] Synergy: {'ENABLED' if include_avatar else 'DISABLED'}")
    
    # 1. Generate Outline
    outline_text = generate_course_outline(topic, user_keys=user_keys)
    if not outline_text: return
    
    outline = parse_outline(outline_text)
    if not outline:
        print("❌ Could not parse outline format.")
        return
        
    # 2. Setup Course Directory
    safe_topic = re.sub(r'[^a-zA-Z0-9]', '_', topic)
    folder_name = f"{safe_topic}_{datetime.now().strftime('%Y%m%d')}"
    course_root = os.path.join(output_dir, folder_name) if output_dir else os.path.join("courses", folder_name)
    os.makedirs(course_root, exist_ok=True)
    
    # Save outline for reference
    with open(os.path.join(course_root, "outline.txt"), "w") as f:
        f.write(outline_text)
        
    print(f"✅ Course Root Established: {course_root}")
    
    # 3. Recursive Production Loop (Parallel Lesson Synthesis)
    for chap_key, details in outline.items():
        chap_dir = os.path.join(course_root, chap_key.replace(" ", "_"))
        os.makedirs(chap_dir, exist_ok=True)
        
        print(f"\n📘 [CHAPTER] Starting {chap_key}: {details['title']} (PARALLEL)")
        
        def process_lesson(i, lesson_title):
            lesson_idx = i + 1
            print(f"🎬 [PARALLEL] Producing Lesson {lesson_idx}: {lesson_title}")
            
            # A. Generate Script
            script = generate_lesson_script(topic, details["title"], lesson_title, user_keys=user_keys)
            if not script: return None
            
            # B. Produce Video
            try:
                final_video_path = run_full_vso.run_full_vso(
                    forced_script=script,
                    forced_topic=f"{topic} {lesson_title}",
                    forced_avatar=include_avatar,
                    horizontal=horizontal,
                    user_keys=user_keys,
                    job_id=job_id # 💓 [TELEMETRY] Restore live progress tracking
                )
                
                if final_video_path and os.path.exists(final_video_path):
                    target_name = f"Lesson_{lesson_idx}_{re.sub(r'[^a-zA-Z0-9]', '_', lesson_title)}.mp4"
                    target_path = os.path.join(chap_dir, target_name)
                    shutil.copy(final_video_path, target_path)
                    print(f"✅ [SUCCESS] Lesson {lesson_idx} Mastered: {target_path}")
                    return target_path
                return None
            except Exception as e:
                print(f"❌ [CRITICAL] Lesson {lesson_idx} failed: {e}")
                return None

        # Process all lessons in this chapter in parallel (Capped at 2 for intense rendering)
        from parallel_helper import ParallelOrchestrator
        orch = ParallelOrchestrator(max_workers=2) 
        orch.parallel_map_indexed(process_lesson, details["lessons"], task_name="Lesson Production")
                
    print(f"\n🏁 [COMPLETED] Vantix Academy Factory has mastered the series: {topic}")
    print(f"📍 Location: {course_root}")
    return course_root

if __name__ == "__main__":
    import sys
    topic = input("🎯 Enter Course Topic: ").strip() if len(sys.argv) < 2 else sys.argv[1]
    
    orient = input("📐 Resolution: (h)orizontal or (v)ertical: ").strip().lower()
    h_flag = (orient == 'h')
    
    av_choice = input("👤 Include AI Avatar Synergy? (y/n): ").strip().lower()
    av_flag = (av_choice == 'y')
    
    run_ecourse_factory(topic, horizontal=h_flag, include_avatar=av_flag)
