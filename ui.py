import streamlit as st
import requests

st.set_page_config(page_title="Évaluation Thermique Algérie", layout="wide")

st.title("منصة تقييم العزل الحراري - الجزائر 🇩🇿")

commune = st.text_input("أدخل اسم البلدية")

if st.button("عرض النتائج"):
    response = requests.get(f"http://localhost:8000/commune/{commune}")
    if response.status_code == 200:
        data = response.json()
        st.subheader("📌 النتائج")
        st.write(f"المنطقة الشتوية: {data['winter_zone']} (Tbe = {data['tbe']} °C)")
        st.write(f"المنطقة الصيفية: {data['summer_zone']}")
        st.json(data['summer_conditions'])
    else:
        st.error("⚠️ البلدية غير موجودة")
