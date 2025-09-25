import json
import os
import uuid

DATA_FILE = "characters.json"
SKILLS_FILE = "skills.json"

# UTILS
def load_characters():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def save_character(character):
    characters = load_characters()
    characters.append(character)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(characters, f, indent=4, ensure_ascii=False)

def create_character(name, class_rpg, race, skill_ids):
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "class": class_rpg,
        "race": race,
        "skills": skill_ids,
        "hp": 100,
        "energy": 100,
        "level": 1
    }

def validate_name(name):
    if not name.strip():
        return False, "El personaje debe tener un nombre."
    characters = load_characters()
    if any(char["name"] == name for char in characters):
        return False, "Ya existe un personaje con ese nombre."
    return True, ""

def load_skills():
    with open(SKILLS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)