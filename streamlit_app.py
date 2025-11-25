import streamlit as st
import json
from utils import load_characters, save_character, create_character, validate_name, load_skills
from search_index import CharacterIndex
from functionality_search_bptree import create_characters_bptrees, search_by_class, search_by_race 

# ---------------- CARGAR SKILLS ----------------
skills_info = load_skills()
skill_ids = list(skills_info.keys())

with open("skills.json", "r", encoding="utf-8") as f:
    skills_info = json.load(f)

st.set_page_config(page_title="Gestor RPG", layout="centered", page_icon=":performing_arts:")
st.header("Gestor de Personajes RPG")

# -------------------- B+ TREE (solo se crea UNA VEZ) --------------------
if "bptrees" not in st.session_state:
    # bptrees is a dict with keys: 'class', 'race'
    st.session_state.bptrees = create_characters_bptrees()

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
    "🌳 Buscar con filtros (B+ Tree)"
])

# ============================================================
# ---------------------- TAB 1: CREAR PERSONAJE --------------
# ============================================================
with tab1:
    if "selected_skills" not in st.session_state:
        st.session_state.selected_skills = []

    with st.form("character_form", clear_on_submit=False, border=False):
        with st.container():
            name = st.text_input("Nombre del personaje",
                                 placeholder="Ingresa un nombre",
                                 max_chars=16)
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

            submitted = st.form_submit_button("Crear personaje", type="primary")

            if submitted:
                is_name_valid, invalid_msg = validate_name(name)

                if not is_name_valid:
                    name_error_msg.error(invalid_msg)

                elif len(st.session_state.selected_skills) != 6:
                    skills_error_msg.error("Debes seleccionar exactamente 6 habilidades.")

                else:
                    character = create_character(name, class_rpg, race,
                                                 st.session_state.selected_skills)
                    save_character(character)

                    # Recargar índices
                    if "character_index" in st.session_state:
                        st.session_state.character_index.reload()

                    st.session_state.bptree_class = create_characters_bptree()
                    st.session_state.bptree_race = create_characters_race_bptree()

                    st.success("¡Personaje creado exitosamente!")
                    st.json(character)

                    st.session_state.selected_skills = []
                    st.rerun()

        st.subheader("📂 Personajes registrados")
        characters = load_characters()
        st.write(f"Actualmente hay **{len(characters)}** personajes.")


# ============================================================
# ---------------------- TAB 2: BUSCAR POR NOMBRE ------------
# ============================================================
with tab2:
    st.subheader("Buscar personaje por nombre o prefijo")
    st.caption("💡 Si no ingresas nada, se mostrarán todos.")

    query = st.text_input("🔎 Buscar", key="search_input").strip()

    search_button = st.button("Buscar", type="primary")
    enter_pressed = query != st.session_state.last_query
    search_triggered = search_button or enter_pressed

    if not st.session_state.search_results and not query:
        chars = load_characters()
        st.session_state.search_results = chars
        st.session_state.results_shown = 20
        st.session_state.last_query = ""
        st.success(f"Se encontraron {len(chars)} personajes.")

    elif search_triggered:
        st.session_state.last_query = query

        if not query:
            chars = load_characters()
            st.session_state.search_results = chars
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
# ----------------- TAB 3: BUSCAR (B+ TREE) -------------------
# ============================================================
with tab3:
    st.subheader("Buscar personaje por Clase / Raza (B+ Tree)")
    st.caption("⚡ Filtrado usando B+ Trees.")

    order_mode = st.selectbox(
        "Ordenar resultados",
        ["A-Z (Nombre)", "Z-A (Nombre)"],
        index=0
    )

    class_query = st.selectbox(
        "Clase (opcional)",
        options=[""] + [
            "Guerrero", "Mago", "Clérigo", "Paladín", "Bárbaro",
            "Asesino", "Druida", "Arquero", "Nigromante", "Monje"
        ],
        index=0
    )
    race_query = st.selectbox(
        "Raza (opcional)",
        options=[""] + [
            "Humano", "Elfo", "Enano", "Orco", "Gnomo",
            "Centauro", "Cíclope", "Duende", "Sirena"
        ],
        index=0
    )

    if st.button("Filtrar (B+ Tree)", type="primary"):
        trees = st.session_state.bptrees
        sets = []

        if class_query:
            class_results = search_by_class(trees["class"], class_query) or []
            sets.append(class_results)

        if race_query:
            race_results = search_by_race(trees["race"], race_query) or []
            sets.append(race_results)

        # Caso: SIN filtros → devolver todo
        if not sets:
            results = load_characters()
            st.success(f"Sin filtros: se muestran {len(results)} personajes.")

        # Caso: 1 o 2 filtros → intersecar resultados
        else:
            name_sets = [set([c["name"] for c in s]) for s in sets]
            intersect_names = set.intersection(*name_sets) if name_sets else set()

            all_characters = load_characters()
            results = [c for c in all_characters if c["name"] in intersect_names]

            if not results:
                st.warning("No se encontraron personajes con los criterios seleccionados.")
            else:
                st.success(f"{len(results)} personaje(s) encontrados.")

        # Mostrar resultados
        if results:
            if order_mode == "A-Z (Nombre)":
                results = sorted(results, key=lambda c: c["name"].lower())
            else:
                results = sorted(results, key=lambda c: c["name"].lower(), reverse=True)

            for c in results:
                with st.expander(f"📜 {c['name']} ({c['class']} - {c['race']})"):
                    st.write(f"**PV:** {c['hp']} | **Energía:** {c['energy']} | **Nivel:** {c['level']}")
                    st.write("**Habilidades:**")
                    for skill_id in c["skills"]:
                        info = skills_info.get(skill_id, {"name": "❓ Desconocida"})
                        st.markdown(f"- {info['name']}")
