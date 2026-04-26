import streamlit as st
from groq import Groq

# Инициализация клиента Groq (вставь свой API ключ)
client = Groq(api_key="ТВОЙ_API_КЛЮЧ")

# Настройка страницы
st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

# Стили для красоты
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3em;
        background-color: #f0f2f6;
    }
    .sos-button>button {
        background-color: #ff4b4b !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# Заголовок и Описание
st.title("Опора 🌱")

with st.expander("ℹ️ Что такое «Опора»?"):
    st.write("""
    **Опора** — это твой анонимный уголок спокойствия. 
    Здесь нет регистрации, а твои сообщения удаляются сразу после закрытия вкладки. 
    Используй чат, чтобы выговориться, или кнопку SOS, если нужна помощь.
    """)

# Блок SOS (Экстренная помощь)
st.subheader("Экстренная помощь")
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown('<div class="sos-button">', unsafe_allow_html=True)
    if st.button("📞 Детский телефон доверия"):
        st.info("Позвоните по номеру: **8-800-2000-122** (Бесплатно и анонимно)")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    if st.button("🧘 Техника дыхания"):
        st.write("Вдох (4 сек) — Задержка (4 сек) — Выдох (4 сек) — Задержка (4 сек)")

st.divider()

# Логика Чат-бота
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение истории (только для текущей сессии)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Расскажи, что у тебя на душе..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Промпт для ИИ, чтобы он был поддерживающим
        system_prompt = "Ты — Опора, бережный и анонимный ИИ-помощник. Твоя цель — выслушать и поддержать человека. Не давай строгих советов, если не просят, просто будь рядом."
        
        full_response = ""
        # Запрос к Groq
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                *st.session_state.messages
            ],
            stream=True,
        )
        
        placeholder = st.empty()
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
