import streamlit as st
from groq import Groq
import random

# --- 1. КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="Опора", layout="centered")

# Функция связи с ИИ
def ask_ai(messages):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты Опора — теплый и краткий помощник. Твоя задача — выслушать и поддержать человека."}] + messages,
            max_tokens=500
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Ошибка: {e}"

# Список поддерживающих фраз
AFFIRMATIONS = [
    "Ты справляешься лучше, чем тебе кажется. ✨",
    "Твои чувства важны. Позволь им быть. ❤️",
    "Маленькие шаги тоже ведут к большим целям. 🌱",
    "Ты ценен просто потому, что ты есть. ⭐",
    "Дыши. Всё обязательно наладится. 🙏"
]

# --- 2. ИНТЕРФЕЙС ПРИЛОЖЕНИЯ ---
st.title("🌱 Опора")

# Вывод случайной фразы при загрузке
if "daily_quote" not in st.session_state:
    st.session_state.daily_quote = random.choice(AFFIRMATIONS)
st.write(f"*{st.session_state.daily_quote}*")

# --- 3. БЛОК ЭКСТРЕННОЙ ПОМОЩИ (SOS) ---
with st.expander("🚨 ЭКСТРЕННАЯ ПОМОЩЬ (SOS)"):
    st.error("Помни: ты не один. Помощь рядом.")
    
    col_btn1, col_btn2 = st.columns(2)
    
    if col_btn1.button("📞 Позвонить детям", use_container_width=True):
        st.session_state.confirm_call = "88002000122"
    
    if col_btn2.button("📞 Психолог МЧС", use_container_width=True):
        st.session_state.confirm_call = "74959895050"

    # Логика подтверждения звонка
    if "confirm_call" in st.session_state and st.session_state.confirm_call:
        st.warning(f"Точно вызвать службу {st.session_state.confirm_call}?")
        c1, c2 = st.columns(2)
        if c1.button("✅ ДА, звонить", type="primary", use_container_width=True):
            # Переход по ссылке tel: для звонка
            st.markdown(f'<meta http-equiv="refresh" content="0; url=tel:{st.session_state.confirm_call}">', unsafe_allow_html=True)
            st.session_state.confirm_call = None
        if c2.button("❌ НЕТ, отмена", use_container_width=True):
            st.session_state.confirm_call = None
            st.rerun()

    st.divider()
    st.subheader("🧘 Техника дыхания")
    st.write("Вдох (4 сек) ➜ Пауза (4 сек) ➜ Выдох (4 сек) ➜ Пауза (4 сек)")
    st.subheader("🌍 Заземление 5-4-3-2-1")
    st.caption("Назови: 5 предметов вокруг, 4 тактильных ощущения, 3 звука, 2 запаха, 1 вкус.")

st.divider()

# --- 4. ЛОГИКА ЧАТА ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Кнопка быстрой очистки чата
if st.button("🗑️ Очистить диалог"):
    st.session_state.messages = []
    st.rerun()

# Отображение сообщений
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода сообщения
if prompt := st.chat_input("Что у тебя на душе?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Слушаю..."):
            response = ask_ai(st.session_state.messages)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
