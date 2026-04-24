import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# 1. Настройка страницы
st.set_page_config(page_title="Опора", page_icon="🌱")

# 2. Безопасное подключение к Google Таблице
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    # Используем ссылку прямо из Secrets
    url = st.secrets["GSHEET_URL"]
except Exception as e:
    st.error("Ошибка конфигурации. Проверь Secrets!")
    st.stop()

# Функция записи (самый простой и надежный метод)
def save_msg(user_name, text):
    try:
        # Читаем то, что уже есть
        df = conn.read(spreadsheet=url)
        # Создаем новую строку (строго 4 колонки, как в твоей таблице)
        new_row = pd.DataFrame([{
            "Дата": datetime.datetime.now().strftime("%d.%m %H:%M"),
            "Пользователь": user_name,
            "Сообщение": text,
            "Ответ": ""
        }])
        # Склеиваем
        updated_df = pd.concat([df, new_row], ignore_index=True)
        # Записываем обратно
        conn.update(spreadsheet=url, data=updated_df)
        return True
    except:
        return False

# --- ЛОГИКА ВХОДА ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Добро пожаловать в Опору")
    with st.form("login"):
        name = st.text_input("Как тебя зовут?")
        # Пароль для всех твоих пользователей (можешь поменять на любой)
        pwd = st.text_input("Пароль доступа", type="password")
        if st.form_submit_button("Войти"):
            if name and pwd == "777": # Пусть будет три семерки для простоты
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("Неверное имя или пароль")
    st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС (после входа) ---
with st.sidebar:
    st.success(f"Вошел как: {st.session_state.user_name}")
    if st.button("Выйти"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    
    with st.expander("🆘 ПОДДЕРЖКА"):
        with st.form("support", clear_on_submit=True):
            u_text = st.text_area("Напиши разработчику:")
            if st.form_submit_button("Отправить"):
                if save_msg(st.session_state.user_name, u_text):
                    st.toast("Сообщение улетело!")
                else:
                    st.error("Ошибка отправки")

    with st.expander("⚙️ АДМИНКА"):
        if st.text_input("Пароль автора", type="password") == "1234":
            st.write("Все сообщения из таблицы:")
            admin_df = conn.read(spreadsheet=url)
            st.dataframe(admin_df)

# --- ЧАТ ---
st.title("🌱 Опора")
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]): st.markdown(m["content"])

if prompt := st.chat_input("Что на душе?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    
    with st.chat_message("assistant"):
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты мудрый друг."}] + st.session_state.messages
        )
        ans = response.choices[0].message.content
        st.markdown(ans)
        st.session_state.messages.append({"role": "assistant", "content": ans})
