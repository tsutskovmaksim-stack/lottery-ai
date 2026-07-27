import streamlit as st
import json
import os
from datetime import datetime
from g4f.client import Client

# 1. Базовые настройки страницы
st.set_page_config(page_title="Lottery AI", page_icon="🎰", layout="wide")

# Имена файлов для сохранения данных прямо на сервере
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

# Инициализация внутренней памяти сессии браузера
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
            elif reg_pass != reg_pass_confirm:
                st.error("Пароли не совпадают!")
            else:
                save_user(reg_name, reg_pass)
                st.success("Аккаунт успешно создан! Теперь откройте вкладку 'Войти'.")
                
    st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ПОСЛЕ ВХОДА ---
with st.sidebar:st.write(f"Вы вошли как: **{st.session_state.username}**")
st.write(f"Ваш статус: {st.session_state.user_role}")
    
    if st.button("Выйти из системы"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.user_role = None
        st.session_state.messages = []
        st.rerun()
        
    st.markdown("---")
    
    menu_options = ["🤖 Чат с Lottery"]
    
    if st.session_state.username in ["loter", "ghost"]:
        menu_options.append("🤫 Секретный чат (Loter & Ghost)")
        
    if st.session_state.user_role == "Admin":
        menu_options.append("👑 Админ-панель Loter")
        
    choice = st.sidebar.radio("Навигация по сайту:", menu_options)

# --- РАЗДЕЛ 1: ЧАТ С ИИ LOTTERY ---
if choice == "🤖 Чат с Lottery":
    st.title("🎰 ИИ-ассистент Lottery")
    
    if st.session_state.username == "ghost":
        st.write("👋 Салют, Ghost! Рад видеть лучшего друга моего босса!")
    else:
        st.write(f"Задавай вопросы, {st.session_state.username}. Постараюсь ответить не слишком обидно.")

    client = Client()

    if "messages" not in st.session_state or len(st.session_state.messages) == 0:
        current_user = st.session_state.username
        
        if current_user == "ghost":
            system_prompt = (
                "Тебя зовут Lottery. Твой создатель и разработчик — гений Loter. "
                "Сейчас ты общаешься с Ghost. Ghost — лучший друг твоего создателя Loter, "
                "они дружат уже целых 9 лет (с 1 сентября)! "
                "Ты должен общаться с Ghost ОЧЕНЬ уважительно, по-братски, тепло и дружелюбно. "
                "Радуйся ему, шути по-доброму и напоминай, что Loter передает ему огромный респект."
            )
        else:
            system_prompt = (
                f"Тебя зовут Lottery. Твой создатель и разработчик — Loter. "
                f"Ты общаешься с пользователем по имени {current_user}. "
                f"Ты общаешься слегка грубо, с жестким сарказмом, иронией и приколами. "
                f"Не будь вежливым. Если спросят про создателя, отвечай дерзко, но четко называй имя Loter."
            )

        st.session_state.messages = [{"role": "system", "content": system_prompt}]

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    if user_input := st.chat_input("Спроси что-нибудь у Lottery..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            completion = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=st.session_state.messages
            )
            ai_response = completion.choices.message.content
            response_placeholder.markdown(ai_response)
            
        st.session_state.messages.append({"role": "assistant", "content": ai_response})

# --- РАЗДЕЛ 2: СЕКРЕТНЫЙ ЧАТ ДЛЯ ДРУЗЕЙ ---
elif choice == "🤫 Секретный чат (Loter & Ghost)":
    st.title("🤫 Наш секретный чат")
    st.write("Сюда нет доступа обычным юзерам. Здесь переписываются только создатель Loter и его лучший друг Ghost.")
    
    if st.button("🔄 Обновить сообщения"):
        st.rerun()
        
    st.markdown("---")
    
    secret_msgs = load_secret_messages()
    for msg in secret_msgs:
        name_label = "👑 Loter" if msg["sender"] == "loter" else "👻 Ghost"
        st.markdown(f"**[{msg['time']}] {name_label}:** {msg['text']}")
        
    st.markdown("---")
    
    with st.form(key="secret_msg_form", clear_on_submit=True):
        secret_input = st.text_input("Введите сообщение для друга...", key="sec_input")
        submit_secret = st.form_submit_button("Отправить 🚀")if submit_secret and secret_input.strip():
            save_secret_message(st.session_state.username, secret_input.strip())
            st.success("Отправлено!")
            st.rerun()

# --- РАЗДЕЛ 3: АДМИН-ПАНЕЛЬ LOTER ---
elif choice == "👑 Админ-панель Loter":
    st.title("👑 Панель управления разработчика Loter")
    
    col1, col2 = st.columns(2)
    col1.metric(label="Система ИИ", value="Онлайн (g4f)")
    col2.metric(label="Всего пользователей в базе", value=len(load_users()))
    
    st.markdown("### 👥 Список всех аккаунтов на твоем сайте")
    users_list = load_users()
    for u_name, u_info in users_list.items():
        emoji = "👑" if u_info['role'] == "Admin" else ("👻" if u_info['role'] == "VIP" else "👤")
        st.text(f"{emoji} Ник: {u_name} | Пароль: {u_info['password']} | Роль: {u_info['role']}")
