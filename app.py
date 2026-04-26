import streamlit as st
from groq import Groq

# Инициализация клиента Groq
client = Groq(api_key="ТВОЙ_API_КЛЮЧ")

# Настройка страницы
st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

# Стили для кнопки SOS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        background-color: #ff4b4b !important;
        color: white !important;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover {
        background-color: #ff3333 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Заголовок
st.title("Опора 🌱")

# Краткое описание пользы
st.info("""
**Опора** — это твоё анонимное пространство. Здесь можно выговориться ИИ-помощнику, не опасаясь за свои данные. Всё удалится после закрытия вкладки.
""")

# Блок SOS
if st.button("🆘 ДЕТСКИЙ ТЕЛЕФОН ДОВЕРИЯ"):
    st.warning("Номер для звонка: **8-800-2000-122** (Анонимно, бесплатно, круглосуточно)")

st.divider()

# Логика чата
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ввод текста
if prompt := st.chat_input("Напиши, что тебя беспокоит..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Промпт для ИИ
        system_prompt = "Ты — Опора, бережный ИИ-помощник. Твоя задача — выслушать пользователя и поддержать его. Будь краток, эмпатичен и не осуждай."
        
        full_response = ""
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
