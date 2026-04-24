import streamlit as st
from groq import Groq

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="Опора 🌱", layout="centered")

# Стилизация заголовка, чтобы он выглядел спокойнее
st.markdown("<h1 style='text-align: center;'>🌱 Опора</h1>", unsafe_allow_html=True)

# Лаконичный системный промт: коротко, бережно, без лишних слов
SYSTEM_PROMPT = """Ты — Опора. Твой стиль общения:
1. Краткость — твой приоритет. Не пиши больше 1-3 коротких предложений. 
2. Ты не даешь советов, пока тебя не попросят. 
3. Твои фразы: "Я здесь", "Я тебя слышу", "Это очень больно, я рядом".
4. Если у человека срыв — используй заземление: "Дыши", "Почувствуй опору под собой".
5. Никаких приветственных простыней текста. Сразу к сути чувств пользователя."""

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_ai(messages):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            max_tokens=300, # Ограничиваем длину ответа на уровне настроек
            temperature=0.5 # Делаем ответы более стабильными и спокойными
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Я рядом, но сейчас не могу ответить. Попробуй еще раз, пожалуйста."

# Отображение истории чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Я слушаю тебя..."):
    # Сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Лаконичный ответ Опоры
    with st.chat_message("assistant"):
        full_response = ask_ai(st.session_state.messages)
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
