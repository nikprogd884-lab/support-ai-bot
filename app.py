import streamlit as st
from groq import Groq

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="Опора 🌱", layout="centered")

# --- CSS: ЭФФЕКТ "АЛИСА 3" (16 МЛН ЦВЕТОВ) ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(
            -45deg, 
            #ee7752, #e73c7e, #23a6d5, #23d5ab, 
            #7952ee, #3c7ee7, #d5a623, #d52323
        );
        background-size: 400% 400%;
        animation: aurora 15s ease infinite;
        height: 100vh;
    }

    @keyframes aurora {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Делаем чат более современным и "стеклянным" */
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        color: white !important;
    }
    
    /* Смена цвета текста заголовка для читаемости на ярком фоне */
    h1 {
        color: white !important;
        text-shadow: 2px 2px 10px rgba(0,0,0,0.2);
    }
    
    p, span {
        color: white !important;
    }

    /* Поле ввода */
    .stChatInputContainer {
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 15px !important;
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
        return "Я здесь. Мы на мгновение потеряли связь, но я рядом. Что ты чувствуешь?"

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
