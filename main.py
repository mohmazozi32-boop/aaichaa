import streamlit as st
import json
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="DTR Thermal Pro", page_icon="🇩🇿", layout="wide")

# --- دالة تحميل البيانات ---
def load_data(file_name):
    if os.path.exists(file_name):
        with open(file_name, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except:
                return None
    return None

def get_comprehensive_wilayas():
    base = load_data('data_communes_algeria.json')
    if not base: return []
    wilayas = base.get('wilayas', [])
    zone_map = {}
    for z_file, z_name in [('communes_zone_A.json', 'A'), ('communes_zone_A1.json', 'A1'), 
                           ('communes_zone_B.json', 'B'), ('communes_zone_C.json', 'C')]:
        data = load_data(z_file)
        if data:
            for item in data:
                if 'id' in item: zone_map[item['id']] = z_name
    for w in wilayas:
        w['thermal_zone_winter'] = zone_map.get(w['id'], w.get('thermal_zone_winter', 'A'))
    return wilayas

# تحميل ملفات البيانات
wilayas_list = get_comprehensive_wilayas()
all_communes = load_data('communes_enriched.json')
materials_data = load_data('dtr_materiaux.json')
verification_data = load_data('dtr_verification.json')

# --- إدارة اللغات ---
if 'lang' not in st.session_state: st.session_state.lang = 'ar'

texts = {
    'ar': {
        'title': "المحلل الحراري للمباني (DTR C 3.2/4)",
        'subtitle': "الجمهورية الجزائرية الديمقراطية الشعبية - CNERIB",
        'location': "الموقع والظروف المناخية",
        'wilaya': "الولاية", 'commune': "البلدية",
        'parois': "خصائص الجدار (الغلاف المادي)",
        'dimensions': "أبعاد الهيكل", 'material': "المادة الأساسية",
        'thickness': "سمك المادة (cm)", 'contact': "نوع التلامس",
        'calc': "إجراء التحليل التقني", 'result_u': "معامل الانتقال (U)",
        'result_c': "الحد المرجعي (c)", 'compliant': "مطابق للمواصفات",
        'non_compliant': "غير مطابق - يحتاج عزل",
        'exterior': "تلامس خارجي مباشر", 'unheated': "تلامس مع فضاء غير مدفأ",
        'summary': "نتائج التحليل الحراري", 'dir': 'rtl',
        'windows': "عدد النوافذ", 'doors': "عدد الأبواب", 'floors': "عدد الطوابق"
    }
}

with st.sidebar:
    st.title("Settings / الإعدادات")
    lang_choice = st.selectbox("Language", options=["العربية", "Français", "English"])
    if lang_choice == "العربية": st.session_state.lang = 'ar'
    elif lang_choice == "Français": st.session_state.lang = 'fr'
    else: st.session_state.lang = 'en'

L = texts[st.session_state.lang]

# --- التصميم CSS ---
st.markdown(f"""
    <style>
    .main {{ direction: {L['dir']}; }}
    </style>
    <div class="header-box">
        <h1>{L['title']}</h1>
        <p>{L['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

col_inputs, col_results = st.columns([1, 1], gap="large")

with col_inputs:
    st.markdown(f"### {L['dimensions']}")
    with st.container(border=True):
        h_val = st.number_input("Hauteur (m)", 1.0, 50.0, 3.0)
        w_val = st.number_input("Largeur (m)", 1.0, 100.0, 10.0)
        l_val = st.number_input("Longueur (m)", 1.0, 200.0, 20.0)
        win_val = st.number_input(L['windows'], 0, 50, 4)
        door_val = st.number_input(L['doors'], 0, 20, 1)
        floor_val = st.number_input(L['floors'], 1, 10, 2)

        if st.button("Afficher le bâtiment"):
            viewer_html = f"""
            <div id="viewer" style="width:100%; height:500px;"></div>
            <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/examples/js/loaders/GLTFLoader.js"></script>
            <script>
              const scene = new THREE.Scene();
              const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
              const renderer = new THREE.WebGLRenderer();
              renderer.setSize(window.innerWidth, 500);
              document.getElementById("viewer").appendChild(renderer.domElement);

              const light = new THREE.DirectionalLight(0xffffff, 1);
              light.position.set(10, 10, 10);
              scene.add(light);

              const loader = new THREE.GLTFLoader();
              loader.load('scene.gltf', function(gltf) {{
                const building = gltf.scene;
                building.scale.set({w_val}/10, {floor_val}, {l_val}/20);
                scene.add(building);
                camera.position.z = 30;
                animate();

                // Ajouter fenêtres
                for (let i=0; i<{win_val}; i++) {{
                  const geo = new THREE.BoxGeometry(0.5,0.5,0.1);
                  const mat = new THREE.MeshBasicMaterial({{color:0x00aaff}});
                  const win = new THREE.Mesh(geo, mat);
                  win.position.set(i*1.5, 1, 0);
                  building.add(win);
                }}
                // Ajouter portes
                for (let j=0; j<{door_val}; j++) {{
                  const geo = new THREE.BoxGeometry(1,2,0.2);
                  const mat = new THREE.MeshBasicMaterial({{color:0x884422}});
                  const door = new THREE.Mesh(geo, mat);
                  door.position.set(j*2, 0, 0);
                  building.add(door);
                }}
              }});

              function animate() {{
                requestAnimationFrame(animate);
                renderer.render(scene, camera);
              }}
            </script>
            """
            st.components.v1.html(viewer_html, height=520)
