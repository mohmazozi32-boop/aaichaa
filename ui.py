import streamlit as st

def set_theme(mode: str):
    """تطبيق ثيم نهار/ليل"""
    if mode == "Nuit":
        st.markdown(
            """
            <style>
            body {background-color: #1e1e1e; color: white;}
            .stButton>button {background-color: #444; color: white;}
            </style>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <style>
            body {background-color: #f9f9f9; color: black;}
            .stButton>button {background-color: #ddd; color: black;}
            </style>
            """,
            unsafe_allow_html=True
        )

def language_selector():
    """اختيار اللغة"""
    lang = st.radio("Choisir la langue / اختر اللغة", ["Français", "العربية"])
    if lang == "العربية":
        st.success("تم اختيار اللغة العربية")
    else:
        st.success("Langue française sélectionnée")
    return lang

def header(title_fr: str, title_ar: str, lang: str):
    """عرض العنوان حسب اللغة"""
    if lang == "العربية":
        st.title(title_ar)
    else:
        st.title(title_fr)
