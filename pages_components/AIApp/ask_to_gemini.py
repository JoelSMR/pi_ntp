import streamlit as st
from back_pages.AIApp.Utils import gemini_api_utils

def ask_to_gemini():
    with st.container():
        col1,col2=st.columns(2)
        col1.title("Ask to gemini")
        question=st.text_input("Ingresa tu pregunta")
        key= st.text_input("API KEY")
        answer="Aprenderemos Cosas Nuevas"
        if st.button("Preguntar"):
            st.spinner(text="Thinking",show_time=True)
            answer=  gemini_api_utils.ask_question_to_gemini(question,key)
        st.text(answer)

