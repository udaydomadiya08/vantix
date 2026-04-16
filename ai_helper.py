import os
import time
import random
import json
import subprocess
import re
import requests
from datetime import datetime
from functools import wraps
import threading

# === Global API & Model Health Tracker (v110.2) === #
class APIHealth:
    def __init__(self):
        self.lock = threading.RLock() # 🏛️ [VANTIX STABILITY]: Re-entrant lock to prevent recursive deadlocks
        self.provider_priority = ["groq", "openrouter"]
        self.model_priority = {
            "groq": [
                "llama-3.3-70b-versatile",
                "llama-3.1-8b-instant",
                "llama-3.2-3b-preview"
            ],
            "openrouter": [
                "google/gemini-2.0-flash-001",
                "google/gemini-2.0-flash-lite-preview-0102",
                "meta-llama/llama-3.3-70b-instruct", 
                "qwen/qwen-2.5-72b-instruct"
            ],
            "image": [
                "stabilityai/sdxl",
                "openai/dall-e-3"
            ]
        }
        self.cooldowns = {} # {provider:model: timestamp}

    def report_success(self, provider, model=None):
        with self.lock:
            key = f"{provider}:{model}" if model else provider
            if key in self.cooldowns: del self.cooldowns[key]
            
            if provider in self.provider_priority:
                self.provider_priority.remove(provider)
                self.provider_priority.insert(0, provider)

    def report_failure(self, provider, model=None):
        with self.lock:
            key = f"{provider}:{model}" if model else provider
            self.cooldowns[key] = time.time() + 60 # 60 Second Cool-down (Reduced from 300)
            
            if not model and provider in self.provider_priority:
                self.provider_priority.remove(provider)
                self.provider_priority.append(provider)
                
            if model and provider in self.model_priority:
                models = self.model_priority[provider]
                if model in models:
                    models.remove(model)
                    models.append(model)
            print(f"📉 [HEALTH] {provider.upper()}{':' + model if model else ''} cooled-down.")

    def is_healthy(self, provider, model=None):
        with self.lock:
            key = f"{provider}:{model}" if model else provider
            if key in self.cooldowns:
                if time.time() > self.cooldowns[key]:
                    del self.cooldowns[key]
                    return True
                return False
            return True

    def get_providers(self):
        with self.lock:
            return [p for p in self.provider_priority if self.is_healthy(p)]

    def get_models(self, provider):
        with self.lock:
            return [m for m in self.model_priority.get(provider, []) if self.is_healthy(provider, m)]

HEALTH_TRACKER = APIHealth()

# === Response Class === #
class AIResponse:
    def __init__(self, text):
        self.text = text

# === Groq Backend === #
def call_groq(prompt, user_keys=None):
    api_key = (user_keys or {}).get("groq") or os.environ.get("GROQ_API_KEY")
    if not api_key: raise ValueError("Groq API Key missing.")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    models = HEALTH_TRACKER.get_models("groq")
    for model in models:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        try:
            print(f"📡 Groq Requesting {model}...")
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                HEALTH_TRACKER.report_success("groq", model)
                print(f"✅ Groq ({model}) success.")
                return AIResponse(response.json()["choices"][0]["message"]["content"].strip())
            else:
                print(f"⚠️ Groq Error {response.status_code}: {response.text[:150]}")
                # If rate limit, cooldown the model
                if response.status_code == 429:
                    HEALTH_TRACKER.report_failure("groq", model)
        except Exception as e:
            print(f"❌ Groq Exception: {e}")
            HEALTH_TRACKER.report_failure("groq", model)
            
    raise RuntimeError("All Groq models failed.")

# === OpenRouter Backend === #
def call_openrouter(prompt, user_keys=None):
    api_key = (user_keys or {}).get("openrouter") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key: raise ValueError("OpenRouter API Key missing.")
    
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/udaydomadiya08/VIDEOYT",
        "X-Title": "Vantix Video Platform"
    }
    
    models = HEALTH_TRACKER.get_models("openrouter")
    for model in models:
        payload = {"model": model, "messages": [{"role": "user", "content": prompt}], "temperature": 0.7}
        try:
            print(f"📡 Requesting {model}...")
            response = requests.post(url, headers=headers, json=payload, timeout=70)
            if response.status_code == 200:
                HEALTH_TRACKER.report_success("openrouter", model)
                print(f"✅ OpenRouter ({model}) success.")
                return AIResponse(response.json()["choices"][0]["message"]["content"].strip())
            else:
                print(f"⚠️ OpenRouter Error {response.status_code}: {response.text[:150]}")
                if response.status_code in [429, 402]: # Rate limit or Out of credits (cooling down)
                    HEALTH_TRACKER.report_failure("openrouter", model)
                if response.status_code == 401: break # Kill key
        except Exception as e:
            print(f"❌ OpenRouter Exception: {e}")
            HEALTH_TRACKER.report_failure("openrouter", model)
            
    raise RuntimeError("All OpenRouter models failed.")

# === Main Synthesis Entry === #
def generate_ai_response(prompt, user_keys=None, job_id=None):
    import api.telemetry as telemetry
    retry_count = 0
    
    while retry_count < 3:
        providers = HEALTH_TRACKER.get_providers()
        for provider in providers:
            try:
                if job_id: telemetry.update_progress(job_id, f"AI {provider.upper()} Thinking...")
                if provider == "groq": return call_groq(prompt, user_keys=user_keys)
                if provider == "openrouter": return call_openrouter(prompt, user_keys=user_keys)
            except:
                continue # Rapid switch
        
        retry_count += 1
        # 📈 [BACKOFF] Accelerated Recovery Jitter (v120.7)
        sleep_time = (5 * retry_count) + random.uniform(1, 3)
        msg = f"AI Retrying ({retry_count}/3)..."
        if job_id: telemetry.update_progress(job_id, msg)
        print(f"🚨 Global API Exhaustion ({retry_count}/3). Pausing {sleep_time:.1f}s...")
        time.sleep(sleep_time)
    
    raise RuntimeError("Critical: Permanent AI Infrastructure failure.")

# === Image & Other Helpers === #
def generate_image_asset(prompt, user_keys=None):
    api_key = (user_keys or {}).get("openrouter") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key: return None
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    for model in HEALTH_TRACKER.get_models("image"):
        try:
            response = requests.post(url, headers=headers, json={"model": model, "prompt": prompt}, timeout=40)
            if response.status_code == 200:
                data = response.json()
                url = data.get("url") or data.get("choices",[{}])[0].get("message",{}).get("content")
                if url and url.startswith("http"): return url
        except: pass
    return None

def generate_ebook_theme(topic, description="", user_keys=None):
    prompt = f"Design visual DNA for '{topic}'. Return ONLY JSON: primary_rgb, secondary_rgb, layout_mode."
    try:
        response = generate_ai_response(prompt, user_keys=user_keys)
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match: return json.loads(match.group(0))
    except: pass
    return {"primary_rgb": [20, 20, 20], "secondary_rgb": [200, 0, 0], "layout_mode": "Sophisticated"}
