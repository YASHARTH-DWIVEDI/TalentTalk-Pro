from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import operator
from .gemini_client import generate_response

class InterviewState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]
    candidate_id: int
    current_stage: str # "introduction", "technical", "behavioral", "conclusion"
    question_count: int

async def interviewer_node(state: InterviewState):
    messages = state["messages"]
    stage = state.get("current_stage", "introduction")
    
    # Simple prompt logic for MVP - can be enhanced with complex prompt templates
    system_prompt = f"""You are an expert technical interviewer conducting an interview.
    Current Stage: {stage}
    
    Goal: Ask relevant questions based on the resume and previous answers. 
    Be professional but encouraging. 
    If the stage is 'introduction', ask about their background.
    If 'technical', ask coding or system design questions.
    If 'conclusion', thank them and wrap up.
    """
    
    # Construct prompt from history
    # For Gemini, we might need to format history carefully, but simple concatenation works for now
    conversation = "\n".join([f"{m.type}: {m.content}" for m in messages])
    prompt = f"{conversation}\nInterviewer:"
    
    response_text = await generate_response(prompt, system_instruction=system_prompt)
    
    return {"messages": [AIMessage(content=response_text)], "question_count": state.get("question_count", 0) + 1}

def router_node(state: InterviewState):
    # Logic to switch stages or end interview
    count = state.get("question_count", 0)
    stage = state.get("current_stage", "introduction")
    
    if stage == "introduction" and count >= 2:
        return "technical"
    elif stage == "technical" and count >= 5:
        return "conclusion"
    elif stage == "conclusion" and count >= 7:
        return "end"
    return "continue"

# Define Graph
workflow = StateGraph(InterviewState)
workflow.add_node("interviewer", interviewer_node)
workflow.set_entry_point("interviewer")

def route_step(state: InterviewState):
    decision = router_node(state)
    if decision == "end":
        return END
    elif decision == "continue":
        return END # For client-server model, we stop after generation and wait for user input
    else:
        # Update stage logic would go here, for now simple loop
        # In a real app, we'd have a node to update state parameters
        return END 

workflow.add_edge("interviewer", END) # Simplified for Request/Response API pattern

app_graph = workflow.compile()
