import os
import re
import shutil
import subprocess
import json
import requests
import time
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import concurrent.futures
from ai_helper import generate_ai_response, generate_ebook_theme, generate_image_asset

# === CONFIGURATION === #
BRAND_NAME = ""
CTA_BASE = "https://github.com/udaydomadiya08"
INCLUDE_IMAGES = True        # Master toggle for all image generation
INCLUDE_CHAPTER_ART = True  # Toggle for chapter-specific art
NUM_CHAPTERS = 3            # Masterpiece volume
MIN_WORDS_PER_SECTION = 150 # High-velocity calibration

def sanitize_unicode(text):
    """Sanitize non-Latin-1 characters for FPDF helvetica compatibility."""
    if not text: return ""
    replacements = {
        "\u2013": "-",   # en dash
        "\u2014": "--",  # em dash
        "\u201c": '"',   # smart quote left
        "\u201d": '"',   # smart quote right
        "\u2018": "'",   # smart quote single left
        "\u2019": "'",   # smart quote single right
        "\u2022": "*",   # bullet
        "\u2026": "..."  # ellipsis
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    return text.encode("latin-1", "replace").decode("latin-1")

def hex_to_rgb(hex_str):
    """Convert hex string (#RRGGBB) to (R, G, B) list."""
    if not isinstance(hex_str, str) or not hex_str.startswith("#"):
        return hex_str if isinstance(hex_str, list) else [0, 0, 0]
    hex_str = hex_str.lstrip('#')
    return [int(hex_str[i:i+2], 16) for i in (0, 2, 4)]

def download_asset(url, save_path):
    """Download an asset from a URL (e.g., AI-generated image)."""
    if not url: return False
    try:
        print(f"📥 [DOWNLOADING] Asset from: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"❌ [DOWNLOADING] Failed: {e}")
        return False

def generate_subsections(topic, chapter_title, description="", user_keys=None):
    prompt = f"""
    [GOD-MODE SYNTHESIS] 
    Topic: {topic}
    Description: {description}
    Chapter: {chapter_title}
    
    Task: Determine how many subsections this chapter needs to be exhaustive. Return their titles.
    Format: Plain text, one title per line. No bold.
    """
    response = generate_ai_response(prompt, user_keys=user_keys)
    subsections = [line.strip() for line in response.text.split('\n') if line.strip()]
    return subsections

def generate_subsection_content(topic, chapter_title, subsection_title, description="", tone="Expert", user_keys=None):
    # Pacing is handled in ai_helper
    prompt = f"""
    [GOD-MODE LITERARY SYNTHESIS]
    Topic: {topic}
    Description: {description}
    Chapter: {chapter_title}
    Section: {subsection_title}
    Tone: {tone}
    
    Strategy: PAS + Storytelling.
    CRITICAL: Minimum {MIN_WORDS_PER_SECTION} words. Plain text only.
    """
    response = generate_ai_response(prompt, user_keys=user_keys)
    return response.text.strip()

def build_chapter_with_subsections(topic, chapter_title, description="", tone="Expert", user_keys=None):
    subsections = generate_subsections(topic, chapter_title, description, user_keys=user_keys)
    full_content = ""
    
    print(f"🚀 [PARALLEL] Synthesizing {len(subsections)} sections for '{chapter_title}' (Max Workers: 3)...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(3, len(subsections))) as executor:
        # Create a dictionary of future to subsection title
        future_to_sub = {
            executor.submit(generate_subsection_content, topic, chapter_title, sub, description, tone, user_keys): sub 
            for sub in subsections
        }
        
        # Assemble in order
        results = {}
        for future in concurrent.futures.as_completed(future_to_sub):
            sub = future_to_sub[future]
            try:
                results[sub] = future.result()
                print(f"✅ [FINISHED] {sub}")
            except Exception as e:
                print(f"❌ [FAILED] {sub}: {e}")
                results[sub] = "[Content Synthesis Failed]"
        
        # Maintain original order
        for sub in subsections:
            full_content += f"\n{sub.upper()}\n\n{results.get(sub, '')}\n\n"
            
    return full_content.strip(), subsections

class MyPDF(FPDF):
    def __init__(self, theme):
        super().__init__()
        self.theme = theme
        self.current_chapter_title = ""
        self.primary_rgb = hex_to_rgb(theme.get("primary_rgb", [20, 40, 80]))
        self.secondary_rgb = hex_to_rgb(theme.get("secondary_rgb", [30, 60, 120]))
        self.layout_mode = theme.get("layout_mode", "Sophisticated")
        self.alignment = theme.get("alignment", "J")
        self.font_sizes = theme.get("font_sizes", {"h1": 26, "h2": 14, "body": 12})
        self.spacing_cfg = theme.get("spacing", {"line_height": 1.5, "paragraph_gap": 10})

    def header(self):
        if self.page_no() > 1:
            self.set_font("helvetica", "I", 8)
            self.set_text_color(180)
            header_align = "R" if self.layout_mode != "Centered" else "C"
            self.cell(0, 10, f"{self.current_chapter_title} | {BRAND_NAME}", align=header_align, new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(180)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def add_chapter(self, title, content, chapter_art=None):
        self.current_chapter_title = title
        content = sanitize_unicode(content)
        self.add_page()
        
        # 🎨 STABILIZED Y-BUFFERING
        start_y = 35
        if self.layout_mode == "Minimalist":
            start_y = 50
        
        # 🎨 CHAPTER ART
        if chapter_art and os.path.exists(chapter_art):
            try:
                art_h = 80 if self.layout_mode != "Minimalist" else 60
                self.image(chapter_art, x=25, y=start_y, w=self.w - 50, h=art_h)
                self.set_y(start_y + art_h + 15) # Buffered gap
            except:
                self.set_y(start_y)
        else:
            self.set_y(start_y)
            
        self.set_x(self.l_margin) # Defensive reset

        # Chapter Heading (Dynamic Scaling)
        h1_size = self.font_sizes.get("h1", 26)
        h1_lh = h1_size * 0.5 # Header line spacing
        self.set_font("helvetica", "B", h1_size)
        self.set_text_color(*self.primary_rgb)
        
        heading_align = "L" if self.layout_mode != "Centered" else "C"
        self.multi_cell(0, h1_lh, title.upper(), align=heading_align)
        self.ln(self.spacing_cfg.get("paragraph_gap", 10))
        
        # Content body
        body_size = self.font_sizes.get("body", 12)
        body_lh = body_size * 0.6  # Body line spacing
        self.set_font("helvetica", "", body_size)
        self.set_text_color(40)
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                self.ln(5)
                continue
            
            # Subsection Heading Check
            if len(line.split()) < 7 and line.isupper():
                self.ln(10) # Heavy buffer before heading
                h2_size = self.font_sizes.get("h2", 14)
                h2_lh = h2_size * 0.6
                self.set_font("helvetica", "B", h2_size)
                self.set_text_color(*self.secondary_rgb)
                self.multi_cell(0, h2_lh, line, align=heading_align)
                self.set_font("helvetica", "", body_size)
                self.set_text_color(40)
                self.ln(5)
            else:
                # 🛡️ [LAYOUT STABILITY]: Multi-worker horizontal space sanity check
                if self.w - self.l_margin - self.r_margin > 0:
                    self.multi_cell(0, body_lh, line, align=self.alignment)
                else:
                    self.ln(body_lh) # Fallback to vertical break if layout is corrupted

def save_ebook_pdf(title, description, chapters_content, chapters_list, subsections_dict, output_file, theme, cover_image=None, chapter_arts=None):
    pdf = MyPDF(theme)
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # Dynamic Margins based on DNA
    l_m, t_m, r_m = 25, 25, 25
    if theme.get("layout_mode") == "Minimalist":
        l_m, t_m, r_m = 30, 50, 30
    elif theme.get("layout_mode") == "Brutalist":
        l_m, t_m, r_m = 15, 20, 15
        
    pdf.set_margins(left=l_m, top=t_m, right=r_m)

    # 1. Cover Page
    pdf.add_page()
    if cover_image and os.path.exists(cover_image):
        pdf.image(cover_image, x=0, y=0, w=pdf.w, h=pdf.h)
    
    # Stabilized Cover Positioning
    pdf.set_y(pdf.h / 3)
    pdf.set_font("helvetica", "B", 40)
    pdf.set_text_color(255 if cover_image else 40)
    pdf.multi_cell(0, 20, title.upper(), align="C")
    pdf.ln(15)
    pdf.set_font("helvetica", "I", 16)
    pdf.cell(0, 10, "The Vantix Legacy", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    
    # 2. Table of Contents
    pdf.add_page()
    pdf.ln(10)
    pdf.set_font("helvetica", "B", 20)
    pdf.set_text_color(*pdf.secondary_rgb)
    pdf.cell(0, 10, "TABLE OF CONTENTS", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(10)
    
    pdf.set_font("helvetica", "", 13)
    pdf.set_text_color(60)
    for chap in chapters_list:
        pdf.cell(0, 10, f"- {chap.upper()}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        sub_list = subsections_dict.get(chap, [])
        pdf.set_font("helvetica", "I", 11)
        pdf.set_text_color(100)
        for sub in sub_list:
            pdf.set_x(35)
            pdf.cell(0, 8, f"> {sub}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.set_font("helvetica", "", 13)
        pdf.set_text_color(60)
        pdf.ln(3)

    # 3. Chapter Content
    for i, content in enumerate(chapters_content):
        art = chapter_arts[i] if chapter_arts and i < len(chapter_arts) else None
        pdf.add_chapter(chapters_list[i], content, chapter_art=art)
    

    pdf.output(output_file)
    print(f"✅ [STABILIZED] Mastered Vantix Masterpiece: {output_file}")
    return output_file

def automate_ebook_creation(topic, description="", num_chapters=3, min_words=150, theme_color=None, images_toggle=True, user_keys=None, job_id=None, output_dir=None, **kwargs):
    if job_id:
        import api.telemetry as telemetry
        telemetry.update_progress(job_id, "Drafting Manifesto (1/1)")
    """🚀 VANTIX DYNAMIC ENGINE (v1.0): Stabilized Vantix Design"""
    print(f"🏗️ [FACTORY] Initializing Multi-Model Synthesis: {topic}")
    
    # 🛡️ [PATH SENTINEL] Ensure output_dir exists
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Optional override of global config
    global NUM_CHAPTERS, MIN_WORDS_PER_SECTION, INCLUDE_IMAGES
    NUM_CHAPTERS = num_chapters
    MIN_WORDS_PER_SECTION = min_words
    INCLUDE_IMAGES = images_toggle

    # 1. DNA Synthesis
    theme = generate_ebook_theme(topic, description, user_keys=user_keys)
    if theme_color:
        theme['primary_rgb'] = hex_to_rgb(theme_color)
    
    # 2. Outline Synthesis
    print("📋 [PLANNING] Synthesizing Organic Outline...")
    prompt = f"Design a comprehensive ebook outline for: {topic}. Decide on the optimal number of chapters based on the title {topic} and vision: {description}. Return ONLY chapter titles, one per line."
    outline_text = generate_ai_response(prompt, user_keys=user_keys).text
    chapters_list = [line.strip() for line in outline_text.split("\n") if line.strip() and len(line) > 3]
    print(f"📁 [STRUCTURE] AI synthesized {len(chapters_list)} chapters.")
    
    # 3. Vantix Cover Art
    safe_topic = re.sub(r'[^a-zA-Z0-9]', '_', topic.lower())
    cover_temp_name = f"cover_{safe_topic}.png"
    cover_image_path = os.path.join(output_dir, cover_temp_name) if output_dir else cover_temp_name
    
    if INCLUDE_IMAGES:
        style = theme.get('visual_style', 'Cinematic')
        cover_url = generate_image_asset(f"Professional cinematic ebook cover for {topic}. Style: {style}. No text.", user_keys=user_keys)
        if not download_asset(cover_url, cover_image_path):
            cover_image_path = None
    else:
        cover_image_path = None

    from parallel_helper import ParallelOrchestrator
    orch = ParallelOrchestrator(max_workers=2) # 🛡️ [THROTTLING] Reduced from 3 to 2 for Stability (v124.44)
    
    def process_chapter(i, chapter_title):
        # 🛡️ [REDUCE PRESSURE] Industrial Jitter to mitigate Groq RPM limits (v124.44)
        time.sleep(2.5 * i)
        print(f"📝 [SYNTHESIS] Mastering Chapter {i+1}: {chapter_title}")
        art_temp_name = f"art_chap_{i+1}_{safe_topic}.png"
        art_path = os.path.join(output_dir, art_temp_name) if output_dir else art_temp_name
        
        if INCLUDE_IMAGES and INCLUDE_CHAPTER_ART:
            style = theme.get('visual_style', 'Cinematic')
            art_url = generate_image_asset(f"Cinematic scene for '{chapter_title}'. Style: {style}. No text.", user_keys=user_keys)
            if not download_asset(art_url, art_path):
                art_path = None
        else:
            art_path = None
        
        content, subs = build_chapter_with_subsections(topic, chapter_title, description, theme.get('tone', 'Expert'), user_keys=user_keys)
        return {
            "content": content,
            "subsections": subs,
            "art": art_path
        }

    # 4. Production Cycle (Parallel)
    results = orch.parallel_map_indexed(process_chapter, chapters_list, task_name="Chapter Synthesis")

    # 5. Result Integration (Synchronized)
    subsections_dict = {}
    chapters_content = []
    chapter_arts = []

    for i, res in enumerate(results):
        if res:
            subsections_dict[chapters_list[i]] = res["subsections"]
            chapters_content.append(res["content"])
            chapter_arts.append(res["art"])
        else:
            subsections_dict[chapters_list[i]] = []
            chapters_content.append("[Chapter Synthesis Failed]")
            chapter_arts.append(None)

    # 6. Final Master
    filename = f"{safe_topic}_GODLEVEL_STABILIZED.pdf"
    final_output_path = os.path.join(output_dir, filename) if output_dir else filename
    save_ebook_pdf(topic, description, chapters_content, chapters_list, subsections_dict, final_output_path, theme, cover_image=cover_image_path, chapter_arts=chapter_arts)
    print(f"🏁 [GOD-LEVEL] Stabilized Masterpiece Delivered: {final_output_path}")
    return final_output_path

if __name__ == "__main__":
    import sys
    t = input("📚 Topic: ").strip() if len(sys.argv) < 2 else sys.argv[1]
    d = input("👁️ Vision: ").strip() if len(sys.argv) < 3 else sys.argv[2]
    automate_ebook_creation(t, d)
