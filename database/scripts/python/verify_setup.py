#!/usr/bin/env python3
"""Quick verification script to check if setup is correct."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Try loading .env from parent directory
script_dir = Path(__file__).parent
env_paths = [
    script_dir / '.env',
    script_dir.parent / '.env',
    Path.cwd() / '.env'
]

print("🔍 Checking for .env file...")
for env_path in env_paths:
    if env_path.exists():
        print(f"✅ Found .env at: {env_path}")
        load_dotenv(env_path)
        break
    else:
        print(f"❌ Not found: {env_path}")

# Check for API key
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    print(f"\n✅ GROQ_API_KEY is set (length: {len(api_key)} chars)")
    print(f"   Preview: {api_key[:10]}...{api_key[-5:]}")
else:
    print("\n❌ GROQ_API_KEY not found in environment")

print("\n📦 Checking dependencies...")
try:
    import groq
    print("✅ groq package installed")
except ImportError:
    print("❌ groq package NOT installed (run: uv pip install -r requirements.txt)")

try:
    import pandas
    print("✅ pandas package installed")
except ImportError:
    print("❌ pandas package NOT installed")

try:
    import geopy
    print("✅ geopy package installed")
except ImportError:
    print("❌ geopy package NOT installed")

print("\n🎉 Setup verification complete!")
