import json
from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from app.core.config import settings
from app.core.prompts import QUESTION_PROMPT, ANALYSIS_PROMPT, FINAL_REPORT_PROMPT, FOLLOWUP_PROMPT
from app.core.logging_config import logger # Added for video analysis and error logging

class GeminiService:
    def __init__(self):
        # OpenRouter Configuration
        self.llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001",
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.7
        )
        self.json_llm = ChatOpenAI(
            model="google/gemini-2.0-flash-001", 
            openai_api_key=settings.OPENROUTER_API_KEY,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3,
            model_kwargs={"response_format": {"type": "json_object"}}
        )

    async def analyze_video_behavior(self, video_path: str) -> str:
        """Analyzes a video file for behavioral cues and expressions."""
        # Video analysis via OpenRouter (Multimodal) requires sending image frames or video URL.
        # For MVP, we will stub this or use a simple text fallback since we can't upload files to OpenRouter easily via this SDK yet.
        # Alternatively, we could keep the Google SDK *just* for this if a GOOGLE_API_KEY is present.
        
        if settings.GOOGLE_API_KEY:
             try:
                import google.generativeai as genai
                import time
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                model = genai.GenerativeModel('gemini-1.5-flash')
                
                logger.info(f"Uploading video {video_path} to Google for analysis...")
                video_file = genai.upload_file(path=video_path)
                
                while video_file.state.name == "PROCESSING":
                    time.sleep(1)
                    video_file = genai.get_file(video_file.name)
                    
                if video_file.state.name == "FAILED":
                    raise ValueError("Video processing failed by Gemini.")
                    
                prompt = "Analyze this interview video clip. Describe the candidate's facial expressions, body language, and apparent confidence level. Be concise."
                response = model.generate_content([video_file, prompt])
                return response.text
             except Exception as e:
                 logger.error(f"Google Video Analysis failed: {e}")
                 return "Video analysis unavailable (Check Google API Key)."
        
        return "Video analysis requires a valid GOOGLE_API_KEY in addition to OpenRouter."

    async def generate_question(
        self, 
        target_company: str,
        interview_style: str,
        job_role: str,
        difficulty: str,
        topic: str,
        question_num: int,
        total_questions: int,
        history: List[str],
        resume_text: str = None
    ) -> str:
        """Generates the next interview question based on context."""
        
        # Format history string
        history_text = "\n".join(history) if history else "No previous history."
        resume_context = resume_text if resume_text else "No resume provided."
        
        prompt = QUESTION_PROMPT.format(
            target_company=target_company or "Generic Tech Company",
            interview_style=interview_style,
            job_role=job_role,
            difficulty=difficulty,
            topic=topic or "General",
            question_num=question_num,
            total_questions=total_questions,
            history=history_text,
            resume_context=resume_context
        )
        
        response = await self.llm.ainvoke(prompt)
        return response.content


    async def generate_followup_question(
        self,
        target_company: str,
        question: str,
        answer: str
    ) -> str:
        """Generates a follow-up question based on the previous answer."""
        
        prompt = FOLLOWUP_PROMPT.format(
            target_company=target_company or "Generic Tech Company",
            question=question,
            answer=answer
        )
        
        response = await self.llm.ainvoke(prompt)
        return response.content

    async def analyze_response(
        self, 
        question: str, 
        answer: str, 
        job_role: str, 
        difficulty: str
    ) -> Dict[str, Any]:
        """Analyzes the candidate's answer and returns structured data."""
        
        prompt = ANALYSIS_PROMPT.format(
            question=question,
            answer=answer,
            job_role=job_role,
            difficulty=difficulty
        )
        
        try:
            response = await self.json_llm.ainvoke(prompt)
            content = response.content
            # Cleanup json if needed
            if "```json" in content:
                content = content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            return {
                "feedback": "Could not analyze response.",
                "sentiment_score": 0.0,
                "technical_accuracy": 0.0,
                "suggested_improvement": "",
                "is_correct": False,
                "error": str(e)
            }

    async def generate_final_report(
        self,
        target_company: str,
        job_role: str,
        interview_data: str
    ) -> str:
        """Generates the comprehensive final markdown report."""
        
        prompt = FINAL_REPORT_PROMPT.format(
            target_company=target_company or "Generic Tech Company",
            job_role=job_role,
            interview_data=interview_data
        )
        
        response = await self.llm.ainvoke(prompt)
        return response.content

gemini_service = GeminiService()
