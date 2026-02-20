import streamlit as st
import openai
import time
import base64

# --- CONFIGURATION ---
# The key is now pulled securely from Streamlit Secrets
OPENAI_API_KEY = "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"]

# Replace the line below with your YouTube Embed Code from Phase 1
VIDEO_EMBED_CODE = """
<<iframe width="700" height="315" src="https://www.youtube.com/embed/GEYfaDTzGsI?si=8khPkkMGTwIxUQo3" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>>
"""

# Setup Page
st.set_page_config(page_title="Interactive Voice Assistant", page_icon="🤖")

# Custom CSS for Video and Buttons
st.markdown("""
<style>
    .video-container {
        position: relative;
        padding-bottom: 56.25%; /* 16:9 ratio */
        height: 0;
        overflow: hidden;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        margin-bottom: 20px;
    }
    .video-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: 0;
    }
    .stButton>button {
        width: 100%;
        font-size: 18px;
        padding: 10px;
    }
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
    st.title("🤖 Interactive Voice Assistant")
    
    # 1. Display Avatar Video
    st.markdown(f'<div class="video-container">{VIDEO_EMBED_CODE}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 2. Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            # If it was an assistant message, add a small "Replay Audio" button
            if message["role"] == "assistant":
                if st.button("🔊 Replay Answer", key=f"replay_{len(st.session_state.messages)}"):
                    # Trigger JS to speak this specific text
                    st.write(f"<script>window.speakText('{message['content'].replace("'", "\\'")}');</script>", unsafe_allow_html=True)

    # 3. Voice Input Section
    st.subheader("Ask a Question")
    
    # We use a special HTML component to enable the microphone
    # This creates a button that activates the browser's native speech recognition
    st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <button id="mic-btn" style="background-color: #FF4B4B; color: white; border: none; padding: 15px 30px; 
        border-radius: 50px; font-size: 18px; cursor: pointer; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        🎤 Click to Speak
        </button>
        <p id="status" style="color: gray; font-size: 14px;">Click the button above and allow microphone access</p>
    </div>

    <script>
        // Check if browser supports speech recognition
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.lang = 'en-US';
            recognition.interimResults = false;

            const btn = document.getElementById('mic-btn');
            const status = document.getElementById('status');
            const inputArea = document.querySelector('textarea[data-testid="stChatInputTextArea"]');

            btn.onclick = () => {
                recognition.start();
                status.innerText = "Listening... Speak now!";
                btn.style.backgroundColor = "#4CAF50"; // Green while listening
            };

            recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                status.innerText = "You said: " + transcript;
                btn.style.backgroundColor = "#FF4B4B"; // Reset color
                
                // Automatically put text in the chat box and simulate 'Enter'
                // Note: Streamlit's input handling is tricky, so we instruct user to press enter 
                // OR we can try to inject it. For stability, let's just show it and ask user to hit send 
                // BUT to make it seamless, we will use a Streamlit query param trick or just rely on the user hitting enter.
                // Actually, let's just update the status and tell the user to press Enter in the box below.
                alert("Heard: " + transcript + "\\n\\nPlease paste this into the chat box below and press Enter!");
                
                // Better UX: Try to find the textarea and fill it
                if(inputArea) {
                    inputArea.value = transcript;
                    // Trigger input event so Streamlit notices
                    inputArea.dispatchEvent(new Event('input', { bubbles: true }));
                }
            };

            recognition.onerror = (event) => {
                status.innerText = "Error: " + event.error;
                btn.style.backgroundColor = "#FF4B4B";
            };
            
            recognition.onend = () => {
                btn.style.backgroundColor = "#FF4B4B";
                if(status.innerText.includes("Listening")) {
                    status.innerText = "Done listening.";
                }
            };
        } else {
            document.getElementById('mic-btn').style.display = 'none';
            document.getElementById('status').innerText = "Your browser does not support voice input. Please type.";
        }

        // Function to speak text aloud (Text-to-Speech)
        window.speakText = function(text) {
            if ('speechSynthesis' in window) {
                // Cancel any current speaking
                window.speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'en-US';
                utterance.rate = 1.0; // Normal speed
                utterance.pitch = 1.0;
                
                // Optional: Try to find a good voice
                const voices = window.speechSynthesis.getVoices();
                // Prefer Google US English or Microsoft Natural voices if available
                const preferredVoice = voices.find(voice => voice.name.includes('Google US English') || voice.name.includes('Natural'));
                if (preferredVoice) {
                    utterance.voice = preferredVoice;
                }

                window.speechSynthesis.speak(utterance);
            } else {
                alert("Sorry, your browser doesn't support text-to-speech.");
            }
        };
        
        // Load voices immediately
        if ('speechSynthesis' in window) {
            window.speechSynthesis.getVoices();
        }
    </script>
    """, unsafe_allow_html=True)

    # 4. Handle Chat Logic
    if prompt := st.chat_input("Type here or use the mic button above..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            try:
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful virtual assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                ai_reply = response.choices[0].message.content
                message_placeholder.markdown(ai_reply)
                
                # Add to history
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                
                # AUTOMATICALLY SPEAK THE RESPONSE
                # We escape quotes to prevent JS errors
                safe_reply = ai_reply.replace("'", "\\'").replace("\n", " ")
                st.write(f"<script>window.speakText('{safe_reply}');</script>", unsafe_allow_html=True)
                
            except Exception as e:
                error_msg = f"Error: {str(e)}"
                message_placeholder.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})

else:
    st.info("👈 Please log in from the sidebar.")




