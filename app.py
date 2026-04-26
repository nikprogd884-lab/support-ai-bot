import streamlit as st
from groq import Groq

# Инициализация клиента Groq
client = Groq(api_key="ТВОЙ_API_КЛЮЧ")

# Настройка страницы
st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

# Стили для кнопок
st.markdown("""
    <style>
    /* Стиль основной красной кнопки SOS */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        font-weight: bold;
    }
    div[data-testid="stMarkdownContainer"] p {
        font-size: 1.1rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Заголовок
st.title("Опора 🌱")

# Описание
st.info("Это твой анонимный чат поддержки. Все сообщения удаляются после закрытия вкладки.")

# --- БЛОК SOS С ПОДТВЕРЖДЕНИЕМ ---
if "sos_active" not in st.session_state:
    st.session_state.sos_active = False

# Если кнопка SOS еще не нажата
if not st.session_state.sos_active:
    if st.button("🆘 ЭКСТРЕННАЯ ПОМОЩЬ (SOS)", type="primary"):
        st.session_state.sos_active = True
        st.rerun()

# Если нажали SOS, показываем выбор
else:
    st.warning("Вы хотите получить номер телефона доверия?")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Да, показать"):
            st.success("📞 **8-800-2000-122**\n\n(Детский телефон доверия)")
            if st.button("Закрыть номер"):
                st.session_state.sos_active = False
                st.rerun()
                
    with col2:
        if st.button("❌ Нет, назад"):
            st.session_state.sos_active = False
            st.rerun()

st.divider()

# --- ЛОГИКА ЧАТА ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Напиши, что тебя беспокоит..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        system_prompt = "Ты — Опора, бережный ИИ-помощник. Выслушай и поддержи пользователя анонимно."
        
        full_response = ""
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "system", "content": system_prompt}] + st.session_state.messages,
            stream=True,
        )
        
        placeholder = st.empty()
        for chunk in completion:
            if chunk.choices[0].delta.content:
                full_response += chunk.choices[0].delta.content
                placeholder.markdown(full_response + "▌")
        placeholder.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
