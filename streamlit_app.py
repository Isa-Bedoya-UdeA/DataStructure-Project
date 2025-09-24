import streamlit as st
import json
from utils import load_characters, save_character, create_character

# ---------------- CARGAR SKILLS ----------------
with open("skills.json", "r", encoding="utf-8") as f:
    skills_info = json.load(f)

st.set_page_config(page_title="Gestor RPG", layout="centered")
st.header("Gestor de Personajes RPG")

# Tabs
tab1, tab2 = st.tabs(["⚔️ Crear personaje", "🔍 Buscar personaje"])

# ---------------- TAB 1: CREAR PERSONAJE ----------------
with tab1:
    if "selected_skills" not in st.session_state:
        st.session_state.selected_skills = []

    with st.form("character_form", clear_on_submit=True):
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

        submitted = st.form_submit_button("Crear personaje", type="primary")
        if submitted:
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

    # Mostrar personajes guardados
    st.subheader("📂 Personajes registrados en archivo")
    characters = load_characters()
    st.write(f"Actualmente hay **{len(characters)}** personajes guardados.")

# ---------------- TAB 2: BUSCAR PERSONAJE ----------------
with tab2:
    st.subheader("Buscar personaje por nombre")
    query = st.text_input("🔎 Ingresa un fragmento del nombre", key="search_input")

    characters = load_characters()

    if query.strip():
        results = [c for c in characters if query.lower() in c["name"].lower()]
    else:
        results = characters
    if results:
        st.success(f"Se encontraron {len(results)} personajes:")

        for c in results:
            with st.expander(f"📜 {c['name']} ({c['class']} - {c['race']})", expanded=False):
                st.write(f"**Clase:** {c['class']}")
                st.write(f"**Raza:** {c['race']}")
                st.write("**Habilidades:**")
                for skill in c["skills"]:
                    st.markdown(f"- {skill}")
    else:
        st.warning("⚠ No hay personajes registrados.")
