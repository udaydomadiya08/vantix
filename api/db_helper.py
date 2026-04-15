import json
import os
import hashlib
from datetime import datetime
import crypto_helper
from crypto_helper import encrypt_key, decrypt_key

# 🏛️ [AUTHORITY] Dynamic Project Paths (Industrial Synchrony)
DATA_DIR = os.getenv("VANTIX_DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "users.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")
TRANSACTIONS_PATH = os.path.join(DATA_DIR, "transactions.json")
QUOTAS_PATH = os.path.join(DATA_DIR, "quotas.json")

def _load_json_secure(path, default_factory=dict):
    """🛡️ [SELF-HEAL] Safely load JSON, handling empty or corrupt files."""
    if not os.path.exists(path):
        return default_factory()
    try:
        with open(path, "r") as f:
            content = f.read().strip()
            if not content:
                print(f"⚠️ [DATABASE] Self-Healing empty file: {path}")
                return default_factory()
            return json.loads(content)
    except Exception as e:
        print(f"⚠️ [DATABASE] Self-Healing corrupt file: {path} | Error: {e}")
        return default_factory()

def _save_json_atomic(path, data):
    """💾 [ATOMIC] Secure write pattern using temporary file swap."""
    temp_path = f"{path}.tmp"
    try:
        with open(temp_path, "w") as f:
            json.dump(data, f, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, path) # Atomic swap
        return True
    except Exception as e:
        print(f"❌ [DATABASE] Atomic Write Failure: {path} | Error: {e}")
        try:
            with open(path, "w") as f: json.dump(data, f, indent=4)
            return True
        except: return False

def initialize_db():
    if not os.path.exists(DB_PATH):
        _save_json_atomic(DB_PATH, {})

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    initialize_db()
    username = username.lower().strip()
    users = _load_json_secure(DB_PATH)
    
    # 🏛️ [RECONSTITUTION GATE] Auto-Restore 'uday' node if it was lost in corruption
    if username == "uday" and not users.get("uday"):
        print("🛠️ [REANIMATION]: 'uday' node lost. Re-injecting with Industrial Credits...")
        create_user("uday", "initial_reconstitution")
        add_credits("uday", 1000) # Industrial Restoration Grant
        users = _load_json_secure(DB_PATH)

    return users.get(username)

DEFAULT_STRUCTURE = {
    "video": {
        "horizontal": False,
        "include_avatar": False,
        "voice_id": "alloy",
        "visual_source": "pexels"
    },
    "ebook": {
        "num_chapters": 3,
        "min_words": 150,
        "include_images": True,
        "chapter_art": True
    },
    "course": {
        "horizontal": False,
        "include_avatar": False
    }
}

def create_user(username, password):
    initialize_db()
    username = username.lower().strip()
    users = _load_json_secure(DB_PATH)
    
    if username in users:
        return False
    
    users[username] = {
        "username": username,
        "password": hash_password(password),
        "api_keys": {
            "groq": None,
            "openrouter": None,
            "pexels": None,
            "pixabay": None
        },
        "defaults": DEFAULT_STRUCTURE,
        "balance": 50
    }
    
    return _save_json_atomic(DB_PATH, users)

def get_user_keys(username):
    username = username.lower().strip()
    user = get_user(username)
    if user:
        keys = user.get("api_keys", {})
        return {k: decrypt_key(v) if v else None for k, v in keys.items()}
    return {}

def update_user_keys(username, keys):
    initialize_db()
    username = username.lower().strip()
    users = _load_json_secure(DB_PATH)
    
    if username not in users:
        # 🏛️ [EXTREME HEALING] 
        users[username] = {
            "username": username,
            "password": "RECONSTITUTED_NODE",
            "balance": 1000, 
            "api_keys": {},
            "defaults": DEFAULT_STRUCTURE
        }
        
    if not isinstance(users[username].get("api_keys"), dict):
        users[username]["api_keys"] = {
            "groq": None, "openrouter": None, "pexels": None, "pixabay": None
        }
            
    encrypted_keys = {k: encrypt_key(v) if (v and str(v).strip()) else None for k, v in keys.items()}
    users[username]["api_keys"].update(encrypted_keys)
    
    return _save_json_atomic(DB_PATH, users)

def update_user_defaults(username, factory_type, defaults):
    initialize_db()
    username = username.lower().strip()
    users = _load_json_secure(DB_PATH)
    
    if username in users:
        if "defaults" not in users[username]:
            users[username]["defaults"] = {}
        if factory_type not in users[username]["defaults"]:
            users[username]["defaults"][factory_type] = {}
            
        users[username]["defaults"][factory_type].update(defaults)
        return _save_json_atomic(DB_PATH, users)
    return False

def get_user_defaults(username):
    username = username.lower().strip()
    user = get_user(username)
    if user:
        user_defaults = user.get("defaults", {})
        # Merge with DEFAULT_STRUCTURE to ensure all keys exist
        for factory, settings in DEFAULT_STRUCTURE.items():
            if factory not in user_defaults:
                user_defaults[factory] = settings
            else:
                for key, val in settings.items():
                    if key not in user_defaults[factory]:
                        user_defaults[factory][key] = val
        return user_defaults
    return DEFAULT_STRUCTURE

def save_to_history(username, job_id, job_data):
    """🏛️ Archive Job Metadata to Industrial Ledger (Completed Only)"""
    username = username.lower().strip()
    if job_data.get("status") != "completed" or not job_data.get("result_url"):
        return False

    history = _load_json_secure(HISTORY_PATH)
    
    if username not in history:
        history[username] = {}
    
    if job_id not in history[username]:
        history[username][job_id] = job_data
    else:
        history[username][job_id].update(job_data)
        
    return _save_json_atomic(HISTORY_PATH, history)

def _normalize_result_url(url):
    """🏛️ [SANITIZER] Normalize any broken result_url to the correct download endpoint."""
    if not url:
        return url
    # If already a proper download endpoint, return it
    if url.startswith("http://127.0.0.1:8000/download?path="):
        return url
    # Extract the relative path (static/..., courses/..., final_video/...)
    import re
    match = re.search(r'(static/[^\s]+|courses/[^\s]+|final_video/[^\s]+)', url)
    if match:
        return f"http://127.0.0.1:8000/download?path={match.group(1)}"
    return url

def get_user_history(username):
    """📜 Retrieve Production Ledger"""
    username = username.lower().strip()
    history = _load_json_secure(HISTORY_PATH)
    
    user_jobs = history.get(username, {})
    return sorted(
        [{"id": jid, **{**data, "result_url": _normalize_result_url(data.get("result_url"))}}
         for jid, data in user_jobs.items()],
        key=lambda x: x.get("submitted", ""),
        reverse=True
    )

def log_job_initiation(username, job_id):
    """⚔️ [LOG] Record the start of a synthesis job for quota tracking."""
    import time
    username = username.lower().strip()
    quotas = _load_json_secure(QUOTAS_PATH, default_factory=list)
    
    quotas.append({
        "username": username,
        "job_id": job_id,
        "timestamp": time.time()
    })
    
    cutoff = time.time() - (24 * 3600)
    quotas = [q for q in quotas if q["timestamp"] > cutoff]
    
    return _save_json_atomic(QUOTAS_PATH, quotas)

def get_recent_job_count(username, minutes=60):
    """⚖️ [QUOTA] Calculate how many jobs a node initiated in the last window."""
    import time
    username = username.lower().strip()
    quotas = _load_json_secure(QUOTAS_PATH, default_factory=list)
    
    cutoff = time.time() - (minutes * 60)
    return len([q for q in quotas if q["username"] == username and q["timestamp"] > cutoff])

def get_user_balance(username):
    """💎 Retrieve current Vantix power level"""
    username = username.lower().strip()
    user = get_user(username)
    return user.get("balance", 0) if user else 0

def deduct_credits(username, amount):
    """⚖️ Process Synthesis Taxation"""
    initialize_db()
    username = username.lower().strip()
    users = _load_json_secure(DB_PATH)
    
    if username in users:
        current = users[username].get("balance", 0)
        if current < amount:
            return False, current
        
        users[username]["balance"] = current - amount
        success = _save_json_atomic(DB_PATH, users)
        return success, users[username]["balance"]
    return False, 0

def add_credits(username, amount):
    """💳 Reload Production Node"""
    initialize_db()
    username = username.lower().strip()
    users = _load_json_secure(DB_PATH)
    
    if username in users:
        current = users[username].get("balance", 0)
        users[username]["balance"] = current + amount
        
        import time
        tx_data = {"username": username, "amount": amount, "timestamp": time.time(), "date": datetime.now().isoformat()}
        txs = _load_json_secure(TRANSACTIONS_PATH, default_factory=list)
        txs.append(tx_data)
        _save_json_atomic(TRANSACTIONS_PATH, txs)
        
        success = _save_json_atomic(DB_PATH, users)
        return success, users[username]["balance"]
    return False, 0

def get_admin_stats():
    """🏛️ [ORACLE] Aggregate ecosystem-wide production metrics"""
    initialize_db()
    users = _load_json_secure(DB_PATH)
    history = _load_json_secure(HISTORY_PATH)
    
    total_users = len(users)
    total_balance = sum(u.get("balance", 0) for u in users.values())
    
    job_counts = {"video": 0, "ebook": 0, "course": 0, "thumbnail": 0}
    total_jobs = 0
    for user_jobs in history.values():
        for job in user_jobs.values():
            s_type = job.get("stream", "unknown")
            if s_type in job_counts:
                job_counts[s_type] += 1
                total_jobs += 1
    
    txs = _load_json_secure(TRANSACTIONS_PATH, default_factory=list)
    total_invoiced = sum(tx["amount"] for tx in txs)

    return {
        "users": total_users,
        "balance": total_balance,
        "total_jobs": total_jobs,
        "job_breakdown": job_counts,
        "total_invoiced": total_invoiced
    }

def get_all_users_summary():
    """👥 [IDENTITY] List all nodes and their status"""
    initialize_db()
    users = _load_json_secure(DB_PATH)
    summary = []
    for username, data in users.items():
        summary.append({
            "username": username,
            "balance": data.get("balance", 0),
            "keys_configured": sum(1 for v in data.get("api_keys", {}).values() if v)
        })
    return sorted(summary, key=lambda x: x["balance"], reverse=True)
