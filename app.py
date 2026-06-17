import streamlit as st
import requests
import base64

# 1. CONFIGURACIÓN VISUAL Y DE PÁGINA
st.set_page_config(page_title="Aula Virtual - Elena Vila", layout="wide", initial_sidebar_state="expanded")

# Datos de tu GitHub
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "MATEMATICAS"
TOKEN_GITHUB = st.secrets["TOKEN_GITHUB"]

# Estilos visuales más limpios y modernos (CORREGIDO AQUÍ)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .titulo { color: #1E3A8A; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE GITHUB ---
def obtener_archivos(ruta=""):
    url = f"https://api.github.com/repos/{USUARIO_GIT}/{REPOSITORIO_GIT}/contents/{ruta}?ref={RAMA}"
    headers = {"Authorization": f"token {TOKEN_GITHUB}"}
    respuesta = requests.get(url, headers=headers)
    return respuesta.json() if respuesta.status_code == 200 else []

def subir_archivo_a_github(ruta_destino, contenido_bytes, mensaje_commit):
    url = f"https://api.github.com/repos/{USUARIO_GIT}/{REPOSITORIO_GIT}/contents/{ruta_destino}"
    headers = {"Authorization": f"token {TOKEN_GITHUB}", "Accept": "application/vnd.github.v3+json"}
    
    # Codificar el archivo en base64 para GitHub
    contenido_base64 = base64.b64encode(contenido_bytes).decode("utf-8")
    
    datos = {
        "message": mensaje_commit,
        "content": contenido_base64,
        "branch": RAMA
    }
    
    # Verificar si el archivo ya existe para obtener su 'sha' (para poder sobrescribir)
    chequeo = requests.get(url + f"?ref={RAMA}", headers=headers)
    if chequeo.status_code == 200:
        datos["sha"] = chequeo.json()["sha"]
        
    r = requests.put(url, headers=headers, json=datos)
    return r.status_code in [200, 201]

# --- INTERFAZ DE USUARIO ---

# Lateral: Zona de Administración Oculta
st.sidebar.title("🔐 Zona Privada")
es_admin = st.sidebar.checkbox("Modo Administradora")

if es_admin:
    password = st.sidebar.text_input("Contraseña de acceso:", type="password")
    # Puedes cambiar "profe2026" por la contraseña que tú quieras
    if password == "profe2026":
        st.sidebar.success("¡Identidad confirmada!")
        
        st.sidebar.subheader("Subir nuevos apuntes")
        # Detectar carpetas existentes para ofrecerlas en el desplegable
        elementos_raiz = obtener_archivos()
        carpetas_disponibles = [item["name"] for item in elementos_raiz if item["type"] == "dir"]
        carpetas_disponibles.append("+ Crear nueva carpeta...")
        
        carpeta_seleccionada = st.sidebar.selectbox("¿Dónde lo guardamos?", carpetas_disponibles)
        
        if carpeta_seleccionada == "+ Crear nueva carpeta...":
            nueva_carpeta = st.sidebar.text_input("Nombre de la nueva carpeta: (ej: Tema 2)")
            carpeta_destino = nueva_carpeta.strip()
        else:
            carpeta_destino = carpeta_seleccionada

        archivo_subido = st.sidebar.file_uploader("Selecciona el archivo de tu PC", type=["pdf", "docx", "xlsx", "png", "jpg"])
        
        if st.sidebar.button("🚀 Publicar en la Web") and archivo_subido is not None and carpeta_destino:
            bytes_data = archivo_subido.getvalue()
            ruta_final = f"{carpeta_destino}/{archivo_subido.name}" if carpeta_destino else archivo_subido.name
            
            with st.sidebar.spinner("Subiendo archivo..."):
                exito = subir_archivo_a_github(ruta_final, bytes_data, f"Subido desde la web: {archivo_subido.name}")
                if exito:
                    st.sidebar.success(f"¡{archivo_subido.name} subido con éxito!")
                    st.rerun()
                else:
                    st.sidebar.error("Error al subir. Revisa si configuraste bien el Secret en Streamlit.")
    elif password != "":
        st.sidebar.error("Contraseña incorrecta")

# Cuerpo Principal: Vista de los Alumnos
st.title("📚 Aula Virtual - Materiales de Clase")
st.write("Bienvenidos. Desde aquí podéis descargar todos los recursos actualizados.")
st.write("---")

contenido = obtener_archivos()

# Mostrar los archivos de manera elegante
if not contenido:
    st.info("Aún no se han cargado carpetas o archivos en esta sección.")

for item in contenido:
    if item["type"] == "dir":
        # Bloque visual para las carpetas
        with st.container():
            st.markdown(f"<div class='card'><h3 class='titulo'>📁 Carpeta: {item['name']}</h3></div>", unsafe_allow_html=True)
            sub_contenido = obtener_archivos(item["path"])
            
            if not sub_contenido:
                st.text("   (Carpeta vacía temporalmente)")
            
            # Mostrar archivos de la carpeta en columnas claras
            for sub_item in sub_contenido:
                if sub_item["type"] == "file":
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"📄 **{sub_item['name']}**")
                    with col2:
                        st.markdown(f"[📥 Descargar]({sub_item['download_url']})")
            st.write("") # Espaciado
            
    elif item["type"] == "file" and item["name"] not in ["app.py", "README.md", "requirements.txt"]:
        # Archivos sueltos en la raíz
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"📄 **{item['name']}** (Raíz)")
        with col2:
            st.markdown(f"[📥 Descargar]({item['download_url']})")
