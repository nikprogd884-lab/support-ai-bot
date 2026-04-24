import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid
import time

# --- 1. НАСТРОЙКИ ---
st.set_page_config(page_title="Опора 🌱", layout="wide")

conn = st.connection("gsheets", type=GSheetsConnection)
SPREADSHEET_ID = "1oc_E2IHKjJZSjt9fscY93srN77sNeN4qjqFrP4QkRN0"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

# Улучшенная функция загрузки с защитой от сбоев
def load_sheet(sheet_name):
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=0)
        return df.dropna(how='all')
    except Exception:
        # Если листа нет, возвращаем пустой шаблон
        cols = {"Users": ["Имя", "Пароль"], "Chats": ["ID_Чата", "Пользователь", "Заголовок", "Роль", "Сообщение", "Дата"]}
        return pd.DataFrame(columns=cols.get(sheet_name, []))

# Улучшенная функция сохранения с повторными попытками
def save_sheet(sheet_name, df):
    for i in range(3): # Пробуем 3 раза, если Google тормозит
        try:
            conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df.dropna(how='all'))
            return True
        except Exception:
            time.sleep(1) # Ждем секунду перед повтором
    return False

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

# --- 2. АВТОРИЗАЦИЯ И САМОСТОЯТЕЛЬНАЯ РЕГИСТРАЦИЯ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Система Опора")
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])

    with tab1:
        with st.form("login"):
            l_name = st.text_input("Имя").strip()
            l_pwd = st.text_input("Пароль", type="password").strip()
            if st.form_submit_button("Войти"):
                users = load_sheet("Users")
                if not users.empty:
                    # Приводим к строкам для точного сравнения
                    match = users[(users['Имя'].astype(str) == l_name) & (users['Пароль'].astype(str) == l_pwd)]
                    if not match.empty:
                        st.session_state.logged_in = True
                        st.session_state.user_name = l_name
                        st.rerun()
                st.error("Неверные данные или пользователь не существует")

    with tab2:
        with st.form("reg"):
            r_name = st.text_input("Придумайте Имя").strip()
            r_pwd = st.text_input("Придумайте Пароль", type="password").strip()
            if st.form_submit_button("Создать аккаунт"):
                users = load_sheet("Users")
                if r_name in users['Имя'].astype(str).values:
                    st.error("Это имя уже занято, выберите другое")
                elif r_name and r_pwd:
                    new_user = pd.DataFrame([{"Имя": r_name, "Пароль": r_pwd}])
                    success = save_sheet("Users", pd.concat([users, new_user], ignore_index=True))
                    if success:
                        st.success("Успех! Теперь войдите во вкладке 'Вход'")
                    else:
                        st.error("Ошибка связи с базой. Попробуйте еще раз через 5 секунд.")
    st.stop()

# --- 3. ИНТЕРФЕЙС ПОСЛЕ ВХОДА ---
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
        my_chats = all_chats[all_chats['Пользователь'].astype(str) == st.session_state.user_name]
        if not my_chats.empty:
            menu = my_chats[['ID_Чата', 'Заголовок']].drop_duplicates(subset=['ID_Чата'], keep='last')
            for _, row in menu[::-1].iterrows():
                if st.button(f"💬 {row['Заголовок']}", key=row['ID_Чата'], use_container_width=True):
                    st.session_state.active_chat_id = row['ID_Чата']
                    st.rerun()

# --- 4. ОКНО ЧАТА ---
if not st.session_state.active_chat_id:
    st.info("Создайте новый чат в меню слева")
else:
    chat_data = all_chats[all_chats['ID_Чата'] == st.session_state.active_chat_id] if not all_chats.empty else pd.DataFrame()
    title = chat_data['Заголовок'].iloc[0] if not chat_data.empty else "Новый диалог"
    st.title(f"💬 {title}")

    history = []
    for _, row in chat_data.iterrows():
        with st.chat_message(row['Роль']):
            st.markdown(row['Сообщение'])
        history.append({"role": row['Роль'], "content": row['Сообщение']})

    if prompt := st.chat_input("Спроси о чем-нибудь..."):
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
