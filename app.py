import streamlit as st
from groq import Groq
import random

# --- 1. КОНФИГУРАЦИЯ И СВЯЗЬ ---
st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

def ask_ai(messages):
    try:
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
    .tel-link { font-size: 1.8em; font-weight: bold; text-decoration: none; color: #2e7d32; display: block; text-align: center; padding: 0.6em 0; }
    </style>
    """, unsafe_allow_html=True)

# Инициализация состояний
if "daily_quote" not in st.session_state:
    st.session_state.daily_quote = random.choice([
        "Ты справляешься лучше, чем тебе кажется. ✨",
        "Твои чувства важны. Позволь им быть. ❤️",
        "Маленькие шаги тоже ведут к большим целям. 🌱",
        "Ты ценен просто потому, что ты есть. ⭐",
        "Дыши. Всё обязательно наладится. 🙏"
    ])
if "sos_active" not in st.session_state:
    st.session_state.sos_active = False
if "show_number" not in st.session_state:
    st.session_state.show_number = False
if "messages" not in st.session_state:
    st.session_state.messages = []

st.title("🌱 Опора")
st.write(f"*{st.session_state.daily_quote}*")

# --- 3. БЛОК SOS ---
if not st.session_state.sos_active:
    st.markdown('<div class="sos-main">', unsafe_allow_html=True)
    if st.button("🆘 ЭКСТРЕННАЯ ПОМОЩЬ (SOS)"):
        st.session_state.sos_active = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Показать номер Детского телефона доверия?")
    
    if not st.session_state.show_number:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ ДА, показать", type="primary"):
                st.session_state.show_number = True
                st.rerun()
        with c2:
            if st.button("❌ Нет, назад"):
                st.session_state.sos_active = False
                st.rerun()
    else:
        st.success("Нажми на номер, чтобы открыть набор:")
        st.markdown('<a href="tel:88002000122" class="tel-link">📞 8-800-2000-122</a>', unsafe_allow_html=True)
        st.caption("Бесплатно, анонимно, круглосуточно.")
        if st.button("🔙 Назад в чат"):
            st.session_state.show_number = False
            st.session_state.sos_active = False
            st.rerun()

st.divider()

# --- 4. ЛОГИКА ЧАТА ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Что у тебя на душе?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Слушаю тебя..."):
            response = ask_ai(st.session_state.messages)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})

if st.session_state.messages:
    st.write("")
    if st.button("🗑️ Очистить чат (анонимно)"):
        st.session_state.messages = []
        st.rerun()

# --- 5. ДИСКЛЕЙМЕР (компактный, приглушённый, внизу) ---
st.markdown("""
<div style="
    text-align: center; 
    color: #a0a0a0; 
    font-size: 0.6rem; 
    padding: 0.3rem 0 1rem; 
    line-height: 1.3;
">
    ⚠️ «Опора» — ИИ-помощник, а не замена специалисту. Не ставит диагнозы и не назначает лечение.<br>
    В кризисных ситуациях: <strong style="font-weight: normal; color: #999;">112</strong> или <strong style="font-weight: normal; color: #999;">8-800-2000-122</strong> (анонимно, круглосуточно).<br>
    Переписка не сохраняется и полностью анонимна.
</div>
""", unsafe_allow_html=True)
