import streamlit as st
from ollama import Client
import numpy as np
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import io
import easyocr

# ---------------- Models ----------------
VISION_MODEL = "llava"
TEXT_MODEL = "llama3"

ollama_client = Client(host='http://localhost:11434')

@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'], gpu=False)

ocr_reader = load_ocr()

def generate_chat_title(user_msg):
    try:
        prompt = f"Give a short title (3 words) based on this message: '{user_msg}'. Do NOT add quotes."
        response = ollama_client.chat(
            model=TEXT_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except:
        return "New Chat"
    
def extract_text_from_image(image_bytes):
    """
    Advanced OCR Pipeline:
    1. Grayscale & Contrast boost
    2. Sharpness enhancement
    3. EasyOCR detection
    """
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    # --- PRE-PROCESSING FOR 90%+ ACCURACY ---
    # Convert to grayscale to remove color noise
    gray = ImageOps.grayscale(image)
    # Increase contrast significantly (helps separate text from background)
    enhancer = ImageEnhance.Contrast(gray)
    gray = enhancer.enhance(2.5)
    # Sharpen the image to make characters crisper
    gray = gray.filter(ImageFilter.SHARPEN)
    # --- OCR DETECTION ---
    img_array = np.array(gray)
    results = ocr_reader.readtext(img_array, paragraph=True) # paragraph=True maintains block structure
    extracted_text = "\n".join([res[1] for res in results])
    return extracted_text.strip()

st.set_page_config(page_title="Code GENI", layout="wide")

# ---------------- CSS (Corrected for Sidebar) ----------------
st.markdown("""
<style>
/* 1. Force ALL sidebar buttons (New Chat & Chat history) to be full width */
[data-testid="stSidebar"] [data-testid="stBaseButton-secondary"], 
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
    width: 100% !important;
    display: block !important;
    border-radius: 10px !important;
    height: 35px !important;
    border: 1px solid #ddd !important;
}

/* 2. Specific fix for the Trash button: Make it a square and prevent it from stretching */
[data-testid="stSidebar"] [data-testid="column"]:nth-of-type(2) button {
    width: 35px !important;
    min-width: 35px !important;
    padding: 0 !important;
}

/* 3. Red Primary Button Styling (matching your image) */
div.stButton > button[kind="primary"] {
    background-color: #ff4b4b !important;
    color: white !important;
    border: none !important;
}

/* Footer container (unchanged) */
.fixed-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    background: white;
    padding: 10px 20px 20px 20px;
    z-index: 1000;
    border-top: 1px solid #eee;
}

/* Plus Button square styling (unchanged) */
div.stButton > button[kind="secondary"]:not([data-testid="stSidebar"] button) {
    border-radius: 10px !important;
    border: 1px solid #ddd !important;
    height: 35px !important;
    width: 35px !important;
    background-color: white;
}

div[data-testid="stChatInput"] textarea {
    border-radius: 25px !important;
}

.main-content {
    margin-bottom: 100px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- Session States ----------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = {"Chat 1": []}
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "Chat 1"
if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.chat_history["Chat 1"]
if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = False
if "pending_image" not in st.session_state:
    st.session_state.pending_image = None

# ---------------- Sidebar (Updated) ----------------
with st.sidebar:
    st.markdown("<div style='font-size:30px; font-weight:800; text-align:center; margin-bottom:10px;'>CODE GENI</div>", unsafe_allow_html=True)
    
    # New chat button stays outside columns to span full width
    if st.button("New chat", key="new_chat_btn", use_container_width=True):
        new_chat_name = f"Chat {len(st.session_state.chat_history) + 1}"
        st.session_state.chat_history[new_chat_name] = []
        st.session_state.current_chat = new_chat_name
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    for chat_name in list(st.session_state.chat_history.keys()):
        is_selected = chat_name == st.session_state.current_chat
        # Use columns for chat name and delete icon
        col1, col2 = st.columns([5,1]) 
        
        with col1:
            # Selected chat uses 'primary' (Red) while others use 'secondary' (White)
            if st.button(chat_name, key=f"btn_{chat_name}", type="primary" if is_selected else "secondary", use_container_width=True):
                st.session_state.current_chat = chat_name
                st.session_state.messages = st.session_state.chat_history[chat_name]
                st.rerun()
        with col2:
            if st.button("🗑", key=f"del_{chat_name}", use_container_width=True):
                if len(st.session_state.chat_history) > 1:
                    st.session_state.chat_history.pop(chat_name)
                    if is_selected:
                        st.session_state.current_chat = list(st.session_state.chat_history.keys())[0]
                st.rerun()

# ---------------- Chat Display (Unchanged) ----------------
st.title("What Can I Help With?")

st.markdown('<div class="main-content">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Fixed Footer (Unchanged) ----------------
st.markdown('<div class="fixed-footer">', unsafe_allow_html=True)

if st.session_state.show_uploader:
    with st.container():
        uploaded = st.file_uploader(
            "Attach image",
            type=["png", "jpg", "jpeg"],
            label_visibility="collapsed"
        )
        if uploaded:
            st.session_state.pending_image = uploaded.getvalue()
            st.image(uploaded, width=100)

col_btn, col_input = st.columns([1, 15]) 

with col_btn:
    if st.button("＋", key="plus-btn"):
        st.session_state.show_uploader = not st.session_state.show_uploader
        st.rerun()

with col_input:
    user_msg = st.chat_input("Type your message here...")

st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SEND LOGIC (Unchanged) ----------------
if user_msg:
    st.session_state.messages.append({"role": "user", "content": user_msg})

    payload = {"role": "user", "content": user_msg}
    model = TEXT_MODEL

    if st.session_state.pending_image:
        extracted_text = extract_text_from_image(st.session_state.pending_image)

        ocr_prompt = (
            f"The following text was extracted from an image using OCR:\n\n"
            f"{extracted_text if extracted_text else 'No readable text found.'}\n\n"
            f"Now answer the user query based on this text:\n"
            f"'{user_msg}'"
        )

        payload["content"] = ocr_prompt
        model = TEXT_MODEL 

    if st.session_state.current_chat.startswith("Chat"):
        new_title = generate_chat_title(user_msg)
        st.session_state.chat_history[new_title] = st.session_state.chat_history.pop(
            st.session_state.current_chat
        )
        st.session_state.current_chat = new_title

    with st.chat_message("assistant"):
        try:
            response = ollama_client.chat(
                model=model,
                messages=[payload]
            )
            reply = response["message"]["content"]
            st.write(reply)
        except Exception as e:
            reply = f"Error: {e}"
            st.error(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.session_state.chat_history[st.session_state.current_chat] = st.session_state.messages

    st.session_state.pending_image = None
    st.session_state.show_uploader = False
    st.rerun()