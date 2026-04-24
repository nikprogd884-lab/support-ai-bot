import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# 1. Настройка страницы
st.set_page_config(page_title="Опора", page_icon="🌱")

# 2. Подключение к Google Таблице
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = st.secrets["GSHEET_URL"]
except:
    st.error("Ошибка базы данных.")
    st.stop()

# --- ФУНКЦИИ ---
def save_support_msg(user_id, text):
    df = conn.read(spreadsheet=url)
    new_data = pd.DataFrame([{"Дата": datetime.datetime.now().strftime("%d.%m %H:%M"), 
                              "Пользователь": user_id, "Сообщение": text, "Ответ": ""}])
    updated_df = pd.concat([df, new_data], ignore_index=True)
    conn.update(spreadsheet=url, data=updated_df)

# --- АВТОРИЗАЦИЯ (ВХОД) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Вход в Опору")
    with st.form("login_form"):
        user_id = st.text_input("Твой ник или имя")
        password = st.text_input("Пароль", type="password")
        if st.form_submit_button("Войти"):
            if user_id and password: # Можно добавить проверку на конкретный пароль
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.rerun()
            else:
                st.warning("Заполни все поля")
    st.stop() # Дальше кода не будет, пока не войдешь

# --- ЕСЛИ ВОШЛИ, ПОКАЗЫВАЕМ БОТА ---
with st.sidebar:
    st.write(f"👤 Привет, **{st.session_state.user_id}**!")
    if st.button("Выйти"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    
    with st.expander("🆘 Поддержка"):
        with st.form("sup_form", clear_on_submit=True):
            msg = st.text_area("Что случилось?")
            if st.form_submit_button("Отправить"):
                save_support_msg(st.session_state.user_id, msg)
                st.success("Отправлено!")

    with st.expander("⚙️ Админка"):
        if st.text_input("Пароль админа", type="password") == "1234":
            data = conn.read(spreadsheet=url)
            st.dataframe(data)

# --- ЧАТ ---
st.title("🌱 Опора")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Напиши что-нибудь..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты мудрый помощник."}] + st.session_state.messages
        )
        ans = res.choices[0].message.content
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
