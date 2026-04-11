import json
import os

def load_json_file(path: str):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Le fichier {path} est introuvable.")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json_file(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def format_temperature(value: float) -> str:
    return f"{value} °C"

def format_zone(zone: str) -> str:
    return f"Zone {zone}"
