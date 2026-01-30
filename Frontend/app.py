import streamlit as st
import requests
import json
import time

import os

# Configuration
API_URL = "http://localhost:8000/api/v1"

# Try to get from Streamlit Secrets (Cloud)
try:
    if "API_URL" in st.secrets:
        API_URL = st.secrets["API_URL"]
except FileNotFoundError:
    pass
except Exception:
    pass

# Try OS Env (Docker/Render) - Overrides default
if "API_URL" in os.environ:
    API_URL = os.environ["API_URL"]

st.set_page_config(
    page_title="TalentTalk Pro",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #f5f7f9;
    }
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .ai-message {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "interview_active" not in st.session_state:
    st.session_state.interview_active = False

def start_interview(company, role, style, difficulty, max_follow_ups):
    payload = {
        "target_company": company,
        "job_role": role,
        "interview_style": style,
        "difficulty": difficulty,
        "max_follow_ups": max_follow_ups
    }
    try:
        response = requests.post(f"{API_URL}/start", json=payload)
        response.raise_for_status()
        data = response.json()
        
        st.session_state.session_id = data["session_id"]
        st.session_state.interview_active = True
        st.session_state.messages = []
        
        # Add AI greeting
        st.session_state.messages.append({"role": "assistant", "content": data["first_question"]})
        st.rerun()
    except Exception as e:
        st.error(f"Failed to start interview: {e}")

def send_response(text_input, audio_file=None):
    if not st.session_state.session_id:
        return

    # Add user message to UI immediately for responsiveness
    if text_input:
        st.session_state.messages.append({"role": "user", "content": text_input})
    elif audio_file:
         st.session_state.messages.append({"role": "user", "content": "🎤 Audio Response Sent"})

    with st.spinner("Interviewer is thinking..."):
        try:
            files = None
            data = {"session_id": st.session_state.session_id}
            
            if audio_file:
                files = {"audio_file": ("answer.wav", audio_file, "audio/wav")}
            if text_input:
                data["text_input"] = text_input

            response = requests.post(f"{API_URL}/chat", data=data, files=files)
            response.raise_for_status()
            result = response.json()
            
            # Update User Message with Transcript
            if result.get("user_transcript"):
                # If the last message was the placeholder, update it
                if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                     st.session_state.messages[-1]["content"] = f"🎤 {result['user_transcript']}"

            # Display Feedback from Interviewer
            if result.get("feedback"):
                feedback_data = result["feedback"]
                # feedback_data is likely a dict or string depending on Gemini's JSON output
                # Let's extract a friendly message.
                feedback_text = ""
                if isinstance(feedback_data, dict):
                    feedback_text = feedback_data.get("feedback", "")
                else:
                    feedback_text = str(feedback_data)
                
                if feedback_text:
                    st.session_state.messages.append({"role": "assistant", "content": f"**Feedback:** {feedback_text}"})

            if result.get("question"):
                st.session_state.messages.append({"role": "assistant", "content": result["question"], "audio_url": result.get("audio_url")})
            
            if result.get("is_finished"):
                st.session_state.interview_active = False
                st.session_state.messages.append({"role": "system", "content": "Interview Complete. Generating Report..."})
                # Fetch Report
                report_res = requests.get(f"{API_URL}/report/{st.session_state.session_id}")
                if report_res.status_code == 200:
                    report_data = report_res.json()
                    st.session_state.final_report = report_data.get("report")

            st.rerun()

        except requests.exceptions.HTTPError as err:
            # Try to get detailed error from backend
            try:
                error_detail = err.response.json().get("detail", err.response.text)
                st.error(f"Backend Error: {error_detail}")
            except:
                st.error(f"HTTP Error: {err}")
        except Exception as e:
            st.error(f"Error sending message: {e}")

# --- Sidebar ---
with st.sidebar:
    st.title("TalentTalk Pro 🚀")
    st.header("Setup Interview")
    
    target_company = st.text_input("Target Company", "Google")
    job_role = st.text_input("Job Role", "Senior Python Developer")
    
    col1, col2 = st.columns(2)
    with col1:
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    with col2:
        style = st.selectbox("Style", ["Professional", "Friendly", "HR", "Technical"])
    
    # Follow-up Depth Slider
    max_follow_ups = st.slider("Step-by-step Follow-ups (Depth)", 0, 3, 1, 
                               help="How many follow-up questions to ask per main topic.")
    
    # Resume Upload
    resume_file = st.file_uploader("📄 Upload Resume (PDF)", type=["pdf"])
        
    if not st.session_state.interview_active:
        if st.button("Start Interview", type="primary"):
            if resume_file:
                # Start with resume
                try:
                    with st.spinner("Analyzing Resume..."):
                        files = {"resume_file": ("resume.pdf", resume_file, "application/pdf")}
                        data = {
                            "target_company": target_company,
                            "job_role": job_role,
                            "interview_style": style,
                            "job_role": job_role,
                            "interview_style": style,
                            "difficulty": difficulty,
                            "max_follow_ups": max_follow_ups
                        }
                        response = requests.post(f"{API_URL}/start_with_resume", data=data, files=files)
                        response.raise_for_status()
                        res_data = response.json()
                        
                        st.session_state.session_id = res_data["session_id"]
                        st.session_state.interview_active = True
                        st.session_state.messages = [{"role": "assistant", "content": res_data["first_question"]}]
                        st.rerun()
                except requests.exceptions.HTTPError as e:
                    error_msg = "Unknown Error"
                    try:
                        error_msg = e.response.json().get("detail", str(e))
                    except:
                        error_msg = str(e)
                    st.error(f"Failed to start with resume: {error_msg}")
                except Exception as e:
                    st.error(f"Failed to start with resume: {e}")
            else:
                # Standard Start
                start_interview(target_company, job_role, style, difficulty, max_follow_ups)
    else:
        if st.button("End Interview", type="secondary"):
            st.session_state.interview_active = False
            st.rerun()
            
    st.markdown("---")
    if st.session_state.get("final_report"):
        st.success("Report Generated!")
        with st.expander("View Final Report", expanded=True):
            st.markdown(st.session_state.final_report)

# --- Main Interaction Area ---

st.title("AI Interview Session")

# Chat Container
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if msg.get("audio_url"):
                # Construct full URL - ensure backend port is reachable
                # In docker/prod this needs proper handling. 
                # For local: http://localhost:8000 + url
                audio_full_url = f"http://localhost:8000{msg['audio_url']}"
                st.audio(audio_full_url, autoplay=True)

# Input Area (Fixed at bottom)
if st.session_state.interview_active:
    st.markdown("---")
    col_text, col_audio = st.columns([0.8, 0.2])
    
    with col_text:
        text_input = st.chat_input("Type your answer here...")
        if text_input:
            send_response(text_input)
            
    with col_audio:
        # Media Uploader
        media_type = st.radio("Input Type", ["Audio", "Video"], horizontal=True, label_visibility="collapsed")
        
        if media_type == "Audio":
            # Using native Streamlit audio input (requires Streamlit 1.40+)
            audio_value = st.audio_input("🎤 Record your answer")
            if audio_value:
                 # Automatically send when recording stops? Or require button?
                 # st.audio_input returns a file-like object.
                 if st.button("Send Audio Answer", type="primary"):
                     send_response(None, audio_value)
        else:
            uploaded_video = st.file_uploader("📹 Upload Video", type=["mp4", "mov"], key="video_uploader")
            if uploaded_video:
                if st.button("Analyze Video Behavior"):
                    with st.spinner("Analyzing Video..."):
                        try:
                            video_files = {"video_file": ("video.mp4", uploaded_video, "video/mp4")}
                            res = requests.post(f"{API_URL}/analyze_video", files=video_files)
                            if res.status_code == 200:
                                analysis = res.json().get("analysis")
                                st.success("Video Analyzed!")
                                st.info(analysis)
                                # Append to chat as system note
                                st.session_state.messages.append({"role": "system", "content": f"**Video Analysis:** {analysis}"})
                            else:
                                st.error("Analysis Failed")
                        except Exception as e:
                            st.error(f"Error: {e}")

elif st.session_state.get("final_report"):
    st.balloons()
    st.markdown("## 📊 Interview Performance Report")
    st.markdown(st.session_state.final_report)
