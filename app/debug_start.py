import os
import sys
import traceback

print("=== DEBUG START ===")
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"PORT environment variable: {os.environ.get('PORT', 'NOT SET')}")
print(f"Python path: {sys.path}")

# List files in current directory
print("Files in current directory:")
for item in os.listdir('.'):
    print(f"  {item}")

# Check if app directory exists
if os.path.exists('app'):
    print("Contents of app directory:")
    for item in os.listdir('app'):
        print(f"  app/{item}")

print("\n=== TESTING IMPORTS ===")

try:
    print("Importing FastAPI...")
    from fastapi import FastAPI
    print("✓ FastAPI imported successfully")
except Exception as e:
    print(f"✗ FastAPI import failed: {e}")
    traceback.print_exc()

try:
    print("Importing uvicorn...")
    import uvicorn
    print("✓ uvicorn imported successfully")
except Exception as e:
    print(f"✗ uvicorn import failed: {e}")
    traceback.print_exc()

try:
    print("Importing your app...")
    from app.main import app
    print("✓ Your app imported successfully")
except Exception as e:
    print(f"✗ Your app import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n=== STARTING SERVER ===")
try:
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting uvicorn on port {port}")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, log_level="debug")
except Exception as e:
    print(f"✗ Server start failed: {e}")
    traceback.print_exc()
    sys.exit(1)
