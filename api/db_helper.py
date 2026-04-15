import json
import os
import hashlib
import crypto_helper
from crypto_helper import encrypt_key, decrypt_key

# 🏛️ [AUTHORITY] Dynamic Project Paths (Industrial Synchrony)
# Allow redirection to persistent storage (e.g. /data on Hugging Face)
DATA_DIR = os.getenv("VANTIX_DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "users.json")
HISTORY_PATH = os.path.join(DATA_DIR, "history.json")
TRANSACTIONS_PATH = os.path.join(DATA_DIR, "transactions.json")
QUOTAS_PATH = os.path.join(DATA_DIR, "quotas.json")

def initialize_db():
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({}, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user(username):
    initialize_db()
    username = username.lower().strip()
    with open(DB_PATH, "r") as f:
        users = json.load(f)
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
    with open(DB_PATH, "r") as f:
        users = json.load(f)
    
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
    
    with open(DB_PATH, "w") as f:
        json.dump(users, f, indent=4)
        f.flush()
        os.fsync(f.fileno())
    return True

def get_user_keys(username):
    username = username.lower().strip()
    user = get_user(username)
    if user:
        keys = user.get("api_keys", {})
        # Decrypt keys before returning to the engine
        return {k: decrypt_key(v) if v else None for k, v in keys.items()}
    return {}

def update_user_keys(username, keys):
    initialize_db()
    username = username.lower().strip()
    with open(DB_PATH, "r") as f:
        users = json.load(f)
    
    if username not in users:
        # 🏛️ [EXTREME HEALING] Reconstitute missing user node automatically
        print(f"🛠️ [DATABASE] Reconstituting lost identity node for: {username}")
        users[username] = {
            "username": username,
            "password": "RECONSTITUTED_NODE", # Password remains invalid for login, requires reset or token persistence
            "balance": 50, # Industrial Grant
            "api_keys": {},
            "defaults": {
                "video": {"horizontal": False, "voice_id": "alloy", "include_avatar": False},
                "ebook": {"chapters": 3, "min_words": 150},
                "course": {"horizontal": False, "include_avatar": False}
            }
        }
        
    # 🏛️ [IDENTITY SHIELD] Ensure api_keys node exists as a dictionary
    if not isinstance(users[username].get("api_keys"), dict):
        users[username]["api_keys"] = {
            "groq": None, "openrouter": None, "pexels": None, "pixabay": None
        }
            
        # 🧪 [VAULT HEAL] Re-encrypt and overwrite with fresh identity credentials
        encrypted_keys = {k: encrypt_key(v) if (v and str(v).strip()) else None for k, v in keys.items()}
        users[username]["api_keys"].update(encrypted_keys)
        
        with open(DB_PATH, "w") as f:
            json.dump(users, f, indent=4)
            # 🛡️ [RESILIENCE] Graceful sync for restricted environments
            try:
                f.flush()
                os.fsync(f.fileno())
            except Exception:
                pass
            
        print(f"✅ [DATABASE] Vault Synchronized for User='{username}'")
        return True
    return False

def update_user_defaults(username, factory_type, defaults):
    initialize_db()
    username = username.lower().strip()
    with open(DB_PATH, "r") as f:
        users = json.load(f)
    
    if username in users:
        if "defaults" not in users[username]:
            users[username]["defaults"] = {}
        if factory_type not in users[username]["defaults"]:
            users[username]["defaults"][factory_type] = {}
            
        users[username]["defaults"][factory_type].update(defaults)
        with open(DB_PATH, "w") as f:
            json.dump(users, f, indent=4)
            # 🛡️ [RESILIENCE] Graceful sync for restricted environments
            try:
                f.flush()
                os.fsync(f.fileno())
            except Exception:
                pass
        return True
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
    # 🗑️ [CLEAN LEDGER] Only persist completed jobs that have an asset
    if job_data.get("status") != "completed" or not job_data.get("result_url"):
        return False

    if not os.path.exists(HISTORY_PATH):
        with open(HISTORY_PATH, "w") as f: json.dump({}, f)
    
    with open(HISTORY_PATH, "r") as f:
        history = json.load(f)
    
    if username not in history:
        history[username] = {}
    
    # Write/update the completed entry
    if job_id not in history[username]:
        history[username][job_id] = job_data
    else:
        history[username][job_id].update(job_data)
        
    with open(HISTORY_PATH, "w") as f:
        json.dump(history, f, indent=4)
    return True

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
    if not os.path.exists(HISTORY_PATH):
        return []
    
    with open(HISTORY_PATH, "r") as f:
        history = json.load(f)
    
    user_jobs = history.get(username, {})
    # Return as list sorted by timestamp (desc), with normalized URLs
    sorted_history = sorted(
        [{"id": jid, **{**data, "result_url": _normalize_result_url(data.get("result_url"))}}
         for jid, data in user_jobs.items()],
        key=lambda x: x.get("submitted", ""),
        reverse=True
    )
    return sorted_history

def log_job_initiation(username, job_id):
    """⚔️ [LOG] Record the start of a synthesis job for quota tracking."""
    import time
    username = username.lower().strip()
    if not os.path.exists(QUOTAS_PATH):
        with open(QUOTAS_PATH, "w") as f: json.dump([], f)
    
    with open(QUOTAS_PATH, "r") as f:
        quotas = json.load(f)
    
    quotas.append({
        "username": username,
        "job_id": job_id,
        "timestamp": time.time()
    })
    
    # 🧹 [PURGE] Keep quotas file clean (remove jobs older than 24h)
    cutoff = time.time() - (24 * 3600)
    quotas = [q for q in quotas if q["timestamp"] > cutoff]
    
    with open(QUOTAS_PATH, "w") as f:
        json.dump(quotas, f, indent=4)

def get_recent_job_count(username, minutes=60):
    """⚖️ [QUOTA] Calculate how many jobs a node initiated in the last window."""
    import time
    username = username.lower().strip()
    if not os.path.exists(QUOTAS_PATH):
        return 0
    
    with open(QUOTAS_PATH, "r") as f:
        quotas = json.load(f)
    
    cutoff = time.time() - (minutes * 60)
    user_recent_jobs = [q for q in quotas if q["username"] == username and q["timestamp"] > cutoff]
    return len(user_recent_jobs)

def get_user_balance(username):
    """💎 Retrieve current Vantix power level"""
    username = username.lower().strip()
    user = get_user(username)
    return user.get("balance", 0) if user else 0

def deduct_credits(username, amount):
    """⚖️ Process Synthesis Taxation"""
    initialize_db()
    username = username.lower().strip()
    with open(DB_PATH, "r") as f:
        users = json.load(f)
    
    if username in users:
        current = users[username].get("balance", 0)
        if current < amount:
            return False, current
        
        users[username]["balance"] = current - amount
        with open(DB_PATH, "w") as f:
            json.dump(users, f, indent=4)
            # 🛡️ [RESILIENCE] Graceful sync for restricted environments
            try:
                f.flush()
                os.fsync(f.fileno())
            except Exception:
                pass 
        return True, users[username]["balance"]
    return False, 0

def add_credits(username, amount):
    """💳 Reload Production Node"""
    initialize_db()
    username = username.lower().strip()
    with open(DB_PATH, "r") as f:
        users = json.load(f)
    
    if username in users:
        current = users[username].get("balance", 0)
        users[username]["balance"] = current + amount
        
        # 📜 [TRANSACTION LEDGER] Record the injection
        import time
        tx_data = {
            "username": username,
            "amount": amount,
            "timestamp": time.time(),
            "date": os.popen("date").read().strip()
        }
        if not os.path.exists(TRANSACTIONS_PATH):
            with open(TRANSACTIONS_PATH, "w") as f: json.dump([], f)
        with open(TRANSACTIONS_PATH, "r") as f:
            txs = json.load(f)
        txs.append(tx_data)
        with open(TRANSACTIONS_PATH, "w") as f: json.dump(txs, f, indent=4)
        
        with open(DB_PATH, "w") as f:
            json.dump(users, f, indent=4)
            # 🛡️ [RESILIENCE] Graceful sync for restricted environments
            try:
                f.flush()
                os.fsync(f.fileno())
            except Exception:
                pass 
        return True, users[username]["balance"]
    return False, 0

def get_admin_stats():
    """🏛️ [ORACLE] Aggregate ecosystem-wide production metrics"""
    initialize_db()
    with open(DB_PATH, "r") as f: users = json.load(f)
    if not os.path.exists(HISTORY_PATH): history = {}
    else:
        with open(HISTORY_PATH, "r") as f: history = json.load(f)
    
    total_users = len(users)
    total_balance = sum(u.get("balance", 0) for u in users.values())
    
    # Synthesis Breakdown
    job_counts = {"video": 0, "ebook": 0, "course": 0, "thumbnail": 0}
    total_jobs = 0
    for user_jobs in history.values():
        for job in user_jobs.values():
            s_type = job.get("stream", "unknown")
            if s_type in job_counts:
                job_counts[s_type] += 1
                total_jobs += 1
    
    # Revenue (from transactions)
    total_invoiced = 0 # In cents/credits context
    if os.path.exists(TRANSACTIONS_PATH):
        with open(TRANSACTIONS_PATH, "r") as f:
            txs = json.load(f)
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
    with open(DB_PATH, "r") as f: users = json.load(f)
    summary = []
    for username, data in users.items():
        summary.append({
            "username": username,
            "balance": data.get("balance", 0),
            "keys_configured": sum(1 for v in data.get("api_keys", {}).values() if v)
        })
    return sorted(summary, key=lambda x: x["balance"], reverse=True)
