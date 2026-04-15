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
                "openai/dall-e-3"
            ]
        }
        self.last_failure = {}

    def report_success(self, provider, model=None):
        with self.lock:
            if provider in self.provider_priority:
                self.provider_priority.remove(provider)
                self.provider_priority.insert(0, provider)
            
            if model and provider in self.model_priority:
                models = self.model_priority[provider]
                if model in models:
                    models.remove(model)
                    models.insert(0, model)

    def report_failure(self, provider, model=None):
        with self.lock:
            self.last_failure[provider if not model else f"{provider}:{model}"] = time.time()
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

# === Response Class === #
class AIResponse:
    def __init__(self, text):
        self.text = text

# === Groq Backend === #
def call_groq(prompt, user_keys=None):
    api_key = (user_keys or {}).get("groq") or os.environ.get("GROQ_API_KEY")
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
                # 🛠️ DIAGNOSTIC HUD: Print exact error message
                print(f"⚠️ Groq Error {response.status_code}: {response.text[:200]}")
                HEALTH_TRACKER.report_failure("groq", model)
        except Exception as e:
            print(f"❌ Groq Exception: {e}")
            HEALTH_TRACKER.report_failure("groq", model)
            
    raise RuntimeError("All Groq models failed.")

# === OpenRouter Backend === #
def call_openrouter(prompt, user_keys=None):
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
                # 🛠️ DIAGNOSTIC HUD: Print exact error message
                print(f"⚠️ OpenRouter Error {response.status_code}: {response.text[:200]}")
                HEALTH_TRACKER.report_failure("openrouter", model)
        except Exception as e:
            print(f"❌ OpenRouter Exception: {e}")
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
                HEALTH_TRACKER.report_failure(provider)
                time.sleep(2) # Micro-cooldown between providers
        
        print(f"🚨 Global API Exhaustion. Pausing 30s to replenish rate limits...")
        time.sleep(30)

# === Image & Other Helpers === #
def generate_image_asset(prompt, user_keys=None):
    api_key = (user_keys or {}).get("openrouter") or os.environ.get("OPENROUTER_API_KEY")
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
