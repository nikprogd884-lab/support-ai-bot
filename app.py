import streamlit as st
from groq import Groq

# 1. Очистка ключа: .strip() уберет пробелы и невидимые символы
# ВНИМАНИЕ: Проверь, чтобы в самом ключе не было русских букв С или А (иногда путают раскладку)
RAW_KEY = "ТВОЙ_API_КЛЮЧ"
client = Groq(api_key=RAW_KEY.strip())

st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

# Стили (оставил только самое нужное)
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 20px; height: 3.5em; font-weight: bold; }
    .main-sos-btn button { background-color: #ff4b4b !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("Опора 🌱")
st.info("Анонимный чат поддержки. Данные удаляются при закрытии вкладки.")

# --- SOS ЛОГИКА ---
if "sos_active" not in st.session_state:
    st.session_state.sos_active = False

if not st.session_state.sos_active:
    st.markdown('<div class="main-sos-btn">', unsafe_allow_html=True)
    if st.button("🆘 ЭКСТРЕННАЯ ПОМОЩЬ (SOS)"):
        st.session_state.sos_active = True
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
else:
    st.warning("Показать номер телефона доверия?")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✅ Да"):
            st.success("📞 **8-800-2000-122**")
    with c2:
        if st.button("❌ Нет"):
            st.session_state.sos_active = False
            st.rerun()

st.divider()

# --- ЧАТ ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("Напиши мне..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # ВАЖНО: Системный промпт на английском, чтобы избежать UnicodeError. 
        # ИИ все равно поймет, что отвечать надо по-русски, так как ты пишешь по-русски.
        api_messages = [
            {"role": "system", "content": "You are 'Opora', a helpful assistant. Respond in Russian language only."}
        ]
        for m in st.session_state.messages:
            api_messages.append({"role": m["role"], "content": m["content"]})
        
        try:
            # Используем твой рабочий метод стриминга
            stream = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=api_messages,
                stream=True,
            )
            
            response_text = ""
            placeholder = st.empty()
            for chunk in stream:
                content = chunk.choices[0].delta.content
                if content:
                    response_text += content
                    placeholder.markdown(response_text + "▌")
            placeholder.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            # Если ошибка все равно есть, выводим её текст полностью для диагностики
            st.error(f"Ошибка API: {str(e)}")
