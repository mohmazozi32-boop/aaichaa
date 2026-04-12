import streamlit as st
import json
from evaluation_dtr import MoteurFormulesDTR, Paroi, TypeIsolation
from zonage1 import AlgerianClimateEnricher
from categorize import Categorizer

# تحميل البيانات
with open("data_communes_algeria.json", "r", encoding="utf-8") as f:
    communes_data = json.load(f)["wilayas"]

# تهيئة المحركات
moteur = MoteurFormulesDTR()
climate = AlgerianClimateEnricher()
categorizer = Categorizer()

# إعداد الواجهة
st.set_page_config(page_title="Évaluation Thermique Algérie", layout="wide")

# رأس الصفحة
st.markdown(
    """
    <style>
    .title {
        font-size: 36px;
        font-weight: bold;
        color: #006400; /* أخضر */
        text-align: center;
    }
    .subtitle {
        font-size: 20px;
        color: #B22222; /* أحمر */
        text-align: center;
    }
    .card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        border: 2px solid #006400;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="title">منصة تقييم العزل الحراري - الجزائر 🇩🇿</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">واجهة احترافية لحساب المناطق المناخية ومعاملات DTR</div>', unsafe_allow_html=True)

# اختيار البلدية من قائمة منسدلة
commune_names = [c["name"] for c in communes_data]
commune = st.selectbox("📍 اختر البلدية", commune_names)

if st.button("عرض النتائج"):
    commune_data = next((c for c in communes_data if c["name"] == commune), None)
    if commune_data:
        winter_zone, tbe = climate.determine_winter_zone(commune_data, communes_data)
        summer_zone, summer_conditions = climate.determine_summer_zone(commune_data, communes_data)
        classification = categorizer.classify_commune(commune_data)

        # بطاقة النتائج المناخية
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📌 النتائج المناخية")
        st.write(f"**المنطقة الشتوية:** {winter_zone} (Tbe = {tbe} °C)")
        st.write(f"**المنطقة الصيفية:** {summer_zone}")
        st.json(summer_conditions)
        st.markdown('</div>', unsafe_allow_html=True)

        # بطاقة معاملات DTR
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📌 معاملات DTR")
        paroi1 = Paroi("Mur béton", TypeIsolation.REPARTIE, 0.5, 0.2, 2.0)
        paroi2 = Paroi("Mur brique", TypeIsolation.REPARTIE, 0.6, 0.25, 1.8)
        kl = moteur.calculer_kl_liaison_deux_parois("isolation_repartie_identiques", paroi1, paroi2)
        st.write(f"**kl calculé:** {kl} W/m·°C")
        st.markdown('</div>', unsafe_allow_html=True)

        # بطاقة التصنيف
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("📌 التصنيف")
        st.write(f"تصنيف البلدية: **{classification}**")
        st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("⚠️ البلدية غير موجودة في قاعدة البيانات")

# قسم جانبي لعرض المواد
st.sidebar.title("📂 قاعدة بيانات المواد")
materiau_id = st.sidebar.text_input("أدخل ID مادة (مثال: polystyrene_expanse)")
if st.sidebar.button("عرض المادة"):
    with open("dtr_materiaux.json", "r", encoding="utf-8") as f:
        materiaux_data = json.load(f)
    found = next((m for m in materiaux_data["materiaux_homogenes"] if m["id"] == materiau_id), None)
    if not found:
        found = next((m for m in materiaux_data["materiaux_heterogenes"] if m["id"] == materiau_id), None)
    if found:
        st.sidebar.json(found)
    else:
        st.sidebar.error("❌ المادة غير موجودة")
