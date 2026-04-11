import streamlit as st

# ---------- إعداد الثيم ----------
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

    /* الخلفية العامة */
    body {{
        background-color: {bg};
        color: {text};
    }}

    .main {{
        background-color: {bg};
    }}

    /* الكروت */
    .card {{
        background-color: {card};
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }}

    /* العناوين */
    h1, h2, h3 {{
        color: #006233;
        font-weight: bold;
    }}

    /* الأزرار */
    .stButton>button {{
        background: linear-gradient(90deg, #006233, #d21034);
        color: white;
        border-radius: 10px;
        font-weight: bold;
        padding: 10px 18px;
        border: none;
        transition: 0.3s;
    }}

    .stButton>button:hover {{
        transform: scale(1.05);
        opacity: 0.9;
    }}

    /* Inputs */
    input, textarea {{
        background-color: {card} !important;
        color: {text} !important;
        border-radius: 8px !important;
    }}

    /* Selectbox */
    div[data-baseweb="select"] > div {{
        background-color: {card};
        color: {text};
        border-radius: 8px;
    }}

    /* Header */
    .app-header {{
        background: linear-gradient(90deg, #006233, #d21034);
        padding: 18px;
        border-radius: 12px;
        text-align: center;
        color: white;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }}

    .subtitle {{
        text-align: center;
        font-size: 16px;
        margin-bottom: 25px;
        color: {text};
    }}

    </style>
    """, unsafe_allow_html=True)


# ---------- اختيار اللغة ----------
def language_selector():
    lang = st.radio(
        "Choisir la langue / اختر اللغة",
        ["Français", "العربية"],
        horizontal=True
    )
    return lang


# ---------- Header احترافي ----------
def header(title_fr: str, title_ar: str, lang: str):

    if lang == "العربية":
        st.markdown(
            f"""
            <div class="app-header">{title_ar}</div>
            <div class="subtitle">منصة تقييم العزل الحراري حسب المعايير الجزائرية</div>
            """,
            unsafe_allow_html=True
        )

        # تفعيل اتجاه RTL
        st.markdown(
            """
            <style>
            body {
                direction: rtl;
                text-align: right;
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    else:
        st.markdown(
            f"""
            <div class="app-header">{title_fr}</div>
            <div class="subtitle">Plateforme d’évaluation thermique وفق DTR Algérien</div>
            """,
            unsafe_allow_html=True
        )


# ---------- Card helper ----------
def card_start():
    st.markdown('<div class="card">', unsafe_allow_html=True)

def card_end():
    st.markdown('</div>', unsafe_allow_html=True)
