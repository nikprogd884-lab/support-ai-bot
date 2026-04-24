import streamlit as st
from groq import Groq

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="Опора 🌱", layout="centered")

# --- CSS ДЛЯ МЯГКОГО ПЕРЕЛИВА ФОНА ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f3f7f9, #e8f5e9, #f3e5f5, #e3f2fd);
        background-size: 400% 400%;
        animation: gradientAnimation 20s ease infinite;
    }

    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Делаем блоки сообщений чуть прозрачными для красоты */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.6) !important;
        border-radius: 15px;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>🌱 Опора</h1>", unsafe_allow_html=True)

# --- ЛОГИКА ИИ ---
SYSTEM_PROMPT = """Ты — Опора. Ты безопасное и живое пространство для человека.
Твоя задача — чувствовать контекст:
1. Если человек в остром стрессе — отвечай кратко, помогай дышать и заземляться.
2. Если человек хочет выговориться — будь глубоким и вдумчивым слушателем.
3. Избегай шаблонов и длинных вступлений. 
4. Ты мудрый, теплый и устойчивый друг. Твои ответы должны быть искренними."""

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_ai(messages):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            max_tokens=1000,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Я здесь. Просто небольшая заминка в сети. Попробуй еще раз, я никуда не ушел."

# Отображение чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ввод сообщения
if prompt := st.chat_input("Я слушаю тебя..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_response = ask_ai(st.session_state.messages)
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
