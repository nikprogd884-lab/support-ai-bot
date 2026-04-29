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

# --- 2. ИНИЦИАЛИЗАЦИЯ СОСТОЯНИЙ ---
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
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# --- 3. ПЕРЕКЛЮЧАТЕЛЬ ТЕМЫ (в сайдбаре, ДО применения стилей) ---
with st.sidebar:
    new_dark_mode = st.toggle("🌙 Тёмная тема", value=st.session_state.dark_mode)
    if new_dark_mode != st.session_state.dark_mode:
        st.session_state.dark_mode = new_dark_mode
        st.rerun()  # Принудительная перерисовка при переключении
    st.caption("Переключение мгновенно. Сохраняется в рамках сессии.")

# --- 4. ПРИМЕНЕНИЕ СТИЛЕЙ (после переключателя!) ---
# Базовые стили
st.markdown("""
    <style>
    * { transition: background-color 0.3s ease, color 0.3s ease; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; }
    .sos-main button { background-color: #ff4b4b !important; color: white !important; border: none; }
    .tel-link { font-size: 1.8em; font-weight: bold; text-decoration: none; color: #2e7d32; display: block; text-align: center; padding: 0.6em 0; }
    </style>
    """, unsafe_allow_html=True)

# Тёмная тема (применяется только если включена)
if st.session_state.dark_mode:
    st.markdown("""
    <style>
    :root {
        --bg: #181820 !important; 
        --surface: #242430 !important; 
        --text: #e4e4ec !important; 
        --border: #38384a !important; 
        --link: #8b9aff !important;
    }
    .stApp { background-color: var(--bg) !important; color: var(--text) !important; }
    .main .block-container { background-color: var(--bg) !important; }
    .stChatMessage { background-color: var(--surface) !important; border-radius: 14px; }
    input, textarea, select { background-color: var(--surface) !important; color: var(--text) !important; border-color: var(--border) !important; }
    button:not(.sos-main button) { background-color: var(--surface) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    button:not(.sos-main button):hover { background-color: #2e2e3c !important; }
    .stAlert > div { background-color: var(--surface) !important; color: var(--text) !important; border-color: var(--border) !important; }
    .stTextInput > div > div > input { background-color: var(--surface) !important; color: var(--text) !important; }
    .stTextInput > div > div > input::placeholder { color: #888 !important; }
    h1, h2, h3, p, div, span, label { color: var(--text) !important; }
    a { color: var(--link) !important; }
    .tel-link { color: #4ade80 !important; }
    .stDivider { border-top-color: var(--border) !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌱 Опора")
st.write(f"*{st.session_state.daily_quote}*")

# --- 5. БЛОК SOS ---
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

# --- 6. ЛОГИКА ЧАТА ---
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

# --- 7. ДИСКЛЕЙМЕР ---
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
