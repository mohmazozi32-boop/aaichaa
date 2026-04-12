import streamlit as st
import requests

st.set_page_config(page_title="Évaluation Thermique Algérie", layout="wide")

st.title("منصة تقييم العزل الحراري - الجزائر 🇩🇿")

commune = st.text_input("أدخل اسم البلدية")

API_URL = "http://127.0.0.1:8000"

if st.button("عرض النتائج"):

    if not commune.strip():
        st.warning("يرجى إدخال اسم البلدية")
    else:
        try:
            # =========================
            # API CALL مع حماية
            # =========================
            response = requests.get(
                f"{API_URL}/commune/{commune}",
                timeout=5
            )

            # =========================
            # STATUS CHECK
            # =========================
            if response.status_code == 200:
                data = response.json()

                st.success("تم جلب البيانات بنجاح")

                # =========================
                # DISPLAY RESULTS
                # =========================
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("المنطقة الشتوية", data["winter_zone"])

                with col2:
                    st.metric("TBE", f"{data['tbe']} °C")

                with col3:
                    st.metric("المنطقة الصيفية", data["summer_zone"])

                st.subheader("تفاصيل الصيف")
                st.json(data["summer_conditions"])

            elif response.status_code == 404:
                st.error("❌ البلدية غير موجودة")

            else:
                st.error(f"خطأ في السيرفر: {response.text}")

        except requests.exceptions.ConnectionError:
            st.error("❌ لا يمكن الاتصال بالـ API (تأكد أن FastAPI يعمل)")
        except requests.exceptions.Timeout:
            st.error("⏳ انتهت مهلة الاتصال")
        except Exception as e:
            st.error(f"خطأ غير متوقع: {e}")
