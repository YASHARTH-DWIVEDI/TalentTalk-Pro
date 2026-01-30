import requests
import json
import os

API_URL = "http://localhost:8000/api/v1"

def create_dummy_wav(filename="test_audio.wav"):
    # Create a minimal valid WAV file header
    import wave
    import struct
    with wave.open(filename, 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(44100)
        # Write 1 second of silence
        data = struct.pack('<h', 0) * 44100
        wav_file.writeframes(data)

def test_chat_audio():
    create_dummy_wav()
    
    # 1. Start Interview
    print("Starting Interview...")
    start_res = requests.post(f"{API_URL}/start", json={
        "target_company": "Google",
        "job_role": "Python Dev",
        "interview_style": "Professional",
        "difficulty": "Medium"
    })
    
    session_id = start_res.json()["session_id"]
    print(f"Session ID: {session_id}")

    # 2. Send Audio Message
    print("Sending Audio Message...")
    
    # We must send session_id as data, and file in files
    data = {"session_id": session_id}
    files = {"audio_file": ("test_audio.wav", open("test_audio.wav", "rb"), "audio/wav")}
    
    try:
        chat_res = requests.post(f"{API_URL}/chat", data=data, files=files)
        print(f"Status: {chat_res.status_code}")
        print(f"Response: {chat_res.text}")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_chat_audio()
