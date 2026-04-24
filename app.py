import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- 1. НАСТРОЙКИ СТРАНИЦЫ ---
st.set_page_config(page_title="Опора 🌱", layout="wide")

# --- 2. ПОДКЛЮЧЕНИЕ К ТАБЛИЦЕ ---
# Сюда мы вставляем тот кусочек, о котором ты спрашивал
conn = st.connection("gsheets", type=GSheetsConnection)

def load_sheet(sheet_name):
    # ВАЖНО: Вставь сюда ссылку на свою таблицу!
    url = "ССЫЛКА_НА_ТВОЮ_ТАБЛИЦУ"
    try:
        return conn.read(spreadsheet=url, worksheet=sheet_name, ttl=0)
    except Exception:
        # Если лист пустой или не найден, создаем структуру
        cols = {
            "Users": ["Имя", "Пароль"],
            "Chats": ["ID_Чата", "Пользователь", "Заголовок", "Роль", "Сообщение", "Дата"],
            "Support": ["Дата", "Пользователь", "Сообщение"]
        }
        return pd.DataFrame(columns=cols.get(sheet_name, []))

def save_sheet(sheet_name, df):
    url = "ССЫЛКА_НА_ТВОЮ_ТАБЛИЦУ"
    conn.update(spreadsheet=url, worksheet=sheet_name, data=df)

# --- 3. ФУНКЦИЯ ДЛЯ ИИ ---
def ask_ai(messages, system_prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        full_context = [{"role": "system", "content": system_prompt}] + messages
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=full_context,
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка ИИ: {e}"

# --- 4. АВТОРИЗАЦИЯ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Система Опора")
    choice = st.radio("Действие:", ["Вход", "Регистрация"])
    
    with st.form("auth"):
        u_name = st.text_input("Имя")
        u_pwd = st.text_input("Пароль", type="password")
        if st.form_submit_button("ОК"):
            users_df = load_sheet("Users")
            if choice == "Вход":
                user_match = users_df[(users_df['Имя'] == u_name) & (users_df['Пароль'] == u_pwd)]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.user_name = u_name
                    st.rerun()
                else:
                    st.error("Неверные данные")
            else:
                if u_name in users_df['Имя'].values:
                    st.error("Имя занято")
                elif u_name and u_pwd:
                    new_user = pd.DataFrame([{"Имя": u_name, "Пароль": u_pwd}])
                    save_sheet("Users", pd.concat([users_df, new_user], ignore_index=True))
                    st.success("Аккаунт создан! Войдите.")
    st.stop()

# --- 5. МЕНЮ (САЙДБАР) ---
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

with st.sidebar:
    st.title(f"👤 {st.session_state.user_name}")
    if st.button("➕ Новый чат", use_container_width=True):
        st.session_state.active_chat_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    all_chats = load_sheet("Chats")
    my_chats = all_chats[all_chats['Пользователь'] == st.session_state.user_name]
    
    if not my_chats.empty:
        menu = my_chats[['ID_Чата', 'Заголовок']].drop_duplicates(subset=['ID_Чата'], keep='last')
        for _, row in menu[::-1].iterrows():
            if st.button(f"💬 {row['Заголовок']}", key=row['ID_Чата'], use_container_width=True):
                st.session_state.active_chat_id = row['ID_Чата']
                st.rerun()

    st.divider()
    # Поддержка
    with st.expander("🆘 Поддержка"):
        with st.form("sup"):
            msg = st.text_area("Что случилось?")
            if st.form_submit_button("Отправить"):
                sup_df = load_sheet("Support")
                new_sup = pd.DataFrame([{"Дата": datetime.now().strftime("%d.%m %H:%M"), "Пользователь": st.session_state.user_name, "Сообщение": msg}])
                save_sheet("Support", pd.concat([sup_df, new_sup], ignore_index=True))
                st.success("Отправлено!")

# --- 6. ОСНОВНОЙ ЧАТ ---
if not st.session_state.active_chat_id:
    st.title("🌱 Опора")
    st.info("Создайте чат в меню слева")
else:
    this_chat = all_chats[all_chats['ID_Чата'] == st.session_state.active_chat_id]
    chat_title = this_chat['Заголовок'].iloc[0] if not this_chat.empty else "Новый диалог"
    st.title(f"💬 {chat_title}")

    # История
    history = []
    for _, row in this_chat.iterrows():
        with st.chat_message(row['Роль']):
            st.markdown(row['Сообщение'])
        history.append({"role": row['Роль'], "content": row['Сообщение']})

    # Ввод
    if prompt := st.chat_input("Напиши мне..."):
        if this_chat.empty:
            chat_title = ask_ai([{"role": "user", "content": prompt}], "Придумай название из 2 слов. Только текст.").strip().replace('"', '')

        with st.chat_message("user"): st.markdown(prompt)
        
        with st.chat_message("assistant"):
            ans = ask_ai(history + [{"role": "user", "content": prompt}], "Ты Опора. Отвечай кратко.")
            st.markdown(ans)
        
        # Сохранение пары сообщений
        u_row = pd.DataFrame([{"ID_Чата": st.session_state.active_chat_id, "Пользователь": st.session_state.user_name, "Заголовок": chat_title, "Роль": "user", "Сообщение": prompt, "Дата": datetime.now().strftime("%Y-%m-%d %H:%M")}])
        a_row = pd.DataFrame([{"ID_Чата": st.session_state.active_chat_id, "Пользователь": st.session_state.user_name, "Заголовок": chat_title, "Роль": "assistant", "Сообщение": ans, "Дата": datetime.now().strftime("%Y-%m-%d %H:%M")}])
        
        save_sheet("Chats", pd.concat([all_chats, u_row, a_row], ignore_index=True))
        st.rerun()
