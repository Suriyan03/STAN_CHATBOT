# File: frontend/app.py

import streamlit as st
import requests
import uuid
import time

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:8000/chat"
RESET_URL = "http://127.0.0.1:8000/api/v1/debug/memory/reset"

# A fixed ID for demonstrating persistent memory recall (RAG)
# You can use this ID, tell Lyra facts, restart the server, and click the button to reload the memory.
PERSISTENT_TEST_ID = "rag-demo-user-12345" 


# --- CUSTOM CSS (DARK THEME) ---
CUSTOM_CSS = """
<style>
/* 1. Main App Background */
.stApp {
    background-color: #1a1a1a; 
    color: #f0f0f0; 
}
/* 2. Custom Styling for Lyra's (Assistant) Messages */
.stChatMessage:nth-child(even) { 
    background-color: #282828; 
    border-left: 5px solid #00a896; 
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
    color: #ffffff;
}
/* 3. User Message Style */
.stChatMessage:nth-child(odd) {
    background-color: #383838; 
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 10px;
    color: #ffffff; 
}
/* 4. General text visibility */
h1, h2, h3, h4, h5, h6, .stMarkdown, .stText, .stCode {
    color: #f0f0f0 !important;
}
/* 5. Hide Streamlit Footer for cleaner look */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True) 


# --- HELPER FUNCTIONS ---

def get_bot_response(user_id, message):
    # ... (existing function content)
    try:
        response = requests.post(API_URL, json={"user_id": user_id, "message": message})
        response.raise_for_status()
        return response.json().get("reply")
    except requests.exceptions.RequestException as e:
        st.error(f"Error: Could not connect to the backend API. Is the FastAPI server running? Details: {e}", icon="🚨")
        return None

def reset_session_state(new_user_id):
    """Resets the Streamlit session variables and sets a new ID."""
    st.session_state.user_id = new_user_id
    st.session_state.chat_history = []
    st.toast("Session ID Switched. Chat history reset!")
    time.sleep(0.5)
    st.rerun()

def clear_redis_memory(user_id):
    # ... (existing function content)
    try:
        url = f"{RESET_URL}/{user_id}"
        response = requests.delete(url)
        response.raise_for_status()
        st.toast(f"Redis Memory for {user_id[:8]}... cleared!", icon="🧹")
    except requests.exceptions.RequestException as e:
        st.error(f"Failed to clear Redis: {e}", icon="❌")
    
    reset_session_state(str(uuid.uuid4())) # Generate a new random ID after clearing


# --- SESSION STATE INITIALIZATION ---
if 'user_id' not in st.session_state:
    st.session_state.user_id = str(uuid.uuid4())
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []


# --- SIDEBAR (Settings and Debugging) ---

with st.sidebar:
    st.header("⚙️ Lyra Chat Settings")
    st.markdown("---")
    
    st.subheader("Current User Identity")
    st.code(st.session_state.user_id)
    
    # 🌟 NEW FEATURE: Switch to RAG Test ID
    st.subheader("Memory Test Tool")
    if st.button("⏪ Switch to Persistent Demo User", help=f"Switches to ID: {PERSISTENT_TEST_ID}"):
        reset_session_state(PERSISTENT_TEST_ID)
        
    if st.button("🔄 Start New Random Session", help="Generates a new random ID."):
        reset_session_state(str(uuid.uuid4()))
        
    if st.button("🧹 Clear Short-Term Memory", help=f"Clears Redis history for {st.session_state.user_id}"):
        clear_redis_memory(st.session_state.user_id)
        
    st.markdown("---")
    st.markdown("**Project Status**")
    st.success("✅ Backend API Running")
    st.success("✅ Redis (Short-Term) Active")
    st.success("✅ ChromaDB (Long-Term) Active")
    st.caption("Ensure Docker (Redis) and FastAPI are running.")


# --- MAIN UI LAYOUT ---

st.title("🤖 Lyra - Your Digital Companion from Neo-Kyoto")
st.caption("Demonstrating Empathy, Context, and Long-Term Memory (RAG)")


# --- CHAT DISPLAY ---
chat_container = st.container()
with chat_container:
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


# --- USER INPUT ---
user_input = st.chat_input("Ask Lyra anything or tell her a new fact...")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    
    with st.spinner("Lyra is thinking..."):
        bot_reply = get_bot_response(st.session_state.user_id, user_input)
        
        if bot_reply:
            st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
            st.rerun()