import google.generativeai as genai
from ..core.config import get_settings

settings = get_settings()

def configure_genai():
    genai.configure(api_key=settings.GOOGLE_API_KEY)

def get_gemini_model(model_name: str = "gemini-1.5-flash", system_instruction: str = None):
    configure_genai()
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=system_instruction
    )

async def generate_response(prompt: str, system_instruction: str = None):
    model = get_gemini_model(system_instruction=system_instruction)
    response = await model.generate_content_async(prompt)
    return response.text
