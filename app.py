
import streamlit as st
import json
import os
import requests
from datetime import datetime

# 1. Базовые настройки страницы
st.set_page_config(page_title="Lottery AI", page_icon="🎰", layout="wide")

# Имена файлов для баз данных прямо на сервере
DB_FILE = "users_db.json"
SECRET_CHAT_FILE = "secret_chat.json"

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С БАЗОЙ ПОЛЬЗОВАТЕЛЕЙ ---
def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "loter": {"password": "m69l0mja", "role": "Admin"},
        "ghost": {"password": "ghost777", "role": "VIP"}
    }

def save_user(username, password):
    users = load_users()
    users[username.lower()] = {"password": password, "role": "User"}
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С СЕКРЕТНЫМ ЧАТОМ ---
def load_secret_messages():
    if os.path.exists(SECRET_CHAT_FILE):
        with open(SECRET_CHAT_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_secret_message(sender, text):
    messages = load_secret_messages()
    time_str = datetime.now().strftime("%d.%m %H:%M")
    messages.append({"sender": sender, "text": text, "time": time_str})
    with open(SECRET_CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# Инициализация сессии браузера
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None

# --- ИНТЕРФЕЙС ВХОДА И РЕГИСТРАЦИИ ---
if not st.session_state.logged_in:
    st.title("🎰 Добро пожаловать в проект Lottery")
    
    tab1, tab2 = st.tabs(["🔑 Войти", "📝 Зарегистрироваться"])
    
    with tab1:
        st.subheader("Вход в аккаунт")
        login_name = st.text_input("Username (на английском)", key="login_name").strip().lower()
        login_pass = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Войти", key="btn_login"):
            users = load_users()
            if login_name in users and users[login_name]["password"] == login_pass:
                st.session_state.logged_in = True
                st.session_state.username = login_name
                st.session_state.user_role = users[login_name]["role"]
                st.success(f"Успешный вход! Привет, {login_name}.")
                st.rerun()
            else:
                st.error("Неверное имя пользователя или пароль.")
                
    with tab2:
        st.subheader("Создать новый аккаунт")
        reg_name = st.text_input("Придумайте Username (английские буквы)", key="reg_name").strip().lower()
        reg_pass = st.text_input("Придумайте Password", type="password", key="reg_pass")
        reg_pass_confirm = st.text_input("Повторите Password", type="password", key="reg_pass_confirm")
        
        if st.button("Создать аккаунт", key="btn_reg"):
            users = load_users()
            if not reg_name.isalnum():
                st.error("Имя должно состоять только из английских букв и цифр!")
            elif reg_name in ["loter", "ghost"]:
                st.error("Это имя зарезервировано создателями!")
            elif reg_name in users:
                st.error("Такое имя уже занято!")
            elif len(reg_pass) < 4:
                st.error("Пароль должен быть не менее 4 символов!")
