from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import os
import sys
import uuid
import jwt
import json
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools

# 🔗 Path Synchronization: Ensure root and local modules are visible to the API
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if current_dir not in sys.path: sys.path.append(current_dir)
if parent_dir not in sys.path: sys.path.append(parent_dir)

import run_full_vso
import ebook
import ecourse_factory
import thumbnail_service
import db_helper
import research_helper

app = FastAPI(title="Vantix Core Engine (v1.0)")
security = HTTPBearer()
SECRET_KEY = "VANTIX_ULTRA_SECRET_2026"
ALGORITHM = "HS256"

# 🔒 [SECURITY] Allow Frontend access (Industrial Origin Echo)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001,*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in ALLOWED_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📂 [DELIVERY] Mount Static Assets (Absolute Project Mapping)
os.makedirs(os.path.join(parent_dir, "static/videos"), exist_ok=True)
os.makedirs(os.path.join(parent_dir, "static/ebooks"), exist_ok=True)
os.makedirs(os.path.join(parent_dir, "static/thumbnails"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(parent_dir, "static")), name="static")
app.mount("/final_video", StaticFiles(directory=os.path.join(parent_dir, "final_video")), name="final_video")
app.mount("/courses", StaticFiles(directory=os.path.join(parent_dir, "courses")), name="courses")

# 🏛️ [DELIVERY] Industrial Forced Download Route
@app.get("/download")
async def download_file(path: str):
    full_path = os.path.join(parent_dir, path)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="Industrial node: File not found.")
    
    file_name = os.path.basename(full_path)
    return FileResponse(
        path=full_path,
        filename=file_name,
        media_type='application/octet-stream'
    )

# 📊 [STATE] Industrial Queue Management System
JOB_STATUS = {}
CANCELLED_JOBS = set() # 🕹️ Vantix Kills
EXECUTOR = ThreadPoolExecutor(max_workers=5) # Global pool for heavy compute

class StreamQueueManager:
    def __init__(self):
        self.queues = {} # {(username, stream_type): asyncio.Queue()}
        self.active_workers = set()

    async def add_job(self, username, stream_type, job_id, func, kwargs):
        key = (username, stream_type)
        if key not in self.queues:
            self.queues[key] = asyncio.Queue()
        
        await self.queues[key].put((job_id, func, kwargs))
        # 📝 [IDENTITY] Save topic so Library can display meaningful titles
        topic = kwargs.get("topic", stream_type)
        job_data = {"status": "queued", "stream": stream_type, "topic": topic, "submitted": datetime.now().isoformat()}
        JOB_STATUS[job_id] = job_data
        
        # 🏛️ [PERSISTENCE] Initial Entry
        db_helper.save_to_history(username, job_id, job_data)
        
        if key not in self.active_workers:
            asyncio.create_task(self.worker(username, stream_type))

    async def worker(self, username, stream_type):
        key = (username, stream_type)
        self.active_workers.add(key)
        queue = self.queues[key]
        
        while not queue.empty():
            job_id, func, kwargs = await queue.get()
            
            # 🕹️ [CANCEL CHECK] Skip if job was killed while in queue
            if job_id in CANCELLED_JOBS:
                print(f"🛑 [WORKER] Skipping Cancelled Job: {job_id}")
                JOB_STATUS[job_id]["status"] = "cancelled"
                db_helper.save_to_history(username, job_id, JOB_STATUS[job_id])
                queue.task_done()
                continue

            print(f"⚙️ [WORKER] Processing {stream_type} Job: {job_id}")
            JOB_STATUS[job_id]["status"] = "processing"
            JOB_STATUS[job_id]["start"] = datetime.now().isoformat()
            
            try:
                # Wrap long-running synchronous code in run_in_executor with partial for kwargs
                loop = asyncio.get_event_loop()
                result_path = await loop.run_in_executor(EXECUTOR, functools.partial(func, **kwargs))
                
                JOB_STATUS[job_id]["status"] = "completed"
                
                # 🛰️ [VANTIX URL] Map Absolute Path to Industrial Download Route
                if result_path and isinstance(result_path, str):
                    try:
                        # Extract the path relative to project root
                        rel_path = os.path.relpath(result_path, parent_dir).replace("\\", "/")
                        # Final Web URL construction via 127.0.0.1 (Industrial Recovery)
                        JOB_STATUS[job_id]["result_url"] = f"http://127.0.0.1:8000/download?path={rel_path}"
                    except Exception as path_err:
                        print(f"⚠️ URL Mapping Error: {path_err}")
                        JOB_STATUS[job_id]["result_url"] = None

                print(f"✅ [WORKER] Completed {stream_type} Job: {job_id} -> {JOB_STATUS[job_id].get('result_url')}")
            except Exception as e:
                print(f"❌ [WORKER] Factor Synthesis Failed: {e}")
                JOB_STATUS[job_id]["status"] = "failed"
                JOB_STATUS[job_id]["error"] = str(e)
            finally:
                # 🏛️ [PERSISTENCE] Terminal State Sync
                db_helper.save_to_history(username, job_id, JOB_STATUS[job_id])
                queue.task_done()
        
        print(f"🏁 [WORKER] Stream {stream_type} for {username} idle.")
        self.active_workers.remove(key)

QUEUE_MANAGER = StreamQueueManager()

async def vantix_reaper():
    """💀 Silent background loop that destroys assets older than 24 hours."""
    import time
    while True:
        try:
            print("💀 [VANTIX] Scanning for expired ephemeral assets...")
            now = time.time()
            cutoff = now - (24 * 3600)  # 24 hours
            
            # Scan directories
            dirs_to_clean = [
                os.path.join(parent_dir, "static/videos"),
                os.path.join(parent_dir, "static/ebooks"),
                os.path.join(parent_dir, "static/thumbnails"),
                os.path.join(parent_dir, "final_video"),
                os.path.join(parent_dir, "courses")
            ]
            
            deleted_files = 0
            for d in dirs_to_clean:
                if not os.path.exists(d): continue
                for filename in os.listdir(d):
                    filepath = os.path.join(d, filename)
                    if os.path.isfile(filepath):
                        # Don't delete dotfiles or important placeholders
                        if filename.startswith('.'): continue
                        if os.path.getmtime(filepath) < cutoff:
                            try:
                                os.remove(filepath)
                                deleted_files += 1
                                print(f"💀 [REAPER] Destroyed expired asset: {filename}")
                            except Exception as e:
                                pass
            
            if deleted_files > 0:
                print(f"💀 [REAPER] Swept {deleted_files} assets into oblivion to maintain zero-cost storage cap.")
                
        except Exception as e:
            print(f"⚠️ [REAPER ERROR] {e}")
            
        await asyncio.sleep(3600)  # Run every 60 minutes

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(vantix_reaper())

# --- Models ---
class UserAuth(BaseModel):
    username: str
    password: str

class APIKeys(BaseModel):
    groq: str = None
    openrouter: str = None
    pexels: str = None
    pixabay: str = None

    class Config:
        extra = "allow" # Be flexible with frontend payloads

class VideoRequest(BaseModel):
    topic: str = ""
    script: str = None
    mode: str = "topic" # topic, script, news, niche
    niche: str = None
    avatar: bool = None # Changed to bool to handle frontend toggles cleanly
    horizontal: bool = None
    voice_id: str = "alloy"

class EbookRequest(BaseModel):
    topic: str
    description: str = ""
    chapters: int = 3
    min_words: int = 150
    theme_color: str = "#1e293b"
    images_toggle: bool = True

class CourseRequest(BaseModel):
    topic: str
    horizontal: bool = False
    include_avatar: bool = False

class ThumbnailRequest(BaseModel):
    topic: str

class DefaultsRequest(BaseModel):
    factory_type: str
    settings: dict

# --- Auth Utilities ---
def create_token(username: str):
    expire = datetime.utcnow() + timedelta(days=7)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# --- Auth Endpoints ---
@app.post("/auth/signup")
def signup(user: UserAuth):
    if db_helper.create_user(user.username, user.password):
        return {"message": "User created successfully", "token": create_token(user.username)}
    raise HTTPException(status_code=400, detail="User already exists")

@app.post("/auth/login")
def login(user: UserAuth):
    existing = db_helper.get_user(user.username)
    if existing and existing["password"] == db_helper.hash_password(user.password):
        return {"token": create_token(user.username), "username": user.username}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/user/keys")
def get_user_keys(username: str = Depends(get_current_user)):
    return db_helper.get_user_keys(username)

@app.post("/user/keys")
def update_user_keys(keys: APIKeys, username: str = Depends(get_current_user)):
    db_helper.update_user_keys(username, keys.dict(exclude_unset=True))
    return {"message": "Keys updated successfully"}

@app.get("/user/defaults")
def get_user_defaults(username: str = Depends(get_current_user)):
    return db_helper.get_user_defaults(username)

@app.post("/user/defaults")
def update_user_defaults(req: DefaultsRequest, username: str = Depends(get_current_user)):
    db_helper.update_user_defaults(username, req.factory_type, req.settings)
    return {"message": f"Defaults for {req.factory_type} updated"}

# --- Home ---
@app.get("/")
def read_root():
    return {"status": "Vantix Engine Active", "version": "1.0"}

# --- Endpoints ---

@app.post("/generate/video")
async def generate_video(
    request: VideoRequest, 
    username: str = Depends(get_current_user),
    x_groq_key: str = Header(None),
    x_openrouter_key: str = Header(None),
    x_pexels_key: str = Header(None),
    x_pixabay_key: str = Header(None)
):
    """🎬 Industrial Video Production"""
    job_id = str(uuid.uuid4())
    db_keys = db_helper.get_user_keys(username)
    db_defaults = db_helper.get_user_defaults(username).get("video", {})
    
    # --- 🧠 ResearchIntelligence Phase ---
    enriched_topic = request.topic
    if request.mode == "news":
        enriched_topic = research_helper.get_news_summary(request.topic)
        print(f"📰 [RESEARCH] News Summary Enriched: {enriched_topic[:100]}...")
    elif request.mode == "niche":
        enriched_topic = research_helper.get_niche_trends(request.niche)
        print(f"🎯 [RESEARCH] Niche Trend Discovered: {enriched_topic}")
    
    user_keys = {
        "groq": x_groq_key or db_keys.get("groq"),
        "openrouter": x_openrouter_key or db_keys.get("openrouter"),
        "pexels": x_pexels_key or db_keys.get("pexels"),
        "pixabay": x_pixabay_key or db_keys.get("pixabay")
    }
    
    # ⚙️ [DEFAULTS MERGE] Properly merge frontend explicit options with saved defaults
    req_dict = request.model_dump(exclude_unset=True) if hasattr(request, "model_dump") else request.dict(exclude_unset=True)
    
    kwargs = {
        "forced_topic": enriched_topic,
        "forced_script": request.script,
        "mode": request.mode,
        "niche": request.niche,
        # If frontend explicitly sent true/false use it, otherwise fallback to database
        "forced_avatar": req_dict.get("avatar", db_defaults.get("include_avatar", False)),
        "horizontal": req_dict.get("horizontal", db_defaults.get("horizontal", False)),
        "voice_id": req_dict.get("voice_id", db_defaults.get("voice_id", "alloy")),
        "visual_source": req_dict.get("visual_source", db_defaults.get("visual_source", "pexels")),
        "user_keys": user_keys
    }
    
    await QUEUE_MANAGER.add_job(username, "video", job_id, run_full_vso.run_full_vso, kwargs)
    return {"job_id": job_id, "message": "Short production stream initiated", "topic": request.topic}

@app.post("/generate-thumbnail")
async def generate_thumbnail(request: ThumbnailRequest, username: str = Depends(get_current_user)):
    """🎨 Synthesize an Omnipotent High-CTR Thumbnail"""
    job_id = str(uuid.uuid4())
    user_keys = db_helper.get_user_keys(username)
    
    kwargs = {
        "topic": request.topic,
        "user_keys": user_keys
    }
    
    await QUEUE_MANAGER.add_job(username, "thumbnail", job_id, thumbnail_service.create_vantix_thumbnail, kwargs)
    return {"job_id": job_id, "message": "Thumbnail synthesis engine active", "topic": request.topic}

@app.post("/generate/ebook")
async def generate_ebook(
    request: EbookRequest, 
    username: str = Depends(get_current_user),
    x_groq_key: str = Header(None),
    x_openrouter_key: str = Header(None)
):
    """📚 Industrial E-book Production"""
    job_id = str(uuid.uuid4())
    db_keys = db_helper.get_user_keys(username)
    
    user_keys = {
        "groq": x_groq_key or db_keys.get("groq"),
        "openrouter": x_openrouter_key or db_keys.get("openrouter")
    }
    
    kwargs = {
        "topic": request.topic,
        "description": request.description,
        "num_chapters": request.chapters,
        "min_words": request.min_words,
        "theme_color": request.theme_color,
        "images_toggle": request.images_toggle,
        "user_keys": user_keys
    }
    
    await QUEUE_MANAGER.add_job(username, "ebook", job_id, ebook.automate_ebook_creation, kwargs)
    return {"job_id": job_id, "message": "E-book queued in research stream", "topic": request.topic}

@app.post("/generate/course")
async def generate_course(
    request: CourseRequest,
    username: str = Depends(get_current_user),
    x_groq_key: str = Header(None),
    x_openrouter_key: str = Header(None)
):
    """🎓 Industrial E-course Production"""
    job_id = str(uuid.uuid4())
    db_keys = db_helper.get_user_keys(username)
    
    user_keys = {
        "groq": x_groq_key or db_keys.get("groq"),
        "openrouter": x_openrouter_key or db_keys.get("openrouter")
    }
    
    import ecourse_factory
    kwargs = {
        "topic": request.topic,
        "horizontal": request.horizontal,
        "include_avatar": request.include_avatar,
        "user_keys": user_keys
    }
    
    await QUEUE_MANAGER.add_job(username, "course", job_id, ecourse_factory.run_ecourse_factory, kwargs)
    return {"job_id": job_id, "message": "E-course queued in educational stream", "topic": request.topic}

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    # 🏛️ [VANTIX PERSISTENCE] Check In-Memory first, then fall back to Ledger
    # Public access (unguessable UUID) prevents fetch failure during preflight/auth-lag
    if job_id in JOB_STATUS:
        return JOB_STATUS[job_id]
    
    # 🕵️ Global search for historical records
    # Note: We return status 200 even for past jobs to keep the polling loop healthy
    history_path = os.path.join(parent_dir, "api/history.json")
    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            all_history = json.load(f)
            # Flattened scan across all users for this specific job ID (Vantix Recovery)
            for user, jobs in all_history.items():
                if job_id in jobs:
                    return jobs[job_id]
        
    raise HTTPException(status_code=404, detail="Industrial node: Job identity unknown.")

@app.delete("/status/{job_id}")
def cancel_job(job_id: str):
    """🗑️ Vantix Kill & Purge — Cancelled jobs are deleted entirely"""
    CANCELLED_JOBS.add(job_id)
    
    # Remove from in-memory state immediately
    if job_id in JOB_STATUS:
        del JOB_STATUS[job_id]
    
    # 🏛️ [PURGE] Remove from persistent ledger across all users
    history_file = os.path.join(parent_dir, "api/history.json")
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            history = json.load(f)
        for user in history:
            if job_id in history[user]:
                del history[user][job_id]
                print(f"🗑️ [PURGE] Job {job_id} permanently deleted from {user}'s ledger.")
        with open(history_file, "w") as f:
            json.dump(history, f, indent=4)
    
    return {"status": "purged", "job_id": job_id}

@app.get("/history")
def get_history(username: str = Depends(get_current_user)):
    """📜 Retrieve Production Ledger from Disk (Identity Traced)"""
    print(f"🏛️ [IDENTITY] Serving production ledger for: {username}")
    return db_helper.get_user_history(username)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
