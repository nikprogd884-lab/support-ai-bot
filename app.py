import streamlit as st
from groq import Groq
import datetime

# 1. Настройка страницы
st.set_page_config(page_title="Опора", page_icon="🌱")

# Инициализация базы данных сообщений (в памяти сервера)
if "support_db" not in st.session_state:
    st.session_state.support_db = []

# 2. Подключение к Groq
if "GROQ_API_KEY" in st.secrets:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
else:
    st.error("Добавь GROQ_API_KEY в Secrets!")
    st.stop()

# 3. Боковое меню (Sidebar)
with st.sidebar:
    st.title("Меню")
    
    # --- РАЗДЕЛ ДЛЯ ПОЛЬЗОВАТЕЛЯ ---
    with st.expander("🆘 Написать в поддержку"):
        st.write("Нашли ошибку? Напишите нам анонимно.")
        with st.form("support_form", clear_on_submit=True):
            user_text = st.text_area("Ваше сообщение")
            submit = st.form_submit_button("Отправить")
            if submit and user_text:
                # Сохраняем сообщение с датой
                msg_data = {
                    "time": datetime.datetime.now().strftime("%d.%m %H:%M"),
                    "text": user_text,
                    "answer": None
                }
                st.session_state.support_db.append(msg_data)
                st.success("Отправлено! Разработчик скоро прочитает.")

    st.divider()

    # --- РАЗДЕЛ ДЛЯ ТЕБЯ (АДМИНКА) ---
    with st.expander("⚙️ Вход для автора"):
        password = st.text_input("Введите пароль", type="password")
        # ПРИДУМАЙ ПАРОЛЬ (замени '2406' на свой)
        if password == "2406": 
            st.subheader("Сообщения от пользователей:")
            if not st.session_state.support_db:
                st.write("Пока жалоб нет 👍")
            else:
                for i, msg in enumerate(st.session_state.support_db):
                    st.info(f"**[{msg['time']}]**: {msg['text']}")
                    # Поле для твоего ответа
                    if msg['answer']:
                        st.write(f"✅ Твой ответ: {msg['answer']}")
                    else:
                        ans = st.text_input(f"Ответить на #{i}", key=f"ans_{i}")
                        if st.button(f"Опубликовать ответ #{i}"):
                            st.session_state.support_db[i]['answer'] = ans
                            st.rerun()
        elif password:
            st.error("Неверный пароль")

# 4. Основной чат (Тот же код, что был)
st.title("🌱 Опора")

SYSTEM_PROMPT = """Ты — 'Опора', мудрый друг. Говори просто, без занудства и клише. Кратко и по делу. Будь тактичным."""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Что на душе?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": SYSTEM_PROMPT}] + 
                         [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                temperature=0.85
            )
            answer = response.choices[0].message.content
            st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        except:
            st.error("Ошибка связи.")
