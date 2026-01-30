import asyncio
import os
import sys

# Add backend to path (Correctly)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.gemini_service import gemini_service

async def test_report():
    print("Testing Final Report Generation...")
    
    # Dummy Interview Data
    interview_data = [
        {
            "question": "Explain the difference between a List and a Tuple in Python.",
            "answer": "A list is mutable, meaning you can change it. A tuple is immutable. Lists use square brackets, tuples use parentheses.",
            "analysis": {"feedback": "Good basic definition.", "sentiment_score": 0.8}
        },
        {
            "question": "What is a decorator?",
            "answer": "I am not sure, I think it decorates a function?",
            "analysis": {"feedback": "Vague answer.", "sentiment_score": 0.3}
        }
    ]
    
    import json
    data_str = json.dumps(interview_data, indent=2)
    
    try:
        report = await gemini_service.generate_final_report(
            target_company="Google",
            job_role="Senior Python Developer",
            interview_data=data_str
        )
        
        print("\n--- GENERATED REPORT ---\n")
        print(report)
        print("\n------------------------\n")
        
        # Validation
        if "Full Interview Transcript" in report:
            print("✅ Section Found: Full Interview Transcript")
        else:
            print("❌ MISSING: Full Interview Transcript")
            
        if "Actionable Suggestions" in report:
            print("✅ Section Found: Actionable Suggestions")
        else:
             print("❌ MISSING: Actionable Suggestions")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_report())
