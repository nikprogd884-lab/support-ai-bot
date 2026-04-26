import streamlit as st
from groq import Groq

# 1. Инициализация (убедись, что ключ вставлен верно)
client = Groq(api_key="ТВОЙ_API_КЛЮЧ")

# Настройка страницы
st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

# Стили
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        height: 3.5em;
        font-weight: bold;
    }
    /* Красная кнопка SOS */
    .main-sos-btn button {
        background-color: #ff4b4b !important;
        color: white !important;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Опора 🌱")

# Описание
st.info("Это твой анонимный чат поддержки. Все сообщения удаляются после закрытия вкладки.")

# --- БЛОК SOS ---
if "sos_active" not in st.session_state:
    st.session_state.sos_active = False

if not st.session_state.sos_active:
    st.markdown('<div class="main-sos-btn">', unsafe_allow_html=True)
    if st.button("🆘 ЭКСТРЕННАЯ ПОМОЩЬ (SOS)"):
        st.session_state.sos_active = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Вы хотите получить номер телефона доверия?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Да, показать"):
            st.success("📞 **8-800-2000-122**\n\n(Детский телефон доверия)")
    with col2:
        if st.button("❌ Нет, назад"):
            st.session_state.sos_active = False
            st.rerun()

st.divider()

# --- ЧАТ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение истории
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ввод сообщения
if prompt := st.chat_input("Напиши, что тебя беспокоит..."):
    # Добавляем сообщение пользователя в историю
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Ответ ИИ
    with st.chat_message("assistant"):
        # Оставляем системный промпт максимально простым
        messages_for_api = [
            {"role": "system", "content": "Ты — Опора, бережный помощник. Отвечай на русском языке."}
        ]
        # Добавляем историю сообщений
        for m in st.session_state.messages:
            messages_for_api.append({"role": m["role"], "content": m["content"]})
        
        full_response = ""
        try:
            # Прямой запрос к API
            completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages_for_api,
                stream=True,
            )
            
            placeholder = st.empty()
            for chunk in completion:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    placeholder.markdown(full_response + "▌")
            placeholder.markdown(full_response)
            
            # Сохраняем ответ ассистента
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error("Произошла ошибка при получении ответа. Пожалуйста, проверьте API-ключ.")
