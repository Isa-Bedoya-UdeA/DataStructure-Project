import streamlit as st
import json
from utils import load_characters, save_character, create_character, validate_name, load_skills

skills_info = load_skills()
skill_ids = list(skills_info.keys())

# ---------------- CARGAR SKILLS ----------------
with open("skills.json", "r", encoding="utf-8") as f:
    skills_info = json.load(f)

st.set_page_config(page_title="Gestor RPG", layout="centered", page_icon=":performing_arts:")
st.header("Gestor de Personajes RPG")

# Tabs
tab1, tab2 = st.tabs(["⚔️ Crear personaje", "🔍 Buscar personaje"])

# ---------------- TAB 1: CREAR PERSONAJE ----------------
with tab1:
    if "selected_skills" not in st.session_state:
        st.session_state.selected_skills = []

    with st.form("character_form", clear_on_submit=True, border=False):
        with st.container(horizontal_alignment="center"):
            name = st.text_input("Nombre del personaje", placeholder="Ingresa un nombre", max_chars=16)
            name_error_msg = st.empty()
            class_rpg = st.selectbox("Clase", ["Guerrero", "Mago", "Clérigo", "Paladín", "Bárbaro", "Asesino", "Druida", "Arquero", "Nigromante", "Monje"])
            race = st.selectbox("Raza", ["Humano", "Elfo", "Enano", "Orco", "Gnomo", "Centauro", "Cíclope", "Duende", "Sirena"])
            
            st.caption("**Selecciona 6 habilidades**")
            
            cols = st.columns(3)
            for i, skill_id in enumerate(skill_ids):
                info = skills_info[skill_id]
                col = cols[i % 3]
                with col:
                    selected = st.toggle(
                        f"{info['name']}",
                        value=skill_id in st.session_state.selected_skills,
                        help=f"""{info["description"]}\n
            Tipo: {info["type"]} | Objetivo: {info["target"]}
            Valor: {info["value"]} | Rareza: {info["rarity"]} | Fuente: {info["source"]}
            """
                    )
                    if selected and skill_id not in st.session_state.selected_skills:
                        st.session_state.selected_skills.append(skill_id)
                    elif not selected and skill_id in st.session_state.selected_skills:
                        st.session_state.selected_skills.remove(skill_id)
            skills_error_msg = st.empty()
            with st.container(width=250):
                submitted = st.form_submit_button("Crear personaje", type="primary", width="stretch")
            if submitted:
                is_name_valid, invalid_msg = validate_name(name)
                if not is_name_valid:
                    name_error_msg.error(invalid_msg, icon=":material/release_alert:")
                elif len(st.session_state.selected_skills) != 6:
                    skills_error_msg.error("Debes seleccionar exactamente 6 habilidades.", icon=":material/release_alert:")
                else:
                    character = create_character(name, class_rpg, race, st.session_state.selected_skills)
                    save_character(character)
                    st.success("¡Personaje creado exitosamente!", icon=":material/done_outline:")
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
        st.success(f"Se encontraron {len(results)} personajes:", icon=":material/done_outline:")

        for c in results:
            with st.expander(f"📜 {c['name']} ({c['class']} - {c['race']})", expanded=False):
                st.write(f"**Clase:** {c['class']}")
                st.write(f"**Raza:** {c['race']}")
                st.write(f"**PV:** {c['hp']} | **Energía:** {c['energy']} | **Nivel:** {c['level']}")
                st.write("**Habilidades:**")
                for skill_id in c["skills"]:
                    info = skills_info.get(skill_id, {"name": "❓ Desconocida"})
                    st.markdown(f"- {info['name']}")

    else:
        st.warning("No hay personajes registrados.", icon=":material/data_alert:")
