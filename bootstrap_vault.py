import sys
import os
# Add current directory to path so we can import api modules
sys.path.append(os.path.abspath("api"))

import db_helper

def bootstrap():
    username = "uday"
    initial_vault = {
        "groq": os.environ.get("GROQ_API_KEY", ""),
        "openrouter": os.environ.get("OPENROUTER_API_KEY", ""),
        "pexels": os.environ.get("PEXELS_API_KEY", ""),
        "pixabay": os.environ.get("PIXABAY_API_KEY", "")
    }
    
    print(f"🔐 [BOOTSTRAP] Injecting production keys for user '{username}'...")
    success = db_helper.update_user_keys(username, initial_vault)
    
    if success:
        print("✅ [SUCCESS] Vantix Vault synchronized with encrypted credentials.")
    else:
        print("❌ [FAILED] Vault rejection: User not found.")

if __name__ == "__main__":
    bootstrap()
