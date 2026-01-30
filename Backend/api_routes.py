from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .agents.workflow import app_graph, InterviewState
from langchain_core.messages import HumanMessage, AIMessage

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str # Ideally used to load state from DB

# In-memory store for MVP state (replace with Redis/DB in production)
session_store = {}

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    session_id = request.session_id
    user_input = request.message
    
    # Initialize state if new
    if session_id not in session_store:
        session_store[session_id] = {
            "messages": [],
            "candidate_id": 1, # Mock
            "current_stage": "introduction",
            "question_count": 0
        }
    
    current_state = session_store[session_id]
    
    # Add user message
    current_state["messages"].append(HumanMessage(content=user_input))
    
    # Run graph
    # LangGraph invoke returns the final state
    result = await app_graph.ainvoke(current_state)
    
    # Update store
    session_store[session_id] = result
    
    # Get last message
    last_message = result["messages"][-1]
    
    return {
        "response": last_message.content,
        "stage": result.get("current_stage")
    }
