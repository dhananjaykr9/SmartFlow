import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in .env")
else:
    print(f"API Key loaded (starts with): {api_key[:5]}...")
    genai.configure(api_key=api_key)

    print("\n--- Querying Google API for Available Models ---")
    try:
        # List all models that support content generation
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Found: {m.name}")
    except Exception as e:
        print(f"Connection Error: {e}")