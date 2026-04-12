import streamlit as st
from backend import Backend

backend = Backend()

st.title("واجهة إضافية لتقييم العزل الحراري")

commune = st.text_input("أدخل اسم البلدية")

if st.button("عرض النتائج"):
    data = backend.get_commune_info(commune)
    if data:
        st.json(data)
    else:
        st.error("⚠️ البلدية غير موجودة")
