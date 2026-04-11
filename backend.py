import utils
import Evaluation_Formules_DTR
import zonage1

def load_communes_data(path="data_communes_algeria.json"):
    return utils.load_json_file(path)

def get_climate_zones(commune_name, data):
    climate_engine = zonage1.AlgerianClimateEnricher()
    wilaya_data = climate_engine.find_wilaya_by_name(commune_name, data["wilayas"])
    zone_hiver, tbe = climate_engine.determine_winter_zone(wilaya_data, data["wilayas"])
    zone_ete, conditions = climate_engine.determine_summer_zone(wilaya_data, data["wilayas"])
    return {
        "zone_hiver": zone_hiver,
        "temp_base_hiver": tbe,
        "zone_ete": zone_ete,
        "conditions_ete": conditions
    }

def compute_thermal_bridge():
    from Evaluation_Formules_DTR import MoteurFormulesDTR, Paroi, TypeIsolation
    moteur = MoteurFormulesDTR()
    paroi1 = Paroi("Mur béton", TypeIsolation.REPARTIE, 0.5, 0.2, 2.0)
    paroi2 = Paroi("Mur brique", TypeIsolation.REPARTIE, 0.6, 0.25, 1.8)
    kl = moteur.calculer_kl_liaison_deux_parois("isolation_repartie_identiques", paroi1, paroi2)
    return kl

def evaluate_commune(commune_name):
    data = load_communes_data()
    climate = get_climate_zones(commune_name, data)
    kl_value = compute_thermal_bridge()
    return {
        "commune": commune_name,
        "climate": climate,
        "kl_value": kl_value
    }
