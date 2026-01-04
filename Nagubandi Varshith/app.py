import streamlit as st
import time
import json
import os
from backend.ocr import extract_text_from_image
from backend.normalize import normalize_ocr_text
from backend.prompt import build_image_debug_prompt


from backend.llm import generate_response, generate_title
from backend.prompt import build_prompt
from backend.memory import init_chat, add_message

def save_index(index):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)


def create_new_chat(chat_index):
    ts = int(time.time())
    chat_file = f"chat_{ts}.json"

    chat_index[chat_file] = {
        "title": "New Chat",
        "pinned": False,
        "created_at": ts
    }

    save_index(chat_index)
    
    with open(os.path.join(CHAT_DIR, chat_file), "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)

    return chat_file





# ---------------- CONFIG ----------------
CHAT_DIR = "chats"
INDEX_FILE = os.path.join(CHAT_DIR, "index.json")
os.makedirs(CHAT_DIR, exist_ok=True)

if not os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="CODEGEN AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CSS (MATCH SCREENSHOT) ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg, #0e0e11, #121212);
    color: white;
}

section[data-testid="stSidebar"] {
    background-color: #0b0b0e;
    border-right: 1px solid #1f1f1f;
}

.sidebar-title {
    font-size: 22px;
    font-weight: 600;
}

.chat-title {
    font-size: 36px;
    font-weight: 700;
    text-align: center;
}

.chat-subtitle {
    text-align: center;
    color: #9aa0a6;
    margin-bottom: 20px;
}

.upload-card {
    border: 1px dashed #2a2a2a;
    border-radius: 14px;
    padding: 20px;
    background-color: #15151a;
    margin-bottom: 20px;
}

.upload-card small {
    color: #9aa0a6;
}

div[data-testid="stChatInput"] textarea {
    background-color: #1a1a1f;
    border-radius: 30px;
    border: 1px solid #2a2a2a;
    padding: 16px;
    color: white;
}

.stChatMessage {
    padding: 10px;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ---------------- SESSION STATE ----------------
if "chat" not in st.session_state:
    st.session_state.chat = init_chat()

if "current_chat_file" not in st.session_state:
    st.session_state.current_chat_file = None

if "uploaded_context" not in st.session_state:
    st.session_state.uploaded_context = ""

# ---------------- LOAD CHAT INDEX ----------------
with open(INDEX_FILE, "r", encoding="utf-8") as f:
    chat_index = json.load(f)
    


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("##  CODEGEN AI")
    st.caption("AI coding assistant")

    # -------- New Chat --------
    if st.button("➕ New Chat", use_container_width=True):
        st.session_state.chat = init_chat()
        st.session_state.uploaded_context = ""
        st.session_state.current_chat_file = create_new_chat(chat_index)
        st.rerun()

    st.divider()

    # -------- Search --------
    search_query = st.text_input(
        "Search chats",
        placeholder="Search by title…"
    ).lower()

    st.divider()
    st.markdown("### Chats")

    # -------- Sort chats (Pinned → Recent) --------
    sorted_chats = sorted(
        chat_index.items(),
        key=lambda x: (
            not x[1]["pinned"],        # pinned first
            -x[1]["created_at"]        # newest first
        )
    )

    for file, meta in sorted_chats:
        title = meta["title"]

        if search_query and search_query not in title.lower():
            continue

        row = st.columns([6, 1, 1, 1])

        # ---- Open chat ----
        with row[0]:
            if st.button(title, key=f"open_{file}", use_container_width=True):
                with open(os.path.join(CHAT_DIR, file), "r", encoding="utf-8") as f:
                    st.session_state.chat = json.load(f)
                st.session_state.current_chat_file = file
                st.rerun()

        # ---- Pin / Unpin ----
        with row[1]:
            if st.button("📌" if not meta["pinned"] else "📍", key=f"pin_{file}"):
                chat_index[file]["pinned"] = not meta["pinned"]
                save_index(chat_index)
                st.rerun()

        # ---- Rename ----
        with row[2]:
            if st.button("✏️", key=f"rename_{file}"):
                new_title = st.text_input(
                    "Rename chat",
                    value=title,
                    key=f"rename_input_{file}"
                )
                if new_title.strip():
                    chat_index[file]["title"] = new_title.strip()
                    save_index(chat_index)
                    st.rerun()

        # ---- Delete ----
        with row[3]:
            if st.button("🗑️", key=f"delete_{file}"):
                os.remove(os.path.join(CHAT_DIR, file))
                chat_index.pop(file)
                save_index(chat_index)

                if st.session_state.current_chat_file == file:
                    st.session_state.chat = init_chat()
                    st.session_state.current_chat_file = None

                st.rerun()
            
# ---------------- MAIN HEADER ----------------
st.markdown("<div class='chat-title'>CODEGEN AI</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='chat-subtitle'>Your AI-powered coding assistant. Upload files and get code suggestions.</div>",
    unsafe_allow_html=True
)

# ---------------- ATTACH FILES UI ----------------
st.markdown("""
<div class="upload-card">
<b>📎 Attach files</b><br><br>
Drag and drop files here<br>
<small>TXT, MD, PY, JAVA, JS</small>
</div>
""", unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Upload code / error screenshot",
    type=["txt", "md", "py", "java", "js", "png", "jpg", "jpeg"],
    label_visibility="collapsed"
)


    
from backend.ocr import extract_text_from_image
from backend.prompt import build_image_debug_prompt


if uploaded_file and uploaded_file.type.startswith("image"):
    with st.spinner("Analyzing code from image..."):
        ocr_text = extract_text_from_image(uploaded_file)

        prompt = build_image_debug_prompt(ocr_text)

        with st.chat_message("assistant"):
            box = st.empty()
            full_response = ""

            for chunk in generate_response(
                prompt,
                model="deepseek-coder:6.7b",
                stream=True
            ):
                full_response += chunk
                box.markdown(full_response)

        st.session_state.chat.append({
            "role": "assistant",
            "content": full_response
        })



# ---------------- CHAT DISPLAY ----------------
for i, msg in enumerate(st.session_state.chat):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=False)
        
# ---------------- USER INPUT ----------------
if user_input := st.chat_input("Message..."):
    st.session_state.chat = add_message(
        st.session_state.chat, "user", user_input
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    context = ""
    if st.session_state.uploaded_context:
        context = (
            "\nCONTEXT FROM FILE:\n"
            + st.session_state.uploaded_context
            + "\nEND CONTEXT\n"
        )

    prompt = build_prompt(st.session_state.chat) + context

    with st.chat_message("assistant"):
        box = st.empty()
        full_response = ""
        cursor = True

        with st.spinner("Thinking..."):
            for chunk in generate_response(prompt, model="llama3", stream=True):
                full_response += chunk
                box.markdown(
                    full_response + ("▍" if cursor else ""),
                    unsafe_allow_html=False
                )
                cursor = not cursor
                time.sleep(0.03)

        box.markdown(full_response, unsafe_allow_html=False)

    st.session_state.chat = add_message(
        st.session_state.chat, "assistant", full_response
    )

    # -------- AUTO CHAT NAMING (LLAMA) --------
       
    current_file = st.session_state.current_chat_file

    if (
        current_file
        and chat_index[current_file]["title"] == "New Chat"
    ):
        title = generate_title(user_input)
        chat_index[current_file]["title"] = title or user_input[:30]
        save_index(chat_index)

    # -------- SAVE CHAT CONTENT --------
    if current_file :
        with open(
        os.path.join(CHAT_DIR, current_file),
        "w",
        encoding="utf-8"
        ) as f:
            json.dump(st.session_state.chat, f, indent=2)

    st.rerun()