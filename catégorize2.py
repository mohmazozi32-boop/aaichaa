import json
import os

# 1. Chargement du dataset des 69 wilayas
with open('data_communes_algeria.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

wilayas_list = data.get('wilayas', [])

# 2. Dictionnaire des paramètres physiques par Zone (Hiver)
# Température de base (Tbe) selon le DTR C3-2
ZONE_PHYSICS = {
    "A":  {"tbe": 3,  "description": "Littoral / Plaines"},
    "A1": {"tbe": 7,  "description": "Littoral spécifique (Bejaia, Skikda...)"},
    "B":  {"tbe": -2, "description": "Hautes Plaines"},
    "C":  {"tbe": 1,  "description": "Nord Sahara"},
    "D":  {"tbe": 4,  "description": "Sud Sahara / Hoggar"},
    "Inconnue": {"tbe": 0, "description": "Donnée manquante"}
}

# 3. Règles de correspondance (Mapping)
# Note : Pour votre projet, ce mapping assure la transition 48 -> 69 wilayas
ZONING_RULES = {
    "Adrar": {"default": "D", "exceptions": {"Tinerkouk": "C", "Bordj Badji Mokhtar": "C"}},
    "Chlef": {"default": "A", "exceptions": {"Ténès": "A1", "Oued Goussine": "A1"}},
    "Laghouat": {"default": "B", "exceptions": {"Laghouat": "C", "Hassi R'mel": "C"}},
    "Oum El Bouaghi": {"default": "B", "exceptions": {}},
    "Batna": {"default": "B", "exceptions": {"Barika": "C", "Seggana": "C"}},
    "Béjaïa": {"default": "A", "exceptions": {"Béjaïa": "A1", "Toudja": "A1"}},
    "Biskra": {"default": "C", "exceptions": {"Khangat Sidi Nadji": "B"}},
    "Béchar": {"default": "D", "exceptions": {"Béchar": "C", "Abadla": "C"}},
    "Blida": {"default": "A", "exceptions": {}},
    "Bouira": {"default": "A", "exceptions": {"Sour El Ghozlane": "B"}},
    "Tamanrasset": {"default": "D", "exceptions": {"Tamanrasset": "C", "In Guezzam": "C"}},
    "Tébessa": {"default": "B", "exceptions": {"Negrine": "C", "Ferkane": "C"}},
    "Alger": {"default": "A", "exceptions": {}},
    "Sétif": {"default": "B", "exceptions": {"Bougaa": "A"}},
    "Skikda": {"default": "A", "exceptions": {"Skikda": "A1", "Collo": "A1"}},
    "Ouargla": {"default": "D", "exceptions": {"El Borma": "C"}},
    "Oran": {"default": "A", "exceptions": {}},
    "El Oued": {"default": "C", "exceptions": {"Djamaa": "D", "El M'ghair": "D"}},
    # Ajoutez ici les autres wilayas mères selon le même modèle...
}

# 4. Traitement
categorized_data = {}

for item in wilayas_list:
    name = item['name']
    parent_name = item.get('parent_wilaya', name) # Héritage pour les nouvelles wilayas
    
    # Détermination de la zone
    rule = ZONING_RULES.get(parent_name, {"default": "B", "exceptions": {}})
    zone = rule['exceptions'].get(name, rule['default'])
    
    # Enrichissement avec les données physiques
    physics = ZONE_PHYSICS.get(zone)
    item['thermal_metadata'] = {
        "zone_hiver": zone,
        "temp_base_hiver": physics['tbe'],
        "climat_type": physics['description']
    }
    
    # Groupement par zone
    if zone not in categorized_data:
        categorized_data[zone] = []
    categorized_data[zone].append(item)

# 5. Sauvegarde
for zone, items in categorized_data.items():
    output_file = f"communes_zone_{zone}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(items, f, indent=4, ensure_ascii=False)
    print(f"Exporté : {output_file} ({len(items)} entités)")
