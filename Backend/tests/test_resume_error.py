import requests
import io

API_URL = "http://localhost:8000/api/v1"

def test_resume_upload():
    print("Testing Resume Upload...")
    
    # Create a dummy PDF file in memory
    pdf_content = b"%PDF-1.5\n%..."
    # Real minimal PDF header/trailer is better to avoid pypdf error if it validates
    # But for a 500 server error, it might be even earlier.
    # Let's try to use a real small valid pdf structure or just text if pypdf is lenient.
    # Actually, let's create a minimal valid PDF using reportlab or fpdf if installed?
    # No, let's just use a dummy text file renamed as .pdf and see if pypdf handles exception gracefully
    # If pypdf crashes on invalid pdf, that might be the 500.
    
    dummy_pdf = io.BytesIO(b"This is a dummy pdf content")
    
    files = {'resume_file': ('test_resume.pdf', dummy_pdf, 'application/pdf')}
    data = {
        "target_company": "Test Corp",
        "job_role": "Tester",
        "interview_style": "Professional",
        "difficulty": "Easy"
    }
    
    try:
        response = requests.post(f"{API_URL}/start_with_resume", files=files, data=data)
        print(f"Status Code: {response.status_code}")
        print("Response Body:")
        print(response.text) # Print full text
        with open("error_log.txt", "w", encoding="utf-8") as f:
            f.write(response.text)
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    test_resume_upload()
