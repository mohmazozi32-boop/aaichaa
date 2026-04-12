import streamlit as st
import requests

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="Thermal Algeria Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# THEME (Dark / Light)
# =========================
mode = st.sidebar.radio("🌗 الوضع", ["نهاري", "ليلي"])

if mode == "ليلي":
    bg = "#0e1117"
    card = "#1c1f26"
    text = "#ffffff"
    accent = "#ff4b4b"
    green = "#00c853"
else:
    bg = "#f5f7fb"
    card = "#ffffff"
    text = "#111111"
    accent = "#d00000"
    green = "#1b8a3a"

st.markdown(
    f"""
    <style>
    .main {{
        background-color: {bg};
        color: {text};
    }}
    .card {{
        background-color: {card};
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 15px;
    }}
    .title {{
        font-size: 28px;
        font-weight: bold;
        color: {accent};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# HEADER
# =========================
st.markdown("<div class='title'>🏗 منصة تقييم العزل الحراري - الجزائر</div>", unsafe_allow_html=True)

st.write("ابحث عن البلدية لمعرفة التصنيف المناخي (شتاء / صيف)")

# =========================
# INPUT
# =========================
commune = st.text_input("🔎 اسم البلدية")

# =========================
# BUTTON
# =========================
if st.button("عرض النتائج"):

    if commune.strip() == "":
        st.warning("يرجى إدخال اسم البلدية")
    else:
        try:
            response = requests.get(f"http://localhost:8000/commune/{commune}")

            if response.status_code == 200:
                data = response.json()

                # =========================
                # CARDS
                # =========================
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.markdown(f"""
                    <div class='card'>
                    <h3>❄ المنطقة الشتوية</h3>
                    <h2 style="color:{accent}">{data['winter_zone']}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    st.markdown(f"""
                    <div class='card'>
                    <h3>🌡 TBE</h3>
                    <h2>{data['tbe']} °C</h2>
                    </div>
                    """, unsafe_allow_html=True)

                with col3:
                    st.markdown(f"""
                    <div class='card'>
                    <h3>☀ المنطقة الصيفية</h3>
                    <h2 style="color:{green}">{data['summer_zone']}</h2>
                    </div>
                    """, unsafe_allow_html=True)

                # =========================
                # DETAILS
                # =========================
                st.markdown("### 📊 تفاصيل الصيف")

                st.json(data["summer_conditions"])

            else:
                st.error("⚠️ البلدية غير موجودة")

        except Exception as e:
            st.error(f"خطأ في الاتصال بالـ API: {e}")
