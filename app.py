import streamlit as st
import openai
import time
import base64

# --- CONFIGURATION ---
OPENAI_API_KEY = "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"

# REPLACE THIS LINK WITH YOUR HUMAN IMAGE LINK FROM UNSPLASH/PExELS
# Make sure it ends in .jpg or .png
AVATAR_IMAGE_URL = "https://ibb.co/4wq1gt9b"

st.set_page_config(page_title="Human-Like Assistant", page_icon="🤖")

# --- CUSTOM CSS FOR HUMAN INTERACTION ---
st.markdown(f"""
<style>
    /* Container for the avatar */
    .avatar-container {{
        position: relative;
        width: 300px;
        height: 300px;
        margin: 0 auto 20px auto;
        border-radius: 50%;
        overflow: hidden;
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        border: 5px solid white;
    }}

    /* The Image itself */
    .avatar-img {{
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }}

    /* Breathing Animation (Simulates life) */
    @keyframes breathe {{
        0% {{ transform: scale(1); }}
        50% {{ transform: scale(1.03); }}
        100% {{ transform: scale(1); }}
    }}

    .breathing {{
        animation: breathe 3s infinite ease-in-out;
    }}

    /* Speaking Animation (Glowing Ring) */
    @keyframes speak-pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(66, 133, 244, 0.7); }}
        70% {{ box-shadow: 0 0 0 20px rgba(66, 133, 244, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(66, 133, 244, 0); }}
    }}

    .speaking {{
        animation: speak-pulse 1.5s infinite;
        border-color: #4285F4; /* Blue border when speaking */
    }}
    
    /* Listening Animation (Orange Ring) */
    @keyframes listen-pulse {{
        0% {{ box-shadow: 0 0 0 0 rgba(255, 165, 0, 0.7); }}
        70% {{ box-shadow: 0 0 0 20px rgba(255, 165, 0, 0); }}
        100% {{ box-shadow: 0 0 0 0 rgba(255, 165, 0, 0); }}
    }}

    .listening {{
        animation: listen-pulse 1s infinite;
        border-color: #FFA500; /* Orange border when listening */
    }}

    .status-text {{
        text-align: center;
        font-weight: bold;
        color: #555;
        margin-top: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: LOGIN ---
with st.sidebar:
    st.title("🔐 Login")
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if email and password:
                st.session_state.logged_in = True
                st.success("Logged in!")
                st.rerun()
            else:
                st.error("Please enter details")
    else:
        st.success(f"Welcome!")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- MAIN APP ---
if st.session_state.logged_in:
    st.title("🤖 Human-Like Virtual Assistant")
    
    # Dynamic State for Avatar Animation
    if 'avatar_state' not in st.session_state:
        st.session_state.avatar_state = "idle" # idle, listening, speaking

    # Display Avatar with Dynamic Class
    avatar_class = "breathing" # Always breathing
    status_msg = "Ready to help"
    
    if st.session_state.avatar_state == "listening":
        avatar_class += " listening"
        status_msg = "👂 Listening..."
    elif st.session_state.avatar_state == "speaking":
        avatar_class += " speaking"
        status_msg = "🗣️ Speaking..."

    # Render the Avatar
    st.markdown(f"""
    <div class="avatar-container {avatar_class}">
        <img src="{AVATAR_IMAGE_URL}" class="avatar-img" alt="Assistant">
    </div>
    <div class="status-text">{status_msg}</div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message["role"] == "assistant":
                if st.button("🔊 Replay", key=f"replay_{len(st.session_state.messages)}"):
                    safe_reply = message['content'].replace("'", "\\'").replace("\n", " ")
                    st.write(f"<script>window.speakText('{safe_reply}');</script>", unsafe_allow_html=True)

    st.subheader("Ask a Question")
    
    # Voice Input Script
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <button id="mic-btn" style="background-color: #FF4B4B; color: white; border: none; padding: 15px 30px; 
        border-radius: 50px; font-size: 18px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        🎤 Click to Speak
        </button>
        <p id="status" style="color: gray; font-size: 14px; margin-top:5px;">Click to start voice interaction</p>
    </div>

    <script>
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';
            
            const btn = document.getElementById('mic-btn');
            const status = document.getElementById('status');
            const inputArea = document.querySelector('textarea[data-testid="stChatInputTextArea"]');

            btn.onclick = () => {
                // Tell Streamlit to change avatar state to listening
                // We do this by updating a dummy element or just relying on the visual cue
                // For simplicity in this no-code hack, we rely on the user seeing the button change
                recognition.start();
                status.innerText = "Listening...";
                btn.style.backgroundColor = "#FFA500"; // Orange
                
                // Note: Changing the Streamlit session state from JS directly is hard without components.
                // The visual cue here is the button turning orange.
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                status.innerText = "Heard: " + transcript;
                btn.style.backgroundColor = "#FF4B4B";
                
                if(inputArea) {
                    inputArea.value = transcript;
                    inputArea.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };
            
            recognition.onerror = () => {
                status.innerText = "Error. Try typing.";
                btn.style.backgroundColor = "#FF4B4B";
            };
        } else {
            document.getElementById('mic-btn').style.display = 'none';
            document.getElementById('status').innerText = "Browser doesn't support voice.";
        }

        window.speakText = function(text) {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'en-US';
                
                // Try to find a natural voice
                const voices = window.speechSynthesis.getVoices();
                const preferredVoice = voices.find(voice => voice.name.includes('Google US English') || voice.name.includes('Natural'));
                if (preferredVoice) utterance.voice = preferredVoice;

                // Visual cue: We can't easily toggle Streamlit state from here, 
                // but the browser will speak.
                
                window.speechSynthesis.speak(utterance);
            }
        };
        if ('speechSynthesis' in window) window.speechSynthesis.getVoices();
    </script>
    """, unsafe_allow_html=True)

    # Chat Logic
    if prompt := st.chat_input("Type here or use the mic..."):
        # Set state to thinking (default breathing is fine)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            # Update avatar state to speaking (Hack: Rerun not needed if we use JS, but let's try to update text)
            # Since we can't easily trigger a full rerun for the avatar class mid-stream without complexity,
            # we will rely on the "Speaking" logic in the JS below triggering the visual via CSS if possible,
            # OR we just accept the "Breathing" state and let the audio do the work.
            # To make it truly dynamic, we would need a Streamlit Component, which is too complex for this guide.
            # Instead, we will just ensure the audio plays.
            
            try:
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful, friendly human-like assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                ai_reply = response.choices[0].message.content
                message_placeholder.markdown(ai_reply)
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                
                # Speak
                safe_reply = ai_reply.replace("'", "\\'").replace("\n", " ")
                st.write(f"<script>window.speakText('{safe_reply}');</script>", unsafe_allow_html=True)
                
            except Exception as e:
                message_placeholder.error(f"Error: {str(e)}")

else:
    st.info("👈 Please log in.")


