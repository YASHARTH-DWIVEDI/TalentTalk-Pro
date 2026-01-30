import google.generativeai as genai
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())
from app.core.config import settings

def test_raw_genai():
    print("Testing Raw GenAI...")
    if not settings.GOOGLE_API_KEY:
        print("No API Key found!")
        return

    genai.configure(api_key=settings.GOOGLE_API_KEY)
    
    # Try listing models
    print("Listing models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(m.name)
                break
    except Exception as e:
        print(f"List Models Failed: {e}")
        
    print(f"Loaded Key: {settings.GOOGLE_API_KEY[:5]}...{settings.GOOGLE_API_KEY[-5:]}")
    
    # Try generation
    print("Generating content with gemini-pro...")
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content("Hello")
        print(f"Response Success: {response.text[:20]}...")
    except Exception as e:
        print(f"Generation Failed: {e}")
        # Print full type of error
        print(type(e))

if __name__ == "__main__":
    test_raw_genai()
