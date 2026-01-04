# """Streamlit ChatGPT-style frontend with image and voice input support."""
# """
# The Python script is a Streamlit frontend for a ChatGPT-style chat interface with support for image
# and voice input, allowing users to interact with an AI assistant for various tasks.

# :param title: The `title` parameter in the code is used to specify the title of a chat conversation.
# It can be provided when creating a new chat or when updating the title of an existing chat. The
# title helps identify and differentiate between different chat conversations, making it easier for
# users to manage and navigate through their
# :type title: Optional[str]
# :return: The code provided is a Streamlit frontend application that simulates a chat interface with
# ChatGPT-style functionality. It includes features such as image and voice input support. The code
# defines functions for creating and managing chat conversations, rendering chat history, handling
# user prompts, injecting custom CSS for styling, and interacting with the backend to generate
# responses based on user input.
# """

import base64
import io
import json
import re
import random
from typing import Any, Dict, List, Optional

import streamlit as st
from PIL import Image
import os
import requests
from streamlit.errors import StreamlitSecretNotFoundError

# If you prefer to hardcode an API key directly in this file (not recommended for production),
# put it here as a string. Leave empty to use environment or Streamlit secrets.
#"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" = ""
GROQ_BASE_URL_DIRECT = ""
GEMINI_API_KEY_DIRECT = ""
OLLAMA_API_URL = "http://localhost:11434/api/generate"

# Audio processing imports
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False


CHAT_MODES = ["Chat", "Generate Code", "Explain Code"]
MODEL_OPTIONS = ["gpt-oss-120b", "llama3", "deepseek-r1", "deepseek-ocr:3b"]
DEFAULT_SYSTEM_PROMPT = "You are ChatGPT, a large language model trained by OpenAI. You are helpful, creative, clever, and very friendly."
CODE_BLOCK_PATTERN = re.compile(r"```(?P<lang>[\w+\-]*)\n(?P<code>.*?)```", re.DOTALL)
OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"

# Random Concept Explainer Data
CONCEPTS_BY_DIFFICULTY = {
    "Beginner": [
        {"category": "Data Structures", "topic": "Arrays vs Linked Lists"},
        {"category": "Algorithms", "topic": "Linear Search"},
        {"category": "Web Dev", "topic": "What is HTTP?"},
        {"category": "CS Basics", "topic": "What is a Variable?"},
        {"category": "AI", "topic": "What is Machine Learning?"},
        {"category": "Data Structures", "topic": "Stack and Queue basics"},
        {"category": "Algorithms", "topic": "Bubble Sort"},
        {"category": "Web Dev", "topic": "HTML vs CSS vs JavaScript"},
        {"category": "CS Basics", "topic": "What is an Operating System?"},
        {"category": "AI", "topic": "Supervised vs Unsupervised Learning"},
    ],
    "Intermediate": [
        {"category": "Data Structures", "topic": "Hashmap collision resolution"},
        {"category": "Algorithms", "topic": "Two Pointers technique"},
        {"category": "Web Dev", "topic": "REST vs GraphQL"},
        {"category": "CS Basics", "topic": "Process vs Thread"},
        {"category": "AI", "topic": "Gradient Descent optimization"},
        {"category": "Data Structures", "topic": "Binary Search Trees"},
        {"category": "Algorithms", "topic": "Merge Sort vs Quick Sort"},
        {"category": "Web Dev", "topic": "CORS and how it works"},
        {"category": "CS Basics", "topic": "Virtual Memory"},
        {"category": "AI", "topic": "Overfitting and Regularization"},
    ],
    "Advanced": [
        {"category": "Data Structures", "topic": "Red-Black Trees balancing"},
        {"category": "Algorithms", "topic": "Dynamic Programming - State compression"},
        {"category": "Web Dev", "topic": "Microservices architecture patterns"},
        {"category": "CS Basics", "topic": "Deadlock prevention algorithms"},
        {"category": "AI", "topic": "Self-attention in Transformers"},
        {"category": "Data Structures", "topic": "B+ Trees for databases"},
        {"category": "Algorithms", "topic": "A* pathfinding algorithm"},
        {"category": "Web Dev", "topic": "Event-driven architecture"},
        {"category": "CS Basics", "topic": "Memory management and Garbage Collection"},
        {"category": "AI", "topic": "Reinforcement Learning - Q-Learning"},
    ]
}

# Random Writing Tasks Data
WRITING_TASKS_BY_TONE = {
    "Formal": [
        {"type": "Email", "prompt": "Write a professional apology email for missing a meeting"},
        {"type": "Email", "prompt": "Write a formal request for a deadline extension"},
        {"type": "Documentation", "prompt": "Write API documentation for a user authentication endpoint"},
        {"type": "Resume", "prompt": "Write a resume bullet point for leading a software migration project"},
        {"type": "Email", "prompt": "Write a professional introduction email to a new client"},
        {"type": "Report", "prompt": "Write an executive summary for a quarterly performance report"},
        {"type": "Proposal", "prompt": "Write a project proposal introduction for a new mobile app"},
    ],
    "Friendly": [
        {"type": "Email", "prompt": "Write a friendly follow-up email after a job interview"},
        {"type": "Social Media", "prompt": "Write an engaging LinkedIn post about starting a new job"},
        {"type": "Message", "prompt": "Write a warm welcome message for new team members"},
        {"type": "Blog", "prompt": "Write a casual blog intro about learning to code"},
        {"type": "Social Media", "prompt": "Write an Instagram caption for a team building event"},
        {"type": "Email", "prompt": "Write a friendly reminder email for an upcoming team lunch"},
        {"type": "Newsletter", "prompt": "Write a friendly company newsletter opening paragraph"},
    ],
    "Humorous": [
        {"type": "Social Media", "prompt": "Write a funny tweet about debugging code at 3 AM"},
        {"type": "Product", "prompt": "Write a humorous product description for a rubber duck debugger"},
        {"type": "Email", "prompt": "Write a playfully sarcastic out-of-office auto-reply"},
        {"type": "Story", "prompt": "Write a short funny story about a programmer's first day at work"},
        {"type": "Social Media", "prompt": "Write a witty LinkedIn post about surviving Monday meetings"},
        {"type": "Caption", "prompt": "Write a humorous error message for a 404 page"},
        {"type": "Bio", "prompt": "Write a funny developer bio for a GitHub profile"},
    ]
}

# Random Bug Generator Data
BUGGY_CODE_SNIPPETS = [
    {
        "language": "python",
        "title": "Off-by-one error in loop",
        "buggy_code": '''def sum_first_n(arr, n):
    """Sum the first n elements of arr"""
    total = 0
    for i in range(1, n + 1):  
        total += arr[i]
    return total

''',
        "fixed_code": '''def sum_first_n(arr, n):
    """Sum the first n elements of arr"""
    total = 0
    for i in range(n):  # Fixed: start from 0
        total += arr[i]
    return total''',
        "explanation": "The loop started at index 1 instead of 0, causing it to skip the first element and potentially access an out-of-bounds index.",
        "prevention": "Always remember Python uses 0-based indexing. Use range(n) for first n elements."
    },
    {
        "language": "python",
        "title": "Mutable default argument",
        "buggy_code": '''def add_item(item, items=[]):  
    items.append(item)
    return items

# Try calling:
# print(add_item("a"))  # ['a']
# print(add_item("b"))  # Expect ['b'], but get ['a', 'b']!''',
        "fixed_code": '''def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items''',
        "explanation": "Mutable default arguments (like lists) are created once at function definition, not each call. All calls share the same list!",
        "prevention": "Never use mutable objects (lists, dicts) as default arguments. Use None and create inside the function."
    },
    {
        "language": "javascript",
        "title": "Async/Await missing",
        "buggy_code": '''async function fetchUserData(userId) {
    const response = fetch(`/api/users/${userId}`);  
    const data = response.json();
    return data;
}

''',
        "fixed_code": '''async function fetchUserData(userId) {
    const response = await fetch(`/api/users/${userId}`);
    const data = await response.json();
    return data;
}''',
        "explanation": "Missing 'await' keywords cause the function to return Promises instead of waiting for the actual values.",
        "prevention": "Always use 'await' when calling async functions or Promise-returning methods like fetch()."
    },
    {
        "language": "javascript",
        "title": "Variable hoisting issue",
        "buggy_code": '''function printNumbers() {
    for (var i = 0; i < 3; i++) {
        setTimeout(function() {
            console.log(i);  
        }, 100);
    }
}
''',
        "fixed_code": '''function printNumbers() {
    for (let i = 0; i < 3; i++) {
        setTimeout(function() {
            console.log(i);  // Fixed: prints 0, 1, 2
        }, 100);
    }
}''',
        "explanation": "'var' is function-scoped, so all callbacks share the same 'i'. By the time they run, the loop has finished and i=3.",
        "prevention": "Use 'let' instead of 'var' for block-scoped variables, especially in loops with closures."
    },
    {
        "language": "python",
        "title": "Infinite loop",
        "buggy_code": '''def find_target(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid  
        else:
            right = mid  
    return -1''',
        "fixed_code": '''def find_target(arr, target):
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1  # Fixed
        else:
            right = mid - 1  # Fixed
    return -1''',
        "explanation": "Without +1/-1, the search space never shrinks when mid equals left or right, causing an infinite loop.",
        "prevention": "In binary search, always shrink the search space by excluding mid: left = mid + 1 or right = mid - 1."
    },
    {
        "language": "java",
        "title": "Null pointer exception",
        "buggy_code": '''public String getUserName(User user) {
    return user.getName().toUpperCase();  
}

''',
        "fixed_code": '''public String getUserName(User user) {
    if (user == null || user.getName() == null) {
        return "Unknown";
    }
    return user.getName().toUpperCase();
}''',
        "explanation": "Calling methods on null references throws NullPointerException. Both the user object and getName() result could be null.",
        "prevention": "Always validate inputs and check for null before calling methods. Consider using Optional in Java 8+."
    },
    {
        "language": "python",
        "title": "String comparison bug",
        "buggy_code": '''def check_password(input_pwd, stored_pwd):
    if input_pwd is stored_pwd:  
        return True
    return False

''',
        "fixed_code": '''def check_password(input_pwd, stored_pwd):
    if input_pwd == stored_pwd:  # Fixed: use == for value comparison
        return True
    return False''',
        "explanation": "'is' checks object identity (same memory location), '==' checks value equality. Different string objects with same content fail 'is' check.",
        "prevention": "Use '==' for comparing values, 'is' only for None checks or intentional identity comparison."
    },
    {
        "language": "javascript",
        "title": "Type coercion bug",
        "buggy_code": '''function isAdult(age) {
    if (age == "18") {  
        return true;
    }
    return age > 18;
}

''',
        "fixed_code": '''function isAdult(age) {
    const numAge = Number(age);
    if (numAge >= 18) {
        return true;
    }
    return false;
}''',
        "explanation": "Using == allows type coercion which can cause unexpected behavior. String/number comparisons with > are unpredictable.",
        "prevention": "Always use === for comparisons and explicitly convert types. Consider TypeScript for type safety."
    },
    {
        "language": "python",
        "title": "Wrong variable scope",
        "buggy_code": '''total = 0

def add_to_total(value):
    total = total + value  
    return total

add_to_total(5)''',
        "fixed_code": '''total = 0

def add_to_total(value):
    global total  # Fixed: declare global
    total = total + value
    return total

# Or better - avoid global state:
def add_to_total(current_total, value):
    return current_total + value''',
        "explanation": "Assignment inside a function creates a local variable. Python sees 'total = ...' and treats 'total' as local, but it's read before assignment.",
        "prevention": "Avoid modifying global variables. Pass values as parameters and return results. Use 'global' keyword only when necessary."
    },
    {
        "language": "java",
        "title": "Array index out of bounds",
        "buggy_code": '''public int getLastElement(int[] arr) {
    return arr[arr.length];  
}

''',
        "fixed_code": '''public int getLastElement(int[] arr) {
    if (arr == null || arr.length == 0) {
        throw new IllegalArgumentException("Array is empty");
    }
    return arr[arr.length - 1];  // Fixed: length - 1
}''',
        "explanation": "Array indices go from 0 to length-1. Accessing arr[length] is always out of bounds.",
        "prevention": "Remember: last valid index = length - 1. Add bounds checking and handle empty arrays."
    }
]


def get_secret_or_env(key: str) -> Optional[str]:
    """Fetch a secret from environment first, then Streamlit secrets (safely)."""
    env_val = os.environ.get(key)
    if env_val:
        return env_val
    try:
        if hasattr(st, "secrets"):
            return st.secrets.get(key)
    except StreamlitSecretNotFoundError:
        return None
    except Exception:
        return None
    return None


def create_persistent_chat(title: Optional[str] = None) -> str:
    """Create a saved conversation and return its identifier."""
    chat_id = str(st.session_state.chat_counter)
    st.session_state.chat_counter += 1
    default_title = title or f"New chat {chat_id}"
    st.session_state.chats[chat_id] = {"title": default_title, "messages": []}
    return chat_id


def ensure_current_chat() -> None:
    """Make sure we have at least one persistent chat selected."""
    if not st.session_state.chats:
        chat_id = create_persistent_chat()
        st.session_state.current_chat_id = chat_id
    elif st.session_state.current_chat_id not in st.session_state.chats:
        st.session_state.current_chat_id = next(iter(st.session_state.chats.keys()))


def init_session_state() -> None:
    """Bootstrap all keys required by the UI."""
    st.session_state.setdefault("chat_counter", 1)
    st.session_state.setdefault("chats", {})
    st.session_state.setdefault("current_chat_id", "")
    st.session_state.setdefault("is_temp_chat", False)
    st.session_state.setdefault("temp_messages", [])
    st.session_state.setdefault("display_name", "User")
    st.session_state.setdefault("mode_select", CHAT_MODES[0])
    st.session_state.setdefault("model_select", MODEL_OPTIONS[0])
    st.session_state.setdefault("system_prompt_area", DEFAULT_SYSTEM_PROMPT)
    st.session_state.setdefault("show_search_box", False)
    st.session_state.setdefault("chat_search", "")
    st.session_state.setdefault("sidebar_notice", "")
    st.session_state.setdefault("uploaded_image", None)
    st.session_state.setdefault("voice_text", "")
    st.session_state.setdefault("show_image_upload", False)
    st.session_state.setdefault("show_voice_input", False)
    st.session_state.setdefault("new_chat_name", "")
    st.session_state.setdefault("show_rename_input", False)
    st.session_state.setdefault("rename_chat_title", "")
    st.session_state.setdefault("auto_send_voice", False)
    # Feature toggles for enhanced buttons
    st.session_state.setdefault("concept_difficulty", "Intermediate")
    st.session_state.setdefault("writing_tone", "Formal")
    st.session_state.setdefault("show_concept_explainer", False)
    st.session_state.setdefault("show_writing_generator", False)
    st.session_state.setdefault("show_bug_debugger", False)
    st.session_state.setdefault("current_concept", None)
    st.session_state.setdefault("current_writing_task", None)
    st.session_state.setdefault("current_bug", None)
    st.session_state.setdefault("auto_send_prompt", False)
    st.session_state.setdefault("pending_prompt", "")
    st.session_state.setdefault("regenerate_index", None)
    st.session_state.setdefault("tts_playing", False)
    st.session_state.setdefault("tts_message_index", None)

    ensure_current_chat()


def inject_custom_css() -> None:
    """Inject Code Gen AI-inspired dark theme styling."""
    st.markdown(
        """
        <style>
        :root { color-scheme: dark; }
        body, .stApp, .block-container {
            background-color: #212121;
            color: #ececec;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 6rem;
            max-width: 800px;
        }
        div[data-testid="stSidebar"] {
            background-color: #171717;
            border-right: 1px solid #2f2f2f;
        }
        div[data-testid="stSidebar"] * {
            color: #ececec !important;
        }
        .sidebar-logo {
            font-size: 1.1rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
            padding: 0.5rem;
        }
        .sidebar-section-title {
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 0.12em;
            color: #8e8e8e;
            margin: 1.5rem 0 0.5rem 0;
            font-weight: 500;
        }
        div[data-testid="stChatMessage"] {
            margin-bottom: 0;
            padding: 1.5rem 0;
        }
        .chat-bubble {
            width: 100%;
            line-height: 1.6;
        }
        .assistant-bubble { 
            background: transparent;
        }
        .user-bubble { 
            background: transparent;
        }
        .hero-card {
            text-align: center;
            margin: 4rem auto 2rem auto;
            padding: 2.5rem;
            max-width: 700px;
            position: relative;
        }
        .hero-glow {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(16, 163, 127, 0.15) 0%, transparent 70%);
            border-radius: 50%;
            pointer-events: none;
            animation: glow-pulse 4s ease-in-out infinite;
        }
        @keyframes glow-pulse {
            0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
            50% { opacity: 1; transform: translate(-50%, -50%) scale(1.1); }
        }
        .hero-logo {
            width: 80px;
            height: 80px;
            border-radius: 24px;
            background: linear-gradient(135deg, #10a37f 0%, #0d8c6d 50%, #076d54 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 1.5rem auto;
            font-size: 2.2rem;
            box-shadow: 0 20px 40px rgba(16, 163, 127, 0.3), 0 0 60px rgba(16, 163, 127, 0.1);
            animation: float 3s ease-in-out infinite;
            position: relative;
            z-index: 1;
        }
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-8px); }
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.75rem;
            letter-spacing: -0.02em;
        }
        .hero-subtitle { 
            color: #8e8e8e; 
            font-size: 1.1rem;
            margin-bottom: 2.5rem;
            line-height: 1.6;
        }
        .hero-badges {
            display: flex;
            justify-content: center;
            gap: 0.75rem;
            margin-bottom: 2rem;
            flex-wrap: wrap;
        }
        .hero-badge {
            background: rgba(16, 163, 127, 0.1);
            border: 1px solid rgba(16, 163, 127, 0.3);
            border-radius: 20px;
            padding: 0.4rem 0.9rem;
            font-size: 0.75rem;
            color: #10a37f;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .suggestion-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 1rem;
            max-width: 600px;
            margin: 0 auto;
        }
        .suggestion-card {
            background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%);
            border: 1px solid #3a3a3a;
            border-radius: 16px;
            padding: 1.25rem;
            text-align: left;
            font-size: 0.9rem;
            color: #ececec;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .suggestion-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, rgba(16, 163, 127, 0.1) 0%, transparent 100%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        .suggestion-card:hover {
            border-color: #10a37f;
            transform: translateY(-4px);
            box-shadow: 0 12px 24px rgba(0, 0, 0, 0.3), 0 0 0 1px rgba(16, 163, 127, 0.2);
        }
        .suggestion-card:hover::before {
            opacity: 1;
        }
        .suggestion-icon {
            font-size: 1.5rem;
            margin-bottom: 0.75rem;
            display: block;
        }
        .suggestion-title {
            font-weight: 600;
            margin-bottom: 0.3rem;
            color: #fff;
        }
        .suggestion-desc {
            font-size: 0.8rem;
            color: #8e8e8e;
            line-height: 1.4;
        }
        div[data-testid="stChatInput"] > div {
            border: 1px solid #424242;
            border-radius: 24px;
            background: #2f2f2f;
            padding: 0.25rem 0.5rem;
        }
        div[data-testid="stChatInput"] textarea {
            background: transparent !important;
            color: #ececec !important;
        }
        div[data-testid="stSidebar"] button {
            border-radius: 8px;
            border: 1px solid #424242;
            background: #2f2f2f;
            transition: all 0.2s;
        }
        div[data-testid="stSidebar"] button:hover {
            background: #424242;
        }
        .input-toolbar {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 0.5rem;
            padding: 0 0.5rem;
        }
        .toolbar-btn {
            background: #2f2f2f;
            border: 1px solid #424242;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            color: #ececec;
            cursor: pointer;
            font-size: 0.85rem;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }
        .toolbar-btn:hover {
            background: #424242;
        }
        .toolbar-btn.active {
            background: #10a37f;
            border-color: #10a37f;
        }
        .image-preview {
            max-width: 300px;
            border-radius: 12px;
            margin: 0.5rem 0;
            border: 1px solid #424242;
        }
        .voice-status {
            background: #2f2f2f;
            border: 1px solid #424242;
            border-radius: 12px;
            padding: 1rem;
            margin: 0.5rem 0;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .voice-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #10a37f;
            animation: pulse 1.5s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.5; transform: scale(1.1); }
        }
        .model-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            background: #2f2f2f;
            border: 1px solid #424242;
            border-radius: 6px;
            padding: 0.25rem 0.6rem;
            font-size: 0.75rem;
            color: #8e8e8e;
        }
        .attachment-preview {
            background: #2f2f2f;
            border: 1px solid #424242;
            border-radius: 12px;
            padding: 0.75rem;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .attachment-preview img {
            width: 60px;
            height: 60px;
            object-fit: cover;
            border-radius: 8px;
        }
        .attachment-info {
            flex: 1;
        }
        .attachment-name {
            font-size: 0.85rem;
            color: #ececec;
        }
        .attachment-size {
            font-size: 0.75rem;
            color: #8e8e8e;
        }
        .remove-attachment {
            color: #8e8e8e;
            cursor: pointer;
            font-size: 1.2rem;
        }
        .message-actions {
            display: flex;
            gap: 0.5rem;
            margin-top: 0.75rem;
            opacity: 0.7;
            transition: opacity 0.2s ease;
        }
        .message-actions:hover {
            opacity: 1;
        }
        .action-btn {
            background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%);
            border: 1px solid #3a3a3a;
            border-radius: 20px;
            padding: 0.35rem 0.75rem;
            color: #a0a0a0;
            font-size: 0.75rem;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 0.35rem;
            transition: all 0.2s ease;
        }
        .action-btn:hover {
            background: linear-gradient(145deg, #3a3a3a 0%, #2f2f2f 100%);
            border-color: #10a37f;
            color: #10a37f;
            transform: translateY(-1px);
        }
        .action-btn.playing {
            background: linear-gradient(145deg, #10a37f 0%, #0d8c6d 100%);
            border-color: #10a37f;
            color: #fff;
            animation: pulse-glow 1.5s infinite;
        }
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 0 5px rgba(16, 163, 127, 0.3); }
            50% { box-shadow: 0 0 15px rgba(16, 163, 127, 0.6); }
        }
        .action-btn .icon {
            font-size: 0.85rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_sidebar_notice(message: str) -> None:
    """Store a short notice message for sidebar alerts."""
    st.session_state.sidebar_notice = message


def get_active_messages() -> List[Dict[str, Any]]:
    """Return the list that represents the active conversation."""
    if st.session_state.is_temp_chat:
        return st.session_state.temp_messages
    return st.session_state.chats[st.session_state.current_chat_id]["messages"]


def start_tts(text: str, message_index: int) -> None:
    """Start text-to-speech for the given text using browser's Web Speech API."""
    # Clean the text for TTS (remove markdown, code blocks, etc.)
    clean_text = re.sub(r'```[\s\S]*?```', 'code block omitted', text)
    clean_text = re.sub(r'`[^`]+`', '', clean_text)
    clean_text = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_text)
    clean_text = re.sub(r'\*([^*]+)\*', r'\1', clean_text)
    clean_text = re.sub(r'#{1,6}\s*', '', clean_text)
    clean_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', clean_text)
    clean_text = clean_text.strip()
    
    st.session_state.tts_playing = True
    st.session_state.tts_message_index = message_index
    st.session_state.tts_text = clean_text
    
    # Use JavaScript Web Speech API for TTS
    js_code = f'''
    <script>
        const utterance = new SpeechSynthesisUtterance(`{clean_text.replace('`', '').replace('"', '\\"').replace("'", "\\'")[:2000]}`);
        utterance.rate = 1.0;
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        
        // Try to use a good voice
        const voices = speechSynthesis.getVoices();
        const preferredVoice = voices.find(v => v.name.includes('Google') || v.name.includes('Microsoft'));
        if (preferredVoice) utterance.voice = preferredVoice;
        
        speechSynthesis.speak(utterance);
    </script>
    '''
    st.components.v1.html(js_code, height=0)


def stop_tts() -> None:
    """Stop text-to-speech playback."""
    st.session_state.tts_playing = False
    st.session_state.tts_message_index = None
    
    # Use JavaScript to stop speech
    js_code = '''
    <script>
        speechSynthesis.cancel();
    </script>
    '''
    st.components.v1.html(js_code, height=0)


def regenerate_response(messages: List[Dict[str, Any]], index: int, mode: str, system_prompt: str, model: str) -> None:
    """Regenerate the assistant response at the given index."""
    if index <= 0 or index >= len(messages):
        return
    
    # Find the user message before this assistant message
    user_msg_index = index - 1
    if messages[user_msg_index].get("role") != "user":
        return
    
    user_prompt = messages[user_msg_index].get("content", "")
    user_image = messages[user_msg_index].get("image")
    
    # Remove the old assistant message
    messages.pop(index)
    
    # Generate new response (this will be handled in main loop)
    st.session_state.regenerate_prompt = user_prompt
    st.session_state.regenerate_image = user_image


def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string."""
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


def transcribe_audio(audio_bytes: bytes) -> str:
    """Transcribe audio to text using speech recognition."""
    if not SPEECH_RECOGNITION_AVAILABLE:
        return "[Speech recognition not available. Install: pip install SpeechRecognition]"
    
    recognizer = sr.Recognizer()
    
    try:
        # Convert audio bytes to AudioFile
        audio_file = io.BytesIO(audio_bytes)
        with sr.AudioFile(audio_file) as source:
            audio_data = recognizer.record(source)
        
        # Use Google's free speech recognition
        text = recognizer.recognize_google(audio_data)
        return text
    except sr.UnknownValueError:
        return "[Could not understand audio]"
    except sr.RequestError as e:
        return f"[Speech recognition error: {e}]"
    except Exception as e:
        return f"[Audio processing error: {e}]"


def stream_generate(model: str, prompt: str, image: Optional[Image.Image] = None):
    """Stream generate response from Ollama API as a generator."""
    headers = {"Content-Type": "application/json"}
    
    # Use chat API for models like deepseek-ocr:3b
    if model in ["deepseek-ocr:3b"]:
        # Build message with images if provided
        message = {
            "role": "user",
            "content": prompt
        }
        
        if image is not None:
            encoded_image = image_to_base64(image)
            message["images"] = [encoded_image]
        
        payload = {
            "model": model,
            "messages": [message],
            "stream": True
        }
        
        try:
            response = requests.post(
                OLLAMA_CHAT_URL,
                headers=headers,
                json=payload,
                stream=True,
                timeout=120
            )
            response.raise_for_status()
            
            # Stream and yield only the assistant content
            for line in response.iter_lines():
                if not line:
                    continue
                
                try:
                    data = json.loads(line.decode("utf-8"))
                except json.JSONDecodeError:
                    continue
                
                # Extract content from message
                if "message" in data and "content" in data["message"]:
                    content = data["message"]["content"]
                    if content:
                        yield content
                
                # Stop when done
                if data.get("done"):
                    break
                
        except requests.exceptions.RequestException as e:
            yield f"[Error connecting to Ollama: {e}. Make sure Ollama is running locally.]"
        except Exception as e:
            yield f"[Ollama API error: {e}]"
    else:
        # Use /api/generate for other models (llama3, deepseek-r1)
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }

        if image is not None:
            encoded_image = image_to_base64(image)
            payload["images"] = [encoded_image]

        try:
            with requests.post(OLLAMA_API_URL, headers=headers, json=payload, stream=True, timeout=60) as resp:
                resp.raise_for_status()
                
                for raw_line in resp.iter_lines(decode_unicode=True):
                    if not raw_line:
                        continue
                    
                    line = raw_line.strip()
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    
                    chunk_text = None
                    if "message" in obj and isinstance(obj["message"], dict):
                        chunk_text = obj["message"].get("content")
                    elif "response" in obj:
                        chunk_text = obj.get("response")
                    
                    if chunk_text:
                        yield chunk_text
                    
                    if obj.get("done") is True:
                        break
        except requests.exceptions.RequestException as e:
            yield f"[Error connecting to Ollama: {e}. Make sure Ollama is running locally.]"
        except Exception as e:
            yield f"[Ollama API error: {e}]"


def parse_and_render_segments(content: str) -> None:
    """Render Markdown text mixed with fenced code blocks."""
    start = 0
    for match in CODE_BLOCK_PATTERN.finditer(content):
        text_chunk = content[start : match.start()].strip()
        if text_chunk:
            st.markdown(text_chunk)

        language = match.group("lang") or "text"
        st.code(match.group("code"), language=language.strip())
        start = match.end()

    tail = content[start:].strip()
    if tail:
        st.markdown(tail)


def render_chat_history(messages: List[Dict[str, Any]]) -> None:
    """Loop through session messages and display them with avatars and bubbles."""
    for idx, message in enumerate(messages):
        role = message.get("role", "assistant")
        avatar = "👤" if role == "user" else "✨"
        
        # Create unique key suffix using index and content hash
        content_hash = hash(message.get("content", ""))
        unique_key = f"{idx}_{content_hash}_{role}"
        
        with st.chat_message(role, avatar=avatar):
            # Show image if present in message
            if "image" in message and message["image"]:
                st.image(message["image"], width=300)
            
            st.markdown(f"<div class='chat-bubble'>", unsafe_allow_html=True)
            parse_and_render_segments(message.get("content", ""))
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Add action buttons for assistant messages
            if role == "assistant" and message.get("content"):
                btn_col1, btn_col2, btn_col3, _ = st.columns([1, 1, 1, 5])
                
                with btn_col1:
                    is_playing = st.session_state.get("tts_playing") and st.session_state.get("tts_message_index") == idx
                    if st.button(
                        "🔊 Read" if not is_playing else "⏹️ Stop",
                        key=f"tts_btn_{unique_key}",
                        help="Read this response aloud",
                        use_container_width=True
                    ):
                        if is_playing:
                            stop_tts()
                        else:
                            start_tts(message.get("content", ""), idx)
                
                with btn_col2:
                    if st.button(
                        "🔄 Redo",
                        key=f"regen_btn_{unique_key}",
                        help="Regenerate this response",
                        use_container_width=True
                    ):
                        st.session_state.regenerate_index = idx
                        st.rerun()
                
                with btn_col3:
                    if st.button(
                        "📋 Copy",
                        key=f"copy_btn_{unique_key}",
                        help="Copy to clipboard",
                        use_container_width=True
                    ):
                        st.session_state[f"show_copy_{idx}"] = True
                        st.rerun()
                
                # Show copy modal with text area for easy copying
                if st.session_state.get(f"show_copy_{idx}", False):
                    with st.expander("📋 Copy Text", expanded=True):
                        content_to_copy = message.get("content", "")
                        st.text_area(
                            "Select all (Ctrl+A) and copy (Ctrl+C):",
                            value=content_to_copy,
                            height=200,
                            key=f"copy_area_{idx}",
                            label_visibility="visible"
                        )
                        
                        col_close, col_download = st.columns(2)
                        with col_close:
                            if st.button("✕ Close", key=f"close_copy_{idx}", use_container_width=True):
                                st.session_state[f"show_copy_{idx}"] = False
                                st.rerun()
                        with col_download:
                            st.download_button(
                                "💾 Download",
                                data=content_to_copy,
                                file_name="response.txt",
                                mime="text/plain",
                                key=f"download_{idx}",
                                use_container_width=True
                            )
                        
                        # JavaScript to auto-select text
                        st.components.v1.html(
                            f"""
                            <script>
                                setTimeout(function() {{
                                    const textarea = window.parent.document.querySelector('textarea[aria-label="Select all (Ctrl+A) and copy (Ctrl+C):"]');
                                    if (textarea) {{
                                        textarea.select();
                                        textarea.focus();
                                    }}
                                }}, 100);
                            </script>
                            """,
                            height=0
                        )


def set_empty_state_action(prefill_text: str, *, show_image_upload: bool = False) -> None:
    """Apply suggestion card action and optionally open the image uploader."""
    st.session_state.prefill_prompt = prefill_text
    if show_image_upload:
        st.session_state.show_image_upload = True
        st.session_state.show_voice_input = False


def trigger_concept_explainer() -> None:
    """Trigger the random concept explainer feature."""
    st.session_state.show_concept_explainer = True
    st.session_state.show_writing_generator = False
    st.session_state.show_bug_debugger = False
    # Pick a random concept based on difficulty
    difficulty = st.session_state.get("concept_difficulty", "Intermediate")
    concepts = CONCEPTS_BY_DIFFICULTY.get(difficulty, CONCEPTS_BY_DIFFICULTY["Intermediate"])
    st.session_state.current_concept = random.choice(concepts)


def trigger_writing_generator() -> None:
    """Trigger the random writing generator feature."""
    st.session_state.show_writing_generator = True
    st.session_state.show_concept_explainer = False
    st.session_state.show_bug_debugger = False
    # Pick a random writing task based on tone
    tone = st.session_state.get("writing_tone", "Formal")
    tasks = WRITING_TASKS_BY_TONE.get(tone, WRITING_TASKS_BY_TONE["Formal"])
    st.session_state.current_writing_task = random.choice(tasks)


def trigger_bug_debugger() -> None:
    """Trigger the random bug debugger feature."""
    st.session_state.show_bug_debugger = True
    st.session_state.show_concept_explainer = False
    st.session_state.show_writing_generator = False
    # Pick a random buggy code snippet
    st.session_state.current_bug = random.choice(BUGGY_CODE_SNIPPETS)


def generate_concept_prompt(concept: dict, difficulty: str) -> str:
    """Generate a prompt for the AI to explain a concept."""
    return f"""Explain the concept of "{concept['topic']}" from the category "{concept['category']}" at a {difficulty} level.

Please provide:
1. **Simple Explanation** (2-3 sentences for beginners)
2. **Structured Explanation** (detailed breakdown with key points)
3. **Real-World Analogy** (relatable comparison)
4. **Interview Question** (one common interview question on this topic with a brief answer)

Make sure to adjust the complexity based on the {difficulty} level."""


def generate_writing_prompt(task: dict, tone: str) -> str:
    """Generate a prompt for the AI to create writing content."""
    return f"""Generate a {tone.lower()} {task['type'].lower()} with the following task:

"{task['prompt']}"

Please create a complete, well-written piece that matches the {tone.lower()} tone. Include proper formatting and structure appropriate for a {task['type']}."""


def generate_bug_prompt(bug: dict) -> str:
    """Generate a prompt for the bug debugger feature."""
    return f"""I'm practicing debugging! Here's a buggy {bug['language']} code snippet:

**Bug Title:** {bug['title']}

```{bug['language']}
{bug['buggy_code']}
```

Please analyze this code and provide:
1. **What's wrong?** - Identify the bug
2. **Fixed Code** - Show the corrected version
3. **Explanation** - Why did this bug occur?
4. **Prevention Tips** - How to avoid this in the future

Help me understand this debugging challenge!"""


def render_empty_state(display_name: str) -> None:
    """Stunning ChatGPT-style welcome screen with animated suggestions and interactive features."""
    
    # Get current model for display
    current_model = st.session_state.get("model_select", MODEL_OPTIONS[0])
    current_mode = st.session_state.get("mode_select", CHAT_MODES[0])
    
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-glow"></div>
            <div class="hero-logo">✨</div>
            <div class="hero-title">Hi {display_name}, how can I help?</div>
            <div class="hero-subtitle">
                I'm your AI coding assistant. Ask me anything, upload an image for analysis,<br>
                or use voice input to get started.
            </div>
            <div class="hero-badges">
                <span class="hero-badge">🤖 {current_model}</span>
                <span class="hero-badge">💬 {current_mode}</span>
                <span class="hero-badge">⚡ Streaming</span>
                <span class="hero-badge">🖼️ Vision</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Stunning suggestion cards
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        # Card 1: Explain a concept - with difficulty toggle
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">💡</span>
                <div class="suggestion-title">Explain a concept</div>
                <div class="suggestion-desc">Random tech concept with explanations & interview Q</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Difficulty toggle
        diff_col1, diff_col2 = st.columns([2, 3])
        with diff_col1:
            st.selectbox(
                "Difficulty",
                options=["Beginner", "Intermediate", "Advanced"],
                key="concept_difficulty",
                label_visibility="collapsed"
            )
        with diff_col2:
            st.button(
                "💡 Random Concept",
                use_container_width=True,
                key="sug1",
                on_click=trigger_concept_explainer,
            )
        
        # Card 3: Debug my code - Random bug generator
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">🔧</span>
                <div class="suggestion-title">Debug Practice</div>
                <div class="suggestion-desc">Random buggy code snippet to find and fix</div>
            </div>
        """, unsafe_allow_html=True)
        st.button(
            "🔧 Random Bug Challenge",
            use_container_width=True,
            key="sug3",
            on_click=trigger_bug_debugger,
        )
            
    with col2:
        # Card 2: Write something - with tone control
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">✍️</span>
                <div class="suggestion-title">Write something</div>
                <div class="suggestion-desc">Random writing task: emails, docs, creative content</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Tone toggle
        tone_col1, tone_col2 = st.columns([2, 3])
        with tone_col1:
            st.selectbox(
                "Tone",
                options=["Formal", "Friendly", "Humorous"],
                key="writing_tone",
                label_visibility="collapsed"
            )
        with tone_col2:
            st.button(
                "✍️ Random Writing",
                use_container_width=True,
                key="sug2",
                on_click=trigger_writing_generator,
            )
        
        # Card 4: Image Analysis (unchanged)
        st.markdown("""
            <div class="suggestion-card" style="pointer-events: none;">
                <span class="suggestion-icon">🖼️</span>
                <div class="suggestion-title">Analyze an image</div>
                <div class="suggestion-desc">Upload and get insights from images</div>
            </div>
        """, unsafe_allow_html=True)
        st.button(
            "🖼️ Analyze an image",
            use_container_width=True,
            key="sug4",
            on_click=set_empty_state_action,
            args=("",),
            kwargs={"show_image_upload": True},
        )
    
    # Show feature panels based on selection
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Concept Explainer Panel
    if st.session_state.get("show_concept_explainer") and st.session_state.get("current_concept"):
        concept = st.session_state.current_concept
        difficulty = st.session_state.get("concept_difficulty", "Intermediate")
        
        with st.container():
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%); 
                            border: 1px solid #10a37f; border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
                    <h3 style="color: #10a37f; margin-bottom: 0.5rem;">💡 Random Concept Challenge</h3>
                    <p style="color: #8e8e8e; font-size: 0.9rem;">Difficulty: <strong style="color: #ececec;">{difficulty}</strong></p>
                    <div style="background: #2f2f2f; border-radius: 8px; padding: 1rem; margin-top: 0.5rem;">
                        <span style="color: #10a37f; font-size: 0.8rem;">{concept['category']}</span>
                        <h4 style="color: #fff; margin: 0.5rem 0;">{concept['topic']}</h4>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns([2, 2, 1])
            with col_a:
                if st.button("🚀 Explain This!", key="send_concept", use_container_width=True):
                    prompt = generate_concept_prompt(concept, difficulty)
                    st.session_state.pending_prompt = prompt
                    st.session_state.auto_send_prompt = True
                    st.session_state.show_concept_explainer = False
                    st.rerun()
            with col_b:
                if st.button("🎲 New Concept", key="new_concept", use_container_width=True):
                    trigger_concept_explainer()
                    st.rerun()
            with col_c:
                if st.button("✕", key="close_concept"):
                    st.session_state.show_concept_explainer = False
                    st.rerun()
    
    # Writing Generator Panel
    if st.session_state.get("show_writing_generator") and st.session_state.get("current_writing_task"):
        task = st.session_state.current_writing_task
        tone = st.session_state.get("writing_tone", "Formal")
        
        with st.container():
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%); 
                            border: 1px solid #f59e0b; border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
                    <h3 style="color: #f59e0b; margin-bottom: 0.5rem;">✍️ Random Writing Task</h3>
                    <p style="color: #8e8e8e; font-size: 0.9rem;">Tone: <strong style="color: #ececec;">{tone}</strong></p>
                    <div style="background: #2f2f2f; border-radius: 8px; padding: 1rem; margin-top: 0.5rem;">
                        <span style="color: #f59e0b; font-size: 0.8rem;">{task['type']}</span>
                        <h4 style="color: #fff; margin: 0.5rem 0; font-size: 1rem;">{task['prompt']}</h4>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns([2, 2, 1])
            with col_a:
                if st.button("🚀 Generate This!", key="send_writing", use_container_width=True):
                    prompt = generate_writing_prompt(task, tone)
                    st.session_state.pending_prompt = prompt
                    st.session_state.auto_send_prompt = True
                    st.session_state.show_writing_generator = False
                    st.rerun()
            with col_b:
                if st.button("🎲 New Task", key="new_writing", use_container_width=True):
                    trigger_writing_generator()
                    st.rerun()
            with col_c:
                if st.button("✕", key="close_writing"):
                    st.session_state.show_writing_generator = False
                    st.rerun()
    
    # Bug Debugger Panel
    if st.session_state.get("show_bug_debugger") and st.session_state.get("current_bug"):
        bug = st.session_state.current_bug
        
        with st.container():
            st.markdown(f"""
                <div style="background: linear-gradient(145deg, #2a2a2a 0%, #1f1f1f 100%); 
                            border: 1px solid #ef4444; border-radius: 16px; padding: 1.5rem; margin: 1rem 0;">
                    <h3 style="color: #ef4444; margin-bottom: 0.5rem;">🔧 Debug Challenge</h3>
                    <p style="color: #8e8e8e; font-size: 0.9rem;">Language: <strong style="color: #ececec;">{bug['language'].upper()}</strong></p>
                    <div style="background: #2f2f2f; border-radius: 8px; padding: 1rem; margin-top: 0.5rem;">
                        <span style="color: #ef4444; font-size: 0.8rem;">🐛 Bug Type</span>
                        <h4 style="color: #fff; margin: 0.5rem 0;">{bug['title']}</h4>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Show buggy code
            st.markdown("**🔍 Find the bug in this code:**")
            st.code(bug['buggy_code'], language=bug['language'])
            
            col_a, col_b, col_c, col_d = st.columns([2, 2, 2, 1])
            with col_a:
                if st.button("🚀 Analyze Bug!", key="send_bug", use_container_width=True):
                    prompt = generate_bug_prompt(bug)
                    st.session_state.pending_prompt = prompt
                    st.session_state.auto_send_prompt = True
                    st.session_state.show_bug_debugger = False
                    st.rerun()
            with col_b:
                if st.button("👀 Show Answer", key="show_answer", use_container_width=True):
                    st.session_state[f"show_bug_answer_{id(bug)}"] = True
            with col_c:
                if st.button("🎲 New Bug", key="new_bug", use_container_width=True):
                    trigger_bug_debugger()
                    st.rerun()
            with col_d:
                if st.button("✕", key="close_bug"):
                    st.session_state.show_bug_debugger = False
                    st.rerun()
            
            # Show answer if requested
            if st.session_state.get(f"show_bug_answer_{id(bug)}"):
                st.markdown("---")
                st.markdown("**✅ Fixed Code:**")
                st.code(bug['fixed_code'], language=bug['language'])
                st.markdown(f"**💡 Explanation:** {bug['explanation']}")
                st.markdown(f"**🛡️ Prevention:** {bug['prevention']}")
    


def clear_conversation() -> None:
    """Clear only the currently active conversation."""
    messages = get_active_messages()
    messages.clear()
    st.session_state.uploaded_image = None


def delete_chat(chat_id: str) -> None:
    """Remove a saved chat and keep selection valid."""
    if chat_id in st.session_state.chats:
        st.session_state.chats.pop(chat_id)
        if st.session_state.current_chat_id == chat_id:
            next_chat = next(iter(st.session_state.chats), "")
            if next_chat:
                st.session_state.current_chat_id = next_chat
            else:
                st.session_state.current_chat_id = create_persistent_chat()


def rename_chat(chat_id: str, new_title: str) -> None:
    """Rename a chat with a new title."""
    if chat_id in st.session_state.chats and new_title.strip():
        st.session_state.chats[chat_id]["title"] = new_title.strip()
        st.session_state.show_rename_input = False
        st.session_state.rename_chat_title = ""


def summarize_title(prompt: str) -> str:
    """Generate a short title from the first user message."""
    condensed = prompt.strip().splitlines()[0][:40]
    return condensed + ("…" if len(prompt.strip()) > len(condensed) else "") or "New chat"


def send_to_backend(
    messages: List[Dict[str, Any]],
    *,
    mode: str,
    system_prompt: str,
    model: str,
    image: Optional[Image.Image] = None,
):
    """Send messages to the selected backend model and yield assistant text chunks for streaming.

    Behavior:
    - If `model` == "gpt-oss-120b" use the Groq/OpenAI-compatible Responses API.
      The function will first attempt to use the `openai.OpenAI` SDK if available,
      otherwise it will POST to the configured `GROQ_BASE_URL` using `requests`.
    - For llama3/deepseek-r1, uses Ollama API.
    - For other modes/models the function falls back to a friendly stub message.

    Keys:
    - Put credentials in `st.secrets` or environment variables:
      - `GROQ_API_KEY` and optional `GROQ_BASE_URL` for Groq/OpenAI-compatible API
    """

    user_prompt = next(
        (msg.get("content", "") for msg in reversed(messages) if msg.get("role") == "user"),
        "",
    )

    # If there is an image, attach a short descriptor to the prompt
    if image is not None:
        try:
            b64 = image_to_base64(image)
            user_prompt = f"[Image attached: base64_png({len(b64)} bytes)]\n\n" + user_prompt
        except Exception:
            user_prompt = "[Image attached]\n\n" + user_prompt

    if not user_prompt:
        yield "Hi there! Send a message or upload an image and I'll respond."
        return
    
    # Apply mode-specific instructions to the prompt
    mode_instructions = ""
    if mode == "Generate Code":
        mode_instructions = "You are a code generation assistant. Generate clean, efficient, and well-commented code based on the user's request. Always include code examples in your response.\n\n"
    elif mode == "Explain Code":
        mode_instructions = "You are a code explanation assistant. Provide clear, detailed explanations of code, breaking down how it works step by step. Explain concepts, logic flow, and best practices.\n\n"
    else:  # Chat mode
        mode_instructions = f"{system_prompt}\n\n"
    
    # Prepend mode instructions to user prompt
    full_prompt = mode_instructions + user_prompt

    # --------------------
    # Groq / OpenAI-compatible (gpt-oss-120b)
    # --------------------
    if model == "gpt-oss-120b":
        groq_api_key = get_secret_or_env("GROQ_API_KEY")
        # allow hardcoded fallback for convenience during local testing
        if not groq_api_key and "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":
            groq_api_key = "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".strip() or None

        groq_base = get_secret_or_env("GROQ_BASE_URL") or GROQ_BASE_URL_DIRECT or "https://api.groq.com/openai/v1"
        if not groq_api_key:
            yield "[GROQ API key not found. Set `GROQ_API_KEY` in Streamlit secrets, environment variables, or `GROQ_API_KEY_DIRECT` in this file.]"
            return

        try:
            from openai import OpenAI
            
            client = OpenAI(
                api_key=groq_api_key,
                base_url=groq_base,
            )
            
            response = client.responses.create(
                input=full_prompt,
                model="openai/gpt-oss-120b",
                stream=True
            )
            
            for event in response:
                if hasattr(event, "delta"):
                    delta = event.delta
                    if hasattr(delta, "text") and delta.text:
                        yield delta.text
                    elif isinstance(delta, str):
                        yield delta
                elif isinstance(event, str):
                    yield event
        except ImportError:
            yield "[OpenAI SDK not installed. Install: pip install openai]"
        except Exception as http_err:
            yield f"[Error calling Groq/OpenAI endpoint: {http_err}]"
        return

    # --------------------
    # Ollama Models (llama3, deepseek-r1)
    # --------------------
    if model in ["llama3", "deepseek-r1", "deepseek-ocr:3b"]:
        yield from stream_generate(model, full_prompt, image)
        return

    # --------------------
    # Mode-based helper behavior (existing helpful stubs)
    # --------------------
    if mode == "Generate Code":
        yield (
            f"Here's the code you requested! 🚀\n\n"
            "```python\n"
            "def solution(data):\n"
            '    """Generated based on your requirements."""\n'
            "    # Implementation goes here\n"
            "    result = process(data)\n"
            "    return result\n"
            "```\n\n"
            "**Key points:**\n"
            "- Clean and readable structure\n"
            "- Follows best practices\n"
            "- Ready to customize\n\n"
            "Would you like me to explain any part or make modifications?"
        )
        return

    if mode == "Explain Code":
        yield (
            "Let me break this down for you! 📚\n\n"
            "**Overview:**\n"
            "The code you shared performs a specific operation with clear logic.\n\n"
            "**Step-by-step explanation:**\n"
            "1. **Input handling** - Validates and processes input data\n"
            "2. **Core logic** - Performs the main computation\n"
            "3. **Output** - Returns the processed result\n\n"
            "**Complexity:** O(n) time, O(1) space\n\n"
            "Any questions about specific parts?"
        )
        return

    # Default fallback
    yield (
        f"Great question! Here's a friendly stub reply while the model call is not configured.\n\n"
        f"Your input: \"{user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}\"\n\n"
        f"Selected model: `{model}`\n"
        "To enable live responses, set API keys in Streamlit `secrets.toml` or environment variables and install the SDKs."
    )


def handle_user_prompt(
    user_prompt: str, 
    mode: str, 
    system_prompt: str, 
    model: str,
    image: Optional[Image.Image] = None
) -> None:
    """Persist the new user prompt, get assistant reply with streaming, and re-render."""
    messages = get_active_messages()
    
    # Create message with optional image
    user_message = {"role": "user", "content": user_prompt}
    if image:
        user_message["image"] = image
    
    messages.append(user_message)
    
    # Display user message
    with st.chat_message("user", avatar="👤"):
        if image:
            st.image(image, width=300)
        st.markdown(user_prompt)
    
    # Display streaming assistant response
    with st.chat_message("assistant", avatar="✨"):
        message_placeholder = st.empty()
        full_response = ""
        
        for chunk in send_to_backend(
            messages,
            mode=mode,
            system_prompt=system_prompt,
            model=model,
            image=image,
        ):
            full_response += chunk
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
    
    messages.append({"role": "assistant", "content": full_response})

    # Clear the uploaded image after sending
    st.session_state.uploaded_image = None

    if not st.session_state.is_temp_chat and user_prompt.strip():
        chat_meta = st.session_state.chats[st.session_state.current_chat_id]
        if chat_meta.get("title") in {"New chat", ""} or chat_meta.get("title", "").startswith("New chat "):
            chat_meta["title"] = summarize_title(user_prompt)


def start_new_chat(title: Optional[str] = None) -> None:
    """Start a fresh conversation respecting the temp toggle."""
    st.session_state.uploaded_image = None
    if st.session_state.is_temp_chat:
        st.session_state.temp_messages = []
    else:
        chat_id = create_persistent_chat(title)
        st.session_state.current_chat_id = chat_id


def handle_new_chat_button() -> None:
    """Callback for sidebar button to create a chat with custom title."""
    custom_title = st.session_state.get("new_chat_name", "").strip() or None
    start_new_chat(custom_title)
    st.session_state.new_chat_name = ""


def search_in_chat(chat_id: str, query: str) -> tuple[bool, str]:
    """Search for query in chat title and messages. Returns (found, match_type)."""
    chat = st.session_state.chats[chat_id]
    query_lower = query.lower()
    
    # Search in title
    if query_lower in chat["title"].lower():
        return True, "title"
    
    # Search in message content
    for message in chat.get("messages", []):
        content = message.get("content", "").lower()
        if query_lower in content:
            return True, "content"
    
    return False, ""


def render_chat_list() -> None:
    """Renderable list of saved chats similar to ChatGPT sidebar with enhanced search."""
    if not st.session_state.chats:
        st.caption("No saved chats yet.")
        return

    all_chat_ids = list(st.session_state.chats.keys())
    query = st.session_state.chat_search.strip().lower()
    
    # Enhanced search: filter by title or content
    if query:
        matched_chats = {}
        for cid in all_chat_ids:
            found, match_type = search_in_chat(cid, query)
            if found:
                matched_chats[cid] = match_type
        
        chat_ids = list(matched_chats.keys())
        
        if not chat_ids:
            st.warning(f"🔍 No chats found matching '{st.session_state.chat_search}'")
            st.caption("Try searching with different keywords or check your chat titles and messages.")
            return
        
        # Show search results count
        st.success(f"✓ Found {len(chat_ids)} chat(s) matching '{st.session_state.chat_search}'")
    else:
        chat_ids = all_chat_ids

    current_id = st.session_state.current_chat_id
    
    # Only switch to first result if current chat is not in the filtered list AND we have results
    if current_id not in chat_ids and chat_ids:
        # Don't auto-switch, just show the list without selection
        # User can click to switch
        index = 0
    else:
        index = chat_ids.index(current_id) if current_id in chat_ids else 0
    
    # Format function to show match indicator
    def format_chat_title(cid: str) -> str:
        title = st.session_state.chats[cid]["title"]
        if query:
            _, match_type = search_in_chat(cid, query)
            if match_type == "title":
                return f"📌 {title}"
            elif match_type == "content":
                return f"💬 {title}"
        return title
    
    selection = st.radio(
        "Your chats",
        options=chat_ids,
        index=index,
        format_func=format_chat_title,
        label_visibility="collapsed",
        key="chat_history_selector",
        help="📌 = Match in title, 💬 = Match in messages" if query else None
    )
    if selection != current_id:
        st.session_state.current_chat_id = selection
        st.rerun()

    # Chat actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✏️ Rename", key="rename_chat_btn", use_container_width=True):
            st.session_state.show_rename_input = not st.session_state.show_rename_input
            if st.session_state.show_rename_input:
                current_title = st.session_state.chats[st.session_state.current_chat_id]["title"]
                st.session_state.rename_chat_title = current_title
    
    with col2:
        if st.button("🗑️ Delete", key="delete_selected_chat", use_container_width=True):
            delete_chat(st.session_state.current_chat_id)
            st.rerun()
    
    # Rename input section
    if st.session_state.show_rename_input:
        new_title = st.text_input(
            "New chat title",
            value=st.session_state.rename_chat_title,
            key="rename_input",
            placeholder="Enter new title..."
        )
        
        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("✓ Save", key="save_rename", use_container_width=True):
                if new_title.strip():
                    rename_chat(st.session_state.current_chat_id, new_title)
                    st.rerun()
        with col_b:
            if st.button("✕ Cancel", key="cancel_rename", use_container_width=True):
                st.session_state.show_rename_input = False
                st.rerun()


def render_sidebar() -> tuple[str, str, str]:
    """Full sidebar layout mimicking ChatGPT."""
    with st.sidebar:
        st.markdown('<div class="sidebar-logo">✨ Code Gen AI</div>', unsafe_allow_html=True)
        
        st.text_input(
            "New chat name",
            key="new_chat_name",
            placeholder="Optional title",
        )
        st.button(
            "➕ New chat",
            use_container_width=True,
            on_click=handle_new_chat_button,
        )

        # Search
        st.markdown('<div class="sidebar-section-title">Search</div>', unsafe_allow_html=True)
        search = st.text_input(
            "Search chats",
            key="chat_search",
            placeholder="Search your chats...",
            label_visibility="collapsed"
        )

        # Temp chat toggle
        temp_toggle = st.toggle(
            "Temporary chat",
            value=st.session_state.is_temp_chat,
            help="Temporary chats won't be saved",
        )
        if temp_toggle != st.session_state.is_temp_chat:
            st.session_state.is_temp_chat = temp_toggle
            if temp_toggle:
                st.session_state.temp_messages = []
            else:
                ensure_current_chat()

        # Chat history
        if not st.session_state.is_temp_chat:
            st.markdown('<div class="sidebar-section-title">Recent</div>', unsafe_allow_html=True)
            render_chat_list()

        st.markdown("---")
        
        # Model & Settings
        st.markdown('<div class="sidebar-section-title">Settings</div>', unsafe_allow_html=True)
        
        model = st.selectbox(
            "Model",
            options=MODEL_OPTIONS,
            key="model_select",
            help="Select the AI model to use"
        )
        
        mode = st.selectbox(
            "Mode", 
            options=CHAT_MODES, 
            key="mode_select",
            help="Select conversation mode"
        )
        
        with st.expander("⚙️ Advanced"):
            display_name = st.text_input("Your name", value=st.session_state.display_name)
            st.session_state.display_name = display_name or "User"
            
            system_prompt = st.text_area(
                "System prompt",
                value=DEFAULT_SYSTEM_PROMPT,
                height=100,
                key="system_prompt_area",
            )

        if st.button("🗑️ Clear chat", use_container_width=True):
            clear_conversation()
            st.rerun()

    

    return mode, model, system_prompt


def render_input_toolbar() -> tuple[Optional[Image.Image], str]:
    """Render attachment toolbar with image and voice inputs."""
    uploaded_image = None
    voice_text = ""
    
    # Toolbar buttons
    col1, col2, col3 = st.columns([1, 1, 6])
    
    with col1:
        if st.button("📷 Image", key="img_btn", help="Upload an image"):
            st.session_state.show_image_upload = not st.session_state.show_image_upload
            st.session_state.show_voice_input = False
    
    with col2:
        if st.button("🎤 Voice", key="voice_btn", help="Voice input"):
            st.session_state.show_voice_input = not st.session_state.show_voice_input
            st.session_state.show_image_upload = False
    
    # Image upload section
    if st.session_state.show_image_upload:
        with st.container():
            uploaded_file = st.file_uploader(
                "Upload an image",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                key="image_uploader",
                label_visibility="collapsed"
            )
            if uploaded_file:
                uploaded_image = Image.open(uploaded_file)
                st.session_state.uploaded_image = uploaded_image
                st.image(uploaded_image, width=200, caption="Ready to send")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ Keep", use_container_width=True):
                        st.session_state.show_image_upload = False
                with col_b:
                    if st.button("✕ Remove", use_container_width=True):
                        st.session_state.uploaded_image = None
                        st.rerun()
    
    # Voice input section
    if st.session_state.show_voice_input:
        with st.container():
            st.info("🎤 Record your voice message (auto-transcription enabled)")
            
            audio_value = st.audio_input(
                "Record your message",
                key="audio_recorder",
                label_visibility="collapsed"
            )
            
            if audio_value:
                st.audio(audio_value)
                
                # Auto-transcribe when audio is recorded
                if audio_value and "last_audio_hash" not in st.session_state or st.session_state.get("last_audio_hash") != hash(audio_value.getvalue()):
                    st.session_state.last_audio_hash = hash(audio_value.getvalue())
                    
                    with st.spinner("🎙️ Auto-transcribing..."):
                        audio_bytes = audio_value.read()
                        
                        if SPEECH_RECOGNITION_AVAILABLE:
                            tmp_path = None
                            try:
                                import wave
                                import tempfile
                                import os
                                import time
                                
                                # Save to temp file for speech recognition
                                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                    tmp.write(audio_bytes)
                                    tmp_path = tmp.name
                                
                                # Ensure file is closed before using it
                                time.sleep(0.1)
                                
                                recognizer = sr.Recognizer()
                                with sr.AudioFile(tmp_path) as source:
                                    audio_data = recognizer.record(source)
                                
                                # Ensure AudioFile is closed before cleanup
                                voice_text = recognizer.recognize_google(audio_data)
                                st.session_state.voice_text = voice_text
                                st.session_state.auto_send_voice = True
                                
                                st.success(f"✅ Transcribed: {voice_text}")
                                st.info("💬 Sending to AI automatically...")
                                st.rerun()
                                    
                            except Exception as e:
                                st.error(f"❌ Transcription error: {e}")
                                st.session_state.voice_text = ""
                            finally:
                                # Clean up temp file with retry
                                if tmp_path and os.path.exists(tmp_path):
                                    for i in range(3):  # Try 3 times
                                        try:
                                            os.unlink(tmp_path)
                                            break
                                        except PermissionError:
                                            time.sleep(0.1)  # Wait a bit and retry
                                        except Exception:
                                            break  # Give up on other errors
                        else:
                            st.warning("⚠️ Install `SpeechRecognition` for auto-transcription: `pip install SpeechRecognition`")
                
                # Manual transcribe button as backup
                col_manual, col_clear = st.columns(2)
                with col_manual:
                    if st.button("🔄 Re-transcribe", use_container_width=True):
                        with st.spinner("🎙️ Transcribing..."):
                            audio_bytes = audio_value.read()
                            
                            if SPEECH_RECOGNITION_AVAILABLE:
                                tmp_path = None
                                try:
                                    import wave
                                    import tempfile
                                    import os
                                    import time
                                    
                                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                        tmp.write(audio_bytes)
                                        tmp_path = tmp.name
                                    
                                    # Ensure file is closed before using it
                                    time.sleep(0.1)
                                    
                                    recognizer = sr.Recognizer()
                                    with sr.AudioFile(tmp_path) as source:
                                        audio_data = recognizer.record(source)
                                    
                                    # Ensure AudioFile is closed before cleanup
                                    voice_text = recognizer.recognize_google(audio_data)
                                    st.session_state.voice_text = voice_text
                                    
                                    st.success(f"✅ Re-transcribed: {voice_text}")
                                except Exception as e:
                                    st.error(f"❌ Transcription error: {e}")
                                finally:
                                    # Clean up temp file with retry
                                    if tmp_path and os.path.exists(tmp_path):
                                        for i in range(3):  # Try 3 times
                                            try:
                                                os.unlink(tmp_path)
                                                break
                                            except PermissionError:
                                                time.sleep(0.1)  # Wait a bit and retry
                                            except Exception:
                                                break  # Give up on other errors
                
                with col_clear:
                    if st.button("🗑️ Clear", use_container_width=True):
                        st.session_state.voice_text = ""
                        if "last_audio_hash" in st.session_state:
                            del st.session_state.last_audio_hash
                        st.rerun()
    
    # Show pending image preview
    if st.session_state.uploaded_image and not st.session_state.show_image_upload:
        with st.container():
            col_img, col_remove = st.columns([4, 1])
            with col_img:
                st.image(st.session_state.uploaded_image, width=80)
            with col_remove:
                if st.button("✕", key="remove_preview"):
                    st.session_state.uploaded_image = None
                    st.rerun()
    
    return st.session_state.uploaded_image, st.session_state.get("voice_text", "")


def main() -> None:
    st.set_page_config(
        page_title="Code Gen AI",
        page_icon="✨",
        layout="wide"
    )
    inject_custom_css()
    init_session_state()

    mode, model, system_prompt = render_sidebar()
    messages = get_active_messages()

    # Main chat area
    if messages:
        render_chat_history(messages)
    else:
        render_empty_state(st.session_state.display_name)

    # Input toolbar and chat input in linear layout
    st.markdown("---")
    

    # Create linear input layout: text input (left) -> voice (middle) -> image (right)
    input_col1, input_col2, input_col3 = st.columns([8, 0.8, 0.8])
    
    with input_col1:
        # Pre-fill prompt if set
        default_prompt = st.session_state.get("prefill_prompt", "")
        if default_prompt:
            st.session_state.prefill_prompt = ""
        
        # Use voice text as default if available (for manual input)
        voice_text = st.session_state.get("voice_text", "")
        if voice_text and st.session_state.voice_text and not st.session_state.get("auto_send_voice", False):
            default_prompt = voice_text
            st.session_state.voice_text = ""
        
        # Chat input
        attached_image = st.session_state.uploaded_image
        placeholder = "Message Code Gen AI..."
        if attached_image:
            placeholder = "Ask about this image..."
        
        user_prompt = st.chat_input(placeholder)
    
    with input_col2:
        if st.button("🎤", key="voice_btn_main", help="Voice input", use_container_width=True):
            st.session_state.show_voice_input = not st.session_state.show_voice_input
            st.session_state.show_image_upload = False
            st.rerun()
    
    with input_col3:
        if st.button("📷", key="img_btn_main", help="Upload an image", use_container_width=True):
            st.session_state.show_image_upload = not st.session_state.show_image_upload
            st.session_state.show_voice_input = False
            st.rerun()
    
    # Show image/voice upload sections below the input
    if st.session_state.show_image_upload:
        with st.container():
            uploaded_file = st.file_uploader(
                "Upload an image",
                type=["png", "jpg", "jpeg", "gif", "webp"],
                key="image_uploader",
                label_visibility="collapsed"
            )
            if uploaded_file:
                uploaded_image = Image.open(uploaded_file)
                st.session_state.uploaded_image = uploaded_image
                st.image(uploaded_image, width=200, caption="Ready to send")
                
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("✓ Keep", use_container_width=True):
                        st.session_state.show_image_upload = False
                        st.rerun()
                with col_b:
                    if st.button("✕ Remove", use_container_width=True):
                        st.session_state.uploaded_image = None
                        st.rerun()
    
    if st.session_state.show_voice_input:
        with st.container():
            st.info("🎤 Record your voice message (auto-transcription enabled)")
            
            audio_value = st.audio_input(
                "Record your message",
                key="audio_recorder",
                label_visibility="collapsed"
            )
            
            if audio_value:
                st.audio(audio_value)
                
                # Auto-transcribe when audio is recorded
                if audio_value and "last_audio_hash" not in st.session_state or st.session_state.get("last_audio_hash") != hash(audio_value.getvalue()):
                    st.session_state.last_audio_hash = hash(audio_value.getvalue())
                    
                    with st.spinner("🎙️ Auto-transcribing..."):
                        audio_bytes = audio_value.read()
                        
                        if SPEECH_RECOGNITION_AVAILABLE:
                            tmp_path = None
                            try:
                                import wave
                                import tempfile
                                import os
                                import time
                                
                                # Save to temp file for speech recognition
                                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                    tmp.write(audio_bytes)
                                    tmp_path = tmp.name
                                
                                # Ensure file is closed before using it
                                time.sleep(0.1)
                                
                                recognizer = sr.Recognizer()
                                with sr.AudioFile(tmp_path) as source:
                                    audio_data = recognizer.record(source)
                                
                                # Ensure AudioFile is closed before cleanup
                                voice_text = recognizer.recognize_google(audio_data)
                                st.session_state.voice_text = voice_text
                                st.session_state.auto_send_voice = True
                                
                                st.success(f"✅ Transcribed: {voice_text}")
                                st.info("💬 Sending to AI automatically...")
                                st.rerun()
                                    
                            except Exception as e:
                                st.error(f"❌ Transcription error: {e}")
                                st.session_state.voice_text = ""
                            finally:
                                # Clean up temp file with retry
                                if tmp_path and os.path.exists(tmp_path):
                                    for i in range(3):  # Try 3 times
                                        try:
                                            os.unlink(tmp_path)
                                            break
                                        except PermissionError:
                                            time.sleep(0.1)  # Wait a bit and retry
                                        except Exception:
                                            break  # Give up on other errors
                        else:
                            st.warning("⚠️ Install `SpeechRecognition` for auto-transcription: `pip install SpeechRecognition`")
                
                # Manual transcribe button as backup
                col_manual, col_clear = st.columns(2)
                with col_manual:
                    if st.button("🔄 Re-transcribe", use_container_width=True):
                        with st.spinner("🎙️ Transcribing..."):
                            audio_bytes = audio_value.read()
                            
                            if SPEECH_RECOGNITION_AVAILABLE:
                                tmp_path = None
                                try:
                                    import wave
                                    import tempfile
                                    import os
                                    import time
                                    
                                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                                        tmp.write(audio_bytes)
                                        tmp_path = tmp.name
                                    
                                    # Ensure file is closed before using it
                                    time.sleep(0.1)
                                    
                                    recognizer = sr.Recognizer()
                                    with sr.AudioFile(tmp_path) as source:
                                        audio_data = recognizer.record(source)
                                    
                                    # Ensure AudioFile is closed before cleanup
                                    voice_text = recognizer.recognize_google(audio_data)
                                    st.session_state.voice_text = voice_text
                                    
                                    st.success(f"✅ Re-transcribed: {voice_text}")
                                except Exception as e:
                                    st.error(f"❌ Transcription error: {e}")
                                finally:
                                    # Clean up temp file with retry
                                    if tmp_path and os.path.exists(tmp_path):
                                        for i in range(3):  # Try 3 times
                                            try:
                                                os.unlink(tmp_path)
                                                break
                                            except PermissionError:
                                                time.sleep(0.1)  # Wait a bit and retry
                                            except Exception:
                                                break  # Give up on other errors
                
                with col_clear:
                    if st.button("🗑️ Clear", use_container_width=True):
                        st.session_state.voice_text = ""
                        if "last_audio_hash" in st.session_state:
                            del st.session_state.last_audio_hash
                        st.rerun()
    
    # Show pending image preview
    if st.session_state.uploaded_image and not st.session_state.show_image_upload:
        with st.container():
            col_img, col_remove = st.columns([4, 1])
            with col_img:
                st.image(st.session_state.uploaded_image, width=80)
            with col_remove:
                if st.button("✕", key="remove_preview"):
                    st.session_state.uploaded_image = None
                    st.rerun()
    
    # Handle auto-send voice input
    if st.session_state.get("auto_send_voice", False) and st.session_state.get("voice_text", ""):
        voice_prompt = st.session_state.voice_text
        st.session_state.voice_text = ""
        st.session_state.auto_send_voice = False
        st.session_state.show_voice_input = False
        
        handle_user_prompt(
            voice_prompt.strip(),
            mode,
            system_prompt.strip(),
            model,
            image=st.session_state.uploaded_image
        )
        st.rerun()
    
    # Handle auto-send for enhanced buttons (Concept Explainer, Writing Generator, Bug Debugger)
    if st.session_state.get("auto_send_prompt", False) and st.session_state.get("pending_prompt", ""):
        pending_prompt = st.session_state.pending_prompt
        st.session_state.pending_prompt = ""
        st.session_state.auto_send_prompt = False
        
        handle_user_prompt(
            pending_prompt.strip(),
            mode,
            system_prompt.strip(),
            model,
            image=st.session_state.uploaded_image
        )
        st.rerun()
    
    # Handle regenerate response
    if st.session_state.get("regenerate_index") is not None:
        regen_index = st.session_state.regenerate_index
        st.session_state.regenerate_index = None
        
        messages = get_active_messages()
        if regen_index > 0 and regen_index < len(messages):
            # Get the user message before this assistant response
            user_msg_index = regen_index - 1
            if messages[user_msg_index].get("role") == "user":
                user_prompt_regen = messages[user_msg_index].get("content", "")
                user_image_regen = messages[user_msg_index].get("image")
                
                # Remove the old assistant message
                messages.pop(regen_index)
                
                # Display existing messages
                render_chat_history(messages)
                
                # Generate new response with streaming
                with st.chat_message("assistant", avatar="✨"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    for chunk in send_to_backend(
                        messages,
                        mode=mode,
                        system_prompt=system_prompt.strip(),
                        model=model,
                        image=user_image_regen,
                    ):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                
                messages.append({"role": "assistant", "content": full_response})
                st.rerun()
    
    if user_prompt:
        handle_user_prompt(
            user_prompt.strip(), 
            mode, 
            system_prompt.strip(), 
            model,
            image=st.session_state.uploaded_image
        )
        st.session_state.show_image_upload = False
        st.session_state.show_voice_input = False
        st.rerun()
    st.markdown('---')


if __name__ == "__main__":
    main()
