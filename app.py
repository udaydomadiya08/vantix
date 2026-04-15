import os
# 🛡️ [ENV-SANITIZATION]: Neutralizing auto-proxy injection for Groq SDK
os.environ.pop("HTTP_PROXY", None)
os.environ.pop("HTTPS_PROXY", None)
os.environ.pop("http_proxy", None)
os.environ.pop("https_proxy", None)

import groq
# 🛡️ [ABS-SOVEREIGN IMMUNITY]: Killing 'proxies' bug at the root
try:
    _orig_init = groq.Client.__init__
    def _new_init(self, *args, **kwargs):
        kwargs.pop("proxies", None)
        return _orig_init(self, *args, **kwargs)
    groq.Client.__init__ = _new_init
    groq.Groq.__init__ = _new_init
except Exception as e:
    print(f"⚠️ Immunity Patch Failed: {e}")

# 🛰️ [SOVEREIGN ENGINE] Hugging Face Deployment Node
import sys

# 🚀 Add the api directory to path so we can import the hardened engine
sys.path.append(os.path.join(os.getcwd(), "api"))

try:
    from api.main import app as vantix_app
    app = vantix_app
    print("✅ [DEPLOYMENT]: Hardened Vantix Engine loaded successfully.")
except ImportError as e:
    print(f"❌ [DEPLOYMENT]: Failed to load api.main. Error: {e}")
    # Fallback to a basic status if the import fails during transition
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    
    app = FastAPI()
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    def read_root():
        return {"status": "Vantix Bridge Active", "version": "Industrial Hardening Active (Root Fallback)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
