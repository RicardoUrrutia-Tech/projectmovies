import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials
import json
import os

# --- Configuración de credenciales ---

if os.path.exists("/content/projectmovies/projectmovies-firebase.json"):
    # Modo local en Colab
    if not firebase_admin._apps:
        cred = credentials.Certificate('/content/projectmovies/projectmovies-firebase.json')
        firebase_admin.initialize_app(cred)
    db = firestore.client()
else:
    # Modo producción en Streamlit Cloud
    key_dict = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])  # ✅ CORREGIDO
    creds = service_account.Credentials.from_service_account_info(key_dict)
    db = firestore.Client(credentials=creds, project="projectmovies-df977")  # ✅ CORREGIDO: nombre correcto del proyecto

# --- Función para cargar datos de Firestore ---
@st.cache_data
def load_data():
    movies_ref = db.collection(u'movies').stream()
    movies_list = [doc.to_dict() for doc in movies_ref]
    return pd.DataFrame(movies_list)

# Cargar datos al iniciar la app
df = load_data()

# --- Interfaz de la app ---
st.set_page_config(page_title="Dashboard de Películas", page_icon="🎬", layout="wide")

st.title("🎬 Dashboard de Películas")
st.markdown("Consulta, filtra e inserta nuevas películas usando Firestore como base de datos.")

# --- Sidebar ---
st.sidebar.header("Opciones del Dashboard")

# ✅ 1. Checkbox para mostrar todos los filmes
if st.sidebar.checkbox("Mostrar todos los filmes"):
    st.subheader("Listado completo de filmes")
    st.dataframe(df)

# ✅ 2. Buscar por título
st.sidebar.subheader("Buscar por título")
search_title = st.sidebar.text_input("Título del filme")
if st.sidebar.button("Buscar"):
    result = df[df['name'].str.contains(search_title, case=False, na=False)]
    st.write(f"Resultados de búsqueda para '{search_title}':")
    st.dataframe(result)

# ✅ 3. Filtrar por director
st.sidebar.subheader("Filtrar por director")
directors = df['director'].dropna().unique().tolist()
selected_director = st.sidebar.selectbox("Selecciona un director", directors)
if st.sidebar.button("Filtrar"):
    result = df[df['director'] == selected_director]
    st.write(f"Películas dirigidas por {selected_director} (Total: {len(result)}):")
    st.dataframe(result)

# ✅ 4. Formulario para agregar nuevo filme
st.sidebar.subheader("Agregar nuevo filme")
new_company = st.sidebar.text_input("Compañía")
new_director = st.sidebar.text_input("Director")
new_genre = st.sidebar.text_input("Género")
new_name = st.sidebar.text_input("Nombre del filme")

if st.sidebar.button("Agregar filme"):
    if new_name:
        doc_ref = db.collection('movies').document()
        doc_ref.set({
            'company': new_company,
            'director': new_director,
            'genre': new_genre,
            'name': new_name
        })
        st.sidebar.success(f"🎉 Filme '{new_name}' agregado exitosamente!")
    else:
        st.sidebar.error("Por favor, ingresa al menos el nombre del filme.")

st.sidebar.markdown("---")
st.sidebar.info("Proyecto por Ricardo Urrutia - Streamlit + Firebase")
