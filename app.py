import streamlit as st
from groq import Groq

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="Опора 🌱", layout="centered")
st.title("🌱 Опора")
st.caption("Простой чат без сохранения истории и аккаунтов")

# Инициализация истории сообщений только в памяти браузера
if "messages" not in st.session_state:
    st.session_state.messages = []

# Функция для запроса к ИИ
def ask_ai(messages):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты Опора. Мудрый друг и помощник."}] + messages,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка: {e}"

# Отображение чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Напиши мне что-нибудь..."):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Получаем ответ от ИИ
    with st.chat_message("assistant"):
        full_response = ask_ai(st.session_state.messages)
        st.markdown(full_response)
    
    # Добавляем ответ ИИ в историю
    st.session_state.messages.append({"role": "assistant", "content": full_response})
