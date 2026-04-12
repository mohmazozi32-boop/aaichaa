from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

from evaluation_dtr import MoteurFormulesDTR
from zonage1 import AlgerianClimateEnricher

app = FastAPI(title="Thermal Insulation Algeria API")

# =========================
# CORS (لربط الواجهة لاحقاً)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # لاحقاً نحدد الدومين
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# تحميل البيانات مرة واحدة (أفضل أداء)
# =========================
with open("data_communes_algeria.json", "r", encoding="utf-8") as f:
    DATA = json.load(f)

WILAYAS = DATA.get("wilayas", [])

# =========================
# الخدمات
# =========================
moteur = MoteurFormulesDTR()
climate = AlgerianClimateEnricher()


# =========================
# API
# =========================
@app.get("/health")
def health_check():
    return {"status": "ok", "message": "API is running"}

@app.get("/commune/{name}")
def get_commune_info(name: str):
    commune = next(
        (c for c in WILAYAS if c["name"].lower() == name.lower()),
        None
    )

    if not commune:
        raise HTTPException(status_code=404, detail="Commune not found")

    winter_zone, tbe = climate.determine_winter_zone(commune, WILAYAS)
    summer_zone, summer_conditions = climate.determine_summer_zone(commune, WILAYAS)

    return {
        "commune": commune["name"],
        "winter_zone": winter_zone,
        "tbe": tbe,
        "summer_zone": summer_zone,
        "summer_conditions": summer_conditions
    }
