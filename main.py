import streamlit as st
import backend
import ui

st.set_page_config(page_title="Évaluation Thermique Algérie", layout="wide")

# ---------- اختيار الثيم ----------
theme = st.radio("Mode d'affichage", ["Jour", "Nuit"])

# ---------- ألوان حسب الثيم ----------
if theme == "Jour":
    bg_color = "#f5f7fa"
    card_color = "#ffffff"
    text_color = "#1a1a1a"
else:
    bg_color = "#0e1117"
    card_color = "#1c1f26"
    text_color = "#ffffff"

# ---------- تصميم احترافي ----------
st.markdown(f"""
<style>

/* الخلفية العامة */
body {{
    background-color: {bg_color};
}}

/* الحاوية الرئيسية */
.main {{
    background-color: {bg_color};
}}

/* العنوان الرئيسي */
.title {{
    font-size: 40px;
    font-weight: bold;
    color: #006233;
    text-align: center;
    margin-bottom: 10px;
}}

/* subtitle */
.subtitle {{
    text-align: center;
    color: {text_color};
    font-size: 18px;
    margin-bottom: 30px;
}}

/* cards */
.card {{
    background-color: {card_color};
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}}

/* العناوين */
h2, h3 {{
    color: #006233;
}}

/* الأزرار */
.stButton>button {{
    background: linear-gradient(90deg, #006233, #d21034);
    color: white;
    font-weight: bold;
    border-radius: 10px;
    padding: 10px 20px;
    border: none;
}}

/* selectbox و input */
div[data-baseweb="select"] > div {{
    background-color: {card_color};
    color: {text_color};
}}

input {{
    background-color: {card_color} !important;
    color: {text_color} !important;
}}

/* شريط علوي */
.header {{
    background: linear-gradient(90deg, #006233, #d21034);
    padding: 15px;
    border-radius: 12px;
    text-align: center;
    color: white;
    font-size: 22px;
    font-weight: bold;
    margin-bottom: 20px;
}}

</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="header">Évaluation Thermique Algérie</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">منصة تقييم العزل الحراري حسب المعايير الجزائرية</div>', unsafe_allow_html=True)

# ---------- اللغة ----------
lang = ui.language_selector()

# ---------- إدخال البيانات ----------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("إدخال بيانات المبنى")

surface = st.number_input("Surface totale (m²)", min_value=10.0, step=1.0)
hauteur = st.number_input("Hauteur sous plafond (m)", min_value=2.0, step=0.1)
materiau = st.selectbox("Matériau principal", ["Béton", "Brique", "Pierre", "Autre"])
isolation = st.selectbox("Type d'isolation", ["Répartie", "Rapportée", "Aucune"])

st.markdown('</div>', unsafe_allow_html=True)

# ---------- اختيار الولاية ----------
data = backend.load_communes_data()
wilayas = [w["name"] for w in data["wilayas"]]

st.markdown('<div class="card">', unsafe_allow_html=True)
wilaya = st.selectbox("اختر الولاية", options=wilayas)
st.markdown('</div>', unsafe_allow_html=True)

# ---------- النتائج ----------
results = backend.evaluate_commune(wilaya)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("النتائج المناخية")
st.write(results["climate"])
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("معامل الجسر الحراري")
st.write(f"kl = {results['kl_value']} W/m.°C")
st.markdown('</div>', unsafe_allow_html=True)
