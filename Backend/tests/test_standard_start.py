import requests

API_URL = "http://localhost:8000/api/v1"

def test_start():
    print("Testing Standard Start...")
    payload = {
        "target_company": "Google",
        "job_role": "Engineer",
        "interview_style": "Professional",
        "difficulty": "Medium"
    }
    
    try:
        response = requests.post(f"{API_URL}/start", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_start()
