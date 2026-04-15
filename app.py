# 🛰️ [SOVEREIGN ENGINE] Hugging Face Deployment Node
import os
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
