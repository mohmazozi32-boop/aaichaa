from fastapi import FastAPI
import json
from evaluation_dtr import MoteurFormulesDTR
from zonage1 import AlgerianClimateEnricher

app = FastAPI(title="DTR Thermal Backend")

moteur = MoteurFormulesDTR()
climate = AlgerianClimateEnricher()

# تحميل البيانات
with open("data_communes_algeria.json", "r", encoding="utf-8") as f:
    communes_data = json.load(f)["wilayas"]

with open("dtr_materiaux.json", "r", encoding="utf-8") as f:
    materiaux_data = json.load(f)

with open("dtr_coefficients.json", "r", encoding="utf-8") as f:
    coeffs_data = json.load(f)

@app.get("/commune/{name}")
def get_commune_info(name: str):
    commune = next((c for c in communes_data if c["name"].lower() == name.lower()), None)
    if not commune:
        return {"error": "Commune not found"}
    
    winter_zone, tbe = climate.determine_winter_zone(commune, communes_data)
    summer_zone, summer_conditions = climate.determine_summer_zone(commune, communes_data)
    
    return {
        "commune": name,
        "winter_zone": winter_zone,
        "tbe": tbe,
        "summer_zone": summer_zone,
        "summer_conditions": summer_conditions
    }

@app.get("/materiau/{id}")
def get_materiau(id: str):
    for m in materiaux_data["materiaux_homogenes"]:
        if m["id"] == id:
            return m
    for m in materiaux_data["materiaux_heterogenes"]:
        if m["id"] == id:
            return m
    return {"error": "Matériau non trouvé"}

@app.get("/coefficients")
def get_coefficients():
    return coeffs_data

@app.get("/ponts_thermiques")
def get_ponts_thermiques():
    return coeffs_data["ponts_thermiques"]

@app.get("/verification")
def get_verification():
    with open("dtr_verification.json", "r", encoding="utf-8") as f:
        return json.load(f)
