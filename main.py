import streamlit as st
import backend
import ui

st.set_page_config(page_title="Évaluation Thermique Algérie", layout="wide")

# تطبيق ألوان علم الجزائر في التصميم
st.markdown(
    """
    <style>
    body {
        background-image: url('https://upload.wikimedia.org/wikipedia/commons/7/77/Flag_of_Algeria.svg');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    .main {
        background-color: rgba(255,255,255,0.85);
        padding: 20px;
        border-radius: 10px;
    }
    h1, h2, h3 {
        color: #006233; /* الأخضر */
    }
    .stButton>button {
        background-color: #d21034; /* الأحمر */
        color: white;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# اختيار اللغة
lang = ui.language_selector()

# اختيار الثيم (نهار/ليل)
theme = st.radio("Mode d'affichage", ["Jour", "Nuit"])
ui.set_theme(theme)

# عنوان الصفحة
ui.header("Évaluation Thermique Algérie", "منصة تقييم العزل الحراري - الجزائر", lang)

# إدخال بيانات المبنى
st.subheader("إدخال بيانات المبنى")
surface = st.number_input("Surface totale (m²)", min_value=10.0, step=1.0)
hauteur = st.number_input("Hauteur sous plafond (m)", min_value=2.0, step=0.1)
materiau = st.selectbox("Matériau principal", ["Béton", "Brique", "Pierre", "Autre"])
isolation = st.selectbox("Type d'isolation", ["Répartie", "Rapportée", "Aucune"])

# تحميل قائمة الولايات
data = backend.load_communes_data()
wilayas = [w["name"] for w in data["wilayas"]]

# اختيار الولاية
wilaya = st.selectbox("اختر الولاية", options=wilayas)

# حساب النتائج
results = backend.evaluate_commune(wilaya)

st.subheader("النتائج المناخية")
st.write(results["climate"])

st.subheader("معامل الجسر الحراري")
st.write(f"kl = {results['kl_value']} W/m.°C")
