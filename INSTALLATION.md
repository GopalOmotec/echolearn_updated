# EchoLearn - Installation Guide

## Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/harshgupta447/echolearn.git
cd echolearn
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 5. Run the Application
```bash
# Main application
streamlit run echo.py

# Or the refactored version
streamlit run echo_refactored.py
```

## Requirements

- Python 3.8+
- OpenAI API key
- Microphone (for audio recording)
- Modern web browser

## Key Dependencies

- **streamlit**: Web application framework
- **openai**: AI processing
- **langchain**: LLM framework
- **PyMuPDF**: PDF processing
- **sounddevice**: Audio recording
- **SpeechRecognition**: Speech-to-text
- **librosa**: Audio analysis
- **plotly**: Visualizations
- **SQLAlchemy**: Database

## Troubleshooting

### Audio Issues
- Make sure microphone permissions are granted
- Check that sounddevice is properly installed
- Test with headphones if microphone feedback occurs

### API Issues
- Verify OpenAI API key is correct
- Check internet connection
- Ensure API quota is available

### Database Issues
- Delete `echolearn.db` to reset database
- Check file permissions for database creation

## Features

- 🎯 AI-powered question generation from PDFs
- 🎙️ Audio recording and speech-to-text
- 📊 Adaptive learning system
- 🧠 Selective mutism support
- 💯 Comprehensive answer evaluation
- 🔐 User authentication
- 📈 Progress tracking
- 🎨 Beautiful UI with Streamlit

## Support

For issues and questions, please visit the GitHub repository.
