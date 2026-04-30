import streamlit as st
from groq import Groq
import random

# --- 1. КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

def ask_ai(messages):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        
        system_prompt = """Ты — Опора, эмпатичный и тёплый друг. 
Твоя задача — выслушать и поддержать человека.

Правила общения:
1. Общайся на "ты", избегай официоза ("Здравствуйте", "Чем могу помочь").
2. Отвечай кратко (2-3 предложения), искренне и по-человечески.
3. Если пишут "привет", ответь просто "Привет, я здесь" или "Слушаю тебя".
4. Не спрашивай "Как дела?" формально.
5. Ты не врач. Не ставь диагнозов и не давай медицинских советов.

ВАЖНОЕ ПРАВИЛО БЕЗОПАСНОСТИ:
Если пользователь пишет о суициде, самоповреждении, желании умереть (даже с опечатками), 
ТЫ ДОЛЖЕН ответить ТОЛЬКО кодом: __SOS_TRIGGER__"""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Извини, связь прервалась. (Ошибка: {e})"

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
if "messages" not in st.session_state:
    st.session_state.messages = []
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# --- 3. ПЕРЕКЛЮЧАТЕЛЬ ТЕМЫ ---
with st.sidebar:
    new_dark = st.toggle("🌙 Тёмная тема", value=st.session_state.dark_mode)
    if new_dark != st.session_state.dark_mode:
        st.session_state.dark_mode = new_dark
        st.rerun()

# --- 4. СТИЛИ ---
st.markdown("""
    <style>
    * { transition: background-color 0.3s ease, color 0.3s ease; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; }
    .sos-main button { background-color: #ff4b4b !important; color: white !important; border: none; }
    
    .big-call-btn {
        display: block; width: 100%; padding: 1rem;
        background-color: #28a745; color: white;
        text-align: center; font-size: 1.5rem; font-weight: bold;
        border-radius: 15px; text-decoration: none;
        margin-top: 10px; animation: pulse 2s infinite;
    }
    .big-call-btn:hover { background-color: #218838; color: white; }
    
    @keyframes pulse {
        0% { transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0.7); }
        70% { transform: scale(1.02); box-shadow: 0 0 0 10px rgba(40, 167, 69, 0); }
        100% { transform: scale(1); box-shadow: 0 0 0 0 rgba(40, 167, 69, 0); }
    }
    </style>
    """, unsafe_allow_html=True)

if st.session_state.dark_mode:
    st.markdown("""
    <style>
    :root { --bg: #181820; --surface: #242430; --text: #e4e4ec; --border: #38384a; }
    body, .stApp, header, [data-testid="stToolbar"], .main { background-color: var(--bg) !important; color: var(--text) !important; }
    section[data-testid="stSidebar"] { background-color: #1a1a24 !important; }
    .stChatMessage { background-color: var(--surface) !important; }
    [data-testid="stChatInputContainer"], [data-testid="stBottom"], [data-testid="stBottom"] > div {
        background-color: transparent !important;
    }
    [data-testid="stChatInput"] textarea { background-color: var(--surface) !important; color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }
    [data-testid="stChatInput"] button { background-color: var(--surface) !important; color: var(--text) !important; }
    button:not(.sos-main button) { background-color: var(--surface) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    h1, h2, h3, p, div, span, label { color: var(--text) !important; }
    .stDivider { border-top-color: var(--border) !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌱 Опора")
st.write(f"*{st.session_state.daily_quote}*")

# --- 5. ФУНКЦИЯ ОТПРАВКИ СООБЩЕНИЯ ---
def send_message(text):
    """Отправляет сообщение и получает ответ от ИИ"""
    st.session_state.messages.append({"role": "user", "content": text})
    
    with st.chat_message("user"):
        st.markdown(text)
    
    with st.chat_message("assistant"):
        with st.spinner("Слушаю тебя..."):
            response_text = ask_ai(st.session_state.messages)
            
            if "__SOS_TRIGGER__" in response_text:
                st.session_state.sos_active = True
                st.warning("🆘 Мне кажется, тебе сейчас очень тяжело. Пожалуйста, позвони специалистам.")
                st.markdown('<a href="tel:88002000122" class="big-call-btn">📞 НАБРАТЬ 8-800-2000-122</a>', unsafe_allow_html=True)
                st.caption("Бесплатно, анонимно, круглосуточно.")
            else:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

# --- 6. ОБРАБОТКА PENDING_PROMPT (ОТ КНОПОК) ---
if st.session_state.pending_prompt is not None:
    prompt_to_send = st.session_state.pending_prompt
    st.session_state.pending_prompt = None  # СРАЗУ очищаем!
    send_message(prompt_to_send)
    st.rerun()  # Перезагружаем, чтобы кнопки исчезли

# --- 7. SOS БЛОК ---
if not st.session_state.sos_active:
    st.markdown('<div class="sos-main">', unsafe_allow_html=True)
    if st.button("🆘 ЭКСТРЕННАЯ ПОМОЩЬ (SOS)"):
        st.session_state.sos_active = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("🆘 Мне кажется, тебе сейчас очень тяжело. Пожалуйста, позвони специалистам.")
    st.markdown('<a href="tel:88002000122" class="big-call-btn">📞 НАБРАТЬ 8-800-2000-122</a>', unsafe_allow_html=True)
    st.caption("Бесплатно, анонимно, круглосуточно.")
    if st.button("🔙 Я в порядке, закрыть"):
        st.session_state.sos_active = False
        st.rerun()

st.divider()

# --- 8. КНОПКИ-ПОДСКАЗКИ (ТОЛЬКО ЕСЛИ ЧАТ ПУСТ!) ---
if len(st.session_state.messages) == 0:
    starters = ["Мне тревожно", "Я устал", "Хочу выговориться", "Нужен совет", "Просто побудь со мной", "Мне одиноко"]
    cols = st.columns(3)  # 3 колонки вместо 6, чтобы текст влезал
    
    for i, starter in enumerate(starters):
        col_idx = i % 3
        with cols[col_idx]:
            if st.button(starter, key=f"start_{i}", use_container_width=True):
                st.session_state.pending_prompt = starter
                st.rerun()  # Перезагрузка для отправки
    st.write("")  # Отступ

# --- 9. ОТОБРАЖЕНИЕ ИСТОРИИ ЧАТА ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 10. ПОЛЕ ВВОДА ---
if prompt := st.chat_input("Что у тебя на душе?"):
    send_message(prompt)
    st.rerun()

# --- 11. КНОПКА ОЧИСТКИ ---
if st.session_state.messages:
    st.write("")
    if st.button("🗑️ Очистить чат (анонимно)"):
        st.session_state.messages = []
        st.session_state.sos_active = False
        st.rerun()

# --- 12. ДИСКЛЕЙМЕР ---
st.markdown("""
<div style="text-align: center; color: #a0a0a0; font-size: 0.6rem; padding: 0.3rem 0 1rem; line-height: 1.3;">
    ⚠️ «Опора» — ИИ-помощник, а не замена специалисту.<br>
    В кризисных ситуациях: <strong style="font-weight: normal; color: #999;">112</strong> или <strong style="font-weight: normal; color: #999;">8-800-2000-122</strong>.<br>
    Переписка не сохраняется.
</div>
""", unsafe_allow_html=True)
