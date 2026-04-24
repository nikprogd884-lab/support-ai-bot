import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- 1. НАСТРОЙКА СТРАНИЦЫ ---
st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

# --- 2. ПОДКЛЮЧЕНИЕ К БАЗЕ ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error(f"Ошибка подключения к Google Sheets: {e}")

# --- 3. ФУНКЦИЯ СОХРАНЕНИЯ ДАННЫХ В ТАБЛИЦУ ---
def save_data(user, user_msg, ai_msg=""):
    try:
        # Читаем текущие данные
        existing_data = conn.read(ttl=0)
        
        # Создаем новую строку
        new_entry = pd.DataFrame([{
            "Дата": datetime.now().strftime("%d.%m.%Y %H:%M"),
            "Пользователь": user,
            "Сообщение": user_msg,
            "Ответ": ai_msg
        }])
        
        # Объединяем и обновляем таблицу
        updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
        conn.update(data=updated_df)
        return True
    except Exception as e:
        st.sidebar.error(f"Ошибка сохранения: {e}")
        return False

# --- 4. ЛОГИКА ВХОДА ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🌱 Добро пожаловать в Опору")
    with st.form("login_form"):
        u_name = st.text_input("Как тебя зовут?")
        u_pwd = st.text_input("Пароль доступа", type="password", help="Введи любой пароль")
        if st.form_submit_button("Войти"):
            if u_name:
                st.session_state.logged_in = True
                st.session_state.user_name = u_name
                st.rerun()
            else:
                st.error("Пожалуйста, введи имя")
    st.stop()

# --- 5. БОКОВАЯ ПАНЕЛЬ (АДМИНКА И ПОДДЕРЖКА) ---
with st.sidebar:
    st.write(f"👤 Пользователь: **{st.session_state.user_name}**")
    if st.button("Выйти"):
        st.session_state.logged_in = False
        st.rerun()
    
    st.divider()

    # Форма поддержки
    with st.expander("🆘 НАПИСАТЬ РАЗРАБОТЧИКУ"):
        with st.form("support_form", clear_on_submit=True):
            sup_msg = st.text_area("Опиши проблему:")
            if st.form_submit_button("Отправить"):
                if sup_msg:
                    if save_data(st.session_state.user_name, sup_msg, "ЗАПРОС В ПОДДЕРЖКУ"):
                        st.success("Отправлено!")
                else:
                    st.warning("Напиши текст сообщения")

    # Админка с новым паролем
    with st.expander("⚙️ АДМИН ПАНЕЛЬ"):
        adm_pwd = st.text_input("Пароль администратора", type="password")
        if adm_pwd == "240610":
            st.write("База данных (онлайн):")
            try:
                st.dataframe(conn.read(ttl=0))
            except:
                st.write("Таблица пуста или недоступна")

# --- 6. ЧАТ С НЕЙРОСЕТЬЮ ---
st.title("🌱 Опора")

# Промт для лаконичности
SYSTEM_PROMPT = (
    "Ты — Опора, мудрый и теплый наставник. "
    "Твоя задача: отвечать максимально КРАТКО (1-3 предложения). "
    "Не читай лекций. Сразу давай поддержку или один точный совет."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение чата
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# Поле ввода
if prompt := st.chat_input("Что тебя беспокоит?"):
    # Отображаем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Ответ ИИ
    with st.chat_message("assistant"):
        try:
            client = Groq(api_key=st.secrets["GROQ_API_KEY"])
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + st.session_state.messages,
                max_tokens=150
            )
            ai_answer = response.choices[0].message.content
            st.markdown(ai_answer)
            
            # Сохраняем в историю чата в приложении
            st.session_state.messages.append({"role": "assistant", "content": ai_answer})
            
            # АВТО-СОХРАНЕНИЕ В GOOGLE TABLE
            save_data(st.session_state.user_name, prompt, ai_answer)
            
        except Exception as e:
            st.error(f"Ошибка связи с ИИ: {e}")
