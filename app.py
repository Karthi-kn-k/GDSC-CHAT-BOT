import streamlit as st
import requests
import json
import time
import random
import numpy as np
import speech_recognition as sr
from datetime import datetime
from langdetect import detect
import cv2
import pytesseract
from PIL import Image

# Set up Tesseract OCR path
pytesseract.pytesseract.tesseract_cmd = r"D:\tesseract\tesseract.exe"

# Initialize Streamlit Page Configuration
st.set_page_config(page_title="Coderzz.AI - Your AI Coding Assistant", layout="wide")

# --- Custom CSS for Styling ---
st.markdown(
    """
    <style>
    body {
        background-color: #1e1e2e;
        color: white;
    }
    .stButton button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        transition: background-color 0.3s ease;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stTextArea textarea {
        height: 68px;
    }
    .icon {
        font-size: 24px;
        margin-right: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar with Chat History
st.sidebar.title("💻 Coderzz.AI")
st.sidebar.write("Generate and debug code effortlessly!")

# --- State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "generated_code" not in st.session_state:
    st.session_state.generated_code = ""
if "selected_code_type" not in st.session_state:
    st.session_state.selected_code_type = None
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

# Display Chat History in Sidebar
st.sidebar.subheader("Chat History")
for message in reversed(st.session_state.chat_history[-10:]):
    st.sidebar.markdown(message)

# --- Speech Recognition ---
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Listening...")
        audio = recognizer.listen(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Could not understand the audio"
    except sr.RequestError:
        return "Error with the recognition service"

# --- Image Processing ---
def process_image(image):
    image = Image.open(image)
    text = pytesseract.image_to_string(image)
    return text

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

# Speech Button
if st.button("🎤 Speak Your Query"):
    recognized_text = recognize_speech()
    st.session_state.user_input = recognized_text
    st.rerun() # Force a rerun to update the text area

# Text Input
user_input = st.text_area("📝 Your Question:", value=st.session_state.user_input, key="user_input_widget")

# Image Upload & Processing
st.subheader("📷 Upload an Image to Extract Text")
image_file = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
if image_file:
    extracted_text = process_image(image_file)
    st.text_area("Extracted Text:", extracted_text)

# Document Upload & Processing
st.subheader("📄 Upload a Document for Analysis")
doc_file = st.file_uploader("Upload Document", type=["txt", "pdf"])
if doc_file:
    content = doc_file.read().decode("utf-8")
    st.text_area("Document Content:", content)

# --- Code Generation ---
if st.button("🚀 Generate Code") and user_input:
    try:
        st.session_state.generated_code = f"# Generated code for: {user_input}\n "
        st.code(st.session_state.generated_code, language="python")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.chat_history.append(f"You ({timestamp}): {user_input}")
        st.session_state.chat_history.append(f"Coderzz.AI ({timestamp}): {st.session_state.generated_code}")
    except Exception as e:
        st.error(f"Error generating code: {e}")

# --- Feedback System ---
if st.session_state.generated_code:
    st.write("Was this code helpful?")
    feedback = st.radio("Select feedback:", ("Yes", "No"))

    if st.button("📤 Submit Feedback"):
        if feedback == "yes":
            st.write("THANK YOU FOR YOUR FEEDBACK😊")
        if feedback == "No":
            st.write("What type of code do you need?")
            feedback_type = st.radio("Select type:", (
                "Basic code",
                "Structured code with functions",
                "Code with detailed comments",
                "Optimized code"
            ))
            if st.button("🔄 Optimize Code"):
                st.session_state.generated_code += f"\n# Optimized version: {feedback_type}"  # Simulated improvement
                st.code(st.session_state.generated_code, language="python")
