import streamlit as st
import json
from evaluation_dtr import MoteurFormulesDTR, Paroi, TypeIsolation
from zonage1 import AlgerianClimateEnricher

# تحميل البيانات
with open("data_communes_algeria.json", "r", encoding="utf-8") as f:
    communes_data = json.load(f)["wilayas"]

# تهيئة المحركات
moteur = MoteurFormulesDTR()
climate = AlgerianClimateEnricher()

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
        paroi1 = Paroi("Mur béton", TypeIsolation.REPARTIE, 0.5, 0.2, 2.0)
        paroi2 = Paroi("Mur brique", TypeIsolation.REPARTIE, 0.6, 0.25, 1.8)
        kl = moteur.calculer_kl_liaison_deux_parois("isolation_repartie_identiques", paroi1, paroi2)
        st.write(f"kl calculé = {kl} W/m·°C")
    else:
        st.error("⚠️ البلدية غير موجودة في قاعدة البيانات")
