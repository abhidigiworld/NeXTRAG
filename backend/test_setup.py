"""
Quick test script to verify backend setup
"""
import sys
print(f"Python version: {sys.version}")

# Test imports
try:
    import fastapi
    print("✅ FastAPI imported successfully")
except ImportError as e:
    print(f"❌ FastAPI import failed: {e}")

try:
    import uvicorn
    print("✅ Uvicorn imported successfully")
except ImportError as e:
    print(f"❌ Uvicorn import failed: {e}")

try:
    import pydantic
    print("✅ Pydantic imported successfully")
except ImportError as e:
    print(f"❌ Pydantic import failed: {e}")

try:
    from dotenv import load_dotenv
    print("✅ python-dotenv imported successfully")
except ImportError as e:
    print(f"❌ python-dotenv import failed: {e}")

# Test loading .env
try:
    load_dotenv()
    import os
    api_key = os.getenv("OPENAI_API_KEY", "")
    if api_key:
        print(f"✅ OpenAI API key found: {api_key[:10]}...")
    else:
        print("⚠️  OpenAI API key not set in .env file")
except Exception as e:
    print(f"❌ Error loading .env: {e}")

print("\n" + "="*50)
print("Basic imports test complete!")
print("="*50)
