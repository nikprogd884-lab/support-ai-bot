import streamlit as st
from groq import Groq

# 1. Жесткая очистка ключа через фильтр символов
def super_clean(text):
    # Оставляем только английские буквы, цифры и дефис. Всё остальное — вон.
    return "".join(char for char in text if char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")

RAW_KEY = "ТВОЙ_НОВЫЙ_КЛЮЧ" 
CLEAN_KEY = super_clean(RAW_KEY)

# Инициализация с очищенным ключом
client = Groq(api_key=CLEAN_KEY)

st.set_page_config(page_title="Opora", page_icon="🌱")

# Заголовок и SOS (упростил до предела для теста)
st.title("Опора 🌱")

if st.button("🆘 SOS"):
    st.warning("Телефон доверия: 8-800-2000-122")

st.divider()

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
        # ПРОВЕРКА: Если ошибка вылетает здесь, значит проблема в ТЕКСТЕ СООБЩЕНИЯ (кириллице)
        # В Python 3.14 иногда ломается передача UTF-8 в заголовках.
        try:
            # Важно: передаем промпт как чистый текст
            chat_completion = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Speak Russian."},
                    {"role": "user", "content": prompt}
                ],
                stream=False # Отключим стриминг для теста, так надежнее
            )
            
            response = chat_completion.choices[0].message.content
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})
            
        except Exception as e:
            st.error(f"Ошибка API: {str(e)}")
            st.info("Если видишь ASCII Error — попробуй ввести приветствие на АНГЛИЙСКОМ (Hello).")
