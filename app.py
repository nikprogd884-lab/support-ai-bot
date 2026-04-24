import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import datetime

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Опора", page_icon="🌱")

# --- 2. ПОДКЛЮЧЕНИЕ К БАЗЕ ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Ошибка связи с таблицей: {e}")

# --- 3. ЛОГИКА ВХОДА ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Опора")
    with st.form("login"):
        name = st.text_input("Как тебя зовут?")
        pwd = st.text_input("Пароль", type="password")
        if st.form_submit_button("Войти"):
            if name and pwd:
                st.session_state.logged_in = True
                st.session_state.user_name = name
                st.rerun()
    st.stop()

# --- 4. БОКОВАЯ ПАНЕЛЬ ---
with st.sidebar:
    st.success(f"Привет, {st.session_state.user_name}!")
    if st.button("Выйти"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()
    
    with st.expander("🆘 ПОДДЕРЖКА"):
        with st.form("sup", clear_on_submit=True):
            msg = st.text_area("Напиши разработчику:")
            if st.form_submit_button("Отправить"):
                try:
                    df = conn.read(ttl=0)
                    new_row = pd.DataFrame([{
                        "Дата": datetime.datetime.now().strftime("%d.%m.%Y %H:%M"),
                        "Пользователь": st.session_state.user_name,
                        "Сообщение": msg,
                        "Ответ": ""
                    }])
                    conn.update(data=pd.concat([df, new_row], ignore_index=True))
                    st.success("Отправлено!")
                except Exception as e:
                    st.error(f"Ошибка: {e}")

    with st.expander("⚙️ АДМИНКА"):
        if st.text_input("Пароль админа", type="password") == "1234":
            st.dataframe(conn.read(ttl=0))

# --- 5. ЧАТ С НЕЙРОСЕТЬЮ ---
st.title("🌱 Опора")

# ОБНОВЛЕННЫЙ ПРОМТ: Теперь бот пишет КРАТКО
SYSTEM_PROMPT = (
    "Ты — Опора, мудрый наставник. "
    "ВАЖНОЕ ПРАВИЛО: Отвечай максимально кратко и по делу. "
    "Не пиши длинных вступлений и лекций. "
    "Твой ответ должен содержать 2-4 предложения. "
    "Будь эмпатичным, но лаконичным. Давай один конкретный совет или слова поддержки."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Что у тебя на душе?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                max_tokens=150 # Ограничиваем длину ответа технически
            )
            ans = response.choices[0].message.content
            st.markdown(ans)
            st.session_state.messages.append({"role": "assistant", "content": ans})
        except Exception as e:
            st.error(f"Ошибка: {e}")
