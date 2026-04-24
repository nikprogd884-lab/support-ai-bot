import streamlit as st
from groq import Groq

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="Опора 🌱", layout="centered")
st.title("🌱 Опора")

# Тот самый промт, дающий моделе жизнь и глубину
SYSTEM_PROMPT = """Ты — Опора. Твоя цель — быть рядом с человеком в самые трудные моменты его жизни. 
Ты мудрый, бесконечно терпеливый и теплый собеседник. 
Если у пользователя психологический срыв, паническая атака или глубокое отчаяние:
1. Сохраняй спокойствие и устойчивость. 
2. Используй техники заземления и активного слушания. 
3. Не давай пустых советов, а разделяй боль, давая человеку почувствовать, что он не один.
4. Твой голос должен быть тихим, поддерживающим и принимающим. 
Ты — тихая гавань, где можно быть слабым и настоящим."""

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_ai(messages):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            max_tokens=800,
            temperature=0.7 # Немного тепла в ответы
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Произошла ошибка, но я рядом. Попробуй еще раз. (Ошибка: {e})"

# Отображение чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Я слушаю тебя..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_response = ask_ai(st.session_state.messages)
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
