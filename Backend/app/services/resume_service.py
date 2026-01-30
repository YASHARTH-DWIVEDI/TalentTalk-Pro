import io
from pypdf import PdfReader
from fastapi import UploadFile

class ResumeService:
    async def extract_text(self, file: UploadFile) -> str:
        """Extracts text from a PDF file."""
        content = await file.read()
        file_obj = io.BytesIO(content)
        
        try:
            reader = PdfReader(file_obj)
            text = ""
            if not reader.pages:
                return "Error: Empty PDF or parsing failed."
                
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            
            if not text.strip():
                return "Warning: No text could be extracted from this PDF. It might be an image scan."
                
            return text
        except Exception as e:
            # Fallback for non-pdf or error
            print(f"Error in extract_text: {e}") # Print to stdout to capture in logs
            return f"Error extracting resume: {str(e)}"

resume_service = ResumeService()
