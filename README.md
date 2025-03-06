# GDSC-CHAT-BOT
# Coderzz.AI - Your AI Coding Assistant

## Overview
Coderzz.AI is an AI-powered coding assistant that helps developers generate, debug, and analyze code efficiently. It supports multiple programming languages and features speech recognition, image-to-text conversion, and document analysis.

## Features
- Generate code snippets in Python, JavaScript, Java, and C++
- Speech-to-text functionality for hands-free coding
- Optical Character Recognition (OCR) to extract text from images
- Document analysis for text-based file inputs
- Interactive chat history to track previous queries
- Feedback system to refine generated code

## Installation
### Prerequisites
Ensure you have the following installed:
- Python 3.x
- Streamlit
- Requests
- SpeechRecognition
- OpenCV (cv2)
- pytesseract (Tesseract OCR)
- PIL (Pillow)
- numpy
- langdetect

### Setup
1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/coderzz-ai.git
   cd coderzz-ai
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```

## Usage
1. Launch the Streamlit web app.
2. Select a programming language or enter your query manually.
3. Use the speech recognition feature to input queries via voice.
4. Upload images or documents to extract text for further processing.
5. View, edit, and improve generated code based on feedback.

## File Structure
```
├── app.py             # Main Streamlit application file
├── requirements.txt   # List of required Python packages
├── README.md          # Project documentation
├── assets/            # Image and UI assets (if any)
├── modules/           # Additional processing modules (if needed)
```



