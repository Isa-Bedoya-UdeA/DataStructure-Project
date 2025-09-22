import streamlit as st

with st.form("character_form", clear_on_submit=True):
    st.title("Creador de Personaje RPG")
    
    name = st.text_input("Nombre del personaje")
    class_rpg = st.selectbox("Clase", ["Guerrero", "Mago", "Clérigo", "Paladín", "Bárbaro", "Asesino", "Druida", "Arquero", "Nigromante", "Monje"])
    race = st.selectbox("Raza", ["Humano", "Elfo", "Enano", "Orco", "Gnomo", "Centauro", "Ciclope", "Duende", "Sirena"])
    skills = st.multiselect("Habilidades", ["Ataque físico", "Ataque mágico", "Sigilo", "Curación"]) 
    
    submitted = st.form_submit_button("Crear personaje")
    
    if submitted:
        st.write(f"¡Personaje creado!")
        st.write(f"Nombre: {name}")
        st.write(f"Clase: {class_rpg}")
        st.write(f"Raza: {race}")
        st.write(f"Habilidades: {', '.join(skills)}")
