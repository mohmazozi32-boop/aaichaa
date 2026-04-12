from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json

from evaluation_dtr import MoteurFormulesDTR
from zonage1 import AlgerianClimateEnricher

app = FastAPI(title="DTR Thermal Backend - Algeria")

# =========================
# CORS (لواجهة Streamlit / React)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# SERVICES
# =========================
moteur = MoteurFormulesDTR()
climate = AlgerianClimateEnricher()

# =========================
# LOAD DATA (مرة واحدة فقط)
# =========================
with open("data_communes_algeria.json", "r", encoding="utf-8") as f:
    communes_data = json.load(f)["wilayas"]

with open("dtr_materiaux.json", "r", encoding="utf-8") as f:
    materiaux_data = json.load(f)

with open("dtr_coefficients.json", "r", encoding="utf-8") as f:
    coeffs_data = json.load(f)

# =========================
# HEALTH CHECK
# =========================
@app.get("/health")
def health():
    return {"status": "ok", "message": "DTR Backend running"}

# =========================
# COMMUNE INFO
# =========================
@app.get("/commune/{name}")
def get_commune_info(name: str):
    commune = next(
        (c for c in communes_data if c["name"].lower() == name.lower()),
        None
    )

    if not commune:
        raise HTTPException(status_code=404, detail="Commune not found")

    winter_zone, tbe = climate.determine_winter_zone(commune, communes_data)
    summer_zone, summer_conditions = climate.determine_summer_zone(commune, communes_data)

    return {
        "commune": commune["name"],
        "winter_zone": winter_zone,
        "tbe": tbe,
        "summer_zone": summer_zone,
        "summer_conditions": summer_conditions
    }

# =========================
# MATERIAU
# =========================
@app.get("/materiau/{id}")
def get_materiau(id: str):
    for m in materiaux_data.get("materiaux_homogenes", []):
        if m["id"] == id:
            return m

    for m in materiaux_data.get("materiaux_heterogenes", []):
        if m["id"] == id:
            return m

    raise HTTPException(status_code=404, detail="Matériau non trouvé")

# =========================
# COEFFICIENTS
# =========================
@app.get("/coefficients")
def get_coefficients():
    return coeffs_data

# =========================
# PONTS THERMIQUES
# =========================
@app.get("/ponts_thermiques")
def get_ponts_thermiques():
    return coeffs_data.get("ponts_thermiques", {})

# =========================
# VERIFICATION DTR
# =========================
@app.get("/verification")
def get_verification():
    try:
        with open("dtr_verification.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        raise HTTPException(status_code=404, detail="Verification file missing")
