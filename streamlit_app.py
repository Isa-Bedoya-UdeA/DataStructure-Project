import streamlit as st
from utils import load_characters, save_character, create_character

# ---- CONFIG ----
st.set_page_config(page_title="Gestor RPG", layout="centered")
st.title("Gestor de Personajes RPG")

# Tabs
tab1, tab2 = st.tabs(["🧙 Crear Personaje", "📜 Consultar Personajes"])

# ---- TAB 1: Crear personaje ----
with tab1:
    st.header("Creador de Personaje")

    if "selected_skills" not in st.session_state:
        st.session_state.selected_skills = []

    name = st.text_input("Nombre del personaje", placeholder="Ingresa un nombre", max_chars=16)
    class_rpg = st.selectbox("Clase", ["Guerrero", "Mago", "Clérigo", "Paladín", "Bárbaro", "Asesino", "Druida", "Arquero", "Nigromante", "Monje"])
    race = st.selectbox("Raza", ["Humano", "Elfo", "Enano", "Orco", "Gnomo", "Centauro", "Cíclope", "Duende", "Sirena"])

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

# ---- TAB 2: Consultar personajes ----
with tab2:
    st.header("🧙‍♂️ Gestor de Personajes")

    characters = load_characters()
    search_query = st.text_input(
        "🔎 Buscar personaje por nombre:",
        key="search_character_tab2"  # 👈 clave única
    )

    # Filtrar resultados
    if search_query:
        results = [
            char for char in characters
            if search_query.lower() in char["name"].lower()
        ]
    else:
        results = characters
        
    if results:
        st.subheader(f"Resultados encontrados: {len(results)}")
        for char in results:
            with st.expander(f"📌 {char['name']}"):
                st.write(f"**Clase:** {char['class']}")
                st.write(f"**Raza:** {char['race']}")
                st.write(f"**Habilidades:** {', '.join(char['skills'])}")
    else:
        st.warning("⚠️ No se encontraron personajes con ese nombre.")