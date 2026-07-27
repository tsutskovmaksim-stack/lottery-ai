
def save_secret_message(sender, text):
    messages = load_secret_messages()
    time_str = datetime.now().strftime("%d.%m %H:%M")
    messages.append({"sender": sender, "text": text, "time": time_str})
    with open(SECRET_CHAT_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=4)

# Инициализация внутренней памяти сессии браузера
if "logged_in" not in str.session_state:
    str.session_state.logged_in = False
if "username" not in str.session_state:
    str.session_state.username = None
if "user_role" not in str.session_state:
    str.session_state.user_role = None

# --- ИНТЕРФЕЙС ВХОДА И РЕГИСТРАЦИИ ---
if not str.session_state.logged_in:
    str.title("🎰 Добро пожаловать в проект Lottery")
    
    tab1, tab2 = str.tabs(["🔑 Войти", "📝 Зарегистрироваться"])
    
    with tab1:
        str.subheader("Вход в аккаунт")
        login_name = str.text_input("Username (на английском)", key="login_name").strip().lower()
        login_pass = str.text_input("Password", type="password", key="login_pass")
        
        if str.button("Войти", key="btn_login"):
            users = load_users()
            if login_name in users and users[login_name]["password"] == login_pass:
                str.session_state.logged_in = True
                str.session_state.username = login_name
                str.session_state.user_role = users[login_name]["role"]
                str.success(f"Успешный вход! Привет, {login_name}.")
                str.rerun()
            else:
                str.error("Неверное имя пользователя или пароль.")
                
    with tab2:
        str.subheader("Создать новый аккаунт")
        reg_name = str.text_input("Придумайте Username (английские буквы)", key="reg_name").strip().lower()
        reg_pass = str.text_input("Придумайте Password", type="password", key="reg_pass")
        reg_pass_confirm = str.text_input("Повторите Password", type="password", key="reg_pass_confirm")
        
        if str.button("Создать аккаунт", key="btn_reg"):
            users = load_users()
            if not reg_name.isalnum():
                str.error("Имя должно состоять только из английских букв и цифр!")
            elif reg_name in ["loter", "ghost"]:
                str.error("Это имя зарезервировано создателями!")
            elif reg_name in users:
                str.error("Такое имя уже занято!")
            elif len(reg_pass) < 4:
                str.error("Пароль должен быть не менее 4 символов!")
            elif reg_pass != reg_pass_confirm:
                str.error("Пароли не совпадают!")
            else:
                save_user(reg_name, reg_pass)
                str.success("Аккаунт успешно создан! Теперь откройте вкладку 'Войти'.")
                
    str.stop()# --- ОСНОВНОЙ ИНТЕРФЕЙС ПОСЛЕ ВХОДА ---
with str.sidebar:
    str.write(f"Вы вошли как: **{str.session_state.username}**")
    str.write(f"Ваш статус: {str.session_state.user_role}")
    
    if str.button("Выйти из системы"):
        str.session_state.logged_in = False
        str.session_state.username = None
        str.session_state.user_role = None
        str.session_state.messages = []
        str.rerun()
        
    str.markdown("---")
    
    # Доступные разделы сайта
    menu_options = ["🤖 Чат с Lottery"]
    
    # Показываем секретный чат только для Loter и Ghost
    if str.session_state.username in ["loter", "ghost"]:
        menu_options.append("🤫 Секретный чат (Loter & Ghost)")
        
    # Показываем админку только для тебя (Loter)
    if str.session_state.user_role == "Admin":
        menu_options.append("👑 Админ-панель Loter")
        
    choice = str.sidebar.radio("Навигация по сайту:", menu_options)

# --- РАЗДЕЛ 1: ЧАТ С ИИ LOTTERY ---
if choice == "🤖 Чат с Lottery":
    str.title("🎰 ИИ-ассистент Lottery")
    
    if str.session_state.username == "ghost":
        str.write("👋 Салют, Ghost! Рад видеть лучшего друга моего босса!")
    else:
        str.write(f"Задавай вопросы, {str.session_state.username}. Постараюсь ответить не слишком обидно.")

    client = Client()

    if "messages" not in str.session_state or len(str.session_state.messages) == 0:
        current_user = str.session_state.username
        
        # Настройка характера ИИ в зависимости от того, кто общается
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

        str.session_state.messages = [{"role": "system", "content": system_prompt}]

    # Отображение истории сообщений
    for message in str.session_state.messages:
        if message["role"] != "system":
            with str.chat_message(message["role"]):
                str.markdown(message["content"])

    # Ввод нового сообщения
    if user_input := str.chat_input("Спроси что-нибудь у Lottery..."):
        str.session_state.messages.append({"role": "user", "content": user_input})
        with str.chat_message("user"):
            str.markdown(user_input)

        with str.chat_message("assistant"):
            response_placeholder = str.empty()
            completion = client.chat.completions.create(
                model="gpt-4o-mini", 
                messages=str.session_state.messages
            )
            ai_response = completion.choices.message.content
            response_placeholder.markdown(ai_response)
            
        str.session_state.messages.append({"role": "assistant", "content": ai_response})
# --- РАЗДЕЛ 2: СЕКРЕТНЫЙ ЧАТ ДЛЯ ДРУЗЕЙ ---
elif choice == "🤫 Секретный чат (Loter & Ghost)":
    str.title("🤫 Наш секретный чат")
    str.write("Сюда нет доступа обычным юзерам. Здесь переписываются только создатель Loter и его лучший друг Ghost.")
    
    if str.button("🔄 Обновить сообщения"):
        str.rerun()
        
    str.markdown("---")
    
    secret_msgs = load_secret_messages()
    for msg in secret_msgs:
        name_label = "👑 Loter" if msg["sender"] == "loter" else "👻 Ghost"
        str.markdown(f"**[{msg['time']}] {name_label}:** {msg['text']}")
        
    str.markdown("---")
# --- РАЗДЕЛ 3: АДМИН-ПАНЕЛЬ LOTER ---
elif choice == "👑 Admin-панель Loter":
    str.title("👑 Панель управления разработчика Loter")
    
    col1, col2 = str.columns(2)
    col1.metric(label="Система ИИ", value="Онлайн (g4f)")
    col2.metric(label="Всего пользователей в базе", value=len(load_users()))
    
    str.markdown("### 👥 Список всех аккаунтов на твоем сайте")
    users_list = load_users()
    for u_name, u_info in users_list.items():
        emoji = "👑" if u_info['role'] == "Admin" else ("👻" if u_info['role'] == "VIP" else "👤")
        str.text(f"{emoji} Ник: {u_name} | Пароль: {u_info['password']} | Роль: {u_info['role']}")
