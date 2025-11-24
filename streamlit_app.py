import streamlit as st
import json
from utils import load_characters, save_character, create_character, validate_name, load_skills
from search_index import CharacterIndex
from functionality_search_bptree import create_characters_bptree, search_by_class

# ---------------- CARGAR SKILLS ----------------
skills_info = load_skills()
skill_ids = list(skills_info.keys())

with open("skills.json", "r", encoding="utf-8") as f:
    skills_info = json.load(f)

st.set_page_config(page_title="Gestor RPG", layout="centered", page_icon=":performing_arts:")
st.header("Gestor de Personajes RPG")

# -------------------- B+ TREE (solo se crea UNA VEZ) --------------------
if "bptree" not in st.session_state:
    st.session_state.bptree = create_characters_bptree()

# -------------------- Character Index (solo se carga una vez) --------------------
if "character_index" not in st.session_state:
    st.session_state.character_index = CharacterIndex()

# -------------------- Variables persistentes para listar resultados --------------------
if "search_results" not in st.session_state:
    st.session_state.search_results = []
if "results_shown" not in st.session_state:
    st.session_state.results_shown = 20
if "last_query" not in st.session_state:
    st.session_state.last_query = ""


# --------------------------- TABS ---------------------------
tab1, tab2, tab3 = st.tabs([
    "⚔️ Crear personaje",
    "🔍 Buscar personaje",
    "🌳 Buscar por clase (B+ Tree)"
])


# ============================================================
# ---------------------- TAB 1: CREAR PERSONAJE --------------
# ============================================================
with tab1:
    if "selected_skills" not in st.session_state:
        st.session_state.selected_skills = []

    with st.form("character_form", clear_on_submit=False, border=False):
        with st.container(horizontal_alignment="center"):
            name = st.text_input("Nombre del personaje", placeholder="Ingresa un nombre", max_chars=16)
            name_error_msg = st.empty()

            class_rpg = st.selectbox("Clase", [
                "Guerrero", "Mago", "Clérigo", "Paladín", "Bárbaro",
                "Asesino", "Druida", "Arquero", "Nigromante", "Monje"
            ])

            race = st.selectbox("Raza", [
                "Humano", "Elfo", "Enano", "Orco", "Gnomo",
                "Centauro", "Cíclope", "Duende", "Sirena"
            ])

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
                        Valor: {info["value"]} | Rareza: {info["rarity"]} | Fuente: {info["source"]}"""
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
                    skills_error_msg.error("Debes seleccionar exactamente 6 habilidades.",
                                           icon=":material/release_alert:")

                else:
                    # Crear personaje
                    character = create_character(name, class_rpg, race, st.session_state.selected_skills)
                    save_character(character)

                    # Recargar índice de búsqueda
                    if "character_index" in st.session_state:
                        st.session_state.character_index.reload()

                    st.success("¡Personaje creado exitosamente!", icon=":material/done_outline:")
                    st.json(character)

                    st.session_state.selected_skills = []
                    st.rerun()

        st.subheader("📂 Personajes registrados en archivo")
        characters = load_characters()
        st.write(f"Actualmente hay **{len(characters)}** personajes guardados.")



# ============================================================
# ---------------------- TAB 2: BUSCAR POR NOMBRE ------------
# ============================================================
with tab2:
    st.subheader("Buscar personaje por nombre o prefijo")
    st.caption("💡 Si no ingresas nada, se mostrarán todos los personajes.")

    query = st.text_input("🔎 Ingresa el nombre o parte del nombre",
                          key="search_input").strip()

    search_button = st.button("Buscar", type="primary")
    enter_pressed = query != st.session_state.last_query
    search_triggered = search_button or enter_pressed

    if not st.session_state.search_results and not query:
        all_characters = load_characters()
        st.session_state.search_results = all_characters
        st.session_state.results_shown = 20
        st.session_state.last_query = ""
        st.success(f"Se encontraron {len(all_characters)} personajes.", icon=":material/done_outline:")

    elif search_triggered:
        st.session_state.last_query = query

        if not query:
            all_characters = load_characters()
            st.session_state.search_results = all_characters
            st.session_state.results_shown = 20
        else:
            results = st.session_state.character_index.search_prefix(query)
            st.session_state.search_results = results
            st.session_state.results_shown = 20

    if st.session_state.search_results:
        results = st.session_state.search_results[: st.session_state.results_shown]

        for c in results:
            with st.expander(f"📜 {c['name']} ({c['class']} - {c['race']})"):
                st.write(f"**Clase:** {c['class']}")
                st.write(f"**Raza:** {c['race']}")
                st.write(f"**PV:** {c['hp']} | **Energía:** {c['energy']} | **Nivel:** {c['level']}")
                st.write("**Habilidades:**")
                for skill_id in c["skills"]:
                    info = skills_info.get(skill_id, {"name": "❓ Desconocida"})
                    st.markdown(f"- {info['name']}")

        if len(st.session_state.search_results) > st.session_state.results_shown:
            if st.button("🔽 Cargar más"):
                st.session_state.results_shown += 20
                st.rerun()



# ============================================================
# ----------------- TAB 3: BUSCAR POR CLASE (B+ TREE) --------
# ============================================================
with tab3:
    st.subheader("Buscar personaje por clase usando B+ Tree")
    st.caption("⚡ Búsqueda optimizada con estructura de datos avanzada.")

    class_query = st.selectbox(
        "Selecciona una clase:",
        ["Guerrero", "Mago", "Clérigo", "Paladín", "Bárbaro",
         "Asesino", "Druida", "Arquero", "Nigromante", "Monje"]
    )

    if st.button("Buscar por clase", type="primary"):
        results = search_by_class(st.session_state.bptree, class_query)

        if not results:
            st.warning(f"No existen personajes registrados como {class_query}.")
        else:
            st.success(f"{len(results)} personajes encontrados de clase {class_query}.")

            for c in results:
                with st.expander(f"📜 {c['name']} ({c['race']})"):
                    st.write(f"**PV:** {c['hp']} | **Energía:** {c['energy']} | **Nivel:** {c['level']}")
                    st.write("**Habilidades:**")
                    for skill_id in c["skills"]:
                        info = skills_info.get(skill_id, {"name": "❓ Desconocida"})
                        st.markdown(f"- {info['name']}")
