import streamlit as st
import json
from Evaluation_Formules_DTR import MoteurFormulesDTR, Paroi, TypeIsolation
from zonage1 import AlgerianClimateEnricher
from categorize import Categorizer

# تحميل البيانات
with open("data_communes_algeria.json", "r", encoding="utf-8") as f:
    communes_data = json.load(f)["wilayas"]

with open("dtr_coefficients.json", "r", encoding="utf-8") as f:
    coeffs_data = json.load(f)

with open("dtr_verification.json", "r", encoding="utf-8") as f:
    verification_data = json.load(f)

# تهيئة المحركات
moteur = MoteurFormulesDTR()
climate = AlgerianClimateEnricher()
categorizer = Categorizer()

st.set_page_config(page_title="Évaluation Thermique Algérie", layout="wide")
st.title("منصة تقييم العزل الحراري - الجزائر 🇩🇿")

commune_names = [c["name"] for c in communes_data]
commune = st.selectbox("📍 اختر البلدية", commune_names)

if st.button("عرض النتائج"):
    commune_data = next((c for c in communes_data if c["name"] == commune), None)
    if commune_data:
        winter_zone, tbe = climate.determine_winter_zone(commune_data, communes_data)
        summer_zone, summer_conditions = climate.determine_summer_zone(commune_data, communes_data)
        classification = categorizer.classify_commune(commune_data)

        tab1, tab2, tab3, tab4 = st.tabs(["🏙️ البلدية", "🌡️ المناخ", "🧱 معاملات DTR", "📊 التحقق"])

        with tab1:
            st.write(commune_data)

        with tab2:
            st.write(f"المنطقة الشتوية: {winter_zone} (Tbe = {tbe} °C)")
            st.write(f"المنطقة الصيفية: {summer_zone}")
            st.json(summer_conditions)

        with tab3:
            paroi1 = Paroi("Mur béton", TypeIsolation.REPARTIE, 0.5, 0.2, 2.0)
            paroi2 = Paroi("Mur brique", TypeIsolation.REPARTIE, 0.6, 0.25, 1.8)
            kl = moteur.calculer_kl_liaison_deux_parois("isolation_repartie_identiques", paroi1, paroi2)
            st.write(f"kl calculé = {kl} W/m·°C")
            st.write("معاملات إضافية من DTR:")
            st.json(coeffs_data["echanges_superficiels"]["hiver"])

        with tab4:
            st.write("قيم التحقق التنظيمي:")
            st.json(verification_data["parois_verticales"]["latitude_40N"]["A"]["alt_<500"])

        st.subheader("📌 التصنيف")
        st.write(f"تصنيف البلدية: {classification}")
    else:
        st.error("⚠️ البلدية غير موجودة في قاعدة البيانات")
