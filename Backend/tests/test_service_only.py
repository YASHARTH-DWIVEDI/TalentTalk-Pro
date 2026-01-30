import asyncio
from fastapi import UploadFile
import io
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

from app.services.resume_service import resume_service

async def test_service():
    print("Testing Resume Service Isolation...")
    dummy_content = b"Draft Resume.\nName: John Doe.\nSkills: Python."
    file_obj = io.BytesIO(dummy_content)
    # UploadFile expects a 'file' attribute or we can mock it
    # But wait, UploadFile has .read(). 
    # Let's mock a class that behaves like UploadFile
    class MockUploadFile:
        filename = "test.pdf"
        async def read(self):
            return dummy_content
            
    try:
        text = await resume_service.extract_text(MockUploadFile())
        print(f"Extraction Result: {text}")
    except Exception as e:
        print(f"Service Execution Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_service())
