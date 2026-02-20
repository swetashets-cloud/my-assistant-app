import streamlit as st
import openai
import time

# --- CONFIGURATION ---
# Replace this with your actual OpenAI API Key
# For security in a real app, use Streamlit Secrets, but for testing, paste here:
OPENAI_API_KEY = "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" 

# Replace the line below with your YouTube Embed Code from Phase 1
VIDEO_EMBED_CODE = """
<iframe width="560" height="315" src="https://www.youtube.com/embed/GEYfaDTzGsI?si=8khPkkMGTwIxUQo3" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

"""

# Setup Page
st.set_page_config(page_title="My Virtual Assistant", page_icon="🤖")

# Custom CSS to make the video look good
st.markdown("""
<style>
    .video-container {
        position: relative;
        padding-bottom: 56.25%; /* 16:9 ratio */
        height: 0;
        overflow: hidden;
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .video-container iframe {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        border: 0;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: LOGIN SIMULATION ---
with st.sidebar:
    st.title("🔐 Login")
    
    # Simple Login Logic (No database needed for this demo)
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login"):
                if email and password:
                    st.session_state.logged_in = True
                    st.success("Logged in!")
                    st.rerun()
                else:
                    st.error("Please enter email and password")
        
        with col2:
            if st.button("Google Login"):
                st.info("Google Login requires backend setup. Using Email login for now.")
                # In a real app, you would use Firebase Auth here
    else:
        st.success(f"Welcome! Logged in.")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

# --- MAIN APP AREA ---
if st.session_state.logged_in:
    st.title("🤖 Your Virtual Assistant")
    
    # Display the Avatar Video
    st.markdown("<h3>Meet your Assistant</h3>", unsafe_allow_html=True)
    st.markdown(f'<div class="video-container">{VIDEO_EMBED_CODE}</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Voice/Input Section
    st.subheader("Ask a Question")
    
    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Handle User Input (Text or Voice via Browser)
    # Note: Browsers handle voice-to-text natively in the input box if you click the mic icon
    if prompt := st.chat_input("Type or click the mic to speak..."):
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            
            try:
                client = openai.OpenAI(api_key=OPENAI_API_KEY)
                
                # Call OpenAI
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo", # Cheaper/Faster model
                    messages=[
                        {"role": "system", "content": "You are a helpful virtual assistant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                
                ai_reply = response.choices[0].message.content
                message_placeholder.markdown(ai_reply)
                
                # Add AI response to history
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                
            except Exception as e:
                message_placeholder.error(f"Error connecting to AI: {str(e)}")

else:

    st.info("👈 Please log in from the sidebar to start chatting.")
