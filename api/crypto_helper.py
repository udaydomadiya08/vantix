from cryptography.fernet import Fernet
import os

# === Vantix Cryptographic Engine (v1.0) === #
KEY_FILE = os.path.join(os.path.dirname(__file__), ".identity_vault.key")

def _initialize_vault_key():
    """Ensures a persistent master key exists for the platform's identity vault."""
    # 🏛️ [SaaS Hardening] Prioritize static environment secret for persistence
    env_key = os.getenv("VANTIX_MASTER_KEY")
    if env_key:
        try:
            # Ensure it's valid base64 for Fernet
            return env_key.encode()
        except Exception:
            print("⚠️ [CRYPTO] Provided VANTIX_MASTER_KEY is invalid. Falling back to local file.")

    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        print("🔐 [CRYPTO] New Vantix Master Key generated.")
    
    with open(KEY_FILE, "rb") as f:
        return f.read()

# Singleton Fernet Instance
try:
    _MASTER_KEY = _initialize_vault_key()
    _cipher = Fernet(_MASTER_KEY)
except Exception as e:
    print(f"❌ [CRYPTO] Initialization Failure: {e}")
    _cipher = None

def encrypt_key(plain_text: str) -> str:
    """Encrypts an API key for secure storage."""
    if not plain_text or not _cipher:
        return plain_text
    try:
        if isinstance(plain_text, str):
            plain_text = plain_text.encode()
        return _cipher.encrypt(plain_text).decode()
    except Exception as e:
        print(f"⚠️ [CRYPTO] Encryption Error: {e}")
        return plain_text

def decrypt_key(encrypted_text: str) -> str:
    """Decrypts an API key for industrial synthesis."""
    if not encrypted_text or not _cipher:
        return encrypted_text
    try:
        # Check if it's already a Fernet token (usually starts with gAAAA)
        if not encrypted_text.startswith("gAAAA"):
            return encrypted_text
            
        return _cipher.decrypt(encrypted_text.encode()).decode()
    except Exception as e:
        # If decryption fails, it might be unencrypted legacy data
        print(f"⚠️ [CRYPTO] Decryption Fallback: {e}")
        return encrypted_text
