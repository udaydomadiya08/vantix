import sys
import os
import uuid
import time

# Ensure api/ is in path for db_helper
sys.path.append(os.path.abspath('api'))
import db_helper

def register_ghost_asset(username, filename):
    job_id = str(uuid.uuid4())
    # Construction of result_url matching the corrected logic in api/main.py
    rel_path = f"static/videos/{filename}"
    
    job_data = {
        "id": job_id,
        "username": username,
        "stream": "video",
        "topic": "Life on Mars (Restored)",
        "status": "completed",
        "result_url": f"/download?path={rel_path}",
        "submitted": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    
    success = db_helper.save_to_history(username, job_id, job_data)
    if success:
        print(f"✅ [RESTORATION SUCCESS] Asset '{filename}' registered for user '{username}'.")
        print(f"🔗 Job ID: {job_id}")
    else:
        print(f"❌ [RESTORATION FAILED] Could not commit to database.")

if __name__ == "__main__":
    # Targeting the MASTERED high-fidelity asset identified in the logs
    register_ghost_asset("uday", "vantix_20260416_185713_mastered.mp4")

