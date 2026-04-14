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

# === Global API & Model Health Tracker === #
class APIHealth:
    def __init__(self):
        self.lock = threading.Lock()
        self.provider_priority = ["groq", "openrouter"]
        self.model_priority = {
            "groq": [
                "llama3-70b-8192",
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "mixtral-8x7b-32768"
            ],
            "openrouter": [
                "meta-llama/llama-3.3-70b-instruct", 
                "qwen/qwen-2.5-72b-instruct",
                "mistralai/mistral-large-2411",
                "google/gemma-2-27b-it:free"
            ],
            "image": [
                "stabilityai/stable-diffusion-xl-base-1.0",
                "openai/dall-e-3",
                "google/gemma-2-27b-it:free" # Text-fallback if supported
            ]
        }
        self.last_failure = {}

    def report_success(self, provider, model=None):
        with self.lock:
            # Move successful provider/model to the front
            if provider in self.provider_priority:
                self.provider_priority.remove(provider)
                self.provider_priority.insert(0, provider)
            
            if model and provider in self.model_priority:
                models = self.model_priority[provider]
                if model in models:
                    models.remove(model)
                    models.insert(0, model)
            
            if model and provider == "image": # Special case for image models
                models = self.model_priority["image"]
                if model in models:
                    models.remove(model)
                    models.insert(0, model)

    def report_failure(self, provider, model=None):
        with self.lock:
            self.last_failure[provider if not model else f"{provider}:{model}"] = time.time()
            
            # Move failed provider/model to the back
            if not model and provider in self.provider_priority:
                self.provider_priority.remove(provider)
                self.provider_priority.append(provider)
                
            if model and provider in self.model_priority:
                models = self.model_priority[provider]
                if model in models:
                    models.remove(model)
                    models.append(model)
                    
            print(f"📉 [HEALTH] {provider.upper()}{':' + model if model else ''} deprioritized.")

    def get_providers(self):
        with self.lock:
            return list(self.provider_priority)

    def get_models(self, provider):
        with self.lock:
            return list(self.model_priority.get(provider, []))

HEALTH_TRACKER = APIHealth()

# === Configuration === #
BASE_DELAY = 1

# === Response Class === #
class AIResponse:
    def __init__(self, text):
        self.text = text

# === Groq Backend === #
def call_groq(prompt, user_keys=None):
    # USE USER KEY IF PROVIDED, OTHERWISE FALLBACK TO TEST KEY
    api_key = (user_keys or {}).get("groq") or os.environ.get("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    models = HEALTH_TRACKER.get_models("groq")
    for model in models:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        try:
            print(f"📡 Groq Requesting {model}...")
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                HEALTH_TRACKER.report_success("groq", model)
                print(f"✅ Groq ({model}) success.")
                return AIResponse(response.json()["choices"][0]["message"]["content"].strip())
            else:
                HEALTH_TRACKER.report_failure("groq", model)
        except Exception as e:
            HEALTH_TRACKER.report_failure("groq", model)
            
    raise RuntimeError("All Groq models failed.")

# === OpenRouter Backend === #
def call_openrouter(prompt, user_keys=None):
    # USE USER KEY IF PROVIDED, OTHERWISE FALLBACK TO TEST KEY
    api_key = (user_keys or {}).get("openrouter") or os.environ.get("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/udaydomadiya08/VIDEOYT"
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
                HEALTH_TRACKER.report_failure("openrouter", model)
        except:
            HEALTH_TRACKER.report_failure("openrouter", model)
            
    raise RuntimeError("All OpenRouter models failed.")

# === Main Synthesis Entry === #
def generate_ai_response(prompt, user_keys=None):
    while True:
        providers = HEALTH_TRACKER.get_providers()
        for provider in providers:
            try:
                if provider == "groq": return call_groq(prompt, user_keys=user_keys)
                if provider == "openrouter": return call_openrouter(prompt, user_keys=user_keys)
            except Exception as e:
                print(f"⚠️ {provider.upper()} cycle failed: {e}. Failover...")
                HEALTH_TRACKER.report_failure(provider)
                time.sleep(1)
        
        print(f"🚨 Global API Exhaustion. Pausing 15s...")
        time.sleep(15)

# === Image Synthesis Entry === #
def generate_image_asset(prompt, user_keys=None):
    # IMAGE GEN USUALLY VIA OPENROUTER IN THIS SETUP, BUT CAN BE EXPANDED
    api_key = (user_keys or {}).get("openrouter") or os.environ.get("OPENROUTER_API_KEY")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    models = HEALTH_TRACKER.get_models("image")
    for model in models:
        print(f"🎨 Trying {model}...")
        payload = {"model": model, "prompt": prompt, "response_format": {"type": "url"}}
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=40)
            if response.status_code == 200:
                data = response.json()
                image_url = data.get("url") or data.get("choices", [{}])[0].get("message", {}).get("content")
                if image_url and image_url.startswith("http"):
                    HEALTH_TRACKER.report_success("image", model)
                    return image_url
            HEALTH_TRACKER.report_failure("image", model)
        except:
            HEALTH_TRACKER.report_failure("image", model)
            
    return None

def generate_ebook_theme(topic, description="", user_keys=None):
    prompt = f"Design visual DNA for '{topic}'. Return ONLY JSON: primary_rgb, secondary_rgb, visual_style, layout_mode, alignment, font_sizes, spacing, tone."
    try:
        response = generate_ai_response(prompt, user_keys=user_keys)
        match = re.search(r"\{.*\}", response.text, re.DOTALL)
        if match: return json.loads(match.group(0))
    except: pass
    return {"primary_rgb": [20, 20, 20], "secondary_rgb": [200, 0, 0], "layout_mode": "Sophisticated", "alignment": "J", "font_sizes": {"h1": 30, "h2": 16, "body": 12}, "spacing": {"line_height": 9, "paragraph_gap": 10}, "tone": "Vibrant"}
