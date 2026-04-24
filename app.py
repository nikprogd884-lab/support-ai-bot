import streamlit as st
from groq import Groq
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import uuid

# --- 1. НАСТРОЙКИ ---
st.set_page_config(page_title="Опора 🌱", layout="wide")

# Подключение к Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
SPREADSHEET_ID = "1oc_E2IHKjJZSjt9fscY93srN77sNeN4qjqFrP4QkRN0"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"

def load_messages():
    try:
        df = conn.read(spreadsheet=SHEET_URL, worksheet="Chats", ttl=0)
        return df.dropna(how='all')
    except:
        return pd.DataFrame()

def save_message(df):
    conn.update(spreadsheet=SHEET_URL, worksheet="Chats", data=df)

def ask_ai(messages):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "Ты Опора. Мудрый и теплый собеседник."}] + messages,
            max_tokens=500
        )
        return res.choices[0].message.content
    except Exception as e:
        return f"Ошибка ИИ: {e}"

# --- 2. ИНТЕРФЕЙС ---
st.title("🌱 Опора — Твой собеседник")

# Загружаем историю из таблицы
if "history_df" not in st.session_state:
    st.session_state.history_df = load_messages()

# Если чат пустой, создаем новый ID
if "chat_id" not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())

# Отображаем старые сообщения
for _, row in st.session_state.history_df.iterrows():
    # Фильтруем сообщения только для текущей сессии (чтобы не видеть чужие)
    if row["ID_Чата"] == st.session_state.chat_id:
        with st.chat_message(row["Роль"]):
            st.markdown(row["Сообщение"])

# Поле ввода
if prompt := st.chat_input("Напиши мне что-нибудь..."):
    # Показываем сообщение пользователя
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Формируем контекст для ИИ из текущей сессии
    current_context = []
    session_messages = st.session_state.history_df[st.session_state.history_df["ID_Чата"] == st.session_state.chat_id]
    for _, r in session_messages.iterrows():
        current_context.append({"role": r["Роль"], "content": r["Сообщение"]})
    current_context.append({"role": "user", "content": prompt})

    # Ответ ИИ
    with st.chat_message("assistant"):
        answer = ask_ai(current_context)
        st.markdown(answer)

    # Сохраняем в таблицу
    new_rows = pd.DataFrame([
        {"ID_Чата": st.session_state.chat_id, "Роль": "user", "Сообщение": prompt, "Дата": datetime.now().strftime("%H:%M")},
        {"ID_Чата": st.session_state.chat_id, "Роль": "assistant", "Сообщение": answer, "Дата": datetime.now().strftime("%H:%M")}
    ])
    
    st.session_state.history_df = pd.concat([st.session_state.history_df, new_rows], ignore_index=True)
    save_message(st.session_state.history_df)
    st.rerun()
