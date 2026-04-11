import streamlit as st
from app import backend, ui

st.set_page_config(page_title="Évaluation Thermique Algérie", layout="wide")

# اختيار اللغة
lang = ui.language_selector()

# اختيار الثيم
theme = st.radio("Mode d'affichage", ["Jour", "Nuit"])
ui.set_theme(theme)

# عنوان الصفحة
ui.header("Évaluation Thermique Algérie", "منصة تقييم العزل الحراري - الجزائر", lang)

# تحميل قائمة الولايات
data = backend.load_communes_data()
wilayas = [w["name"] for w in data["wilayas"]]

# اختيار الولاية
wilaya = st.selectbox("اختر الولاية", options=wilayas)

# حساب النتائج
results = backend.evaluate_commune(wilaya)

st.subheader("📊 النتائج المناخية")
st.write(results["climate"])

st.subheader("⚙️ معامل الجسر الحراري")
st.write(f"kl = {results['kl_value']} W/m.°C")
