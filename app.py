import streamlit as st
from groq import Groq

# Настройка внешнего вида
st.set_page_config(page_title="Опора", page_icon="🌱")
st.title("🌱 Система поддержки «Опора»")
st.caption("Я здесь, чтобы выслушать тебя и поддержать в трудную минуту.")

# Проверка ключа
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.warning("Пожалуйста, добавьте GROQ_API_KEY в Secrets на Streamlit Cloud.")
    st.stop()

# История сообщений
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Поле ввода
if prompt := st.chat_input("Расскажи, что случилось?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Тут мы задаем "характер" ИИ
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {
                    "role": "system", 
                    "content": "Ты — эмпатичный и добрый помощник. Твоя цель — психологическая поддержка. Будь кратким, теплым и не давай советов, если тебя не просят, просто сопереживай. Если видишь риск вреда себе — дай контакты помощи."
                },
                *st.session_state.messages
            ]
        )
        answer = response.choices[0].message.content
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
