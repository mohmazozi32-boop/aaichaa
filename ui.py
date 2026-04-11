import streamlit as st

def set_theme(mode: str):
    if mode == "Nuit":
        st.markdown(
            """
            <style>
            body {background-color: #1e1e1e; color: white;}
            .stButton>button {background-color: #d21034; color: white;}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            body {background-color: #f9f9f9; color: black;}
            .stButton>button {background-color: #006233; color: white;}
            </style>
            """,
            unsafe_allow_html=True
        )

def language_selector():
    lang = st.radio("Choisir la langue / اختر اللغة", ["Français", "العربية"])
    return lang

def header(title_fr: str, title_ar: str, lang: str):
    if lang == "العربية":
        st.title(title_ar)
    else:
        st.title(title_fr)
