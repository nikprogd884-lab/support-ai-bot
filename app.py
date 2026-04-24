import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# 1. Настройка страницы
st.set_page_config(page_title="Опора", page_icon="🌱")

# 2. Подключение к базе данных (Google Таблицы)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Ошибка подключения к базе: {e}")

# --- ФУНКЦИЯ ЗАПИСИ В ТАБЛИЦУ ---
def save_msg(user_name, text):
    try:
        # Читаем текущие данные
        df = conn.read()
        # Создаем новую строку
        new_row = pd.DataFrame([{
            "Дата": datetime.datetime.now().strftime("%d.%m %H:%M"),
            "Пользователь": user_name,
            "Сообщение": text,
            "Ответ": ""
        }])
        # Добавляем строку к существующим данным
        updated_df = pd.concat([df, new_row], ignore_index=True)
        # Записываем обратно в Google Sheets
        conn.update(data=updated_df)
        return True
    except Exception as e:
        print(f"Ошибка при записи: {e}")
        return False

# --- ЛОГИКА АВТОРИЗАЦИИ ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Добро пожаловать в Опору")
    with st.form("login_form"):
        name = st.text_input("Как тебя зовут?")
        pwd = st.text_input("Пароль доступа", type="password")
        if st.form_submit_button("Войти"):
            if name and (pwd == "777"):
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.rerun()
            else:
                st.error("Введите имя и верный пароль (777)")
    st.stop()

# --- ОСНОВНОЙ ИНТЕРФЕЙС (после входа) ---
with st.sidebar:
    st.success(f"Вы вошли как: {st.session_state.user_name}")
    if st.button("Выйти"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    
    with st.expander("🆘 ПОДДЕРЖКА"):
        with st.form("sup_form", clear_on_submit=True):
            user_text = st.text_area("Напишите нам:")
            if st.form_submit_button("Отправить"):
                if save_msg(st.session_state.user_name, user_text):
                    st.toast("Сообщение сохранено!")
                else:
                    st.error("Не удалось отправить")

    with st.expander("⚙️ АДМИНКА"):
        if st.text_input("Пароль админа", type="password") == "1234":
            try:
                data = conn.read()
                st.dataframe(data)
            except:
                st.error("Не удалось загрузить данные")

# --- ГЛАВНЫЙ ЧАТ ---
st.title("🌱 Опора")

# Проверка API ключа
if "GROQ_API_KEY" not in st.secrets:
    st.error("Добавьте GROQ_API_KEY в Secrets!")
    st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение истории чата
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Поле ввода чата
if prompt := st.chat_input("Напиши что-нибудь..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Ты мудрый и поддерживающий собеседник."}] + st.session_state.messages
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        except Exception as e:
            st.error(f"Ошибка нейросети: {e}")
