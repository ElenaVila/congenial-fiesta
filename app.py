import streamlit as st
import requests

# Configuración de la ventana del navegador
st.set_page_config(page_title="Apuntes - Elena Vila", layout="centered")

st.title("📚 Aula Virtual - Descarga de Materiales")
st.write("¡Hola! Aquí tenéis los apuntes y ejercicios organizados por carpetas.")

# Tu configuración real de GitHub
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "main"

# Función interna para leer lo que hay en tus carpetas de GitHub
def obtener_archivos(ruta=""):
    url = f"https://api.github.com/repos/{USUARIO_GIT}/{REPOSITORIO_GIT}/contents/{ruta}?ref={RAMA}"
    respuesta = requests.get(url)
    if respuesta.status_code == 200:
        return respuesta.json()
    return []

# Cargar el contenido de la raíz del repositorio
contenido = obtener_archivos()

# Recorrer cada elemento de tu GitHub y mostrarlo de forma bonita
for item in contenido:
    # Si encuentra una carpeta (como 'Matematicas')
    if item["type"] == "dir":
        with st.expander(f"📁 {item['name']}"):
            sub_contenido = obtener_archivos(item["path"])
            for sub_item in sub_contenido:
                if sub_item["type"] == "file":
                    st.write(f"📄 {sub_item['name']}")
                    st.markdown(f"[Descargar archivo]({sub_item['download_url']})")
    
    # Si encuentra un archivo suelto (ocultamos los de configuración)
    elif item["type"] == "file" and item["name"] not in ["app.py", "README.md", "requirements.txt"]:
        st.write(f"📄 {item['name']}")
        st.markdown(f"[Descargar archivo]({item['download_url']})")
