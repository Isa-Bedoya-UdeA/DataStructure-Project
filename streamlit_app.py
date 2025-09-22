import streamlit as st

def create_character(name, class_rpg, race, skills):
    character = {
        "name": name,
        "class": class_rpg,
        "race": race,
        "skills": skills
    }
    return character

with st.form("character_form", clear_on_submit=True):
    st.header("Creador de Personaje RPG")
    
    name = st.text_input("Nombre del personaje", placeholder="Ingresa un nombre para tu personaje", max_chars=16)
    class_rpg = st.selectbox("Clase", ["Guerrero", "Mago", "Clérigo", "Paladín", "Bárbaro", "Asesino", "Druida", "Arquero", "Nigromante", "Monje"], placeholder="Selecciona tu clase")
    race = st.selectbox("Raza", ["Humano", "Elfo", "Enano", "Orco", "Gnomo", "Centauro", "Ciclope", "Duende", "Sirena"], placeholder="Selecciona tu raza")
    skills = st.pills("Habilidades", ["Ataque físico", "Ataque mágico", "Sigilo", "Curación", "Guardia", "Invocación", "Esquivar", "Arquería", "Combate cuerpo a cuerpo"], selection_mode="multi") 
    st.caption("Debes seleccionar 6 habilidades distintas.")

    submitted = st.form_submit_button("Crear personaje")
    
    if submitted:
        st.success('**¡Personaje creado exitosamente!**')
        st.write("### Detalles del Personaje:")
        character = create_character(name, class_rpg,race, skills)
        st.json(character)
