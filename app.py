import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Опора 🌱", layout="wide")

# Подключение к Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
# ТВОЙ ID ТАБЛИЦЫ (Уже вставлен!)
SPREADSHEET_ID = "1oc_E2IHKjJZSjt9fscY93srN77sNeN4qjqFrP4QkRN0"
# Полный URL для надежности
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

# --- 2. ФУНКЦИИ РАБОТЫ С ТАБЛИЦЕЙ ---

def load_sheet(sheet_name):
    try:
        # Открываем через полный URL, так надежнее
        return conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
    except Exception:
        cols = {
            "Users": ["Имя", "Пароль"],
            "Chats": ["ID_Чата", "Пользователь", "Заголовок", "Роль", "Сообщение", "Дата"],
            "Support": ["Дата", "Пользователь", "Сообщение"]
        }
        return pd.DataFrame(columns=cols.get(sheet_name, []))

def save_sheet(sheet_name, df):
    # Очищаем данные от пустых строк перед сохранением
    df = df.dropna(how='all')
    conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)

# --- 3. ФУНКЦИЯ ДЛЯ ИИ ---
def ask_ai(messages, system_prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        full_context = [{"role": "system", "content": system_prompt}] + messages
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_context,
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка ИИ: {e}"

# --- 4. ЛОГИКА ВХОДА ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Система Опора")
    choice = st.radio("Действие:", ["Вход", "Регистрация"])
    
    with st.form("auth_form"):
        u_name = st.text_input("Имя пользователя")
        u_pwd = st.text_input("Пароль", type="password")
        if st.form_submit_button("Подтвердить"):
            users_df = load_sheet("Users")
            if choice == "Вход":
                if not users_df.empty and not users_df[(users_df['Имя'] == u_name) & (users_df['Пароль'] == u_pwd)].empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u_name
                    st.rerun()
                else:
                    st.error("Неверное имя или пароль")
            else:
                if not users_df.empty and u_name in users_df['Имя'].values:
                    st.error("Это имя уже занято")
                elif u_name and u_pwd:
                    new_user = pd.DataFrame([{"Имя": u_name, "Пароль": u_pwd}])
                    # Сохраняем и проверяем
                    combined_users = pd.concat([users_df, new_user], ignore_index=True)
                    save_sheet("Users", combined_users)
                    st.success("Аккаунт создан! Теперь перейдите во 'Вход' и введите данные.")
    st.stop()

# --- 5. МЕНЮ ЧАТОВ (САЙДБАР) ---
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

with st.sidebar:
    st.title(f"👤 {st.session_state.user_name}")
    if st.button("➕ Новый чат", use_container_width=True):
        st.session_state.active_chat_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    all_chats = load_sheet("Chats")
    
    if not all_chats.empty:
        my_chats = all_chats[all_chats['Пользователь'] == st.session_state.user_name]
        if not my_chats.empty:
            chat_list = my_chats[['ID_Чата', 'Заголовок']].drop_duplicates(subset=['ID_Чата'], keep='last')
            for _, row in chat_list[::-1].iterrows():
                if st.button(f"💬 {row['Заголовок']}", key=row['ID_Чата'], use_container_width=True):
                    st.session_state.active_chat_id = row['ID_Чата']
                    st.rerun()

    st.divider()
    with st.expander("🆘 Поддержка"):
        with st.form("sup", clear_on_submit=True):
            support_msg = st.text_area("Ваш вопрос")
            if st.form_submit_button("Отправить"):
                sup_df = load_sheet("Support")
                new_sup = pd.DataFrame([{"Дата": datetime.now().strftime("%d.%m %H:%M"), "Пользователь": st.session_state.user_name, "Сообщение": support_msg}])
                save_sheet("Support", pd.concat([sup_df, new_sup], ignore_index=True))
                st.success("Отправлено!")

# --- 6. ОСНОВНОЙ ЭКРАН ЧАТА ---
if not st.session_state.active_chat_id:
    st.title("🌱 Опора")
    st.info("Создайте или выберите чат слева, чтобы начать.")
else:
    # Загружаем сообщения этого чата
    this_chat_data = all_chats[all_chats['ID_Чата'] == st.session_state.active_chat_id] if not all_chats.empty else pd.DataFrame()
    current_title = this_chat_data['Заголовок'].iloc[0] if not this_chat_data.empty else "Новый диалог"
    
    st.title(f"💬 {current_title}")

    history_for_ai = []
    if not this_chat_data.empty:
        for _, row in this_chat_data.iterrows():
            with st.chat_message(row['Роль']):
                st.markdown(row['Сообщение'])
            history_for_ai.append({"role": row['Роль'], "content": row['Сообщение']})

    if prompt := st.chat_input("Напишите сообщение..."):
        if this_chat_data.empty:
            with st.spinner("Генерация темы..."):
                current_title = ask_ai([{"role": "user", "content": prompt}], "Придумай название из 2 слов. Только текст.")
                current_title = current_title.strip().replace('"', '')

        with st.chat_message("user"):
            st.markdown(prompt)
        u_row = pd.DataFrame([{"ID_Чата": st.session_state.active_chat_id, "Пользователь": st.session_state.user_name, "Заголовок": current_title, "Роль": "user", "Сообщение": prompt, "Дата": datetime.now().strftime("%Y-%m-%d %H:%M")}])

        with st.chat_message("assistant"):
            ans = ask_ai(history_for_ai + [{"role": "user", "content": prompt}], "Ты Опора. Мудрый друг. Отвечай тепло и кратко.")
            st.markdown(ans)
        a_row = pd.DataFrame([{"ID_Чата": st.session_state.active_chat_id, "Пользователь": st.session_state.user_name, "Заголовок": current_title, "Роль": "assistant", "Сообщение": ans, "Дата": datetime.now().strftime("%Y-%m-%d %H:%M")}])

        # Сохраняем всё вместе
        updated_data = pd.concat([all_chats, u_row, a_row], ignore_index=True)
        save_sheet("Chats", updated_data)
        st.rerun()
