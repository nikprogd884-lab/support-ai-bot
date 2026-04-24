import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- НАСТРОЙКИ ---
st.set_page_config(page_title="Опора 🌱", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)
SPREADSHEET_ID = "1oc_E2IHKjJZSjt9fscY93srN77sNeN4qjqFrP4QkRN0"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

def load_sheet(sheet_name):
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        return df.dropna(how='all') # Убираем пустые строки
    except:
        return pd.DataFrame()

def save_sheet(sheet_name, df):
    conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df.dropna(how='all'))

def ask_ai(messages, system_prompt):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=400
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка ИИ: {e}"

# --- ВХОД И РЕГИСТРАЦИЯ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Система Опора")
    choice = st.radio("Действие:", ["Вход", "Регистрация"])
    
    with st.form("auth"):
        u_name = st.text_input("Имя").strip() # Убираем лишние пробелы
        u_pwd = st.text_input("Пароль", type="password").strip()
        
        if st.form_submit_button("Подтвердить"):
            users_df = load_sheet("Users")
            
            if choice == "Регистрация":
                if not users_df.empty and u_name in users_df['Имя'].astype(str).values:
                    st.error("Имя занято")
                elif u_name and u_pwd:
                    new_user = pd.DataFrame([{"Имя": u_name, "Пароль": u_pwd}])
                    save_sheet("Users", pd.concat([users_df, new_user], ignore_index=True))
                    st.success("Готово! Теперь выберите 'Вход'")
            else:
                if not users_df.empty:
                    # Ищем совпадение (приводим всё к строкам для надежности)
                    match = users_df[(users_df['Имя'].astype(str) == u_name) & (users_df['Пароль'].astype(str) == u_pwd)]
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_name = u_name
                        st.rerun()
                st.error("Неверное имя или пароль")
    st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

all_chats = load_sheet("Chats")

with st.sidebar:
    st.title(f"👤 {st.session_state.user_name}")
    if st.button("➕ Новый чат", use_container_width=True):
        st.session_state.active_chat_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    if not all_chats.empty:
        my_chats = all_chats[all_chats['Пользователь'] == st.session_state.user_name]
        if not my_chats.empty:
            menu = my_chats[['ID_Чата', 'Заголовок']].drop_duplicates(subset=['ID_Чата'], keep='last')
            for _, row in menu[::-1].iterrows():
                if st.button(f"💬 {row['Заголовок']}", key=row['ID_Чата'], use_container_width=True):
                    st.session_state.active_chat_id = row['ID_Чаta']
                    st.rerun()

# --- ОКНО ЧАТА ---
if not st.session_state.active_chat_id:
    st.info("Создайте чат слева")
else:
    chat_data = all_chats[all_chats['ID_Чата'] == st.session_state.active_chat_id] if not all_chats.empty else pd.DataFrame()
    title = chat_data['Заголовок'].iloc[0] if not chat_data.empty else "Новый диалог"
    st.title(f"💬 {title}")

    history = []
    for _, row in chat_data.iterrows():
        with st.chat_message(row['Роль']):
            st.markdown(row['Сообщение'])
        history.append({"role": row['Роль'], "content": row['Сообщение']})

    if prompt := st.chat_input("Напиши мне..."):
        if chat_data.empty:
            title = ask_ai([{"role": "user", "content": prompt}], "Придумай название из 2 слов.").strip().replace('"', '')

        with st.chat_message("user"): st.markdown(prompt)
        u_row = pd.DataFrame([{"ID_Чата": st.session_state.active_chat_id, "Пользователь": st.session_state.user_name, "Заголовок": title, "Роль": "user", "Сообщение": prompt, "Дата": datetime.now().strftime("%H:%M")}])

        with st.chat_message("assistant"):
            ans = ask_ai(history + [{"role": "user", "content": prompt}], "Ты Опора. Мудрый друг.")
            st.markdown(ans)
        a_row = pd.DataFrame([{"ID_Чата": st.session_state.active_chat_id, "Пользователь": st.session_state.user_name, "Заголовок": title, "Роль": "assistant", "Сообщение": ans, "Дата": datetime.now().strftime("%H:%M")}])

        save_sheet("Chats", pd.concat([all_chats, u_row, a_row], ignore_index=True))
        st.rerun()
