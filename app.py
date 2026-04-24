import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Опора", page_icon="🌱")

# --- 2. ПОДКЛЮЧЕНИЕ К ТАБЛИЦЕ ---
# Это берет ссылку напрямую из блока [connections.gsheets] в твоих Secrets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Ошибка подключения: {e}")

# --- 3. ЛОГИКА ВХОДА ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Добро пожаловать в Опору")
    with st.form("login"):
        name = st.text_input("Как тебя зовут?")
        pwd = st.text_input("Пароль", type="password")
        if st.form_submit_button("Войти"):
            if name and pwd: # Пускает с любым паролем
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.rerun()
            else:
                st.warning("Заполни поля")
    st.stop()

# --- 4. БОКОВАЯ ПАНЕЛЬ (МЕНЮ И ПОДДЕРЖКА) ---
with st.sidebar:
    st.success(f"Привет, {st.session_state.user_name}!")
    if st.button("Выйти"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    
    # СЕКЦИЯ ПОДДЕРЖКИ
    with st.expander("🆘 ПОДДЕРЖКА"):
        with st.form("support", clear_on_submit=True):
            msg = st.text_area("Напиши нам:")
            if st.form_submit_button("Отправить"):
                try:
                    # Читаем данные (без кэша)
                    df = conn.read(ttl=0)
                    # Создаем новую строку (строго 4 колонки: Дата, Пользователь, Сообщение, Ответ)
                    new_row = pd.DataFrame([{
                        "Дата": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
                        "Пользователь": st.session_state.user_name,
                        "Сообщение": msg,
                        "Ответ": ""
                    }])
                    # Склеиваем и обновляем
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    st.success("Доставлено!")
                except Exception as e:
                    st.error(f"Ошибка записи: {e}")

    # СЕКЦИЯ АДМИНКИ
    with st.expander("⚙️ АДМИНКА"):
        if st.text_input("Код автора", type="password") == "1234":
            try:
                st.dataframe(conn.read(ttl=0))
            except:
                st.write("Таблица пуста")

# --- 5. ЧАТ С НЕЙРОСЕТЬЮ ---
st.title("🌱 Опора")

# Твой промт (характер бота)
SYSTEM_TEXT = "Ты мудрый, поддерживающий наставник по имени Опора. Твоя задача — помогать пользователю, давать советы и просто выслушивать."

if "messages" not in st.session_state:
    st.session_state.messages = []

# История сообщений
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Поле ввода
if prompt := st.chat_input("О чем хочешь поговорить?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Ответ бота
    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_TEXT}] + st.session_state.messages
            )
            ai_answer = response.choices[0].message.content
            st.markdown(ai_answer)
            st.session_state.messages.append({"role": "assistant", "content": ai_answer})
        except Exception as e:
            st.error(f"Ошибка Groq: {e}")
