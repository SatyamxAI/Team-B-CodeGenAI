<<<<<<< HEAD
# Team-B-CodeGenAI
Central repository containing all team submissions and source code for the CodeGen AI project under the Infosys Virtual Internship.
=======
# ✨ Code Gen AI - ChatGPT-Style Code Companion

A feature-rich Streamlit frontend that provides a ChatGPT-like experience for code generation, explanation, and AI-powered assistance. Built with a stunning dark theme UI and packed with interactive features.

![Code Gen AI](https://img.shields.io/badge/Code%20Gen%20AI-v2.0-10a37f?style=for-the-badge)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)

---

## 🚀 Features Overview

### 🎨 **Modern ChatGPT-Inspired UI**
- **Dark Theme**: Beautiful dark mode interface with smooth animations
- **Floating Logo**: Animated hero section with glowing effects
- **Gradient Accents**: Green accent colors inspired by ChatGPT
- **Responsive Layout**: Optimized for various screen sizes
- **Smooth Animations**: Pulse, float, and glow keyframe animations

---

## 🤖 AI Model Integration

### Supported Models
| Model | Provider | Features |
|-------|----------|----------|
| `gpt-oss-120b` | Groq API | Fast inference, streaming |
| `llama3` | Ollama (Local) | Privacy-focused, offline |
| `deepseek-r1` | Ollama (Local) | Code-specialized |
| `deepseek-ocr:3b` | Ollama (Local) | Vision + Language |

### Chat Modes
- **💬 Chat**: General conversation mode
- **👨‍💻 Generate Code**: Code generation with best practices
- **📚 Explain Code**: Step-by-step code explanations

---

## 🎯 Core Features

### 💬 **Chat Management**
- **Multiple Conversations**: Create and manage multiple chat sessions
- **Chat History**: Persistent storage of all conversations
- **Rename Chats**: Custom titles for easy organization
- **Delete Chats**: Remove unwanted conversations
- **Search Chats**: Search by title or message content
  - 📌 Icon indicates title matches
  - 💬 Icon indicates content matches
- **Temporary Chat Mode**: Non-persistent conversations for privacy

### 🖼️ **Image Analysis**
- Upload images (PNG, JPG, JPEG, GIF, WebP)
- AI-powered image analysis using vision models
- Preview images before sending
- Works with `deepseek-ocr:3b` model

### 🎤 **Voice Input**
- **Audio Recording**: Record voice messages directly
- **Auto-Transcription**: Automatic speech-to-text using Google Speech API
- **Auto-Send**: Transcribed text is automatically sent to AI
- **Manual Control**: Re-transcribe or clear options available

---

## ⭐ Interactive Learning Features

### 💡 **Random Concept Explainer**
Learn technical concepts with AI-generated explanations!

**Difficulty Levels:**
- 🟢 Beginner
- 🟡 Intermediate  
- 🔴 Advanced

**Categories Covered:**
- Data Structures (Arrays, Linked Lists, Trees, Hashmaps)
- Algorithms (Sorting, Searching, Dynamic Programming)
- Web Development (HTTP, REST, GraphQL, CORS)
- CS Basics (OS, Memory, Processes, Threads)
- AI/ML (Neural Networks, Transformers, Gradient Descent)

**Output Includes:**
1. Simple Explanation (2-3 sentences)
2. Structured Explanation (detailed breakdown)
3. Real-World Analogy
4. Interview Question with answer

---

### ✍️ **Random Writing Generator**
Generate various types of written content with tone control!

**Tone Options:**
- 📋 Formal
- 😊 Friendly
- 😄 Humorous

**Content Types:**
- Professional emails
- Social media posts (LinkedIn, Twitter, Instagram)
- Documentation & API docs
- Resume bullet points
- Product descriptions
- Blog intros
- Error messages
- Developer bios

---

### 🔧 **Debug Practice (Bug Generator)**
Practice debugging with random buggy code snippets!

**Languages Supported:**
- 🐍 Python
- 🟨 JavaScript
- ☕ Java

**Bug Types Covered:**
| Bug Type | Description |
|----------|-------------|
| Off-by-one errors | Loop index mistakes |
| Mutable defaults | Python's mutable argument trap |
| Async/Await issues | Missing await keywords |
| Variable hoisting | var vs let in closures |
| Infinite loops | Binary search bugs |
| Null pointer | Missing null checks |
| String comparison | `is` vs `==` in Python |
| Type coercion | `==` vs `===` in JavaScript |
| Scope issues | Global vs local variables |
| Index out of bounds | Array access errors |

**Features:**
- 🔍 View buggy code
- 👀 Show Answer button (reveals fix)
- 📝 Explanation of the bug
- 🛡️ Prevention tips
- 🚀 Send to AI for detailed analysis

---

## 🔘 Message Action Buttons

Each AI response includes interactive action buttons:

### 🔊 **Read Aloud (TTS)**
- Text-to-speech using browser's Web Speech API
- Cleans markdown formatting for natural speech
- Removes code blocks, bold text, headers
- Toggle button: "🔊 Read" ↔ "⏹️ Stop"
- Animated glow effect when playing

### 🔄 **Redo (Regenerate)**
- Regenerate any AI response
- Uses the original user prompt
- Streaming output for new response
- Replaces old response automatically

### 📋 **Copy to Clipboard**
- Expandable copy panel
- Pre-selected text area for easy Ctrl+C
- 💾 Download as `.txt` file option
- Auto-focus and select functionality

---

## 🎛️ Sidebar Controls

### Settings Panel
- **Model Selector**: Choose AI model
- **Mode Selector**: Chat/Generate Code/Explain Code
- **Your Name**: Personalized greeting
- **System Prompt**: Customize AI behavior

### Advanced Options
- Custom system prompts
- Display name customization

### Quick Actions
- ➕ New Chat (with optional title)
- 🗑️ Clear Chat
- 🔍 Search Chats
- ✏️ Rename Chat
- 🗑️ Delete Chat

---

## 🖥️ Input Interface

### Linear Input Layout
```
[     Text Input     ] [🎤] [📷]
```
- **Text Input**: Main chat input (left, largest)
- **Voice Button**: Toggle voice recording (middle)
- **Image Button**: Toggle image upload (right)

### Input Features
- Placeholder text changes based on context
- Auto-send for voice transcriptions
- Image preview before sending
- Remove attachment option

---

## 🎨 UI Components

### Hero Welcome Card
- Animated glowing background
- Floating logo with pulse effect
- Personalized greeting
- Feature badges showing:
  - Current model
  - Current mode
  - Streaming status
  - Vision capability

### Suggestion Cards (4 Interactive Cards)
| Card | Icon | Function |
|------|------|----------|
| Random Concept | 💡 | Learn tech concepts by difficulty |
| Writing Help | ✍️ | Generate content with tone control |
| Debug Practice | 🔧 | Practice finding bugs in code |
| Image Analysis | 🖼️ | Analyze images with AI |

### Chat Bubbles
- User avatar: 👤
- Assistant avatar: ✨
- Clean message formatting
- Code block syntax highlighting
- Image display support

---

## 🔧 Technical Stack

### Dependencies
```
streamlit
pillow
requests
openai
SpeechRecognition
```

### APIs Used
- **Groq API**: For `gpt-oss-120b` model
- **Ollama API**: For local models (llama3, deepseek-r1, qwen3-vl)
- **Google Speech API**: For voice transcription
- **Web Speech API**: For text-to-speech (browser)

### Session State Management
All data stored in `st.session_state`:
- Chat counter and history
- Current chat selection
- UI toggles (image, voice panels)
- Feature states (concept, writing, bug)
- TTS playback state
- Regenerate index

---

## 📁 Project Structure

The project follows a **modular architecture** for maintainability:

```
Infosys/
├── run.py                        # Entry point for modular version
├── FrontEnd.py                   # Legacy monolithic version (2200+ lines)
├── requirements.txt              # Python dependencies
├── README.md                     # This documentation
│
├── code_gen_ai/                  # 📦 Modular Package
│   ├── __init__.py               # Package initialization
│   ├── app.py                    # Main application logic
│   ├── config.py                 # Constants, API config, model options
│   ├── data.py                   # Concepts, writing tasks, buggy code data
│   ├── styles.py                 # CSS styling (dark theme)
│   ├── state.py                  # Session state management
│   ├── backend.py                # API integrations (Groq, Ollama)
│   ├── utils.py                  # Helper functions (TTS, transcription)
│   │
│   └── components/               # 🎨 UI Components
│       ├── __init__.py           # Component exports
│       ├── chat.py               # Chat history rendering
│       ├── sidebar.py            # Sidebar UI & chat list
│       ├── empty_state.py        # Hero card & suggestion cards
│       └── input.py              # Text, voice, image input
│
└── __pycache__/                  # Python cache files
```

### Module Descriptions

| Module | Lines | Purpose |
|--------|-------|---------|
| `config.py` | ~40 | API URLs, model options, regex patterns |
| `data.py` | ~250 | Learning data (concepts, tasks, bugs) |
| `styles.py` | ~300 | CSS styling for dark theme |
| `state.py` | ~120 | Session state init & management |
| `backend.py` | ~200 | Groq & Ollama API integration |
| `utils.py` | ~130 | TTS, image encoding, transcription |
| `components/chat.py` | ~110 | Message rendering with actions |
| `components/sidebar.py` | ~170 | Sidebar layout & chat list |
| `components/empty_state.py` | ~280 | Welcome screen & feature panels |
| `components/input.py` | ~200 | Input area with voice/image |
| `app.py` | ~180 | Main entry point |

---

## 🚀 Getting Started

### Installation
```bash
# Navigate to project directory
cd Infosys

# Install dependencies
pip install -r requirements.txt

# Run the MODULAR version (recommended)
streamlit run run.py

# Or run the legacy monolithic version
streamlit run FrontEnd.py
```

### Configuration

#### Groq API (for gpt-oss-120b)
Set your API key:
```bash
# Environment variable
export GROQ_API_KEY="your-api-key"

# Or in Streamlit secrets
# .streamlit/secrets.toml
GROQ_API_KEY = "your-api-key"
```

#### Ollama (for local models)
```bash
# Install Ollama
curl https://ollama.ai/install.sh | sh

# Pull models
ollama pull llama3
ollama pull deepseek-r1
ollama pull deepseek-ocr:3b

# Start Ollama server
ollama serve
```

---

## 🎯 Feature Highlights

| Feature | Description | Status |
|---------|-------------|--------|
| Multi-model support | 4 AI models | ✅ |
| Streaming responses | Real-time output | ✅ |
| Image analysis | Vision model support | ✅ |
| Voice input | Speech-to-text | ✅ |
| Chat management | CRUD operations | ✅ |
| Concept explainer | Random tech topics | ✅ |
| Writing generator | Tone-controlled content | ✅ |
| Bug debugger | Practice debugging | ✅ |
| TTS (Read aloud) | Web Speech API | ✅ |
| Regenerate response | Redo AI responses | ✅ |
| Copy to clipboard | Easy text copying | ✅ |
| Download responses | Save as .txt | ✅ |
| Dark theme | ChatGPT-inspired | ✅ |
| Animations | Smooth UI effects | ✅ |

---

## 🔮 Future Enhancements

- [ ] Export chat history as PDF/Markdown
- [ ] Multiple language support
- [ ] Custom themes
- [ ] Plugin system
- [ ] Code execution sandbox
- [ ] File upload for code review
- [ ] Collaborative features

---

## 📝 License

This project is for educational and demonstration purposes.

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest features
- Submit pull requests

---

<div align="center">

**Made with ❤️ using Streamlit**

✨ **Code Gen AI** - Your AI-Powered Coding Companion ✨

</div>
>>>>>>> d72e97e (Deepesh V Project)
