import fitz  # PyMuPDF
from fastapi import UploadFile

async def parse_resume(file: UploadFile) -> str:
    """
    Extracts text from a PDF file.
    """
    try:
        content = await file.read()
        doc = fitz.open(stream=content, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        print(f"Error parsing resume: {e}")
        return ""
