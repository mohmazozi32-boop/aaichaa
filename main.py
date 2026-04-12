import streamlit as st
import json
from evaluation_dtr import MoteurFormulesDTR
from zonage1 import AlgerianClimateEnricher

# تحميل البيانات
with open("data_communes_algeria.json", "r", encoding="utf-8") as f:
    communes_data = json.load(f)["wilayas"]

with open("dtr_materiaux.json", "r", encoding="utf-8") as f:
    materiaux_data = json.load(f)

with open("dtr_coefficients.json", "r", encoding="utf-8") as f:
    coeffs_data = json.load(f)

# تهيئة المحركات
moteur = MoteurFormulesDTR()
climate = AlgerianClimateEnricher()

# واجهة Streamlit
st.set_page_config(page_title="Évaluation Thermique Algérie", layout="wide")
st.title("منصة تقييم العزل الحراري - الجزائر 🇩🇿")

commune = st.text_input("أدخل اسم البلدية")

if st.button("عرض النتائج"):
    commune_data = next((c for c in communes_data if c["name"].lower() == commune.lower()), None)
    if commune_data:
        winter_zone, tbe = climate.determine_winter_zone(commune_data, communes_data)
        summer_zone, summer_conditions = climate.determine_summer_zone(commune_data, communes_data)

        st.subheader("📌 النتائج المناخية")
        st.write(f"المنطقة الشتوية: {winter_zone} (Tbe = {tbe} °C)")
        st.write(f"المنطقة الصيفية: {summer_zone}")
        st.json(summer_conditions)

        st.subheader("📌 معاملات DTR")
        st.write("مثال حساب معامل kl لجدارين:")
        paroi1 = {"nom": "Mur béton", "epaisseur": 0.2, "K": 2.0}
        paroi2 = {"nom": "Mur brique", "epaisseur": 0.25, "K": 1.8}
        kl = moteur.calculer_kl_liaison_deux_parois(
            "isolation_repartie_identiques",
            moteur.Paroi("Mur béton", moteur.TypeIsolation.REPARTIE, 0.5, 0.2, 2.0),
            moteur.Paroi("Mur brique", moteur.TypeIsolation.REPARTIE, 0.6, 0.25, 1.8)
        )
        st.write(f"kl calculé = {kl} W/m·°C")

    else:
        st.error("⚠️ البلدية غير موجودة في قاعدة البيانات")

# قسم إضافي لعرض المواد
st.sidebar.title("📂 قاعدة بيانات المواد")
materiau_id = st.sidebar.text_input("أدخل ID مادة (مثال: polystyrene_expanse)")
if st.sidebar.button("عرض المادة"):
    found = next((m for m in materiaux_data["materiaux_homogenes"] if m["id"] == materiau_id), None)
    if not found:
        found = next((m for m in materiaux_data["materiaux_heterogenes"] if m["id"] == materiau_id), None)
    if found:
        st.sidebar.json(found)
    else:
        st.sidebar.error("❌ المادة غير موجودة")
