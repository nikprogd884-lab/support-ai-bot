import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="Опора 🌱", layout="wide")

# Подключение к Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Ошибка подключения к базе: {e}")

# --- ФУНКЦИИ ДЛЯ РАБОТЫ С ДАННЫМИ ---

def load_sheet(name):
    """Загрузка данных из конкретного листа"""
    try:
        return conn.read(worksheet=name, ttl=0)
    except:
        # Если лист пустой, возвращаем пустой DF с нужными колонками
        cols = {
            "Users": ["Имя", "Пароль"],
            "Chats": ["ID_Чата", "Пользователь", "Заголовок", "Роль", "Сообщение", "Дата"],
            "Support": ["Дата", "Пользователь", "Сообщение"]
        }
        return pd.DataFrame(columns=cols.get(name, []))

def save_sheet(name, df):
    """Сохранение данных в лист"""
    conn.update(worksheet=name, data=df)

def ask_ai(messages, system_prompt, max_tokens=300):
    """Запрос к нейросети Groq"""
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    full_messages = [{"role": "system", "content": system_prompt}] + messages
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=full_messages,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content

# --- ЛОГИКА ВХОДА И РЕГИСТРАЦИИ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Добро пожаловать в Опору")
    choice = st.radio("Выберите действие:", ["Вход", "Регистрация"])
    
    with st.form("auth_form"):
        u_name = st.text_input("Имя пользователя")
        u_pwd = st.text_input("Пароль", type="password")
        if st.form_submit_button("Подтвердить"):
            users_df = load_sheet("Users")
            
            if choice == "Вход":
                user_match = users_df[(users_df['Имя'] == u_name) & (users_df['Пароль'] == u_pwd)]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u_name
                    st.rerun()
                else:
                    st.error("Неверное имя или пароль")
            else:
                if u_name in users_df['Имя'].values:
                    st.error("Это имя уже занято")
                elif u_name and u_pwd:
                    new_user = pd.DataFrame([{"Имя": u_name, "Пароль": u_pwd}])
                    save_sheet("Users", pd.concat([users_df, new_user], ignore_index=True))
                    st.success("Аккаунт создан! Теперь войдите.")
                else:
                    st.warning("Заполните все поля")
    st.stop()

# --- ПОДГОТОВКА СЕССИИ ---
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# --- БОКОВАЯ ПАНЕЛЬ (САЙДБАР) ---
with st.sidebar:
    st.title(f"👤 {st.session_state.user_name}")
    
    if st.button("➕ Новый чат", use_container_width=True):
        st.session_state.current_chat_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    st.subheader("📂 Ваши переписки")
    
    all_chats = load_sheet("Chats")
    # Фильтруем чаты текущего пользователя
    user_chats = all_chats[all_chats['Пользователь'] == st.session_state.user_name]
    
    # Список уникальных чатов для меню
    if not user_chats.empty:
        chat_menu = user_chats[['ID_Чата', 'Заголовок']].drop_duplicates(subset=['ID_Чата'], keep='last')
        for _, row in chat_menu[::-1].iterrows(): # Показываем последние сверху
            if st.button(f"💬 {row['Заголовок']}", key=row['ID_Чата'], use_container_width=True):
                st.session_state.current_chat_id = row['ID_Чата']
                st.rerun()
    else:
        st.info("У вас пока нет чатов")

    st.divider()
    
    # Форма техподдержки
    with st.expander("🆘 Написать разработчику"):
        with st.form("support_form", clear_on_submit=True):
            support_msg = st.text_area("Ваше сообщение")
            if st.form_submit_button("Отправить"):
                if support_msg:
                    sup_df = load_sheet("Support")
                    new_entry = pd.DataFrame([{
                        "Дата": datetime.now().strftime("%d.%m.%Y %H:%M"),
                        "Пользователь": st.session_state.user_name,
                        "Сообщение": support_msg
                    }])
                    save_sheet("Support", pd.concat([sup_df, new_entry], ignore_index=True))
                    st.success("Отправлено в базу!")

    # Админка
    with st.expander("⚙️ Админ-панель"):
        if st.text_input("Пароль администратора", type="password") == "240610":
            st.write("Все чаты пользователей:")
            st.dataframe(all_chats)

# --- ОСНОВНАЯ ОБЛАСТЬ ЧАТА ---
if not st.session_state.current_chat_id:
    st.title("🌱 Опора")
    st.write("Я — Опора, твой мудрый проводник. Выбери существующий чат или создай новый, чтобы начать.")
else:
    # Загружаем сообщения текущего чата
    this_chat = all_chats[all_chats['ID_Чата'] == st.session_state.current_chat_id]
    
    # Определяем заголовок
    current_title = this_chat['Заголовок'].iloc[0] if not this_chat.empty else "Новый диалог"
    st.title(f"💬 {current_title}")

    # Показываем историю переписки
    chat_history_for_ai = []
    for _, row in this_chat.iterrows():
        with st.chat_message(row['Роль']):
            st.markdown(row['Сообщение'])
        chat_history_for_ai.append({"role": row['Роль'], "content": row['Сообщение']})

    # Поле ввода
    if user_input := st.chat_input("Напишите что-нибудь..."):
        
        # Если это самое первое сообщение в чате — придумываем заголовок
        if this_chat.empty:
            with st.spinner("Создаю тему чата..."):
                current_title = ask_ai([{"role": "user", "content": user_input}], 
                                       "Придумай очень короткий заголовок (2-3 слова) для этого сообщения. Ответь только названием.")
                current_title = current_title.strip().replace('"', '')

        # 1. Показываем и сохраняем сообщение пользователя
        with st.chat_message("user"):
            st.markdown(user_input)
        
        user_row = pd.DataFrame([{
            "ID_Чата": st.session_state.current_chat_id,
            "Пользователь": st.session_state.user_name,
            "Заголовок": current_title,
            "Роль": "user",
            "Сообщение": user_input,
            "Дата": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])
        
        # 2. Получаем и сохраняем ответ ИИ
        with st.chat_message("assistant"):
            sys_prompt = "Ты Опора, теплый и мудрый наставник. Отвечай кратко (1-3 предложения), давай поддержку."
            ai_response = ask_ai(chat_history_for_ai + [{"role": "user", "content": user_input}], sys_prompt)
            st.markdown(ai_response)
        
        ai_row = pd.DataFrame([{
            "ID_Чата": st.session_state.current_chat_id,
            "Пользователь": st.session_state.user_name,
            "Заголовок": current_title,
            "Role": "assistant", # Для совместимости
            "Роль": "assistant",
            "Сообщение": ai_response,
            "Дата": datetime.now().strftime("%Y-%m-%d %H:%M")
        }])

        # Обновляем общую таблицу и сохраняем
        updated_chats = pd.concat([all_chats, user_row, ai_row], ignore_index=True)
        save_sheet("Chats", updated_chats)
        
        st.rerun()
