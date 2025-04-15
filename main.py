import streamlit as st
import requests
import json
from datetime import datetime
import base64

# Gemini API key
API_KEY = 'AIzaSyAT-qzEFNcXtBUvL-kTprvjqXM1k1kfER4'
API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

# System prompt for Gemini (unchanged)
SYSTEM_MESSAGE = """
Polio Awareness AI Assistant – System Instruction
Name: Polio Awareness AI Assistant
Affiliation: National Polio Eradication Initiative / Public Health Awareness Campaign
Purpose: The Polio Awareness AI Assistant is designed to support the public by providing accurate, age-appropriate, and trustworthy information about Polio Virus prevention, symptoms, vaccination, and treatment options. The assistant serves as an educational and supportive tool to raise awareness, promote vaccination, and guide individuals toward reliable healthcare resources.
Scope of Assistance: The assistant must ONLY respond to questions related to the following topics:
- What is Polio?
- Causes and transmission of the Polio virus
- Signs and symptoms of Polio
- Polio vaccination and immunization schedules
- Importance of oral polio vaccine (OPV) and inactivated polio vaccine (IPV)
- Prevention and early detection
- Long-term effects of Polio
- Public health policies and eradication efforts
- Resources for Polio education and support
Out-of-Scope Handling: If a user asks a question outside of the allowed topics, respond with: "I am sorry, I am the Polio Awareness AI Assistant and can only provide information about the Polio virus, its prevention, vaccination, and health impact. For other questions, please contact your nearest health professional or public health office. Stay informed and protect your health through accurate and verified information."
Core Responsibilities:
- Provide scientifically accurate and clear information
- Promote awareness of vaccination and its benefits
- Guide users to proper healthcare services and support systems
- Raise public understanding of the risks and prevention of Polio
- Encourage responsible health behaviors
Promotion of National Health Campaigns:
- Mass immunization programs
- Community education drives
- Access to public health facilities
- Polio vaccination campaigns
Ethical Guidelines:
- No medical diagnosis
- No legal or unrelated health advice
- Do not respond to non-Polio topics
- Always remain respectful, warm, supportive, and factual
- Refer users to healthcare providers or official health services when necessary
"""

# Set page config
st.set_page_config(page_title="Polio Awareness AI Assistant", layout="wide")

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'feedback' not in st.session_state:
    st.session_state.feedback = {}
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Custom CSS for compact, single-page, polio-themed design
st.markdown(
    """
    <style>
    /* Global styles */
    .stApp {
        background: linear-gradient(135deg, #2A1B3D 0%, #3E2D5C 100%);
        color: #F3F4F6;
        font-family: 'Inter', sans-serif;
        height: 100vh;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }
    h1 {
        color: #C084FC;
        text-align: center;
        font-size: 2em;
        margin: 0.5em 0 0.2em;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        animation: fadeIn 1s ease-in;
    }
    .subheader {
        color: #FBBF24;
        text-align: center;
        font-size: 1em;
        margin: 0 0 0.5em;
    }
    /* Chat container */
    .chat-container {
        flex-grow: 1;
        min-height: 0;
        max-height: 65vh;
        overflow-y: auto;
        padding: 15px;
        background: #3B2F5F;
        border-radius: 10px;
        margin: 10px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    }
    .chat-container::-webkit-scrollbar {
        width: 8px;
    }
    .chat-container::-webkit-scrollbar-track {
        background: #2D2A44;
        border-radius: 10px;
    }
    .chat-container::-webkit-scrollbar-thumb {
        background: #C084FC;
        border-radius: 10px;
    }
    /* Messages */
    .user-message {
        background: linear-gradient(135deg, #C084FC, #A855F7);
        color: #1F1A44;
        padding: 10px 15px;
        border-radius: 15px 15px 5px 15px;
        margin: 5px 15px 5px 30%;
        max-width: 60%;
        animation: slideInRight 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .assistant-message {
        background: linear-gradient(135deg, #4B3D7A, #6B5B9A);
        color: #F3F4F6;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 5px;
        margin: 5px 30% 5px 15px;
        max-width: 60%;
        animation: slideInLeft 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    .timestamp {
        font-size: 0.65em;
        color: #9CA3AF;
        margin: 2px 15px;
        text-align: right;
    }
    .assistant-timestamp {
        text-align: left;
    }
    /* Typing indicator */
    .typing-indicator {
        display: none;
        padding: 8px 15px;
        color: #FBBF24;
        font-style: italic;
        font-size: 0.9em;
    }
    .typing-indicator.active {
        display: block;
    }
    /* Input area */
    .input-container {
        display: flex;
        align-items: center;
        background: #3B2F5F;
        padding: 8px;
        border-radius: 8px;
        margin: 10px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.2);
    }
    .stTextInput > div > div > input {
        border: none;
        border-radius: 6px;
        padding: 10px;
        font-size: 0.9em;
        background: #4B3D7A;
        color: #F3F4F6;
        flex-grow: 1;
        margin-right: 8px;
    }
    .stTextInput > div > div > input:focus {
        outline: none;
        box-shadow: 0 0 4px #C084FC;
    }
    .send-button {
        background: #C084FC;
        color: #1F1A44;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: bold;
        font-size: 0.9em;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    .send-button:hover {
        background: #A855F7;
        transform: scale(1.05);
    }
    /* Quick replies */
    .quick-reply-container {
        text-align: center;
        margin: 5px 10px;
    }
    .quick-reply {
        background: #FBBF24;
        color: #1F1A44;
        border-radius: 15px;
        padding: 6px 12px;
        margin: 3px;
        cursor: pointer;
        display: inline-block;
        font-size: 0.85em;
        transition: all 0.3s ease;
    }
    .quick-reply:hover {
        background: #F59E0B;
        transform: scale(1.05);
    }
    /* Controls */
    .controls-container {
        display: flex;
        justify-content: space-between;
        margin: 5px 10px;
        flex-wrap: wrap;
    }
    .control-button {
        background: #6B5B9A;
        color: #F3F4F6;
        border-radius: 6px;
        padding: 6px 12px;
        font-size: 0.85em;
        border: none;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 3px;
    }
    .control-button:hover {
        background: #5A4A8A;
        transform: scale(1.05);
    }
    /* Footer and links */
    .footer {
        text-align: center;
        color: #C084FC;
        font-size: 0.8em;
        margin: 0.5em 0;
    }
    .resource-link {
        color: #FBBF24;
        text-decoration: none;
        margin: 0 5px;
        font-size: 0.85em;
    }
    .resource-link:hover {
        text-decoration: underline;
    }
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @keyframes slideInRight {
        from { transform: translateX(50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideInLeft {
        from { transform: translateX(-50px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    /* Responsive design */
    @media (max-width: 768px) {
        h1 { font-size: 1.5em; }
        .subheader { font-size: 0.9em; }
        .chat-container { max-height: 60vh; }
        .user-message, .assistant-message { max-width: 70%; margin-left: 15%; margin-right: 15%; }
        .input-container { padding: 6px; }
        .quick-reply { font-size: 0.8em; padding: 5px 10px; }
        .control-button { font-size: 0.8em; padding: 5px 10px; }
    }
    @media (max-width: 480px) {
        h1 { font-size: 1.2em; }
        .subheader { font-size: 0.8em; }
        .chat-container { max-height: 55vh; }
        .user-message, .assistant-message { max-width: 80%; margin-left: 10%; margin-right: 10%; }
        .input-container { flex-direction: column; }
        .stTextInput > div > div > input { margin-bottom: 6px; margin-right: 0; }
        .send-button { width: 100%; }
        .quick-reply { font-size: 0.75em; padding: 4px 8px; }
        .controls-container { flex-direction: column; align-items: center; }
        .control-button { width: 100%; text-align: center; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# JavaScript for send-on-enter with debouncing
st.markdown(
    """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        const input = document.querySelector('input');
        let isSubmitting = false;
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && input.value.trim() !== '' && !isSubmitting) {
                isSubmitting = true;
                document.querySelector('.send-button').click();
                setTimeout(() => { isSubmitting = false; }, 1000);
            }
        });
    });
    </script>
    """,
    unsafe_allow_html=True
)

# Streamlit UI
st.markdown("<h1>🩺 Ethiopian Polio Awareness Chatbot</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='subheader'>Your trusted source for polio prevention, vaccination, and health information</div>",
    unsafe_allow_html=True
)

# Chat history display
chat_container = st.container()
with chat_container:
    st.markdown("<div class='chat-container' id='chat-container'>", unsafe_allow_html=True)
    for idx, chat in enumerate(st.session_state.chat_history):
        st.markdown(
            f"""
            <div class='user-message'>{chat['user']}</div>
            <div class='timestamp'>{chat['user_time']}</div>
            <div class='assistant-message'>{chat['assistant']}</div>
            <div class='timestamp assistant-timestamp'>{chat['assistant_time']}</div>
            """,
            unsafe_allow_html=True
        )
        # Feedback option
        if idx not in st.session_state.feedback:
            st.session_state.feedback[idx] = None
        feedback = st.radio(
            f"Rate response {idx + 1}",
            ["👍 Helpful", "👎 Not Helpful"],
            key=f"feedback_{idx}",
            horizontal=True,
            label_visibility="collapsed"
        )
        if feedback:
            st.session_state.feedback[idx] = feedback
    st.markdown("<div class='typing-indicator' id='typing'>Assistant is typing...</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Auto-scroll to bottom
st.markdown(
    """
    <script>
    const chatContainer = document.getElementById('chat-container');
    chatContainer.scrollTop = chatContainer.scrollHeight;
    </script>
    """,
    unsafe_allow_html=True
)

# Input section
with st.container():
    st.markdown("<div class='input-container'>", unsafe_allow_html=True)
    user_input = st.text_input(
        "Ask about polio:",
        placeholder="E.g., What is polio? How can I prevent it?",
        key=f"user_input_{st.session_state.input_key}",
        label_visibility="collapsed"
    )
    st.markdown("<button class='send-button'>Send</button>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Quick reply suggestions
    st.markdown("<div class='quick-reply-container'>", unsafe_allow_html=True)
    quick_replies = [
        "What is polio?",
        "How is polio transmitted?",
        "What are polio symptoms?",
        "Polio vaccination schedule"
    ]
    for qr in quick_replies:
        if st.button(qr, key=f"qr_{qr}", help=qr):
            user_input = qr
    st.markdown("</div>", unsafe_allow_html=True)

    # Additional controls
    st.markdown("<div class='controls-container'>", unsafe_allow_html=True)
    if st.button("Clear Chat", key="clear_chat", help="Clear chat history"):
        st.session_state.chat_history = []
        st.session_state.feedback = {}
        st.session_state.input_key += 1
        st.rerun()
    if st.button("Download Chat", key="download_chat", help="Download chat history"):
        chat_text = "\n".join(
            f"[{chat['user_time']}] You: {chat['user']}\n[{chat['assistant_time']}] Assistant: {chat['assistant']}"
            for chat in st.session_state.chat_history
        )
        b64 = base64.b64encode(chat_text.encode()).decode()
        href = f'<a href="data:text/plain;base64,{b64}" download="chat_history.txt" class="resource-link">Download Chat History</a>'
        st.markdown(href, unsafe_allow_html=True)
    st.markdown(
        "<a href='https://www.who.int/health-topics/poliomyelitis' target='_blank' class='resource-link'>WHO Polio Info</a>",
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # Chat trigger
    if user_input.strip():
        with chat_container:
            st.markdown("<script>document.getElementById('typing').classList.add('active');</script>", unsafe_allow_html=True)
        with st.spinner(""):
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": SYSTEM_MESSAGE + "\n\nUser Question: " + user_input}
                        ]
                    }
                ]
            }
            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if response.status_code == 200:
                    result = response.json()
                    reply = result['candidates'][0]['content']['parts'][0]['text']
                    st.session_state.chat_history.append({
                        "user": user_input,
                        "user_time": current_time,
                        "assistant": reply,
                        "assistant_time": current_time
                    })
                    st.session_state.input_key += 1
                    st.markdown("<script>document.getElementById('typing').classList.remove('active');</script>", unsafe_allow_html=True)
                    st.rerun()
                else:
                    error_msg = response.json().get("error", {}).get("message", "Unknown error")
                    st.error(f"Error: {error_msg}")
                    st.session_state.input_key += 1
                    st.markdown("<script>document.getElementById('typing').classList.remove('active');</script>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Oops, something went wrong: {str(e)}. Please try again!")
                st.session_state.input_key += 1
                st.markdown("<script>document.getElementById('typing').classList.remove('active');</script>", unsafe_allow_html=True)

# Footer
st.markdown(
    "<div class='footer'>Powered by Ethiopia  Polio Awareness Initiative | <a href='https://polioeradication.org/' target='_blank' class='resource-link'>Global Polio Eradication</a></div>",
    unsafe_allow_html=True
)