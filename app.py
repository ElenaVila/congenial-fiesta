import streamlit as st
import requests
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
st.set_page_config(page_title="Aula Virtual - Elena Vila", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #f3f4f6; }
    .folder-box {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .file-box {
        background-color: #ffffff;
        padding: 10px 15px;
        border-radius: 6px;
        margin-bottom: 5px;
        border: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .section-title { color: #1e3a8a; font-weight: bold; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# Credenciales seguras
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "MATEMATICAS"
TOKEN_GITHUB = st.secrets["TOKEN_GITHUB"]

# --- FUNCIONES DE CONEXIÓN CON GITHUB ---
def obtener_contenido(ruta=""):
    url = f"https://api.github.com/repos/{USUARIO_GIT}/{REPOSITORIO_GIT}/contents/{ruta}?ref={RAMA}"
    headers = {"Authorization": f"token {TOKEN_GITHUB}"}
    r = requests.get(url, headers=headers)
    return r.json() if r.status_code == 200 else []

def subir_a_github(ruta_destino, contenido_bytes, mensaje):
    url = f"https://api.github.com/repos/{USUARIO_GIT}/{REPOSITORIO_GIT}/contents/{ruta_destino}"
    headers = {"Authorization": f"token {TOKEN_GITHUB}", "Accept": "application/vnd.github.v3+json"}
    contenido_base64 = base64.b64encode(contenido_bytes).decode("utf-8")
    
    datos = {"message": mensaje, "content": contenido_base64, "branch": RAMA}
    chequeo = requests.get(url + f"?ref={RAMA}", headers=headers)
    if chequeo.status_code == 200:
        datos["sha"] = chequeo.json()["sha"]
        
    r = requests.put(url, headers=headers, json=datos)
    return r.status_code in [200, 201]

# --- ESTRUCTURA DE PESTAÑAS PRINCIPALES ---
st.title("🎓 Aula Virtual Integrada")
pestana_materiales, pestana_entregas, pestana_agenda = st.tabs(["📚 Materiales de Clase", "📤 Entrega de Tareas", "📅 Mi Agenda y Pendientes"])

# ==========================================
# PESTAÑA 1: MATERIALES DE CLASE (EXPLORADOR)
# ==========================================
with pestana_materiales:
    st.markdown("<h2 class='section-title'>📁 Explorador de Asignaturas y Temas</h2>", unsafe_allow_html=True)
    
    # Sistema de navegación dinámico por carpetas (Explorador de archivos)
    elementos_raiz = obtener_contenido()
    carpetas = [item["name"] for item in elementos_raiz if item["type"] == "dir" and item["name"] != "Tareas_Alumnos"]
    
    if carpetas:
        carpeta_sel = st.selectbox("Selecciona la Asignatura / Bloque:", carpetas)
        
        # Entramos en la subcarpeta seleccionada
        sub_elementos = obtener_contenido(carpeta_sel)
        sub_carpetas = [item["name"] for item in sub_elementos if item["type"] == "dir"]
        archivos_sueltos = [item for item in sub_elementos if item["type"] == "file"]
        
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            st.write("📂 **Subcarpetas / Temas disponibles:**")
            if sub_carpetas:
                sub_carpeta_sel = st.selectbox("Ver tema:", ["(Ninguno seleccionado)"] + sub_carpetas)
                if sub_carpeta_sel != "(Ninguno seleccionado)":
                    archivos_sub = obtener_contenido(f"{carpeta_sel}/{sub_carpeta_sel}")
                    for f in archivos_sub:
                        if f["type"] == "file":
                            st.markdown(f"<div class='file-box'>📄 {f['name']} <a href='{f['download_url']}' target='_blank'>📥 Descargar</a></div>", unsafe_allow_html=True)
            else:
                st.info("No hay subcarpetas en este bloque.")
                
        with col_der:
            st.write("📄 **Archivos en la raíz de este bloque:**")
            if archivos_sueltos:
                for f in archivos_sueltos:
                    st.markdown(f"<div class='file-box'>📄 {f['name']} <a href='{f['download_url']}' target='_blank'>📥 Descargar</a></div>", unsafe_allow_html=True)
            else:
                st.info("No hay archivos sueltos aquí.")
    else:
        st.info("Crea tu primera carpeta desde la Zona Privada en el menú lateral.")

# ==========================================
# PESTAÑA 2: BUZÓN DE ENTREGAS PARA ALUMNOS
# ==========================================
with pestana_entregas:
    st.markdown("<h2 class='section-title'>📤 Entrega de Ejercicios y Tareas</h2>", unsafe_allow_html=True)
    st.write("Sube aquí tus resoluciones. Tu profesora recibirá el documento organizado automáticamente.")
    
    with st.form("formulario_entrega", clear_on_submit=True):
        nombre_alumno = st.text_input("Nombre y Apellidos del Alumno:")
        tarea_nombre = st.text_input("Nombre de la Tarea (Ej: Ejercicios Límites Tema 1):")
        archivo_tarea = st.file_uploader("Adjunta tu archivo (PDF, Imagen, Word):", type=["pdf", "docx", "png", "jpg"])
        boton_entrega = st.form_submit_button("Enviar Tarea a la Profesora")
        
        if boton_entrega:
            if nombre_alumno and tarea_nombre and archivo_tarea:
                fecha_hoy = datetime.now().strftime("%Y-%m-%d_%H-%M")
                # Formateamos el nombre del archivo final para que la profe sepa de quién es
                nombre_limpio_alumno = nombre_alumno.replace(" ", "_")
                ruta_entrega = f"Tareas_Alumnos/{tarea_nombre}/{nombre_limpio_alumno}_{fecha_hoy}_{archivo_tarea.name}"
                
                exito = subir_a_github(ruta_entrega, archivo_tarea.getvalue(), f"Tarea entregada por {nombre_alumno}")
                if exito:
                    st.success("🎉 ¡Tu tarea ha sido entregada correctamente! Gracias.")
                else:
                    st.error("Hubo un problema al subir la tarea. Contacta con tu profesora.")
            else:
                st.warning("Por favor, rellena todos los campos del formulario antes de enviar.")

# ==========================================
# PESTAÑA 3: AGENDA Y PENDIENTES DEL ALUMNO
# ==========================================
with pestana_agenda:
    st.markdown("<h2 class='section-title'>📅 Planificador Personal de Clase</h2>", unsafe_allow_html=True)
    st.write("Usa este espacio interactivo para apuntar tus exámenes, tareas o repasos pendientes.")
    
    # Lista de pendientes local por sesión del navegador
    if "tareas_locales" not in st.session_state:
        st.session_state["tareas_locales"] = [
            {"evento": "Examen de Matemáticas I", "fecha": "2026-06-22", "hecho": False},
            {"evento": "Entregar boletín de continuidad", "fecha": "2026-06-25", "hecho": False}
        ]
        
    nueva_tarea = st.text_input("Añadir un recordatorio o pendiente personal:")
    fecha_tarea = st.date_input("Fecha límite:")
    
    if st.button("➕ Añadir a mi lista"):
        if nueva_tarea:
            st.session_state["tareas_locales"].append({"evento": nueva_tarea, "fecha": str(fecha_tarea), "hecho": False})
            st.rerun
