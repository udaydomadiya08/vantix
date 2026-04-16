# Vantix Sovereign Telemetry (v120.2)

# Global status repository shared across all factory nodes
# {job_id: { "pass": "...", "heartbeat": timestamp }}
LIVE_TELEMETRY = {}

def update_progress(job_id: str, pass_name: str):
    """Update the live heartbeat for a specific production job."""
    import time
    LIVE_TELEMETRY[job_id] = {
        "pass": pass_name,
        "heartbeat": time.time()
    }
    print(f"💓 [HEARTBEAT] Job {job_id}: {pass_name}")

def get_progress(job_id: str):
    """Retrieve the latest heartbeat for a production job."""
    return LIVE_TELEMETRY.get(job_id, {"pass": "Initializing...", "heartbeat": 0})
