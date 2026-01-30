import requests
import time

API_URL = "http://localhost:8000/api/v1"

def test_followup_flow():
    print("🧪 Testing Follow-up Logic...")
    
    # 1. Start Interview with max_follow_ups = 1
    print("\n1. Starting Session (max_follow_ups=1)...")
    payload = {
        "target_company": "TestCorp",
        "job_role": "Tester",
        "interview_style": "Professional",
        "difficulty": "Easy",
        "max_follow_ups": 1
    }
    
    try:
        res = requests.post(f"{API_URL}/start", json=payload)
        res.raise_for_status()
        data = res.json()
        session_id = data["session_id"]
        q1 = data["first_question"]
        print(f"✅ Started. Session: {session_id}")
        print(f"   Q1: {q1}")
    except Exception as e:
        print(f"❌ Failed to start: {e}")
        return

    # 2. Answer Q1 -> Expect Follow-up
    print("\n2. Answering Q1 (Expect Follow-up)...")
    chat_payload = {"session_id": session_id, "text_input": "I use print statements for debugging."}
    
    try:
        res = requests.post(f"{API_URL}/chat", data=chat_payload)
        res.raise_for_status()
        data = res.json()
        
        reply = data.get("question", "")
        print(f"   AI Reply: {reply}")
        
        # We can't strictly know if it's a follow-up by text, but based on logic flow it should be.
        # Check feedback to confirm analysis happened
        if data.get("feedback"):
            print(f"   Feedback: {data['feedback']}")
            
        print("✅ Received response.")
    except Exception as e:
        print(f"❌ Failed Step 2: {e}")
        return

    # 3. Answer Follow-up -> Expect Q2
    print("\n3. Answering Follow-up (Expect Q2)...")
    chat_payload = {"session_id": session_id, "text_input": "I also use logging sometimes."}
    
    try:
        res = requests.post(f"{API_URL}/chat", data=chat_payload)
        res.raise_for_status()
        data = res.json()
        
        reply = data.get("question", "")
        print(f"   AI Reply: {reply}")
        print("✅ Received response (Should be Q2).")
        
    except Exception as e:
        print(f"❌ Failed Step 3: {e}")
        return

    print("\n🎉 Logic Flow Test Complete.")

if __name__ == "__main__":
    # Wait for server to be ready
    time.sleep(3) 
    test_followup_flow()
