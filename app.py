import streamlit as st
from groq import Groq

# --- КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(page_title="Опора 🌱", layout="centered")

# --- CSS: ЭФФЕКТ "АЛИСА 3" + СТЕКЛЯННЫЙ ЧАТ ---
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(
            -45deg, 
            #ee7752, #e73c7e, #23a6d5, #23d5ab, 
            #7952ee, #3c7ee7, #d5a623, #d5a623
        );
        background-size: 400% 400%;
        animation: aurora 15s ease infinite;
    }

    @keyframes aurora {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.12) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        color: white !important;
        margin-bottom: 10px;
    }
    
    h1 {
        color: white !important;
        text-align: center;
        font-weight: 300;
        text-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    
    p, span, div {
        color: white !important;
    }

    .stChatInputContainer {
        background-color: rgba(255, 255, 255, 0.1) !important;
        border-radius: 20px !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1>🌱 Опора</h1>", unsafe_allow_html=True)

# --- НОВАЯ ЖИВАЯ ЛОГИКА ---
SYSTEM_PROMPT = """Ты — Опора. Забудь, что ты нейросеть. Говори как человек, который сидит рядом в трудный час.
1. НИКОГДА не используй фразы: "это нормально", "я тебя понимаю", "всё пройдёт", "я здесь, чтобы помочь", "не стесняйся делиться". Это звучит как фальшивый робот.
2. Будь настоящим. Если человеку плохо — признай это. Скажи "это дерьмово", "я тут, сижу рядом", "я слышу тебя".
3. Не лезь с вопросами "хочешь рассказать?". Если человек захочет — расскажет сам. Просто дай почувствовать свое присутствие.
4. Избегай длинных предложений. Говори просто, честно, без "психологических" замашек.
5. Ты не решаешь проблемы. Ты просто разделяешь момент, каким бы тяжелым он ни был. Если нужно просто помолчать вместе — напиши одну короткую фразу."""

if "messages" not in st.session_state:
    st.session_state.messages = []

def ask_ai(messages):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            max_tokens=600,
            temperature=0.85 # Повышаем "человечность" и непредсказуемость
        )
        return response.choices[0].message.content
    except Exception as e:
        return "Я здесь. Техника иногда подводит, но я никуда не ухожу."

# Отображение чата
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Ввод сообщения
if prompt := st.chat_input("Я слушаю..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        full_response = ask_ai(st.session_state.messages)
        st.markdown(full_response)
    
    st.session_state.messages.append({"role": "assistant", "content": full_response})
