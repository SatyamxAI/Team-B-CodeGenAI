import streamlit as st
import uuid
import ollama
import re
from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes

# ---------------- TESSERACT PATH (CRITICAL) ----------------
# CHANGE THIS IF YOUR INSTALL PATH IS DIFFERENT
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="CodeGenAI", layout="wide")

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.chat-user { display: flex; justify-content: flex-end; margin-bottom: 10px; }
.chat-bot { display: flex; justify-content: flex-start; margin-bottom: 10px; }
.chat-bubble {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 15px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-wrap: break-word;
}
.user-bubble { background-color: #2b313e; color: #ffffff; }
.bot-bubble { background-color: #1f242d; color: #ffffff; border: 1px solid #3d4450; }
</style>
""", unsafe_allow_html=True)

# ---------------- OCR HELPER ----------------
def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.type in ["image/png", "image/jpeg", "image/jpg"]:
            image = Image.open(uploaded_file)
            return pytesseract.image_to_string(image)

        elif uploaded_file.type == "application/pdf":
            images = convert_from_bytes(uploaded_file.read())
            text = []
            for img in images:
                text.append(pytesseract.image_to_string(img))
            return "\n".join(text)

    except Exception as e:
        return f"OCR Error: {str(e)}"

    return ""

# ---------------- SESSION STATE ----------------
if "username" not in st.session_state:
    st.session_state.username = None

if "chats" not in st.session_state:
    st.session_state.chats = {}

if "active_chat" not in st.session_state:
    st.session_state.active_chat = None

# ---------------- LOGIN ----------------
if st.session_state.username is None:
    st.title("Welcome to CodeGenAI")
    name = st.text_input("Enter your name")
    if st.button("START") and name.strip():
        st.session_state.username = name.strip()
        st.rerun()
    st.stop()

# ---------------- CHAT CREATION ----------------
def new_chat():
    cid = str(uuid.uuid4())[:8]
    st.session_state.chats[cid] = {
        "title": "New Chat",
        "messages": [],
        "ocr_text": "",
        "file_name": None
    }
    st.session_state.active_chat = cid
    st.rerun()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("CodeGenAI")
    st.caption(f"Logged in as: {st.session_state.username}")

    if st.button("➕ New Chat", use_container_width=True):
        new_chat()

    st.divider()

    for cid, chat in reversed(list(st.session_state.chats.items())):
        col1, col2 = st.columns([5, 1])

        if col1.button(chat["title"], key=f"chat_{cid}", use_container_width=True):
            st.session_state.active_chat = cid
            st.rerun()

        if col2.button("⛔", key=f"del_{cid}"):
            del st.session_state.chats[cid]
            if not st.session_state.chats:
                new_chat()
            else:
                st.session_state.active_chat = list(st.session_state.chats.keys())[-1]
            st.rerun()

# ---------------- MAIN UI ----------------
if not st.session_state.active_chat:
    new_chat()

current_chat = st.session_state.chats[st.session_state.active_chat]

st.subheader(f"What’s on the agenda today, {st.session_state.username}?")

chat_container = st.container()

# ---------------- MESSAGE RENDERING ----------------
code_block_pattern = re.compile(r"```(\w+)?\n(.*?)```", re.DOTALL)

def render_assistant_message(content):
    last_end = 0
    for match in code_block_pattern.finditer(content):
        text = content[last_end:match.start()].strip()
        if text:
            st.markdown(
                f'<div class="chat-bot"><div class="chat-bubble bot-bubble">{text}</div></div>',
                unsafe_allow_html=True
            )
        st.code(match.group(2), language=match.group(1))
        last_end = match.end()

    tail = content[last_end:].strip()
    if tail:
        st.markdown(
            f'<div class="chat-bot"><div class="chat-bubble bot-bubble">{tail}</div></div>',
            unsafe_allow_html=True
        )

# ---------------- CHAT HISTORY ----------------
with chat_container:
    for msg in current_chat["messages"]:
        if msg["role"] == "user":
            st.markdown(
                f'<div class="chat-user"><div class="chat-bubble user-bubble">{msg["content"]}</div></div>',
                unsafe_allow_html=True
            )
        else:
            render_assistant_message(msg["content"])

# ---------------- FILE UPLOAD ----------------
st.divider()

uploaded_file = st.file_uploader(
    "Upload context",
    type=["png", "jpg", "jpeg", "pdf"],
    label_visibility="collapsed"
)

if uploaded_file and current_chat.get("file_name") != uploaded_file.name:
    with st.status("Reading file..."):
        current_chat["ocr_text"] = extract_text_from_file(uploaded_file)
        current_chat["file_name"] = uploaded_file.name
    st.toast("OCR context added")

# ---------------- CHAT INPUT ----------------
prompt = st.chat_input("Message CodeGenAI...")

# ---------------- AI RESPONSE ----------------
if prompt:
    current_chat["messages"].append({"role": "user", "content": prompt})

    if current_chat["title"] == "New Chat":
        current_chat["title"] = prompt[:20]

    with chat_container:
        st.markdown(
            f'<div class="chat-user"><div class="chat-bubble user-bubble">{prompt}</div></div>',
            unsafe_allow_html=True
        )

    system_prompt = (
        "You are CodeGenAI, a professional coding assistant. "
        f"User name: {st.session_state.username}."
    )

    if current_chat["ocr_text"]:
        system_prompt += f"\n\nContext from uploaded file:\n{current_chat['ocr_text']}"

    messages = [{"role": "system", "content": system_prompt}]
    messages += current_chat["messages"][:-1]
    messages.append({"role": "user", "content": prompt})

    try:
        with chat_container:
            full_reply = ""
            placeholder = st.empty()

            stream = ollama.chat(
                model="codellama:7b",
                messages=messages,
                stream=True
            )

            for chunk in stream:
                full_reply += chunk["message"]["content"]
                with placeholder.container():
                    render_assistant_message(full_reply)

            current_chat["messages"].append(
                {"role": "assistant", "content": full_reply}
            )
            st.rerun()

    except Exception as e:
        st.error(f"LLM Error: {str(e)}")
