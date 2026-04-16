import os
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import numpy as np
import requests
from collections import Counter

# 🔗 Path Access
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ai_helper
# Gemini image_service dependency purged. (v103.2)

THUMBNAIL_SIZE = (1280, 720) # YouTube Standard

# 🏛️ [VANTIX TYPOGRAPHY] Industrial Font Discovery (v112.0)
def discover_font():
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "Arial.ttf",
        "Impact.ttf"
    ]
    for c in candidates:
        if os.path.exists(c): return c
    # Check current directory
    local_anton = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Anton-Regular.ttf")
    if os.path.exists(local_anton): return local_anton
    return None

FONT_PATH = discover_font()

def get_readable_color(rgb_color):
    """Determine if black or white will be more readable on the given background color."""
    r, g, b = rgb_color
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return (0, 0, 0) if luminance > 186 else (255, 255, 255)

def get_dominant_color(img, resize_scale=150):
    """Resize image and get the most common RGB color."""
    small_img = img.resize((resize_scale, resize_scale))
    pixels = np.array(small_img).reshape(-1, 3)
    most_common = Counter(map(tuple, pixels)).most_common(1)[0][0]
    return most_common

def generate_viral_headline(topic, user_keys=None):
    """Generate high-CTR YouTube thumbnail text using AI Narrative Synthesis."""
    prompt = f"""
    Generate the most attention-grabbing, high-CTR YouTube thumbnail text for the topic: "{topic}".
    
    RULES:
    - Max 3-5 words.
    - Use "Power Words" (e.g., DOOMED, SECRET, INSANE, FINALLY, HIDDEN).
    - Create a curiosity gap or emotional trigger.
    - All CAPS is preferred for impact.
    - No punctuation or quotes.
    
    Return ONLY the text.
    """
    try:
        response = ai_helper.generate_ai_response(prompt, user_keys=user_keys)
        return response.text.strip().replace('"', '').upper()
    except:
        return topic.upper()

def get_stock_backdrop(topic, pexels_key):
    """🛡️ Fallback Node: Fetch a high-res cinematic stock image from Pexels."""
    if not pexels_key: return None
    print(f"📡 [THUMBNAIL] AI Synthesis unavailable. Fetching stock backdrop for: {topic}")
    
    headers = {"Authorization": pexels_key}
    url = f"https://api.pexels.com/v1/search?query={topic}&per_page=1&orientation=landscape"
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            photos = resp.json().get("photos", [])
            if photos:
                img_url = photos[0]["src"]["large2x"] # 940x627, large enough for 720p resize
                img_resp = requests.get(img_url, timeout=15)
                if img_resp.status_code == 200:
                    os.makedirs("temp/images", exist_ok=True)
                    path = f"temp/images/stock_bg_{os.getpid()}.jpg"
                    with open(path, "wb") as f:
                        f.write(img_resp.content)
                    return path
    except Exception as e:
        print(f"⚠️ [THUMBNAIL] Stock fallback failed: {e}")
    return None

def create_vantix_thumbnail(topic, user_keys=None, output_path=None, job_id=None, **kwargs):
    if job_id:
        import api.telemetry as telemetry
        telemetry.update_progress(job_id, "Designing Viral Thumbnail")
    """
    Graduated Thumbnail Synthesis Engine (v102.0)
    Generates a cinematic backdrop and overlays a viral headline.
    """
    print(f"🎨 [THUMBNAIL] Initializing synthesis for: {topic}")
    
    # 1. Generate Headline
    headline = generate_viral_headline(topic, user_keys=user_keys)
    print(f"📝 [THUMBNAIL] Viral Headline: {headline}")
    
    # 2. Generate Cinematic Backdrop (Purged Gemini Node v103.2)
    # Using Industrial Pexels Node as Primary
    pexels_key = (user_keys or {}).get("pexels")
    original_bg_path = get_stock_backdrop(topic, pexels_key)

    if not original_bg_path or not os.path.exists(original_bg_path):
        print("⚠️ [THUMBNAIL] Background nodes failed or unavailable. Using fallback gradient.")
        img = Image.new("RGB", THUMBNAIL_SIZE, (20, 20, 20))
    else:
        img = Image.open(original_bg_path).convert("RGB")
    
    # Resize to 1280x720
    img = img.resize(THUMBNAIL_SIZE, Image.LANCZOS)
    
    # 3. Graphic Overlay
    draw = ImageDraw.Draw(img)
    
    # Font Calibration
    try:
        font_size = 110
        font = ImageFont.truetype(FONT_PATH, font_size)
    except:
        font = ImageFont.load_default()
        print("⚠️ [THUMBNAIL] Default font used. Supplemental Arial Bold missing.")

    # Multi-line word wrapping if needed
    words = headline.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        # Use textbbox if available (Pillow 10+)
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if (bbox[2] - bbox[0]) > (THUMBNAIL_SIZE[0] * 0.85):
            lines.append(" ".join(current_line))
            current_line = [word]
        else:
            current_line.append(word)
    lines.append(" ".join(current_line))
    
    # Draw logic
    total_h = sum([draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines]) + (len(lines) -1) * 20
    current_y = (THUMBNAIL_SIZE[1] - total_h) // 2
    
    dominant_color = get_dominant_color(img)
    text_color = get_readable_color(dominant_color)
    shadow_color = (0, 0, 0) if text_color == (255, 255, 255) else (255, 255, 255)
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_w = bbox[2] - bbox[0]
        line_h = bbox[3] - bbox[1]
        x = (THUMBNAIL_SIZE[0] - line_w) // 2
        
        # Drop Shadow
        draw.text((x+5, current_y+5), line, font=font, fill=shadow_color)
        # Main Text
        draw.text((x, current_y), line, font=font, fill=text_color)
        
        current_y += line_h + 20

    if not output_path:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        thumb_dir = os.path.join(root_dir, "static/thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        import time
        output_path = os.path.join(thumb_dir, f"thumb_{int(time.time())}.jpg")
        
    img.save(output_path, quality=95)
    print(f"✅ [THUMBNAIL] Graduation Certified: {output_path}")
    return output_path

if __name__ == "__main__":
    # Test script
    create_vantix_thumbnail("The Secret of Infinite AI Wealth")
