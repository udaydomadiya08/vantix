import groq
# 🛡️ [GLOBAL SDK LOCKDOWN]: Neutralizing 'proxies' at the root
try:
    _orig_init = groq.Client.__init__
    def _new_init(self, *args, **kwargs):
        kwargs.pop("proxies", None)
        _orig_init(self, *args, **kwargs)
    groq.Client.__init__ = _new_init
    groq.Groq.__init__ = _new_init # Double-seal
except:
    pass

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
from typing import List, Optional, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools
import stripe

# 💳 [FINANCIALS] Stripe Industrial Protocol
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

# 🏛️ [PRICING] Industrial Credit Tiers
STRIPE_PLANS = {
    "starter": {"amount": 1000, "credits": 100, "name": "Vantix Starter Cell"}, # $10.00
    "core": {"amount": 4500, "credits": 500, "name": "Vantix Engine Core"},   # $45.00
    "grid": {"amount": 15000, "credits": 2000, "name": "Vantix Industrial Grid"} # $150.00
}

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
SECRET_KEY = os.getenv("JWT_SECRET", "VANTIX_ULTRA_SECRET_2026")
ALGORITHM = "HS256"

# 📜 [TRACER] Industrial Audit Ledger
TRACE_LOG = os.path.join(os.path.dirname(__file__), "trace.log")

def log_trace(message: str):
    import datetime
    try:
        with open(TRACE_LOG, "a") as f:
            f.write(f"[{datetime.datetime.now().isoformat()}] {message}\n")
    except:
        pass

# 🛡️ [SOVEREIGN OVERRIDE] Universal CORS Bridge
# We allow all Vercel and HF subdomains explicitly to resolve 'Sovereign Sync Failure'
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https://.*\.vercel\.app|https://.*\.hf\.space|http://localhost:.*|http://127.0.0.1:.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📂 [DELIVERY] Mount Static Assets (Absolute Project Mapping)
try:
    os.makedirs(os.path.join(parent_dir, "static/videos"), exist_ok=True)
    os.makedirs(os.path.join(parent_dir, "static/ebooks"), exist_ok=True)
    os.makedirs(os.path.join(parent_dir, "static/thumbnails"), exist_ok=True)
    os.makedirs(os.path.join(parent_dir, "final_video"), exist_ok=True)
    os.makedirs(os.path.join(parent_dir, "courses"), exist_ok=True)
except Exception:
    # Fail gracefully if filesystem is read-only (Serverless Persistence)
    pass
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
        # 👑 [VANTIX CORE] Global Priority Queue: (priority_score, timestamp, job_id, func, kwargs)
        self.queue = asyncio.PriorityQueue()
        self.active_jobs = {} # {username: count}
        self.is_worker_running = False
        self.MAX_GLOBAL_CONCURRENCY = 5 # Matches EXECUTOR max_workers

    async def add_job(self, username, stream_type, job_id, func, kwargs):
        username = username.lower().strip()
        
        # ⚖️ [FAIRNESS] Calculate starting priority based on momentum
        momentum = db_helper.get_user_momentum(username)
        # Use timestamp as secondary key for Round Robin within same priority bracket
        timestamp = time.time()
        
        await self.queue.put((momentum, timestamp, username, job_id, func, kwargs))
        
        # 📝 [IDENTITY] Initial Status Entry
        topic = kwargs.get("topic", stream_type)
        job_data = {
            "status": "queued", 
            "stream": stream_type, 
            "topic": topic, 
            "submitted": datetime.now().isoformat(),
            "est_wait": 0,
            "position": 0
        }
        JOB_STATUS[job_id] = job_data
        
        # 🛡️ [QUOTA] Log initiation for the hourly ledger
        db_helper.log_job_initiation(username, job_id)
        db_helper.save_to_history(username, job_id, job_data)
        
        print(f"📥 [QUEUED] Job {job_id} for {username}. Priority Weight: {momentum:.2f}")
        
        if not self.is_worker_running:
            asyncio.create_task(self.global_worker())

    async def global_worker(self):
        """🏛️ [ORACLE] The Central Infinite Orchestrator Loop"""
        self.is_worker_running = True
        print("🚀 [VANTIX SCHEDULER] Oracle Node Online. Beginning Fair-Share Rotation.")
        
        while not self.queue.empty():
            # To respect EXECUTOR capacity, we only pull if slots are available
            # However, since run_in_executor uses the ThreadPoolExecutor which already limits concurrency,
            # we can pull and submit. The OS-level FIFO in the executor will handle the physical slots,
            # but OUR PriorityQueue handles the ORDER of submission.
            
            momentum, ts, username, job_id, func, kwargs = await self.queue.get()
            
            # 🕹️ [CANCEL CHECK]
            if job_id in CANCELLED_JOBS:
                print(f"🛑 [SCHEDULER] Skipping Cancelled Job: {job_id}")
                JOB_STATUS[job_id]["status"] = "cancelled"
                db_helper.save_to_history(username, job_id, JOB_STATUS[job_id])
                self.queue.task_done()
                continue

            # 🛠️ [EXECUTION] Fire-and-forget the processing task to allow next queue pull
            asyncio.create_task(self.process_job(username, job_id, func, kwargs))
            
            # Small stagger to prevent race conditions on DB files
            await asyncio.sleep(0.5)

        self.is_worker_running = False
        print("🏁 [VANTIX SCHEDULER] Oracle Node Idle.")

    async def process_job(self, username, job_id, func, kwargs):
        """⚡ [NODE] Individual Job Execution Lifecycle"""
        stream_type = JOB_STATUS[job_id]["stream"]
        print(f"⚙️ [SCHEDULER] Dispatching {stream_type} for {username} (ID: {job_id})")
        
        JOB_STATUS[job_id]["status"] = "processing"
        JOB_STATUS[job_id]["start"] = datetime.now().isoformat()
        db_helper.save_to_history(username, job_id, JOB_STATUS[job_id])
        
        try:
            loop = asyncio.get_event_loop()
            result_path = await loop.run_in_executor(EXECUTOR, functools.partial(func, **kwargs))
            
            JOB_STATUS[job_id]["status"] = "completed"
            if result_path and isinstance(result_path, str):
                rel_path = os.path.relpath(result_path, parent_dir).replace("\\", "/")
                JOB_STATUS[job_id]["result_url"] = f"http://127.0.0.1:8000/download?path={rel_path}"
                
            print(f"✅ [SUCCESS] {stream_type} Completed for {username}")
        except Exception as e:
            print(f"❌ [FAILURE] {stream_type} Failed for {username}: {e}")
            JOB_STATUS[job_id]["status"] = "failed"
            JOB_STATUS[job_id]["error"] = str(e)
        finally:
            db_helper.save_to_history(username, job_id, JOB_STATUS[job_id])
            self.queue.task_done()

    def get_queue_info(self, username, stream_type, job_id):
        """🕵️ [ORACLE] Locate position and calculate Estimated Wait Time."""
        # Peek into PriorityQueue
        q_list = sorted(list(self.queue._queue))
        
        try:
            position = 1
            for momentum, ts, user, jid, _, _ in q_list:
                if jid == job_id: break
                position += 1
            else:
                return 0, 0
            
            # ⏱️ [ESTIMATION] Based on industrial averages and current queue depth
            # Video: 150s, Ebook: 300s, Course: 600s
            DURATIONS = {"video": 120, "ebook": 240, "course": 480, "thumbnail": 30}
            base_time = DURATIONS.get(stream_type, 60)
            
            # Simple Fair-Share Projection: (Position * BaseTime) / AvailableSlots
            # We assume a 20% concurrency overlap
            est_wait = (position * base_time) / 2
            
            # Hard limit for readability
            return position, round(est_wait)
        except Exception:
            return 0, 0

    def get_global_stats(self):
        """🏛️ [ORACLE] Ecosystem Telemetry."""
        total_queued = self.queue.qsize()
        live_jobs = []
        q_list = list(self.queue._queue)
        
        for momentum, ts, user, jid, _, _ in q_list:
            status = JOB_STATUS.get(jid, {})
            live_jobs.append({
                "id": jid, "user": user, "type": status.get("stream"),
                "topic": status.get("topic"), "submitted": status.get("submitted"),
                "priority": round(momentum, 2)
            })
        
        return {
            "live_queue_count": total_queued,
            "live_jobs": sorted(live_jobs, key=lambda x: x.get("submitted", ""), reverse=True),
            "load_percentage": min(round((total_queued / 10) * 100), 100)
        }

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
    script: Optional[str] = None
    mode: str = "topic"
    niche: Optional[str] = None
    avatar: Any = None 
    horizontal: Any = None
    voice_id: str = "alloy"

    class Config:
        extra = "allow"

class EbookRequest(BaseModel):
    topic: str = ""
    description: Optional[str] = ""
    chapters: int = 3
    min_words: int = 150
    theme_color: str = "#1e293b"
    images_toggle: bool = True

    class Config:
        extra = "allow"

class CourseRequest(BaseModel):
    topic: str = ""
    horizontal: Any = False
    include_avatar: Any = False

    class Config:
        extra = "allow"

class ThumbnailRequest(BaseModel):
    topic: str = ""

    class Config:
        extra = "allow"

class DefaultsRequest(BaseModel):
    factory_type: str
    settings: dict

class CheckoutRequest(BaseModel):
    plan_id: str # starter, core, grid

# --- Auth Utilities ---
def create_token(username: str):
    # 🏛️ [SAAS PROTOCOL] 30-Day Industrial Session Window
    expire = datetime.utcnow() + timedelta(days=30)
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
    username = user.username.lower().strip()
    if db_helper.create_user(username, user.password):
        return {"message": "User created successfully", "token": create_token(username)}
    raise HTTPException(status_code=400, detail="User already exists")

@app.post("/auth/login")
def login(user: UserAuth):
    username = user.username.lower().strip()
    existing = db_helper.get_user(username)
    
    # 🏛️ [IDENTITY ADOPTION PROTOCOL]
    # If the admin node was reconstituted with a placeholder, adopts the next login attempt as the master password.
    if username == "uday" and existing:
        reconstitution_hashes = [
            db_helper.hash_password("initial_reconstitution"),
            "RECONSTITUTED_NODE"
        ]
        if existing.get("password") in reconstitution_hashes:
            print(f"🛠️ [ADOPTION]: 'uday' node adopting new master password from current attempt.")
            import json
            users = db_helper._load_json_secure(db_helper.DB_PATH)
            users[username]["password"] = db_helper.hash_password(user.password)
            db_helper._save_json_atomic(db_helper.DB_PATH, users)
            # Refresh 'existing' after adoption
            existing = users[username]

    # 🛡️ [STANDARD HANDSHAKE] Verify Node Identity
    if existing:
        if existing["password"] == db_helper.hash_password(user.password):
            log_trace(f"LOGIN_SUCCESS: User='{username}' | Status=Authenticated")
            return {"token": create_token(username), "username": username}
        else:
            log_trace(f"LOGIN_FAIL: User='{username}' | Reason='Invalid Password'")
    else:
        log_trace(f"LOGIN_FAIL: User='{username}' | Reason='Identity Not Found'")

    raise HTTPException(status_code=401, detail="Vantix Authentication Failure: Invalid credentials or node not found.")

@app.get("/user/keys")
def get_user_keys(username: str = Depends(get_current_user)):
    keys = db_helper.get_user_keys(username)
    log_trace(f"GET_KEYS: User='{username}' | Found={bool(keys)}")
    return keys

@app.post("/user/keys")
def update_user_keys(keys: APIKeys, username: str = Depends(get_current_user)):
    log_trace(f"POST_KEYS: User='{username}' | Payload={list(keys.dict(exclude_unset=True).keys())}")
    success = db_helper.update_user_keys(username, keys.dict(exclude_unset=True))
    if not success:
        raise HTTPException(status_code=500, detail="Industrial Vault write failure.")
    return {"message": "Keys synchronized."}

# 🛰️ [TELEMETRY] Live Industrial Log Proxy (SSE)
@app.get("/admin/logs/stream")
async def stream_logs(request: Request, payload: dict = Depends(get_current_user)):
    if payload != "uday": # get_current_user returns the username string
        raise HTTPException(status_code=403, detail="Sovereign Access Denied.")

    import httpx
    from fastapi.responses import StreamingResponse

    # 🔗 Extract HF Token from Vault (stored in users.json)
    user_data = db_helper.get_user(payload)
    hf_token = user_data.get("keys", {}).get("hf_token") or os.getenv("HF_TOKEN")

    if not hf_token:
        # Fallback to local trace.log if no HF Token is configured
        async def local_generator():
            if os.path.exists(TRACE_LOG):
                with open(TRACE_LOG, "r") as f:
                    # Send last 50 lines initially
                    lines = f.readlines()
                    for line in lines[-50:]:
                        yield f"data: {line}\n\n"
                    # Tail the file (Basic realization)
                    while True:
                        line = f.readline()
                        if line: yield f"data: {line}\n\n"
                        await asyncio.sleep(1)
            else:
                yield "data: [SYSTEM]: Industrial Audit Ledger empty.\n\n"
        return StreamingResponse(local_generator(), media_type="text/event-stream")

    # 🚀 Proxy to Hugging Face API
    async def hf_generator():
        url = "https://huggingface.co/api/spaces/UDAYDOMADIYA/vantix-core/logs/run"
        headers = {"Authorization": f"Bearer {hf_token}"}
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", url, headers=headers) as response:
                async for line in response.aiter_lines():
                    if await request.is_disconnected(): break
                    yield f"data: {line}\n\n"

    return StreamingResponse(hf_generator(), media_type="text/event-stream")

@app.get("/user/defaults")
def get_user_defaults(username: str = Depends(get_current_user)):
    return db_helper.get_user_defaults(username)

@app.post("/user/defaults")
def update_user_defaults(req: DefaultsRequest, username: str = Depends(get_current_user)):
    db_helper.update_user_defaults(username, req.factory_type, req.settings)
    return {"message": f"Defaults for {req.factory_type} updated"}

@app.get("/user/balance")
def get_balance(username: str = Depends(get_current_user)):
    return {"balance": db_helper.get_user_balance(username)}

# --- 🔐 [SECURITY] Vault Sentinel ---
def verify_vault_integrity(keys: dict, groups: list):
    """🛡️ Sentinel: Enforce presence of required industrial nodes (OR-Logic supported)"""
    missing_groups = []
    for group in groups:
        # If any key in the group exists, the group is satisfied
        if not any(keys.get(k) for k in group):
            missing_groups.append(group)
            
    if missing_groups:
        # 🕵️ Map groups to human-readable categories for UX
        readable_map = {
            "groq": "Thinking Node (AI Logic)",
            "openrouter": "Thinking Node (AI Logic)",
            "pexels": "Visual Node (Stock Footage)",
            "pixabay": "Visual Node (Stock Footage)"
        }
        
        category_errors = []
        for group in missing_groups:
            cat_name = readable_map.get(group[0], "Industrial Node")
            category_errors.append(cat_name)

        raise HTTPException(
            status_code=428, 
            detail={
                "error": "vault_locked", 
                "message": f"Vault Locked: Missing {', '.join(category_errors)}. Please configure your keys in the Sovereign Vault.",
                "missing_categories": category_errors
            }
        )
    return True

def verify_industrial_quota(username: str):
    """⚖️ [SENTINEL] Dynamic Industrial Admission Controller (v103.8)"""
    # 🏛️ [SOVEREIGN IMMORTALITY]: Admin node is immune to momentum throttles
    if username.lower() == "uday":
        return True

    momentum = db_helper.get_user_momentum(username)
    
    # 💥 [VANTIX GOVERNANCE]: Only hard-block if the node pressure is critical (Momentum > 1000)
    # This prevents the 'Infrastructure Unreachable' crash on underpowered CPU nodes.
    if momentum > 1000:
        raise HTTPException(
            status_code=429, 
            detail={
                "error": "node_pressure_high", 
                "message": "Vantix Node Pressure High. Your jobs are queued, but new requests are restricted until cooling.",
                "momentum": round(momentum)
            }
        )
    return True

@app.post("/payments/create-checkout-session")
async def create_checkout_session(req: CheckoutRequest, username: str = Depends(get_current_user)):
    """💳 Initiate Industrial Credit Transfer via Stripe"""
    if req.plan_id not in STRIPE_PLANS:
        raise HTTPException(status_code=400, detail="Invalid Industrial Plan")
    
    plan = STRIPE_PLANS[req.plan_id]
    frontend_url = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")[0].strip()
    
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': plan["name"],
                        'description': f"Injection of {plan['credits']} Industrial Credits into Node {username}",
                    },
                    'unit_amount': plan["amount"],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=f"{frontend_url}/recharge?success=true",
            cancel_url=f"{frontend_url}/recharge?canceled=true",
            client_reference_id=username,
            metadata={
                "plan_id": req.plan_id,
                "credits": plan["credits"]
            }
        )
        return {"url": session.url}
    except Exception as e:
        print(f"❌ [STRIPE] Checkout Session Failed: {e}")
        raise HTTPException(status_code=500, detail="Stripe Node failure")

@app.post("/payments/webhook")
async def stripe_webhook(request: Request):
    """🏛️ Webhook Sentinel: Verify and Inject Credits"""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except Exception as e:
        print(f"⚠️ [WEBHOOK] Signature failure: {e}")
        raise HTTPException(status_code=400, detail="Invalid Signature")
    
    # 💎 [SUCCESS EVENT]
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        username = session.get('client_reference_id')
        metadata = session.get('metadata', {})
        credits_to_add = int(metadata.get('credits', 0))
        
        if username and credits_to_add > 0:
            print(f"💎 [STRIPE SUCCESS] Injecting {credits_to_add} Credits for: {username}")
            db_helper.add_credits(username, credits_to_add)
            
    return {"status": "success"}

@app.post("/payments/reload")
def reload_credits(amount: int, username: str = Depends(get_current_user)):
    success, new_balance = db_helper.add_credits(username, amount)
    if success:
        return {"message": "Node Reloaded", "balance": new_balance}
    raise HTTPException(status_code=400, detail="Recharge Failed")

# --- Home ---
@app.get("/")
def read_root():
    return {"status": "Vantix Sovereign Engine Active", "version": "Industrial Hardening Active"}

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
    # ⚖️ [QUOTA] Industrial Sentinel
    verify_industrial_quota(username)

    # ⚖️ [TAXATION] Video Cost: 5 Credits
    success, balance = db_helper.deduct_credits(username, 5)
    if not success:
        raise HTTPException(status_code=402, detail=f"Insufficient Vantix Power. Balance: {balance}")

    try:
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
        
        # 🔐 [SENTINEL] Hard-Lock: Requires (Groq OR OpenRouter) AND (Pexels OR Pixabay)
        verify_vault_integrity(user_keys, [["groq", "openrouter"], ["pexels", "pixabay"]])
        
        # ⚙️ [DEFAULTS MERGE] Properly merge frontend explicit options with saved defaults
        req_dict = request.model_dump(exclude_unset=True) if hasattr(request, "model_dump") else request.dict(exclude_unset=True)
        
        kwargs = {
            "forced_topic": enriched_topic,
            "forced_script": request.script,
            "mode": request.mode,
            "niche": request.niche,
            "forced_avatar": req_dict.get("avatar", db_defaults.get("include_avatar", False)),
            "horizontal": req_dict.get("horizontal", db_defaults.get("horizontal", False)),
            "voice_id": req_dict.get("voice_id", db_defaults.get("voice_id", "alloy")),
            "visual_source": req_dict.get("visual_source", db_defaults.get("visual_source", "pexels")),
            "user_keys": user_keys
        }
        
        await QUEUE_MANAGER.add_job(username, "video", job_id, run_full_vso.run_full_vso, kwargs)
        return {"job_id": job_id, "message": "Short production stream initiated", "topic": request.topic}
    except Exception as e:
        # 🛡️ [REFUND] Immediate credit restoration on node failure
        db_helper.add_credits(username, 5)
        log_trace(f"REFUND: User='{username}' | Job='video' | Reason='{str(e)}'")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Factory node failure: {str(e)}")

@app.get("/version")
async def get_version():
    return {"version": "Industrial Hardening Active", "timestamp": "2026-04-15", "node": "Sovereign-1"}

@app.post("/generate-thumbnail")
async def generate_thumbnail(request: ThumbnailRequest, username: str = Depends(get_current_user)):
    """🎨 Synthesize an Omnipotent High-CTR Thumbnail"""
    # ⚖️ [QUOTA] Industrial Sentinel
    verify_industrial_quota(username)

    # ⚖️ [TAXATION] Thumbnail Cost: 2 Credits
    success, balance = db_helper.deduct_credits(username, 2)
    if not success:
        raise HTTPException(status_code=402, detail=f"Insufficient Vantix Power. Balance: {balance}")

    try:
        job_id = str(uuid.uuid4())
        user_keys = db_helper.get_user_keys(username)
        # 🔐 [SENTINEL] Hard-Lock: Requires (Groq OR OpenRouter)
        verify_vault_integrity(user_keys, [["groq", "openrouter"]])
        
        kwargs = {
            "topic": request.topic,
            "user_keys": user_keys
        }
        
        await QUEUE_MANAGER.add_job(username, "thumbnail", job_id, thumbnail_service.create_vantix_thumbnail, kwargs)
        return {"job_id": job_id, "message": "Thumbnail synthesis engine active", "topic": request.topic}
    except Exception as e:
        # 🛡️ [REFUND] Immediate credit restoration on node failure
        db_helper.add_credits(username, 2)
        log_trace(f"REFUND: User='{username}' | Job='thumbnail' | Reason='{str(e)}'")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Factory node failure: {str(e)}")

@app.post("/generate/ebook")
async def generate_ebook(
    request: EbookRequest, 
    username: str = Depends(get_current_user),
    x_groq_key: str = Header(None),
    x_openrouter_key: str = Header(None)
):
    """📚 Industrial E-book Production"""
    # ⚖️ [QUOTA] Industrial Sentinel
    verify_industrial_quota(username)

    # ⚖️ [TAXATION] E-Book Cost: 10 Credits
    success, balance = db_helper.deduct_credits(username, 10)
    if not success:
        raise HTTPException(status_code=402, detail=f"Insufficient Vantix Power. Balance: {balance}")

    try:
        job_id = str(uuid.uuid4())
        db_keys = db_helper.get_user_keys(username)
        
        user_keys = {
            "groq": x_groq_key or db_keys.get("groq"),
            "openrouter": x_openrouter_key or db_keys.get("openrouter")
        }
        
        # 🔐 [SENTINEL] Hard-Lock: Requires (Groq OR OpenRouter)
        verify_vault_integrity(user_keys, [["groq", "openrouter"]])
        
        db_defaults = db_helper.get_user_defaults(username).get("ebook", {})
        req_dict = request.model_dump(exclude_unset=True) if hasattr(request, "model_dump") else request.dict(exclude_unset=True)

        kwargs = {
            "topic": request.topic,
            "description": req_dict.get("description", db_defaults.get("description", "")),
            "num_chapters": req_dict.get("chapters", db_defaults.get("num_chapters", 3)),
            "min_words": req_dict.get("min_words", db_defaults.get("min_words", 150)),
            "theme_color": req_dict.get("theme_color", db_defaults.get("theme_color", "#1e293b")),
            "images_toggle": req_dict.get("images_toggle", db_defaults.get("include_images", True)),
            "user_keys": user_keys
        }
        
        await QUEUE_MANAGER.add_job(username, "ebook", job_id, ebook.automate_ebook_creation, kwargs)
        return {"job_id": job_id, "message": "E-book queued in research stream", "topic": request.topic}
    except Exception as e:
        # 🛡️ [REFUND] Immediate credit restoration on node failure
        db_helper.add_credits(username, 10)
        log_trace(f"REFUND: User='{username}' | Job='ebook' | Reason='{str(e)}'")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Factory node failure: {str(e)}")

@app.post("/generate/course")
async def generate_course(
    request: CourseRequest,
    username: str = Depends(get_current_user),
    x_groq_key: str = Header(None),
    x_openrouter_key: str = Header(None)
):
    """🎓 Industrial E-course Production"""
    # ⚖️ [QUOTA] Industrial Sentinel
    verify_industrial_quota(username)

    # ⚖️ [TAXATION] E-Course Cost: 25 Credits
    success, balance = db_helper.deduct_credits(username, 25)
    if not success:
        raise HTTPException(status_code=402, detail=f"Insufficient Vantix Power. Balance: {balance}")

    try:
        job_id = str(uuid.uuid4())
        db_keys = db_helper.get_user_keys(username)
        
        user_keys = {
            "groq": x_groq_key or db_keys.get("groq"),
            "openrouter": x_openrouter_key or db_keys.get("openrouter")
        }
        
        # 🔐 [SENTINEL] Hard-Lock: Requires (Groq OR OpenRouter)
        verify_vault_integrity(user_keys, [["groq", "openrouter"]])
        
        db_defaults = db_helper.get_user_defaults(username).get("course", {})
        req_dict = request.model_dump(exclude_unset=True) if hasattr(request, "model_dump") else request.dict(exclude_unset=True)

        import ecourse_factory
        kwargs = {
            "topic": request.topic,
            "horizontal": req_dict.get("horizontal", db_defaults.get("horizontal", False)),
            "include_avatar": req_dict.get("include_avatar", db_defaults.get("include_avatar", False)),
            "user_keys": user_keys
        }
        
        await QUEUE_MANAGER.add_job(username, "course", job_id, ecourse_factory.run_ecourse_factory, kwargs)
        return {"job_id": job_id, "message": "E-course queued in educational stream", "topic": request.topic}
    except Exception as e:
        # 🛡️ [REFUND] Immediate credit restoration on node failure
        db_helper.add_credits(username, 25)
        log_trace(f"REFUND: User='{username}' | Job='course' | Reason='{str(e)}'")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Factory node failure: {str(e)}")

@app.get("/status/{job_id}")
async def get_status(job_id: str):
    # 🏛️ [VANTIX PERSISTENCE] Check In-Memory first, then fall back to Ledger
    # Public access (unguessable UUID) prevents fetch failure during preflight/auth-lag
    if job_id in JOB_STATUS:
        job = JOB_STATUS[job_id]
        if job["status"] == "queued":
            # 🕵️ Calculate live position and wait time
            # We don't have the username/type here easily so we scan
            for (usr, styp), q in QUEUE_MANAGER.queues.items():
                pos, est = QUEUE_MANAGER.get_queue_info(usr, styp, job_id)
                if pos > 0:
                    job["position"] = pos
                    job["est_wait"] = est
                    break
        return job
    
    # 🕵️ Global search for historical records
    history_file = os.path.join(parent_dir, "api/history.json")
    if os.path.exists(history_file):
        with open(history_file, "r") as f:
            all_history = json.load(f)
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
            with open(history_file, "w") as f:
                json.dump(history, f, indent=4)
    
    return {"message": "Job killed and purged from ledger."}

@app.get("/history")
def read_history(username: str = Depends(get_current_user)):
    return db_helper.get_user_history(username)

@app.get("/admin/stats")
def admin_stats(username: str = Depends(get_current_user)):
    if username != "uday":
        raise HTTPException(status_code=403, detail="Industrial protocol: Administrative access restricted.")
    return QUEUE_MANAGER.get_global_stats()

@app.get("/admin/users")
def admin_users(username: str = Depends(get_current_user)):
    if username != "uday":
        raise HTTPException(status_code=403, detail="Industrial protocol: Administrative access restricted.")
    return db_helper.get_all_users_summary()
