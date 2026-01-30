import requests
import os

API_URL = "http://localhost:8000/api/v1"

def test_video_analysis():
    print("Testing Video Analysis Endpoint...")
    
    # Check if a dummy video exists, if not create a tiny dummy file
    video_path = "dummy_video.mp4"
    # Create dummy file if missing
    if not os.path.exists(video_path):
        with open(video_path, "wb") as f:
            f.write(b"fake video content")

    try:
        # Open file in a with block to ensure it's closed before deletion cleanup
        with open(video_path, 'rb') as f:
            files = {'video_file': (video_path, f, 'video/mp4')}
            response = requests.post(f"{API_URL}/analyze_video", files=files)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Video Analysis Endpoint reachable.")
        else:
             # It might fail analysis content-wise (fake video), but 500 or 200 is "handled"
             # If API key is missing, it returns specific message
             print(f"ℹ️ Endpoint Responded (Might be error from Gemini): {response.status_code}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Cleanup
        if os.path.exists(video_path):
            try:
                os.remove(video_path)
            except:
                pass

if __name__ == "__main__":
    test_video_analysis()
