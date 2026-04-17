import threading
import os
import shutil

# 🕹️ [SOVEREIGN SENTINEL] Centralized Cancellation Registry (v125.0)
_CANCELLED_JOBS = set()
_SENTINEL_LOCK = threading.Lock()

class SovereignCancellation(Exception):
    """⚔️ Exception raised to absolute-terminate parallel synthesis nodes."""
    def __init__(self, job_id):
        self.job_id = job_id
        super().__init__(f"Vantix Job {job_id} absolute-terminated by Sentinel.")

def flag_cancellation(job_id: str):
    """🕹️ Inject a termination signal into the global industrial grid."""
    if not job_id: return
    with _SENTINEL_LOCK:
        _CANCELLED_JOBS.add(job_id)
        print(f"🛑 [SENTINEL] Job {job_id} flagged for industrial termination.")

def is_cancelled(job_id: str) -> bool:
    """🕵️ Check if the current worker node should absolute-terminate."""
    if not job_id: return False
    with _SENTINEL_LOCK:
        return job_id in _CANCELLED_JOBS

def check_cancellation(job_id: str):
    """⚔️ Heartbeat check that raises the SovereignCancellation sentinel."""
    if is_cancelled(job_id):
        print(f"⚔️ [SENTINEL] Cancellation detected for {job_id}. Raising Immortal Reaper Exception.")
        raise SovereignCancellation(job_id)

def clear_cancellation(job_id: str):
    """🧹 Purge the signal after successful cleanup."""
    if not job_id: return
    with _SENTINEL_LOCK:
        if job_id in _CANCELLED_JOBS:
            _CANCELLED_JOBS.remove(job_id)

def cleanup_job_assets(job_id: str, project_root: str):
    """🧹 Absolute-purge session data associated with the cancelled job."""
    if not job_id: return
    
    # Session paths follow temp/{job_id} or final_video/{job_id} (if applicable)
    paths_to_purge = [
        os.path.join(project_root, "temp", job_id),
        os.path.join(project_root, "static/videos", f"temp_{job_id}.mp4"), # Specific temp render
    ]
    
    for path in paths_to_purge:
        if os.path.exists(path):
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)
                else:
                    os.remove(path)
                print(f"🧹 [REAPER] Asset purged: {os.path.basename(path)}")
            except Exception as e:
                print(f"⚠️ [REAPER] Asset purge failed for {path}: {e}")
