import groq
import os

print("--- Groq SDK Audit ---")
try:
    client = groq.Groq(api_key="test")
    print("✅ Groq initialized successfully in vacuum.")
except Exception as e:
    print(f"❌ Groq failed: {e}")

try:
    print("Testing with injected proxy...")
    client = groq.Groq(api_key="test", proxies={"http": "test"})
    print("✅ Groq accepted proxy (Old Version detected)")
except TypeError as e:
    print(f"❌ Groq rejected proxy: {e}")
