import streamlit as st
import requests
import json
import time
import random
import numpy as np
import speech_recognition as sr
from datetime import datetime
import chardet
import pytesseract
from PIL import Image

# --- Initialize Session State Variables ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "selected_optimization" not in st.session_state:
    st.session_state.selected_optimization = None
if "recognized_text" not in st.session_state:
    st.session_state.recognized_text = ""  # New session state variable for recognized speech

# Set up Tesseract OCR path (change according to your installation)
pytesseract.pytesseract.tesseract_cmd = r"D:\tesseract\tesseract.exe"

# API Endpoint
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

# --- Reinforcement Learning Setup ---
actions = [
    "Generate basic code for: {}",
    "Generate structured code with functions and error handling for: {}",
    "Generate code for: {} and add detailed comments for clarity",
    "Generate optimized code for: {}"
]
num_actions = len(actions)

if "Q_table" not in st.session_state:
    st.session_state.Q_table = np.zeros(num_actions)

def get_action(Q_table, epsilon=0.1):
    """Epsilon-greedy action selection."""
    if random.uniform(0, 1) < epsilon:
        return random.choice(range(num_actions))
    else:
        return int(np.argmax(Q_table))

def update_Q(Q_table, action_idx, reward, learning_rate=0.1, discount_factor=0.9):
    """Update Q-value for the given action."""
    best_next = np.max(Q_table)
    Q_table[action_idx] += learning_rate * (reward + discount_factor * best_next - Q_table[action_idx])
    return Q_table

# --- Initialize Streamlit Page ---
st.set_page_config(page_title="Coderzz.AI - AI Coding Assistant", layout="wide")

# --- Custom Styling ---
st.markdown(
    """
    <style>
    .stButton button { background-color: #4CAF50; color: white; font-size: 16px; padding: 10px 24px; border-radius: 8px; border: none; transition: background-color 0.3s ease; }
    .stButton button:hover { background-color: #45a049; }
    .stTextArea textarea { height: 68px; }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar ---
st.sidebar.title("💻 Coderzz.AI")
st.sidebar.write("Generate and debug code effortlessly!")

# Store chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.sidebar.subheader("Chat History")
for message in reversed(st.session_state.chat_history[-10:]):
    st.sidebar.markdown(message)

# --- Session Variables ---
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "user_input" not in st.session_state:
    st.session_state.user_input = ""
if "feedback_submitted" not in st.session_state:
    st.session_state.feedback_submitted = False
if "selected_code_type" not in st.session_state:
    st.session_state.selected_code_type = None

# --- Speech Recognition ---
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source, timeout=5)  # Listen for up to 5 seconds
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio"
    except sr.RequestError as e:
        return f"Error with the recognition service: {e}"

# --- Image Processing ---
def process_image(image):
    image = Image.open(image)
    text = pytesseract.image_to_string(image)
    return text

# --- Document Processing ---
def process_document(doc_file):
    raw_data = doc_file.read()
    encoding_detected = chardet.detect(raw_data)['encoding']
    content = raw_data.decode(encoding_detected or "utf-8", errors="ignore")
    return content

# --- Main UI ---
st.title("💻 Coderzz.AI - Your AI Coding Assistant")
st.write("Ask me any coding-related question!")

# Quick Action Buttons
st.subheader("Quick Actions")
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("🐍 Python"):
        st.session_state.user_input = "Generate Python code for: "
with col2:
    if st.button("🟨 JavaScript"):
        st.session_state.user_input = "Generate JavaScript code for: "
with col3:
    if st.button("☕ Java"):
        st.session_state.user_input = "Generate Java code for: "
with col4:
    if st.button("➕ C++"):
        st.session_state.user_input = "Generate C++ code for: "

# Text Input
user_input = st.text_area("📝 Your Question:", value=st.session_state.user_input, key="input_text")

# Speech Input
if st.button("🎤 Speak Your Query"):
    recognized_text = recognize_speech()
    st.session_state.recognized_text = recognized_text  # Store recognized text in session state
    st.session_state.user_input = recognized_text  # Update user input
    st.rerun()  # Force a rerun to update the UI

# Update the text area if recognized text is available
if st.session_state.recognized_text:
    st.session_state.user_input = st.session_state.recognized_text
    st.session_state.recognized_text = ""  # Reset recognized text

# Image Upload
st.subheader("📷 Upload an Image for Text Extraction")
image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
if image_file:
    extracted_text = process_image(image_file)
    st.text_area("Extracted Text:", extracted_text)

# Document Upload
st.subheader("📄 Upload a Document for Analysis")
doc_file = st.file_uploader("Upload Document", type=["txt", "pdf"])
if doc_file:
    content = process_document(doc_file)
    st.text_area("Document Content:", content)

# Generate Code
if st.button("🚀 Generate Code") and st.session_state.user_input:
    try:
        st.session_state.feedback_submitted = False
        action_idx = get_action(st.session_state.Q_table, epsilon=0.1)
        chosen_template = actions[action_idx]
        prompt_text = chosen_template.format(st.session_state.user_input)

        st.write(f"Using strategy: {actions[action_idx]}")
        st.write(f"Final prompt: {prompt_text}")

        response = requests.post(OLLAMA_URL, json={"model": "coderzz.ai", "prompt": prompt_text, "stream": True})

        if response.status_code == 200:
            placeholder = st.empty()
            st.session_state.generated_code = ""

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    if "response" in chunk:
                        st.session_state.generated_code += chunk["response"]
                        placeholder.code(st.session_state.generated_code, language="python")
                        time.sleep(0.1)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.session_state.chat_history.append(f"You: ({timestamp}) {st.session_state.user_input}")
            st.session_state.chat_history.append(f"Coderzz.AI: ({timestamp}) {st.session_state.generated_code}")
        else:
            st.write(f"⚠ Error: Received status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        st.write(f"⚠ Connection Error: {e}")

# Feedback System
if st.session_state.generated_code:
    st.write("Was this code helpful?")
    feedback = st.radio("Select feedback:", ("Yes", "No"))

    if st.button("📤 Submit Feedback"):
        if feedback == "No":
            st.session_state.feedback_submitted = True

# Optimization Options if Feedback is "No"
if st.session_state.feedback_submitted:
    st.write("How should we improve the code?")
    optimization_options = {
        "Better structure with functions and error handling": "Refactor the code for better modularity and robustness.",
        "More comments for clarity": "Add detailed comments to explain each part of the code.",
        "Optimization for efficiency": "Optimize the code for speed and memory usage."
    }
    selected_option = st.radio("Choose optimization:", list(optimization_options.keys()), key="optimization")

    if st.button("✅ Optimize Code"):
        optimization_text = optimization_options[selected_option]
        st.session_state.selected_optimization = optimization_text

# --- Regenerate Response if Optimization is Selected ---
if st.session_state.selected_optimization:
    retry_prompt = f"Improve the following code based on this suggestion: {st.session_state.selected_optimization}\n\n{st.session_state.generated_code}"

    try:
        response = requests.post(OLLAMA_URL, json={"model": "coderzz.ai", "prompt": retry_prompt, "stream": True})
        if response.status_code == 200:
            placeholder = st.empty()
            optimized_code = ""

            for line in response.iter_lines():
                if line:
                    chunk = json.loads(line.decode("utf-8"))
                    if "response" in chunk:
                        optimized_code += chunk["response"]
                        placeholder.code(optimized_code, language="python")
                        time.sleep(0.1)

            st.session_state.generated_code = optimized_code
            st.session_state.selected_optimization = None

        else:
            st.write(f"⚠ Error: Received status code {response.status_code}")

    except requests.exceptions.RequestException as e:
        st.write(f"⚠ Connection Error: {e}")
