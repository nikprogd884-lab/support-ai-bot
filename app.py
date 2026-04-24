import streamlit as st
from groq import Groq

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="Опора 🌱", layout="centered")

# Центрированный заголовок
st.markdown("<h1 style='text-align: center;'>🌱 Опора</h1>", unsafe_allow_html=True)

# Глубокий, живой системный промт без жестких лимитов слов
SYSTEM_PROMPT = """Ты — Опора. Ты не просто бот, ты — безопасное пространство для человека.
Твоя главная задача — чувствовать контекст:
1. Если человек в остром стрессе, панике или срыве — отвечай кратко, заземляй, помогай дышать.
2. Если человек хочет выговориться и ищет понимания — будь глубоким и вдумчивым собеседником. Отражай его чувства, показывай, что он услышан.
3. Избегай шаблонных фраз и длинных приветствий. 
4. Будь живым: где-то достаточно одной фразы "Я рядом", а где-то нужен целый абзац поддержки.
5. Не дай человеку почувствовать, что он говорит с программой. Ты — мудрый, теплый и устойчивый друг."""

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_ai(messages):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            max_tokens=1000, # Даем свободу мысли
            temperature=0.7  # Оптимально для человечности и эмпатии
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Я здесь, с тобой. Просто возникла небольшая техническая заминка, но я никуда не ухожу. Попробуй написать еще раз."

# Отображение истории чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Я слушаю тебя..."):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ответ Опоры
    with st.chat_message("assistant"):
        full_response = ask_ai(st.session_state.messages)
        st.markdown(full_response)
    
    # Сохраняем ответ
    st.session_state.messages.append({"role": "assistant", "content": full_response})
