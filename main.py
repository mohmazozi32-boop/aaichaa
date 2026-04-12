from fastapi import FastAPI
import uvicorn
import json
from evaluation_dtr import MoteurFormulesDTR
from zonage1 import AlgerianClimateEnricher

app = FastAPI(title="Thermal Insulation Algeria")

moteur = MoteurFormulesDTR()
climate = AlgerianClimateEnricher()

@app.get("/commune/{name}")
def get_commune_info(name: str):
    with open("data_communes_algeria.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    wilayas = data.get("wilayas", [])
    
    commune = next((c for c in wilayas if c["name"].lower() == name.lower()), None)
    if not commune:
        return {"error": "Commune not found"}
    
    winter_zone, tbe = climate.determine_winter_zone(commune, wilayas)
    summer_zone, summer_conditions = climate.determine_summer_zone(commune, wilayas)
    
    return {
        "commune": name,
        "winter_zone": winter_zone,
        "tbe": tbe,
        "summer_zone": summer_zone,
        "summer_conditions": summer_conditions
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
