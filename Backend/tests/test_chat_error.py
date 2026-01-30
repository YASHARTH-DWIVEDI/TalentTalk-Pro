import requests
import json

API_URL = "http://localhost:8000/api/v1"

def test_chat():
    # 1. Start Interview
    print("Starting Interview...")
    start_res = requests.post(f"{API_URL}/start", json={
        "target_company": "Google",
        "job_role": "Python Dev",
        "interview_style": "Professional",
        "difficulty": "Medium"
    })
    
    if start_res.status_code != 200:
        print(f"Start failed: {start_res.text}")
        return

    session_id = start_res.json()["session_id"]
    print(f"Session ID: {session_id}")

    # 2. Send Chat Message
    print("Sending Chat Message...")
    chat_payload = {
        "session_id": session_id,
        "text_input": "I have 5 years of experience with Python."
    }
    
    try:
        chat_res = requests.post(f"{API_URL}/chat", data=chat_payload)
        print(f"Status: {chat_res.status_code}")
        print(f"Response: {chat_res.text}")
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    test_chat()
