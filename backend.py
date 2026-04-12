import json
from evaluation_dtr import MoteurFormulesDTR, Paroi, TypeIsolation
from zonage1 import AlgerianClimateEnricher
from categorize import Categorizer

class Backend:
    def __init__(self):
        with open("data_communes_algeria.json", "r", encoding="utf-8") as f:
            self.communes_data = json.load(f)["wilayas"]

        self.moteur = MoteurFormulesDTR()
        self.climate = AlgerianClimateEnricher()
        self.categorizer = Categorizer()

    def get_commune_info(self, name: str):
        commune = next((c for c in self.communes_data if c["name"].lower() == name.lower()), None)
        if not commune:
            return None

        winter_zone, tbe = self.climate.determine_winter_zone(commune, self.communes_data)
        summer_zone, summer_conditions = self.climate.determine_summer_zone(commune, self.communes_data)
        classification = self.categorizer.classify_commune(commune)

        return {
            "commune": name,
            "winter_zone": winter_zone,
            "tbe": tbe,
            "summer_zone": summer_zone,
            "summer_conditions": summer_conditions,
            "classification": classification
        }
