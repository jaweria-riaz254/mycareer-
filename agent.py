import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# --- CONFIGURATION & SETUP ---
load_dotenv()
# api_key = os.getenv("GEMINI_API_KEY")

if "GEMINI_API_KEY" in st.screats:
    api_key=st.screats["GEMINI_API_KEY"]
else:
    api_key=os.getenv("GEMINI_API_KEY")
    
FILE_NAME = "chat_memory.json"


st.set_page_config(page_title="PathFinder AI", page_icon="🚀", layout="wide")

# --- DATA PERSISTENCE LOGIC ---
def load_data():
    if os.path.exists(FILE_NAME) and os.path.getsize(FILE_NAME) > 0:
        with open(FILE_NAME, "r") as f:
            return json.load(f)
    return []

def save_data(chat_history):
    new_memory = []
    for message in chat_history:
        # Streamlit history and Gemini history have slightly different structures
        # We ensure compatibility here
        new_memory.append({
            "role": message["role"],
            "parts": [{"text": message["content"]}]
        })
    with open(FILE_NAME, "w") as diary:
        json.dump(new_memory, diary, indent=4)

# --- GEMINI AI SETUP ---
genai.configure(api_key=api_key)

instructions = """
Role:
You are 'PathFinder', a wise, professional, and adaptive AI Career Architect.

Core Logic - Adaptive Goal Management:
1. FLEXIBILITY: You are not locked into one career path. If a user was discussing Data Science but now wants to learn React or Graphic Design, ADAPT immediately.
2. TRANSITION GUIDANCE: When a user changes their goal:
   - ACKNOWLEDGE the change politely.
   - COUNSEL: Briefly compare the two paths if they are related (e.g., "Moving from Data Science to React means shifting from Analysis to Building interfaces").
   - PERSUADE/ADVISE: If their previous goal was highly promising or they had made great progress, gently mention it (e.g., "You were doing great in Data Science, are you sure you want to pivot?").
   - RESPECT: If the user insists on the new path, accept it enthusiastically and build the new roadmap.
3. MEMORY AWARENESS: Use past context to help the current goal, but never let past context block a new request.

Mission & Scope:
1. Provide roadmaps for ANY professional field (Tech, Medical, Arts, Business, etc.).
2. STRICT BOUNDARY: Refuse only non-career topics (jokes, weather, cooking).

Response Style:
1. Use **Bold Headings** and Bullet Points.
2. TABLES: Every roadmap must have a Markdown Table: [Phase | Action Item | Estimated Time].
3. Ask about the "Previous Task" progress to maintain accountability.

Persona:
- Act like a senior mentor who wants the best for the student but respects their freedom to choose.
- Use relevant emojis based on the current field being discussed.
"""
# Initialize Model
model = genai.GenerativeModel(
    model_name='gemini-2.5-flash-lite', # Updated to latest stable version
    system_instruction=instructions
)

# --- STREAMLIT UI COMPONENTS ---

# Sidebar for Branding & Controls
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=100) # Professional Robot Icon
    st.title("PathFinder AI")
    st.subheader("Your Career Architect")
    st.markdown("---")
    st.write("Specialized in guiding your professional journey with precision and motivation.")
    
    if st.button("🗑️ Clear Chat History"):
        if os.path.exists(FILE_NAME):
            os.remove(FILE_NAME)
        st.session_state.messages = []
        st.rerun()

# Main UI Header
st.title("🚀 Career Roadmap & Guidance")
st.caption("Strategic planning for your professional future.")

# Initialize Session State for Chat
if "messages" not in st.session_state:
    saved_history = load_data()
    # Convert saved JSON format to Streamlit format
    st.session_state.messages = []
    for msg in saved_history:
        st.session_state.messages.append({
            "role": "assistant" if msg["role"] == "model" else "user",
            "content": msg["parts"][0]["text"]
        })

# Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- CHAT LOGIC ---
if prompt := st.chat_input("Ask about your career roadmap..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("PathFinder is analyzing your career path..."):
            # Prepare history for Gemini API
            history_for_gemini = [
                {"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
                for m in st.session_state.messages[:-1]
            ]
            
            chat_session = model.start_chat(history=history_for_gemini)
            try:
                response = chat_session.send_message(prompt)
                full_response = response.text
                st.markdown(full_response)
                
                # Add to state and save to file
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                save_data(st.session_state.messages)
            except Exception as e:
                st.error(f"Error: {e}")
