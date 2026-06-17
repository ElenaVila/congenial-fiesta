import streamlit as st
import requests
import base64
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS CSS
st.set_page_config(page_title="Aula Virtual - Elena Vila", layout="wide")

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
        padding: 12px 15px;
        border-radius: 6px;
        margin-bottom: 8px;
        border: 1px solid #e5e7eb;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .task-box {
        background-color: #fffbeb;
        padding: 12px 15px;
        border-radius: 6px;
        margin-bottom: 8px;
        border: 1px solid #fde68a;
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
pestana_materiales, pestana_entregas, pestana_agenda, pestana_admin = st.tabs([
    "📚 Materiales de Clase", 
    "📤 Entrega de Tareas", 
    "📅 Mi Agenda y Pendientes",
    "👩‍🏫 Panel de Control (Profesora)"
])

# ==========================================
# PESTAÑA 1: MATERIALES DE CLASE (ALUMNOS)
# ==========================================
with pestana_materiales:
    st.markdown("<h2 class='section-title'>📁 Explorador de Asignaturas y Temas</h2>", unsafe_allow_html=True)
    
    elementos_raiz = obtener_contenido()
    # Ocultamos la carpeta de tareas de los alumnos para que ellos no la vean en descargas
    carpetas = [item["name"] for item in elementos_raiz if item["type"] == "dir" and item["name"] != "Tareas_Alumnos"]
    
    if carpetas:
        carpeta_sel = st.selectbox("Selecciona la Asignatura / Bloque:", carpetas, key="student_folder")
        
        sub_elementos = obtener_contenido(carpeta_sel)
        sub_carpetas = [item["name"] for item in sub_elementos if item["type"] == "dir"]
        archivos_sueltos = [item for item in sub_elementos if item["type"] == "file" and item["name"] != ".gitkeep"]
        
        col_izq, col_der = st.columns(2)
        
        with col_izq:
            st.write("📂 **Subcarpetas / Temas disponibles:**")
            if sub_carpetas:
                sub_carpeta_sel = st.selectbox("Ver tema:", ["(Ninguno seleccionado)"] + sub_carpetas, key="student_subfolder")
                if sub_carpeta_sel != "(Ninguno seleccionado)":
                    archivos_sub = obtener_contenido(f"{carpeta_sel}/{sub_carpeta_sel}")
                    for f in archivos_sub:
                        if f["type"] == "file" and f["name"] != ".gitkeep":
                            st.markdown(f"<div class='file-box'>📄 {f['name']} <a href='{f['download_url']}' target='_blank'>📥 Descargar</a></div>", unsafe_allow_html=True)
            else:
                st.info("No hay subcarpetas creadas en este bloque.")
                
        with col_der:
            st.write("📄 **Archivos generales de este bloque:**")
            if archivos_sueltos:
                for f in archivos_sueltos:
                    st.markdown(f"<div class='file-box'>📄 {f['name']} <a href='{f['download_url']}' target='_blank'>📥 Descargar</a></div>", unsafe_allow_html=True)
            else:
                st.info("No hay archivos sueltos en la raíz de esta carpeta.")
    else:
        st.info("Aún no se han publicado materiales en el aula virtual.")

# ==========================================
# PESTAÑA 2: BUZÓN DE ENTREGAS (ALUMNOS)
# ==========================================
with pestana_entregas:
    st.markdown("<h2 class='section-title'>📤 Entrega de Ejercicios y Tareas</h2>", unsafe_allow_html=True)
    st.write("Sube aquí tus resoluciones en formato PDF o imagen. Llegarán directamente al panel de la profesora.")
    
    with st.form("formulario_entrega", clear_on_submit=True):
        nombre_alumno = st.text_input("Nombre y Apellidos del Alumno:")
        tarea_nombre = st.text_input("Nombre o Código de la Tarea (Ej: Tarea 1 - Derivadas):")
        archivo_tarea = st.file_uploader("Adjunta tu documento:", type=["pdf", "docx", "png", "jpg"])
        boton_entrega = st.form_submit_button("Enviar Tarea a la Profesora")
        
        if boton_entrega:
            if nombre_alumno and tarea_nombre and archivo_tarea:
                fecha_hoy = datetime.now().strftime("%Y-%m-%d_%H-%M")
                nombre_limpio_alumno = nombre_alumno.strip().replace(" ", "_")
                tarea_limpia = tarea_nombre.strip().replace(" ", "_")
                
                # Se guarda de forma organizada: Tareas_Alumnos / Nombre_De_La_Tarea / Alumno_archivo.pdf
                ruta_entrega = f"Tareas_Alumnos/{tarea_limpia}/{nombre_limpio_alumno}_{fecha_hoy}_{archivo_tarea.name}"
                
                exito = subir_a_github(ruta_entrega, archivo_tarea.getvalue(), f"Tarea entregada por {nombre_alumno}")
                if exito:
                    st.success("🎉 ¡Tu tarea ha sido entregada correctamente! Tu profesora ya puede verla.")
                else:
                    st.error("Hubo un problema al tramitar la entrega. Avisa a tu profesora.")
            else:
                st.warning("Por favor, completa todos los campos y adjunta un archivo.")

# ==========================================
# PESTAÑA 3: AGENDA DEL ESTUDIANTE
# ==========================================
with pestana_agenda:
    st.markdown("<h2 class='section-title'>📅 Planificador y Recordatorios personales</h2>", unsafe_allow_html=True)
    
    if "tareas_locales" not in st.session_state:
        st.session_state["tareas_locales"] = [
            {"evento": "Repasar tema de continuidad", "fecha": "2026-06-20", "hecho": False},
            {"evento": "Entrega obligatoria: Boletín 1", "fecha": "2026-06-25", "hecho": False}
        ]
        
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.write("✍️ **Añadir un pendiente:**")
        nueva_tarea = st.text_input("¿Qué tienes que hacer?")
        fecha_tarea = st.date_input("Fecha límite:")
        if st.button("➕ Añadir Recordatorio"):
            if nueva_tarea:
                st.session_state["tareas_locales"].append({"evento": nueva_tarea, "fecha": str(fecha_tarea), "hecho": False})
                st.rerun()
    with col_b:
        st.write("🔔 **Tu lista de control:**")
        for idx, t in enumerate(st.session_state["tareas_locales"]):
            st.checkbox(f"📌 {t['evento']} — ⏱️ Límite: `{t['fecha']}`", key=f"todo_{idx}")

# ==========================================
# PESTAÑA 4: PANEL DE CONTROL DE LA PROFESORA
# ==========================================
with pestana_admin:
    st.markdown("<h2 class='section-title'>🔐 Acceso Restringido a Dirección</h2>")
    pass_admin = st.text_input("Introduce la clave de administración para desbloquear las herramientas:", type="password")
    
    if pass_admin == "profe2026":
        st.success("🔒 Sesión de Administradora confirmada.")
        st.write("---")
        
        # CREAMOS DOS SUBSECCIONES DENTRO DEL PANEL DE CONTROL
        sub_pestana_ver, sub_pestana_crear = st.tabs(["📥 VER ENTREGAS DE ALUMNOS", "🛠️ SUBIR MATERIALES Y CREAR CARPETAS"])
        
        # --------------------------------------------------
        # SUB-PESTAÑA A: REVISAR ENTREGAS
        # --------------------------------------------------
        with sub_pestana_ver:
            st.subheader("📁 Bandeja de Entrada de Tareas Recibidas")
            
            # Leer la carpeta raíz donde caen las tareas
            contenido_tareas = obtener_contenido("Tareas_Alumnos")
            carpetas_tareas = [item["name"] for item in contenido_tareas if item["type"] == "dir"]
            
            if carpetas_tareas:
                tarea_a_revisar = st.selectbox("Selecciona la Tarea que quieres corregir:", carpetas_tareas)
                
                # Leer archivos dentro de esa tarea
                archivos_entregados = obtener_contenido(f"Tareas_Alumnos/{tarea_a_revisar}")
                entregas_reales = [f for f in archivos_entregados if f["type"] == "file" and f["name"] != ".gitkeep"]
                
                if entregas_reales:
                    st.info(f"Se han encontrado {len(entregas_reales)} entregas para esta actividad:")
                    for f in entregas_reales:
                        # Re-formatear nombre para mostrarlo más limpio (ej: Juan_Perez_2026-06-17_ejercicio.pdf)
                        nombre_mostrar = f["name"].replace("_", " ")
                        
                        col_name, col_btn = st.columns([4, 1])
                        with col_name:
                            st.markdown(f"<div class='task-box'>📤 <b>Entrega:</b> {nombre_mostrar}</div>", unsafe_allow_html=True)
                        with col_btn:
                            # Botón que descarga el archivo del alumno directamente al ordenador de la profe
                            st.markdown(f"<br><a href='{f['download_url']}' target='_blank'><button style='background-color:#10b981; color:white; border:none; padding:8px 12px; border-radius:5px; cursor:pointer;'>📥 Descargar Archivo</button></a>", unsafe_allow_html=True)
                else:
                    st.warning("Aún ningún alumno ha subido archivos para esta tarea.")
            else:
                st.info("La carpeta 'Tareas_Alumnos' está vacía. Ningún alumno ha enviado nada todavía.")
                
        # --------------------------------------------------
        # SUB-PESTAÑA B: SUBIR Y CREAR ESTRUCTURA
        # --------------------------------------------------
        with sub_pestana_crear:
            st.subheader("🛠️ Panel de Carga de Contenidos")
            tipo_accion = st.radio("¿Qué acción deseas ejecutar?", ["Subir Archivo/Apuntes", "Crear Nueva Carpeta o Asignatura"])
            
            estructura = obtener_contenido()
            lista_carpetas_admin = [item["name"] for item in estructura if item["type"] == "dir" and item["name"] != "Tareas_Alumnos"]
            
            if tipo_accion == "Subir Archivo/Apuntes":
                if lista_carpetas_admin:
                    target_folder = st.selectbox("Selecciona la carpeta principal:", lista_carpetas_admin, key="admin_root")
                    
                    sub_est = obtener_contenido(target_folder)
                    sub_caps = [item["name"] for item in sub_est if item["type"] == "dir"]
                    
                    if sub_caps:
                        sub_target = st.selectbox("Selecciona el tema interno (Opcional):", ["(Ninguna - Guardar en raíz)"] + sub_caps, key="admin_sub")
                        ruta_final_admin = f"{target_folder}/{sub_target}" if sub_target != "(Ninguna - Guardar en raíz)" else target_folder
                    else:
                        ruta_final_admin = target_folder
                        
                    file_to_upload = st.file_uploader("Elige el documento de tu ordenador:")
                    if st.button("🚀 Publicar en la Web") and file_to_upload:
                        path_complete = f"{ruta_final_admin}/{file_to_upload.name}"
                        with st.spinner("Subiendo..."):
                            if subir_a_github(path_complete, file_to_upload.getvalue(), "Nuevo material escolar"):
                                st.success(f"¡{file_to_upload.name} publicado correctamente!")
                                st.rerun()
                else:
                    st.warning("Primero debes crear una carpeta principal.")
                    
            elif tipo_accion == "Crear Nueva Carpeta o Asignatura":
                nivel = st.radio("Jerarquía de la carpeta:", ["Carpeta Principal (Ej: Matemáticas 1º Bach)", "Subcarpeta/Tema (Ej: Tema 1 - Matrices)"])
                
                if nivel == "Carpeta Principal (Ej: Matemáticas 1º Bach)":
                    nombre_nueva = st.text_input("Nombre de la nueva materia:")
                    if st.button("Crear Carpeta Principal") and nombre_nueva:
                        with st.spinner("Creando..."):
                            if subir_a_github(f"{nombre_nueva.strip()}/.gitkeep", b"", "Creando asignatura"):
                                st.success("¡Carpeta principal creada!")
                                st.rerun()
                else:
                    if lista_carpetas_admin:
                        raiz_padre = st.selectbox("¿Dentro de cuál va?", lista_carpetas_admin)
                        nombre_sub = st.text_input("Nombre de la subcarpeta / tema:")
                        if st.button("Crear Subcarpeta") and nombre_sub:
                            with st.spinner("Creando..."):
                                if subir_a_github(f"{raiz_padre}/{nombre_sub.strip()}/.gitkeep", b"", "Creando tema"):
                                    st.success("¡Subcarpeta creada correctamente!")
                                    st.rerun()
    elif pass_admin != "":
        st.error("🔒 Contraseña incorrecta. Acceso denegado.")
