import streamlit as st
import requests

st.title("🤖 Чат с умным ИИ Lottery")

HF_TOKEN = "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"

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.chat_input("Спроси что угодно у Lottery...")

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
        
    with st.chat_message("assistant"):
        res_box = st.empty()
        try:
            url = "https://huggingface.co"
            headers = {"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}
            payload = {
                "messages": [
                    {"role": "system", "content": "Ты ИИ Lottery. Тебя создал Loter. Отвечай дерзко и с сарказмом строго на русском языке."},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 400
            }
            res = requests.post(url, headers=headers, json=payload, timeout=15)
            if res.status_code == 200:
                ai_response = res.json()["choices"]["message"]["content"].strip()
            else:
                ai_response = "Сервер задумался, Loter! Нажми отправку еще раз."
        except Exception:
            ai_response = "Сеть лагает, босс! Повтори запрос."
            
        res_box.markdown(ai_response)
