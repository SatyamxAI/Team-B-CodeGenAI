def init_chat():
    return []

def add_message(chat, role, content):
    chat.append({
        "role": role,
        "content": content
    })
    return chat
