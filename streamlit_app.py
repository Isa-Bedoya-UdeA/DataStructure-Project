import streamlit as st
import json
import os

DATA_FILE = "characters.json"

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

def create_character(name, class_rpg, race, skills):
    return {
        "name": name,
        "class": class_rpg,
        "race": race,
        "skills": skills
    }

# SKILLS DATA
skills_info = {
    "Ataque físico": {
        "description": "Un ataque básico con armas físicas.",
        "type": "Daño",
        "target": "Único",
        "value": 15,
        "rarity": "Primary",
        "source": "General"
    },
    "Ataque mágico": {
        "description": "Un poderoso ataque con magia.",
        "type": "Daño",
        "target": "Múltiple",
        "value": 20,
        "rarity": "Primary",
        "source": "Class"
    },
    "Sigilo": {
        "description": "Permite ocultarse de enemigos.",
        "type": "Defensa",
        "target": "Propio",
        "value": 0,
        "rarity": "Secondary",
        "source": "Class"
    },
    "Curación": {
        "description": "Restaura puntos de vida.",
        "type": "Cura",
        "target": "Aliado",
        "value": 25,
        "rarity": "Primary",
        "source": "Class"
    },
    "Guardia": {
        "description": "Aumenta la defensa temporalmente.",
        "type": "Defensa",
        "target": "Propio",
        "value": 10,
        "rarity": "Secondary",
        "source": "General"
    },
    "Invocación": {
        "description": "Invoca criaturas para el combate.",
        "type": "Daño",
        "target": "Múltiple",
        "value": 30,
        "rarity": "Primary",
        "source": "Class"
    },
    "Esquivar": {
        "description": "Aumenta la probabilidad de evitar ataques.",
        "type": "Defensa",
        "target": "Propio",
        "value": 0,
        "rarity": "Secondary",
        "source": "General"
    },
    "Arquería": {
        "description": "Disparo preciso con arco.",
        "type": "Daño",
        "target": "Único",
        "value": 18,
        "rarity": "Primary",
        "source": "Class"
    },
    "Combate cuerpo a cuerpo": {
        "description": "Ataque directo con golpes físicos.",
        "type": "Daño",
        "target": "Único",
        "value": 12,
        "rarity": "Secondary",
        "source": "General"
    }
}

# INTERFACE
st.set_page_config(page_title="Gestor RPG", layout="centered")
st.header("Creador de Personaje RPG")

if "selected_skills" not in st.session_state:
    st.session_state.selected_skills = []

name = st.text_input("Nombre del personaje", placeholder="Ingresa un nombre", max_chars=16)
class_rpg = st.selectbox("Clase", ["Guerrero", "Mago", "Clérigo", "Paladín", "Bárbaro", "Asesino", "Druida", "Arquero", "Nigromante", "Monje"])
race = st.selectbox("Raza", ["Humano", "Elfo", "Enano", "Orco", "Gnomo", "Centauro", "Cíclope", "Duende", "Sirena"])

st.caption("Selecciona al menos 1 habilidad (máx 6).")

cols = st.columns(3)
for i, (skill, info) in enumerate(skills_info.items()):
    col = cols[i % 3]
    with col:
        selected = st.toggle(
            f"{skill}",
            value=skill in st.session_state.selected_skills,
            help=f"""{info["description"]} \n
Tipo: {info["type"]} | Objetivo: {info["target"]}
Valor: {info["value"]} | Rareza: {info["rarity"]} | Fuente: {info["source"]}
"""
        )
        if selected and skill not in st.session_state.selected_skills:
            if len(st.session_state.selected_skills) < 6:
                st.session_state.selected_skills.append(skill)
        elif not selected and skill in st.session_state.selected_skills:
            st.session_state.selected_skills.remove(skill)

if st.button("Crear personaje", type="primary"):
    if not name.strip():
        st.error("⚠ El personaje debe tener un nombre.")
    elif len(st.session_state.selected_skills) == 0:
        st.error("⚠ Debes seleccionar al menos una habilidad.")
    else:
        character = create_character(name, class_rpg, race, st.session_state.selected_skills)
        save_character(character)
        st.success("¡Personaje creado exitosamente!")
        st.json(character)
        st.session_state.selected_skills = []

# SAVED CHARACTERS
st.subheader("Personajes registrados en archivo")
characters = load_characters()
st.write(f"Actualmente hay **{len(characters)}** personajes guardados.")
