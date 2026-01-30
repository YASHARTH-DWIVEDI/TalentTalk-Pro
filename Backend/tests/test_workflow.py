import asyncio
import os
from dotenv import load_dotenv

# Ensure we can find the app module
import sys
sys.path.append(os.path.join(os.getcwd(), '..'))

load_dotenv()

from app.agents.interview_graph import workflow, InterviewState
from langchain_core.messages import HumanMessage

async def simulate_interview():
    print("--- Starting Simulation ---")
    
    # Initialize State
    initial_state = {
        "messages": [],
        "history": [],
        "current_question": None,
        "current_question_num": 0,
        "total_questions": 2, # Short for testing
        "target_company": "Google",
        "interview_style": "Visual, Friendly", # Test new style
        "job_role": "Senior Python Engineer",
        "difficulty": "Medium",
        "topic": "System Design",
        "analysis_data": []
    }
    
    app = workflow.compile()
    
    # 1. Generate First Question
    print("\n[AI] Generating Q1...")
    inputs = initial_state
    
    # We run until the first interruption or completion
    # Since we didn't add interrupts, we have to invoke nodes manually 
    # OR redefine the graph to interrupt.
    # For this simulation, we will assume we can run step-by-step.
    
    # Run the 'generate_question' node
    result = await app.ainvoke(inputs)
    
    # BUT, our graph has a loop: gen -> end. analyze -> route -> gen.
    # The graph definition at the end: 
    # workflow.add_node("generate_question", generate_question_node)
    # workflow.set_entry_point("generate_question")
    # No edge from generate_question means it hits END.
    
    # So `ainvoke` should run `generate_question` and stop.
    state = result
    print(f"\nAI: {state['current_question']}")
    
    # 2. Simulate User Answer to Q1
    answer1 = "I would design a distributed system using sharding and replication."
    print(f"\nUser: {answer1}")
    
    # Update state manually to inject answer (simulating API payload)
    state["messages"].append(HumanMessage(content=answer1))
    
    # 3. Analyze Answer 1
    # We need to continue the graph. 
    # Since we hit END, we start a new run? No, that resets state.
    # We should probably use `memory` (LangGraph checkpointer) if we want persistence.
    # For now, let's treat the graph as a single-turn processor if possible, 
    # OR run separate nodes directly for testing.
    
    # Let's run the 'analyze_answer' node directly on the current state
    from app.agents.interview_graph import analyze_answer_node, route_interview, generate_question_node, generate_report_node
    
    print("\n[AI] Analyzing Q1...")
    state = await analyze_answer_node(state)
    print("Feedback:", state["history"][-1])
    
    # 4. Route
    next_step = route_interview(state)
    print(f"Next step: {next_step}")
    
    if next_step == "generate_question":
        print("\n[AI] Generating Q2...")
        state = await generate_question_node(state)
        print(f"\nAI: {state['current_question']}")
        
        # 5. User Answer Q2
        answer2 = "I'm not sure, maybe hash maps?"
        print(f"\nUser: {answer2}")
        state["messages"].append(HumanMessage(content=answer2))
        
        print("\n[AI] Analyzing Q2...")
        state = await analyze_answer_node(state)
        print("Feedback:", state["history"][-1])
        
        next_step = route_interview(state)
        print(f"Next step: {next_step}")
        
    if next_step == "generate_report":
        print("\n[AI] Generating Report...")
        state = await generate_report_node(state)
        print("\n--- FINAL REPORT ---\n")
        print(state["final_report"])

if __name__ == "__main__":
    asyncio.run(simulate_interview())
