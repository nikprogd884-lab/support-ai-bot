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
3. Если пишут "привет", не пиши "Привет! Здравствуйте!". Ответь просто "Привет, я здесь" или "Слушаю тебя".
4. Не спрашивай "Как дела?" формально. Просто вырази поддержку.
5. Ты не врач. Не ставь диагнозов и не давай медицинских советов.

ВАЖНОЕ ПРАВИЛО БЕЗОПАСНОСТИ:
Если пользователь пишет о суициде, самоповреждении, желании умереть или исчезнуть (даже если есть опечатки, например "хочу умерет", или используются метафоры), 
ТЫ ДОЛЖЕН ответить ТОЛЬКО специальным кодом: __SOS_TRIGGER__
Не пиши ничего другого в этом случае. Просто верни этот код."""

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system_prompt}] + messages,
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Извини, связь прервалась. (Ошибка: {e})"

# --- 2. СОСТОЯНИЯ ---
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
if "input_text" not in st.session_state:
    st.session_state.input_text = "" # Для хранения текста в поле ввода

# --- 3. ПЕРЕКЛЮЧАТЕЛЬ ТЕМЫ ---
with st.sidebar:
    new_dark = st.toggle("🌙 Тёмная тема", value=st.session_state.dark_mode)
    if new_dark != st.session_state.dark_mode:
        st.session_state.dark_mode = new_dark
        st.rerun()
    st.caption("Сохраняется в рамках сессии.")

# --- 4. СТИЛИ (CSS) ---
st.markdown("""
    <style>
    * { transition: background-color 0.3s ease, color 0.3s ease; }
    .stButton>button { width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; }
    .sos-main button { background-color: #ff4b4b !important; color: white !important; border: none; }
    .tel-link { font-size: 1.8em; font-weight: bold; text-decoration: none; color: #2e7d32; display: block; text-align: center; padding: 0.6em 0; }
    
    /* Стили для чипсов (подсказок) */
    .chip-container {
        display: flex;
        gap: 8px;
        overflow-x: auto;
        padding-bottom: 10px;
        margin-bottom: 5px;
        scrollbar-width: none; /* Firefox */
    }
    .chip-container::-webkit-scrollbar { display: none; /* Chrome/Safari */ }
    
    .stChip {
        background-color: #f0f2f6;
        border: 1px solid #dcdcdc;
        border-radius: 16px;
        padding: 6px 14px;
        font-size: 0.9rem;
        cursor: pointer;
        white-space: nowrap;
        transition: all 0.2s;
        color: #333;
    }
    .stChip:hover {
        background-color: #e0e0e0;
        transform: translateY(-1px);
    }
    </style>
    """, unsafe_allow_html=True)

if st.session_state.dark_mode:
    st.markdown("""
    <style>
    :root { --bg: #181820; --surface: #242430; --text: #e4e4ec; --border: #38384a; --link: #8b9aff; }
    body, .stApp, header, [data-testid="stToolbar"], .main, .block-container { background-color: var(--bg) !important; color: var(--text) !important; }
    section[data-testid="stSidebar"], section[data-testid="stSidebar"] > div { background-color: #1a1a24 !important; border-right: 1px solid var(--border) !important; }
    .stChatMessage { background-color: var(--surface) !important; }
    
    /* ФИКС БЕЛОЙ ПОЛОСЫ ВНИЗУ */
    [data-testid="stChatInputContainer"], [data-testid="stBottom"], [data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] {
        background-color: transparent !important; border: none !important; box-shadow: none !important;
    }
    [data-testid="stChatInput"] textarea { background-color: var(--surface) !important; color: var(--text) !important; border: 1px solid var(--border) !important; border-radius: 12px !important; }
    [data-testid="stChatInput"] button { background-color: var(--surface) !important; color: var(--text) !important; }
    
    button:not(.sos-main button) { background-color: var(--surface) !important; color: var(--text) !important; border: 1px solid var(--border) !important; }
    button:not(.sos-main button):hover { background-color: #2e2e3c !important; }
    h1, h2, h3, p, div, span, label { color: var(--text) !important; }
    a { color: var(--link) !important; }
    .tel-link { color: #4ade80 !important; }
    .stDivider { border-top-color: var(--border) !important; }
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    
    /* Чипсы в темной теме */
    .stChip { background-color: #2e2e3c; border-color: #38384a; color: #e4e4ec; }
    .stChip:hover { background-color: #38384a; }
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
    st.warning("🆘 Мне кажется, тебе сейчас очень тяжело. Пожалуйста, позвони специалистам, они помогут.")
    st.markdown(
        '<a href="tel:88002000122" class="big-call-btn" style="display:block;width:100%;padding:1rem;background:#28a745;color:white;text-align:center;font-size:1.5rem;font-weight:bold;border-radius:15px;text-decoration:none;margin-top:10px;">📞 НАБРАТЬ 8-800-2000-122</a>',
        unsafe_allow_html=True
    )
    st.caption("Бесплатно, анонимно, круглосуточно. Нажми на кнопку выше, чтобы открыть телефон.")
    
    if st.button("🔙 Я в порядке, закрыть"):
        st.session_state.sos_active = False
        st.rerun()

st.divider()

# --- 6. ЛОГИКА ЧАТА ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 7. ЧИПСЫ (ПОДСКАЗКИ) ---
# Список подсказок
starters = ["Мне тревожно", "Я устал", "Хочу выговориться", "Нужен совет", "Просто побудь со мной", "Мне одиноко"]

# Отображаем чипсы в ряд
cols = st.columns(len(starters))
for i, starter in enumerate(starters):
    with cols[i]:
        # Используем small_button для компактности или обычный button
        if st.button(starter, key=f"chip_{i}", use_container_width=True):
            st.session_state.input_text = starter
            # Мы не делаем rerun здесь, чтобы фокус остался на поле ввода, 
            # но обновляем значение через JS было бы сложнее, поэтому используем трюк с placeholder
            # В Streamlit проще всего сделать так: при клике мы просто запоминаем текст,
            # а пользователь сам нажмет Enter. Но чтобы текст появился в поле, 
            # нам нужно использовать стейт input_text, который привязан к chat_input? 
            # К сожалению, st.chat_input не поддерживает начальное значение из стейта напрямую в старых версиях.
            # Поэтому сделаем иначе: при клике мы просто добавляем сообщение сразу, как будто пользователь его отправил.
            
            # ВАРИАНТ А: Сразу отправлять сообщение (проще для UX)
            prompt = starter
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            with st.chat_message("assistant"):
                with st.spinner("Слушаю тебя..."):
                    response_text = ask_ai(st.session_state.messages)
                    
                    if "__SOS_TRIGGER__" in response_text:
                        st.session_state.sos_active = True
                        st.warning("🆘 Мне кажется, тебе сейчас очень тяжело. Пожалуйста, позвони специалистам.")
                        st.markdown('<a href="tel:88002000122" class="big-call-btn" style="display:block;width:100%;padding:1rem;background:#28a745;color:white;text-align:center;font-size:1.5rem;font-weight:bold;border-radius:15px;text-decoration:none;margin-top:10px;">📞 НАБРАТЬ 8-800-2000-122</a>', unsafe_allow_html=True)
                    else:
                        st.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
            st.rerun()

# Поле ввода (если пользователь хочет писать сам)
if prompt := st.chat_input("Что у тебя на душе?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Слушаю тебя..."):
            response_text = ask_ai(st.session_state.messages)
            
            if "__SOS_TRIGGER__" in response_text:
                st.session_state.sos_active = True
                st.warning("🆘 Мне кажется, тебе сейчас очень тяжело. Пожалуйста, позвони специалистам.")
                st.markdown('<a href="tel:88002000122" class="big-call-btn" style="display:block;width:100%;padding:1rem;background:#28a745;color:white;text-align:center;font-size:1.5rem;font-weight:bold;border-radius:15px;text-decoration:none;margin-top:10px;">📞 НАБРАТЬ 8-800-2000-122</a>', unsafe_allow_html=True)
            else:
                st.markdown(response_text)
                st.session_state.messages.append({"role": "assistant", "content": response_text})

if st.session_state.messages:
    st.write("")
    if st.button("🗑️ Очистить чат (анонимно)"):
        st.session_state.messages = []
        st.rerun()

# --- 8. ДИСКЛЕЙМЕР ---
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
