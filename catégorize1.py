import json
import os

# 1. Chargement des données
with open('data_communes_algeria.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

wilayas_list = data.get('wilayas', [])

# 2. Définition des règles de zonage Hiver (DTR C3.2/4)
# 'default': zone pour la majorité des communes
# 'exceptions': communes appartenant à une autre zone
ZONING_RULES = {
    "Adrar": {"default": "D", "exceptions": {"Tinerkouk": "C", "Bordj Badji Mokhtar": "C"}},
    "Chlef": {"default": "A", "exceptions": {"Tenes": "A1", "Oued Ghoussine": "A1", "Sidi Abderrahmane": "A1", "Sidi Akkacha": "A1"}},
    "Laghouat": {"default": "B", "exceptions": {"Laghouat": "C", "Sidi Makhlouf": "C", "Hassi R'mel": "C", "Ain Madhi": "C"}},
    "Oum El Bouaghi": {"default": "B", "exceptions": {}},
    "Batna": {"default": "B", "exceptions": {"Barika": "C", "Seggana": "C", "Mdoukal": "C"}},
    "Bejaia": {"default": "A", "exceptions": {"Bejaia": "A1", "Toudja": "A1", "El Kseur": "A1"}},
    "Biskra": {"default": "C", "exceptions": {"Khangat Sidi Nadji": "B"}},
    "Bechar": {"default": "D", "exceptions": {"Bechar": "C", "Kenadsa": "C", "Taghit": "C", "Abadla": "C"}},
    "Blida": {"default": "A", "exceptions": {}},
    "Bouira": {"default": "A", "exceptions": {"Mezdour": "B", "Bordj Oukhriss": "B", "Dirah": "B"}},
    "Tamanrasset": {"default": "D", "exceptions": {"Tamanrasset": "C", "In Guezzam": "C", "In Salah": "C"}},
    "Tebessa": {"default": "B", "exceptions": {"Negrine": "C", "Ferkane": "C", "Bir El Ater": "C"}},
    "Tlemcen": {"default": "A", "exceptions": {"Sebdou": "B", "Ouled Mimoun": "B", "Maghnia": "A"}},
    "Tiaret": {"default": "B", "exceptions": {}},
    "Tizi Ouzou": {"default": "A", "exceptions": {"Mizrana": "A1"}},
    "Alger": {"default": "A", "exceptions": {}},
    "Djelfa": {"default": "C", "exceptions": {"Ain Ouessara": "B", "Hassi Bahbah": "B", "Guettara": "D"}},
    "Jijel": {"default": "A", "exceptions": {}},
    "Setif": {"default": "B", "exceptions": {"Setif": "B", "BOUGAA": "A", "El Ouricia": "A"}},
    "Saida": {"default": "B", "exceptions": {}},
    "Skikda": {"default": "A", "exceptions": {"Skikda": "A1", "Collo": "A1"}},
    "Sidi Bel Abbes": {"default": "B", "exceptions": {"Sidi Bel Abbes": "A", "Sfisef": "A"}},
    "Annaba": {"default": "A", "exceptions": {}},
    "Guelma": {"default": "A", "exceptions": {"Oued Zenati": "B", "Ain Makhlouf": "B"}},
    "Constantine": {"default": "A", "exceptions": {"Constantine": "A", "El Khroub": "B"}},
    "Medea": {"default": "B", "exceptions": {}},
    "Mostaganem": {"default": "A", "exceptions": {}},
    "M'Sila": {"default": "C", "exceptions": {"Sidi Aissa": "B", "Magra": "B", "Boussaada": "C"}},
    "Mascara": {"default": "B", "exceptions": {"Mascara": "A", "Sig": "A", "Mohammadia": "A"}},
    "Ouargla": {"default": "D", "exceptions": {"El Borma": "C"}},
    "Oran": {"default": "A", "exceptions": {}},
    "El Bayadh": {"default": "B", "exceptions": {"El Abiodh Sidi Cheikh": "C", "Brezina": "C"}},
    "Illizi": {"default": "C", "exceptions": {}},
    "Bordj Bou Arreridj": {"default": "B", "exceptions": {"Bordj Zemoura": "A"}},
    "Boumerdes": {"default": "A", "exceptions": {"Dellys": "A1"}},
    "El Tarf": {"default": "A", "exceptions": {"El Kala": "A1"}},
    "Tindouf": {"default": "D", "exceptions": {}},
    "Tissemsilt": {"default": "B", "exceptions": {"Bordj Bounaama": "A"}},
    "El Oued": {"default": "C", "exceptions": {"Djamaa": "D", "El M'ghair": "D"}},
    "Khenchela": {"default": "B", "exceptions": {"Babar": "C"}},
    "Souk Ahras": {"default": "B", "exceptions": {"Mechroha": "A"}},
    "Tipaza": {"default": "A", "exceptions": {}},
    "Mila": {"default": "A", "exceptions": {"Chelghoum Laid": "B", "Tadjenanet": "B"}},
    "Ain Defla": {"default": "A", "exceptions": {}},
    "Naama": {"default": "B", "exceptions": {}},
    "Ain Temouchent": {"default": "A", "exceptions": {"Beni Saf": "A1"}},
    "Ghardaia": {"default": "C", "exceptions": {"El Guerrara": "D"}},
    "Relizane": {"default": "A", "exceptions": {"Oued Essalem": "B"}},
}

# 3. Traitement et Classification
categorized_data = {}

for item in wilayas_list:
    name = item['name']
    # Déterminer la wilaya mère pour les nouvelles wilayas
    parent_name = item.get('parent_wilaya', name)
    
    # Récupérer la règle
    rule = ZONING_RULES.get(parent_name, {"default": "Inconnue", "exceptions": {}})
    
    # Vérifier si l'entité est une exception (ex: Bir El Ater est dans Negrine Group -> C)
    zone = rule['exceptions'].get(name, rule['default'])
    
    # Ajouter l'info de zone à l'objet
    item['thermal_zone_winter'] = zone
    
    # Classer dans le dictionnaire final
    if zone not in categorized_data:
        categorized_data[zone] = []
    categorized_data[zone].append(item)

# 4. Exportation en fichiers séparés
for zone, communes in categorized_data.items():
    filename = f"communes_zone_{zone}.json"
    with open(filename, 'w', encoding='utf-8') as out_f:
        json.dump(communes, out_f, indent=4, ensure_ascii=False)
    print(f"Fichier généré : {filename} ({len(communes)} communes)")

print("\nTraitement terminé avec succès.")
