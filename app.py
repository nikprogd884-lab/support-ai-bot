import streamlit as st
from groq import Groq
import random

# --- 1. КОНФИГУРАЦИЯ И СВЯЗЬ ---
st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

def ask_ai(messages):
    try:
        # Используем логику из твоего рабочего кода через st.secrets
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты — Опора, теплый и краткий помощник. Твоя задача — выслушать и поддержать человека на русском языке. Будь краток и эмпатичен."}] + messages,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Извини, произошла ошибка связи. Проверь настройки Secrets. (Ошибка: {e})"

# --- 2. ИНТЕРФЕЙС И СТИЛИ ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; }
    .sos-main button { background-color: #ff4b4b !important; color: white !important; border: none; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌱 Опора")

# Случайная фраза поддержки
AFFIRMATIONS = [
    "Ты справляешься лучше, чем тебе кажется. ✨",
    "Твои чувства важны. Позволь им быть. ❤️",
    "Маленькие шаги тоже ведут к большим целям. 🌱",
    "Ты ценен просто потому, что ты есть. ⭐",
    "Дыши. Всё обязательно наладится. 🙏"
]
if "daily_quote" not in st.session_state:
    st.session_state.daily_quote = random.choice(AFFIRMATIONS)
st.write(f"*{st.session_state.daily_quote}*")

# --- 3. БЛОК SOS (ОДНА КНОПКА С ПОДТВЕРЖДЕНИЕМ) ---
if "sos_active" not in st.session_state:
    st.session_state.sos_active = False

if not st.session_state.sos_active:
    st.markdown('<div class="sos-main">', unsafe_allow_html=True)
    if st.button("🆘 ЭКСТРЕННАЯ ПОМОЩЬ (SOS)"):
        st.session_state.sos_active = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Показать номер Детского телефона доверия?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ ДА, показать", type="primary"):
            st.success("📞 **8-800-2000-122**")
            st.caption("Бесплатно, анонимно, круглосуточно.")
    with c2:
        if st.button("❌ Нет, назад"):
            st.session_state.sos_active = False
            st.rerun()

st.divider()

# --- 4. ЛОГИКА ЧАТА ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение диалога
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Что у тебя на душе?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Слушаю тебя..."):
            response = ask_ai(st.session_state.messages)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

# Кнопка очистки в самом низу
if st.session_state.messages:
    st.write("")
    if st.button("🗑️ Очистить чат (анонимно)"):
        st.session_state.messages = []
        st.rerun()
