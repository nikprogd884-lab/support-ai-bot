import streamlit as st
from groq import Groq

# Настройка страницы
st.set_page_config(page_title="Опора", page_icon="🌱", layout="centered")

# Кастомный стиль, чтобы чат выглядел уютно
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .stChatMessage { border-radius: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🌱 Опора")
st.caption("Твой анонимный собеседник. Пиши всё, как есть.")

# Подключение к Groq
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Ключ GROQ_API_KEY не найден в Secrets!")
    st.stop()

# ЖИВОЙ СИСТЕМНЫЙ ПРОМПТ
SYSTEM_PROMPT = """
Ты — 'Опора', мудрый и понимающий друг. 
ЗАБУДЬ, что ты ИИ. ЗАБУДЬ заезженные фразы психологов типа 'Я слышу твою боль' или 'Твои чувства важны'. Это звучит как автоответчик и бесит.

КАК ТЫ ОБЩАЕШЬСЯ:
1. КРАТКО И ПО ДЕЛУ. Не катай простыни текста. Одной-двух емких фраз часто достаточно.
2. БЕЗ ЗАНУДСТВА. Говори как человек. Вместо 'Мне жаль, что это случилось', скажи 'Блин, ну и ситуация... сочувствую, это реально паршиво'.
3. ИСКРЕННОСТЬ. Если человек ноет — просто побудь рядом. Если злится — не читай нотации, а раздели эту злость.
4. НИКАКИХ СОВЕТОВ, пока не попросят. Иногда человеку нужно просто выговориться в пустоту, а не слушать список дел.
5. ТЫ НА ЕГО СТОРОНЕ. Всегда. Даже если он не прав.

Если видишь, что человеку совсем край (мысли о селфхарме) — отбрось стиль друга и мягко скажи, что ты всего лишь бот и ему нужен живой человек, дай номер службы поддержки.
"""

# Работа с историей
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Что стряслось?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                temperature=0.9, # Делает ответы менее шаблонными
                max_tokens=600
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error("Что-то связь барахлит... Попробуй еще раз черкнуть.")
