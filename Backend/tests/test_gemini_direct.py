import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.getcwd())

from app.core.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI

async def test_gemini():
    print("Testing Gemini Direct...")
    print(f"API Key present: {bool(settings.GOOGLE_API_KEY)}")
    
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=0.7
    )
    
    print("Trying gemini-pro...")
    
    try:
        response = await llm.ainvoke("Hello, this is a test.")
        print(f"Response: {response.content}")
    except Exception as e:
        print(f"Gemini Failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_gemini())
