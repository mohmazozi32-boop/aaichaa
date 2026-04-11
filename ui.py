import streamlit as st

def set_theme(mode: str):

    if mode == "Nuit":
        bg = "#0e1117"
        card = "#1c1f26"
        text = "#ffffff"
    else:
        bg = "#f4f6f9"
        card = "#ffffff"
        text = "#1a1a1a"

    st.markdown(f"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700&family=Montserrat:wght@400;600&display=swap');

    body {{
        background-color: {bg};
        color: {text};
        font-family: 'Montserrat', 'Cairo', sans-serif;
    }}

    .main {{
        background-color: {bg};
    }}

    /* Header */
    .app-header {{
        background: linear-gradient(90deg, #006233, #d21034);
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 10px;
    }}

    .subtitle {{
        text-align: center;
        font-size: 16px;
        margin-bottom: 25px;
    }}

    /* Cards */
    .card {{
        background-color: {card};
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }}

    /* Buttons */
    .stButton>button {{
        background: linear-gradient(90deg, #006233, #d21034);
        color: white;
        border-radius: 10px;
        font-weight: bold;
        padding: 10px 18px;
        border: none;
    }}

    /* Arabic */
    .ar {{
        font-family: 'Cairo', sans-serif;
        direction: rtl;
        text-align: right;
    }}

    /* French */
    .fr {{
        font-family: 'Montserrat', sans-serif;
    }}

    </style>
    """, unsafe_allow_html=True)


def language_selector():
    return st.radio(
        "Choisir la langue / اختر اللغة",
        ["Français", "العربية"],
        horizontal=True
    )


def header(title_fr: str, title_ar: str, lang: str):

    if lang == "العربية":
        st.markdown(f"""
        <div class="app-header">{title_ar}</div>
        <div class="subtitle">منصة تقييم العزل الحراري حسب المعايير الجزائرية</div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <style>
        body { direction: rtl; text-align: right; }
        </style>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"""
        <div class="app-header">{title_fr}</div>
        <div class="subtitle">Plateforme d’évaluation thermique وفق DTR</div>
        """, unsafe_allow_html=True)


def card_start():
    st.markdown('<div class="card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)
