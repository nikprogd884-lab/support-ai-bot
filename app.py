import streamlit as st
from groq import Groq

st.set_page_config(page_title="Опора", page_icon="🌱")
st.title("🌱 Система поддержки «Опора»")

# Безопасное получение ключа
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Ключ GROQ_API_KEY не найден в Secrets!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

# Отображение чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Расскажи, что у тебя на душе?"):
    # Добавляем сообщение пользователя
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            # Формируем запрос
            response = client.chat.completions.create(
                model="llama3-8b-8192", # Используем более стабильную модель
                messages=[
                    {"role": "system", "content": "Ты — добрый и эмпатичный помощник. Твоя цель — психологическая поддержка. Отвечай кратко и тепло."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ],
                temperature=0.7
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            
        except Exception as e:
            st.error(f"Произошла ошибка при запросе к Groq:")
            st.code(str(e))
            # Если ошибка в ключе, мы это увидим здесь
