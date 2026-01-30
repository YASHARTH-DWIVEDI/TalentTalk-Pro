from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from app.services.gemini_service import gemini_service
from app.core.logging_config import logger

class InterviewState(TypedDict):
    # Chat history
    messages: List[BaseMessage]
    history: List[str]
    
    # State tracking
    current_question: Optional[str]
    current_question_num: int
    total_questions: int
    follow_up_count: int # Current follow-ups for this question
    max_follow_ups: int # Max allowed
    
    # Context
    target_company: str
    interview_style: str
    job_role: str
    difficulty: str
    topic: str
    resume_text: Optional[str] # New field
    
    # Results
    analysis_data: List[Dict[str, Any]]
    final_report: Optional[str]

# --- Nodes ---

async def generate_question_node(state: InterviewState):
    """Node: Generates the next question or ends interview."""
    logger.info(f"Generating question {state['current_question_num'] + 1}/{state['total_questions']}")
    
    question = await gemini_service.generate_question(
        target_company=state["target_company"],
        interview_style=state["interview_style"],
        job_role=state["job_role"],
        difficulty=state["difficulty"],
        topic=state["topic"],
        question_num=state["current_question_num"] + 1,
        total_questions=state["total_questions"],
        history=state["history"],
        resume_text=state.get("resume_text")
    )
    
    # Update state
    state["current_question"] = question
    state["current_question_num"] += 1
    
    # Add to message history (as AI)
    state["messages"].append(AIMessage(content=question))
    
    # Reset follow-up count for new question
    state["follow_up_count"] = 0
    
    return state

async def generate_follow_up_node(state: InterviewState):
    """Node: Generates a follow-up question."""
    logger.info("Generating Follow-up Question...")
    
    last_user_msg = state["messages"][-1]
    last_answer = last_user_msg.content if isinstance(last_user_msg, HumanMessage) else ""
    
    question = await gemini_service.generate_followup_question(
        target_company=state["target_company"],
        question=state["current_question"],
        answer=last_answer
    )
    
    # Update state
    state["current_question"] = question
    # Do NOT increment current_question_num, as it's the same topic
    state["follow_up_count"] += 1
    
    # Add to message history
    state["messages"].append(AIMessage(content=question))
    
    return state

async def analyze_answer_node(state: InterviewState):
    """Node: Analyzes the user's latest response."""
    last_message = state["messages"][-1]
    
    if not isinstance(last_message, HumanMessage):
        # Should not happen in normal flow
        return state
        
    user_answer = last_message.content
    
    logger.info("Analyzing user answer...")
    analysis = await gemini_service.analyze_response(
        question=state["current_question"],
        answer=user_answer,
        job_role=state["job_role"],
        difficulty=state["difficulty"]
    )
    
    # Append analysis to list
    if "analysis_data" not in state:
        state["analysis_data"] = []
    
    # Store complete analysis object
    analysis_record = {
        "question": state["current_question"],
        "answer": user_answer,
        "analysis": analysis,
        "question_num": state["current_question_num"]
    }
    state["analysis_data"].append(analysis_record)
    
    # Add context to history for the next question generator
    # We include a brief summary so the AI knows how the user did, but not the full JSON
    feedback_short = f"Question: {state['current_question']}\nAnswer: {user_answer}\nFeedback: {analysis.get('feedback', '')}"
    state["history"].append(feedback_short)
    
    # Adaptive Difficulty Logic
    # If strongly positive, increase difficulty. If negative, decrease.
    # Simple implementation for now.
    score = analysis.get("sentiment_score", 0)
    current_diff = state["difficulty"]
    
    if score > 0.7 and current_diff == "Easy":
        state["difficulty"] = "Medium"
    elif score > 0.8 and current_diff == "Medium":
        state["difficulty"] = "Hard"
    elif score < 0.3 and current_diff == "Hard":
        state["difficulty"] = "Medium"
    elif score < 0.2 and current_diff == "Medium":
        state["difficulty"] = "Easy"
        
    return state

async def generate_report_node(state: InterviewState):
    """Node: Generates the final report after all questions."""
    logger.info("Generating Final Report...")
    
    # Prepare data for the prompt
    interview_data_str = json.dumps(state["analysis_data"], indent=2)
    
    report = await gemini_service.generate_final_report(
        target_company=state["target_company"],
        job_role=state["job_role"],
        interview_data=interview_data_str
    )
    
    state["final_report"] = report
    return state

import json

# --- Routing ---

def route_interview(state: InterviewState):
    """Decides whether to continue questioning, follow-up, or end."""
    
    # 1. Check if we should ask a follow-up
    if state.get("follow_up_count", 0) < state.get("max_follow_ups", 0):
        return "generate_follow_up"

    if state["current_question_num"] >= state["total_questions"]:
        return "generate_report"
    return "generate_question"

# --- Graph Definition ---

workflow = StateGraph(InterviewState)

workflow.add_node("generate_question", generate_question_node)
workflow.add_node("generate_follow_up", generate_follow_up_node)
workflow.add_node("analyze_answer", analyze_answer_node)
workflow.add_node("generate_report", generate_report_node)

# Entry point
workflow.set_entry_point("generate_question")

# Transition from Question extraction -> Wait for user input
# NOTE: In a real API, we would pause here. 
# For this graph, we assume the HumanMessage is injected into state 
# externally before resuming. 
# BUT `StateGraph` in basic form runs until END or interrupt.
# Since we are building an API, we will likely run one step at a time or use `interrupt`.
# For MVP simplicity: 
# The "cycle" is: Generate Question -> END (Return to user) -> (User calls API) -> Analyze Answer -> Route

# However, to visualize the logic:
# generate_question -> END (user sees question)
# ... User inputs answer ...
# (Resume with answer) -> analyze_answer -> route -> generate_question/report

# We will define the edge from analyze to route
workflow.add_conditional_edges(
    "analyze_answer",
    route_interview,
    {
        "generate_question": "generate_question",
        "generate_follow_up": "generate_follow_up",
        "generate_report": "generate_report"
    }
)

workflow.add_edge("generate_report", END)

# We define the edge that "ends" a turn to wait for user input.
# In LangGraph terms, `generate_question` finishes, and we return state to the caller.
# The caller (FastAPI) will persist state.
# When user replies, we invoke `analyze_answer` directly?
# OR we define the full loop and use `interrupt_before`.

# Let's use the explicit loop for clarity and compilation,
# but at runtime we might use it differently.
# Ideally: generate_question -> END.
# Then user submits answer -> analyze_answer -> check condition.
