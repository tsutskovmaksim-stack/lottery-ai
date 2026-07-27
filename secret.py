import streamlit as st
import json
import os
from datetime import datetime

st.title("🤫 Секретный чат Loter & Ghost")

SECRET_CHAT_FILE = "secret_chat.json"

def load_msgs():
    if os.path.exists(SECRET_CHAT_FILE):
        with open(SECRET_CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_msg(sender, text):
    msgs = load_msgs()
    time_str = datetime.now().strftime("%d.%m %H:%M")
    msgs.append({"sender": sender, "text": text, "time": time_str})
    with open(SECRET_CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(msgs, f, ensure_ascii=False, indent=4)

if st.button("🔄 Обновить"):
    st.rerun()

for msg in load_msgs():
    label = "👑 Loter" if msg["sender"] == "loter" else "👻 Ghost"
    st.write(f"**[{msg['time']}] {label}:** {msg['text']}")

with st.form(key="msg_form", clear_on_submit=True):
    txt = st.text_input("Сообщение для друга...")
    if st.form_submit_button("Отправить 🚀") and txt.strip():
        # Определяем отправителя из сессии главного файла
        current_user = "loter" # временная заглушка для тестов
        save_msg(current_user, txt.strip())
        st.success("Отправлено!")
        st.rerun()
