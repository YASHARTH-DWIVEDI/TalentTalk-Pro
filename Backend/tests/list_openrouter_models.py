import requests
import os
import sys

sys.path.append(os.getcwd())
from app.core.config import settings

def list_models():
    print("Fetching OpenRouter models...")
    key = settings.OPENROUTER_API_KEY
    if not key:
        print("No OPENROUTER_API_KEY found.")
        return

    headers = {
        "Authorization": f"Bearer {key}",
    }
    
    try:
        response = requests.get("https://openrouter.ai/api/v1/models", headers=headers)
        if response.status_code == 200:
            data = response.json()
            # Filter for google models
            google_models = [m['id'] for m in data['data'] if 'google' in m['id']]
            print("Available Google Models:")
            for m in google_models:
                print(m)
        else:
            print(f"Failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
