import shutil
import os
from uuid import uuid4
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.schemas import InterviewStartRequest, InterviewStartResponse, ChatResponse
from app.agents.interview_graph import workflow
from app.services.voice_service import voice_service
from app.core.logging_config import logger

router = APIRouter()

# In-memory session store for MVP
# In production, use Redis or the SQL database to persist LangGraph state
SESSION_STORE = {}

@router.post("/start", response_model=InterviewStartResponse)
async def start_interview(request: InterviewStartRequest):
    session_id = str(uuid4())
    logger.info(f"Starting session {session_id} for {request.target_company}")
    
    # Initialize State
    initial_state = {
        "messages": [],
        "history": [],
        "current_question": None,
        "current_question_num": 0,
        "total_questions": 5, # Default to 5 questions
        "target_company": request.target_company,
        "interview_style": request.interview_style,
        "job_role": request.job_role,
        "difficulty": request.difficulty,
        "topic": request.topic or "General",
        "analysis_data": []
    }
    
    # Compile graph
    app = workflow.compile()
    
    # Run first step to get Q1
    result = await app.ainvoke(initial_state)
    
    # Store state
    SESSION_STORE[session_id] = result
    
    return InterviewStartResponse(
        session_id=session_id,
        message="Interview initialized.",
        first_question=result["current_question"]
    )

@router.post("/start_with_resume", response_model=InterviewStartResponse)
async def start_interview_with_resume(
    target_company: str = Form("Google"),
    job_role: str = Form("Senior Engineer"),
    interview_style: str = Form("Professional"),
    difficulty: str = Form("Medium"),
    resume_file: UploadFile = File(...)
):
    session_id = str(uuid4())
    logger.info(f"Starting Resume Session {session_id} for {target_company}")
    logger.info(f"Received file: {resume_file.filename}, Size: unknown bytes")
    
    try:
        # 1. Parsing Resume
        from app.services.resume_service import resume_service
        resume_text = await resume_service.extract_text(resume_file)
        logger.info(f"Resume text extracted (First 50 chars): {resume_text[:50]}...")
        
        # 2. Init State
        initial_state = {
            "messages": [],
            "history": [],
            "current_question": None,
            "current_question_num": 0,
            "total_questions": 5, 
            "target_company": target_company,
            "interview_style": interview_style,
            "job_role": job_role,
            "difficulty": difficulty,
            "topic": "Resume Review", # Override topic
            "resume_text": resume_text,
            "analysis_data": []
        }
        
        # 3. Compile & Run
        app = workflow.compile()
        result = await app.ainvoke(initial_state)
        
        SESSION_STORE[session_id] = result
        
        return InterviewStartResponse(
            session_id=session_id,
            message="Interview initialized with Resume.",
            first_question=result["current_question"]
        )
    except Exception as e:
        logger.error(f"Error in start_with_resume: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("/chat", response_model=ChatResponse)
async def chat_interview(
    session_id: str = Form(...),
    text_input: str = Form(None),
    audio_file: UploadFile = File(None)
):
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail="Session not found")
    
    current_state = SESSION_STORE[session_id]
    
    # 1. Handle Input (Text or Audio)
    user_response_text = ""
    
    if audio_file:
        # Save temp file
        temp_filename = f"temp_{session_id}_{uuid4()}.wav"
        with open(temp_filename, "wb") as buffer:
            shutil.copyfileobj(audio_file.file, buffer)
            
        try:
            # Transcribe
            user_response_text = await voice_service.transcribe_audio(temp_filename)
        finally:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
    elif text_input:
        user_response_text = text_input
    else:
        raise HTTPException(status_code=400, detail="No input provided")

    logger.info(f"User Response: {user_response_text}")

    # 2. Update Context with User Answer
    from langchain_core.messages import HumanMessage
    current_state["messages"].append(HumanMessage(content=user_response_text))
    
    try:
        # 3. Run Graph (Analyze -> Route -> Generate/Report)
        from app.agents.interview_graph import analyze_answer_node, route_interview, generate_question_node, generate_report_node
        
        # A. Analyze
        logger.info("Running analyze_answer_node...")
        state = await analyze_answer_node(current_state)
        feedback_item = state["analysis_data"][-1]
        
        # B. Route
        next_step = route_interview(state)
        logger.info(f"Next step routed: {next_step}")
        
        response_data = ChatResponse(
            feedback=feedback_item["analysis"],
            user_transcript=user_response_text
        )
        
        if next_step == "generate_question":
            # C. Generate Next Question
            logger.info("Running generate_question_node...")
            state = await generate_question_node(state)
            response_data.question = state["current_question"]
            
            # D. Audio for Question (TTS)
            os.makedirs("static/audio", exist_ok=True)
            filename = f"q_{session_id}_{state['current_question_num']}.mp3"
            filepath = os.path.join("static/audio", filename)
            
            try:
                await voice_service.generate_audio(state["current_question"], filepath)
                response_data.audio_url = f"/static/audio/{filename}"
            except Exception as e:
                logger.error(f"TTS failed: {e}")
        
        elif next_step == "generate_report":
            # C. Generate Report
            logger.info("Running generate_report_node...")
            response_data.is_finished = True
            state = await generate_report_node(state)
            
        # Update Store
        SESSION_STORE[session_id] = state
        
        return response_data

    except Exception as e:
        logger.error(f"Error in chat_interview logic: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat Error: {str(e)}")

@router.get("/report/{session_id}")
async def get_report(session_id: str):
    if session_id not in SESSION_STORE:
        raise HTTPException(status_code=404, detail="Session not found")
        
    state = SESSION_STORE[session_id]
    if not state.get("final_report"):
        return {"status": "in_progress"}
        
    return {"report": state["final_report"]}

@router.post("/analyze_video")
async def analyze_video(video_file: UploadFile = File(...)):
    temp_filename = f"temp_video_{uuid4()}.mp4"
    with open(temp_filename, "wb") as buffer:
        shutil.copyfileobj(video_file.file, buffer)
        
    try:
        from app.services.gemini_service import gemini_service
        analysis = await gemini_service.analyze_video_behavior(temp_filename)
        return {"analysis": analysis}
    except Exception as e:
        logger.error(f"Video analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
