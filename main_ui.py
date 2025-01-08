import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
from main import handle_query
import speech_recognition as sr

# Configure the page
st.set_page_config(layout="wide", page_title="Multi-Agent Chat Application")

# Sidebar Contents
with st.sidebar:
    st.title("Multi-Agent Chat Application")
    st.markdown(
        """
This is a demo of the Multi-Agent concept.
"""
    )
    add_vertical_space(5)
    st.write("Related to AutoGen")
    if st.button("Clear Chat"):
        if "history" in st.session_state:
            st.session_state["history"] = []

if "history" not in st.session_state:
    st.session_state["history"] = []

# Main Chat Interface
st.title("Chat Interface")

# Display chat history
history = st.session_state["history"]
for message in history:
    role = message["role"]
    content = message["content"]
    with st.chat_message(role):
        st.markdown(content)

# Function to capture voice input
def capture_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening... Please speak into the microphone.")
        try:
            audio = recognizer.listen(source, timeout=10)
            text = recognizer.recognize_google(audio)
            st.success("You said: " + text)
            return text
        except sr.UnknownValueError:
            st.error("Sorry, could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
        except sr.WaitTimeoutError:
            st.error("Listening timed out.")
    return None

# Input Section Fixed at the Bottom
st.markdown(
    """
    <style>
    [data-testid="stVerticalBlock"] {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

col1, col2 = st.columns([3, 1])
with col1:
    user_input = st.chat_input("Type your message here:")
with col2:
    if st.button("🎙️ Speak"):
        voice_input = capture_voice_input()
        if voice_input:
            user_input = voice_input

# Function to add an entry to the chat history
def add_entry(role, content):
    history.append({"role": role, "content": content})
    with st.chat_message(role):
        st.markdown(content)

# Process user input
if user_input:
    # Append user's message to the history
    add_entry("user", user_input)

    # Process the query through the backend
    handle_query(user_input, add_entry)

# Save the updated history
st.session_state["history"] = history