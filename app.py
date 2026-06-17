import streamlit as st
import requests
import base64
import json
from datetime import datetime
import pandas as pd

# =========================================================================
# 1. ESTILO LIMPIO Y COLORIDO DE AULA VIRTUAL (SIN SOLAPAMIENTOS)
# =========================================================================
st.set_page_config(page_title="Aula Virtual", layout="wide")

st.markdown("""
    <style>
    /* Tipografía limpia y profesional */
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Segoe UI', sans-serif !important;
        background-color: #f8fafc !important;
    }

    /* Títulos con personalidad y color */
    .main-title {
        color: #1e3a8a;
        font-weight: 700;
        margin-bottom: 20px;
    }

    /* Contenedor de recursos sin estilos que rompan el uploader */
    .recurso-bloque {
        padding: 15px;
        background-color: #ffffff;
        border-radius: 8px;
        border-left: 5px solid #3b82f6;
        margin-bottom: 12px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Conexión Segura con GitHub Secrets
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "MATEMATICAS"
TOKEN_GITHUB = st.secrets["TOKEN_GITHUB"]

# =========================================================================
# 2. MAQUINARIA DE CONEXIÓN CON GITHUB (SIN ALTERAR LA UTILIDAD)
# =========================================================================
def api_git(ruta="", metodo="GET", datos=None):
    url = f"https://api.github.com/repos/{USUARIO_GIT}/{REPOSITORIO_GIT}/contents/{ruta}?ref={RAMA}"
    headers = {"Authorization": f"token {TOKEN_GITHUB}", "Accept": "application/vnd.github.v3+json"}
    if metodo == "GET":
        r = requests.get(url, headers=headers)
        return r.json() if r.status_code == 200 else []
    elif metodo == "PUT":
        url_put = f"https://api.github.com/repos/{USUARIO_GIT}/{REPOSITORIO_GIT}/contents/{ruta}"
        r = requests.put(url_put, headers=headers, json=datos)
        return r.status_code in [200, 201]
    return []

def enviar_archivo(ruta, contenido_bytes, mensaje):
    datos = {"message": mensaje, "content": base64.b64encode(contenido_bytes).decode("utf-8"), "branch": RAMA}
    chequeo = api_git(ruta)
    if isinstance(chequeo, dict) and "sha" in chequeo:
        datos["sha"] = chequeo["sha"]
    return api_git(ruta, metodo="PUT", datos=datos)

def listar_directorios(ruta=""):
    res = api_git(ruta)
    if isinstance(res, list):
        return [item["name"] for item in res if item["type"] == "dir" and item["name"] not in ["Entregas_Globales"]]
    return []

if "curso_activo" not in st.session_state:
    st.session_state["curso_activo"] = None

# =========================================================================
# 3. NAVEGACIÓN PRINCIPAL DEL AULA VIRTUAL
# =========================================================================
st.sidebar.markdown("<h2 style='color: #1e3a8a; font-weight: 700;'>🏫 Aula Virtual</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
navegacion = st.sidebar.radio("Secciones disponibles:", [
    "📚 Mis Asignaturas",
    "📅 Calendario de Entregas",
    "👩‍🏫 Panel de Gestión Docente"
])

if navegacion != "📚 Mis Asignaturas":
    st.session_state["curso_activo"] = None

# -------------------------------------------------------------------------
# VISTA A: TABLÓN DE ASIGNATURAS CON IMAGEN DE PORTADA PERSONALIZADA
# -------------------------------------------------------------------------
if navegacion == "📚 Mis Asignaturas":
    
    if st.session_state["curso_activo"] is None:
        st.markdown("<h1 class='main-title'>📚 Mis Cursos Activos</h1>", unsafe_allow_html=True)
        st.write("Selecciona una asignatura para acceder a los materiales, unidades didácticas y entregas.")
        
        asignaturas = listar_directorios()
        
        if asignaturas:
            cols = st.columns(3)
            for idx, asig in enumerate(asignaturas):
                with cols[idx % 3]:
                    # Intentar buscar si la asignatura tiene una imagen de portada personalizada guardada
                    archivo_portada = api_git(f"{asig}/portada_curso.png")
                    if not archivo_portada or isinstance(archivo_portada, list):
                        archivo_portada = api_git(f"{asig}/portada_curso.jpg")
                    
                    # Mostrar la portada si existe, si no, un color corporativo por defecto
                    with st.container(border=True):
                        if isinstance(archivo_portada, dict) and "download_url" in archivo_portada:
                            st.image(archivo_portada["download_url"], use_container_width=True)
                        else:
                            st.markdown(f"""
                                <div style='background: linear-gradient(135px, #3b82f6 0%, #1d4ed8 100%); 
                                     height: 120px; border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white;'>
                                     <span style='font-size: 40px;'>📘</span>
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Nombre claro de la asignatura justo debajo de la foto
                        st.markdown(f"<h3 style='margin: 10px 0 5px 0; color: #0f172a;'>{asig.replace('_', ' ')}</h3>", unsafe_allow_html=True)
                        st.write("Acceso al contenido del curso.")
                        
                        if st.button("Entrar al Aula", key=f"open_{asig}"):
                            st.session_state["curso_activo"] = asig
                            st.rerun()
        else:
            st.info("Aún no hay asignaturas registradas en el Aula Virtual.")

    else:
        # INTERIOR DE LA ASIGNATURA
        asig_actual = st.session_state["curso_activo"]
        
        if st.button("⬅️ Volver al listado de asignaturas"):
            st.session_state["curso_activo"] = None
            st.rerun()
            
        st.markdown(f"<h1 class='main-title'>📖 Asignatura: {asig_actual.replace('_', ' ')}</h1>", unsafe_allow_html=True)
        st.write("Unidades didácticas secuenciales publicadas por el profesorado:")
        st.write("---")
        
        temas = listar_directorios(asig_actual)
        if temas:
            for tema in temas:
                with st.expander(f"📁 {tema.replace('_', ' ')}", expanded=True):
                    elementos_tema = api_git(f"{asig_actual}/{tema}")
                    archivos = [e for e in elementos_tema if e["type"] == "file" and e["name"] != ".gitkeep"]
                    
                    if archivos:
                        for el in archivos:
                            es_tarea = el["name"].startswith("TAREA_")
                            
                            if es_tarea:
                                partes = el["name"].split("_", 2)
                                f_limite = partes[1] if len(partes) > 1 else "Sin fecha"
                                t_nombre = partes[2].replace("_", " ").split(".")[0] if len(partes) > 2 else "Tarea"
                                
                                st.markdown(f"""
                                    <div class='recurso-bloque' style='border-left-color: #ef4444; background-color: #fef2f2;'>
                                        <span style='background-color:#ef4444; color:white; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold;'>TAREA OBLIGATORIA</span>
                                        <h4 style='margin:5px 0; color:#991b1b;'>📋 {t_nombre}</h4>
                                        <p style='margin:0; font-size:13px; color:#5f6368;'>Fecha de vencimiento: <b>{f_limite}</b></p>
                                        <p style='margin-top:5px;'><a href='{el['download_url']}' target='_blank' style='color:#ef4444; font-weight:bold;'>📥 Descargar Enunciado de la Actividad</a></p>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Formulario limpio (SIN SOLAPAMIENTOS "upload upload")
                                with st.container(border=True):
                                    st.write("📬 **Formulario de entrega para el alumno:**")
                                    nombre_al = st.text_input("Escribe tus Apellidos y Nombre:", key=f"name_al_{el['name']}")
                                    archivo_al = st.file_uploader("Selecciona tu archivo resuelto (PDF o Imagen):", type=["pdf","png","jpg","jpeg"], key=f"file_al_{el['name']}")
                                    
                                    if st.button("Enviar Tarea al Profesor", key=f"btn_send_{el['name']}"):
                                        if nombre_al and archivo_al:
                                            id_al = nombre_al.strip().replace(" ", "_")
                                            id_tar = el["name"].split(".")[0]
                                            
                                            ruta_file = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/{archivo_al.name}"
                                            ruta_json = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/nota.json"
                                            meta = {"nota": "Sin calificar", "feedback": "Pendiente de corrección.", "fecha": datetime.now().strftime("%d/%m/%Y")}
                                            
                                            if enviar_archivo(ruta_file, archivo_al.getvalue(), "Entrega") and enviar_archivo(ruta_json, json.dumps(meta).encode("utf-8"), "Meta"):
                                                st.success(f"✔️ ¡Hecho! El documento '{archivo_al.name}' se ha entregado correctamente.")
                                        else:
                                            st.warning("Por favor, rellena tu nombre y adjunta un archivo antes de enviar.")
                            else:
                                nombre_mat = el["name"].replace("_", " ").split(".")[0]
                                st.markdown(f"""
                                    <div class='recurso-bloque' style='border-left-color: #10b981; background-color: #f0fdf4;'>
                                        <span style='background-color:#10b981; color:white; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold;'>MATERIAL DE ESTUDIO</span>
                                        <h4 style='margin:5px 0; color:#14532d;'>📖 {nombre_mat}</h4>
                                        <p style='margin:0;'><a href='{el['download_url']}' target='_blank' style='color:#10b981; font-weight:bold;'>📥 Descargar Apuntes / Lecturas</a></p>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("Este bloque temático aún no tiene materiales cargados.")
        else:
            st.info("Esta asignatura no tiene carpetas o temas creados.")

# -------------------------------------------------------------------------
# VISTA B: CALENDARIO ESCOLAR REORGANIZADO EN MATRIZ VISUAL DE CUADRÍCULA
# -------------------------------------------------------------------------
elif navegacion == "📅 Calendario de Entregas":
    st.markdown("<h1 class='main-title'>📅 Agenda y Calendario Escolar</h1>", unsafe_allow_html=True)
    st.write("Cuadrícula visual con todas las actividades ordenadas por fecha de vencimiento.")
    st.write("---")
    
    todas_asig = listar_directorios()
    datos_calendario = []
    
    for asig in todas_asig:
        todos_temas = listar_directorios(asig)
        for tem in todos_temas:
            elementos_tem = api_git(f"{asig}/{tem}")
            if isinstance(elementos_tem, list):
                for e in elementos_tem:
                    if e["type"] == "file" and e["name"].startswith("TAREA_"):
                        partes = e["name"].split("_", 2)
                        f_limite = partes[1] if len(partes) > 1 else "Sin fecha"
                        t_nombre = partes[2].replace("_", " ").split(".")[0] if len(partes) > 2 else "Tarea"
                        
                        datos_calendario.append({
                            "📅 FECHA LÍMITE": f_limite,
                            "📚 ASIGNATURA": asig.replace('_', ' '),
                            "📋 ACTIVIDAD PENDIENTE": t_nombre
                        })
                        
    if datos_calendario:
        df_cal = pd.DataFrame(datos_calendario)
        # Mostrar en forma de cuadrícula de calendario indexada limpia para que no sea una simple línea de texto
        st.data_editor(df_cal, use_container_width=True, disabled=True)
    else:
        st.info("¡Estás al día! No hay actividades programadas en el calendario.")

# -------------------------------------------------------------------------
# VISTA C: PANEL DE CONTROL DOCENTE (PERMITE SUBIR IMAGEN DE PORTADA)
# -------------------------------------------------------------------------
elif navegacion == "👩‍🏫 Panel de Gestión Docente":
    st.markdown("<h1 class='main-title'>👩‍🏫 Despacho Docente</h1>", unsafe_allow_html=True)
    password = st.text_input("Código de Validación Docente:", type="password")
    
    if password == "profe2026":
        st.success("🔒 Sesión de administración iniciada con éxito.")
        st.write("---")
        
        menu_admin = st.selectbox("Selecciona el módulo de gestión:", [
            "🛠️ PUBLICAR TEMAS Y RECURSOS ACADÉMICOS",
            "📥 BANDEJA DE CORRECCIÓN (Ver Respuestas Alumnos)",
            "🏫 ALTA DE NUEVAS ASIGNATURAS CON PORTADA"
        ])
        
        if menu_admin == "🛠️ PUBLICAR TEMAS Y RECURSOS ACADÉMICOS":
            st.subheader("Carga y Publicación Correlativa")
            asig_list = listar_directorios()
            
            if asig_list:
                asig_sel_profe = st.selectbox("Selecciona la asignatura a gestionar:", asig_list)
                gestion_tema = st.radio("¿Qué deseas hacer?", ["Crear una nueva unidad temática", "Añadir recursos a una unidad ya existente"])
                
                if gestion_tema == "Crear una nueva unidad temática":
                    nombre_t = st.text_input("Nombre de la unidad (Ej: Tema 2 Derivadas):")
                    tema_ruta_final = nombre_t.strip().replace(" ", "_")
                else:
                    temas_ex = listar_directorios(asig_sel_profe)
                    tema_ruta_final = st.selectbox("Elige el tema:", temas_ex) if temas_ex else None
                    
                if tema_ruta_final:
                    tipo_archivo = st.radio("Clasificación del Recurso Escolar:", ["📖 Material Formativo", "📋 Tarea Evaluante"])
                    
                    if tipo_archivo == "📋 Tarea Evaluante":
                        f_limite_p = st.date_input("Fijar fecha de vencimiento:")
                        fichero_p = st.file_uploader("Adjunta el archivo del enunciado:", key="u_tarea_doc")
                        
                        if st.button("🚀 Publicar Tarea de forma Oficial") and fichero_p:
                            nombre_archivo_git = f"TAREA_{str(f_limite_p)}_{fichero_p.name.replace(' ', '_')}"
                            ruta_completa = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            
                            enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init")
                            if enviar_archivo(ruta_completa, fichero_p.getvalue(), "Carga"):
                                st.success("✔️ Tarea subida con éxito.")
                                st.rerun()
                    else:
                        fichero_p = st.file_uploader("Adjunta los apuntes o guías académicas:", key="u_mat_doc")
                        if st.button("🚀 Publicar Material Didáctico") and fichero_p:
                            nombre_archivo_git = fichero_p.name.replace(' ', '_')
                            ruta_completa = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            
                            enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init")
                            if enviar_archivo(ruta_completa, fichero_p.getvalue(), "Carga"):
                                st.success("✔️ Material subido con éxito.")
                                st.rerun()

        elif menu_admin == "📥 BANDEJA DE CORRECCIÓN (Ver Respuestas Alumnos)":
            st.subheader("Bandeja de Entrada de Ejercicios")
            asig_list = listar_directorios()
            
            if asig_list:
                asig_eval = st.selectbox("Selecciona Asignatura:", asig_list)
                entregas_raiz = api_git(f"Entregas_Globales/{asig_eval}")
                carpetas_tareas = [c["name"] for c in entregas_raiz if c["type"] == "dir"]
                
                if carpetas_tareas:
                    tarea_eval = st.selectbox("Selecciona la Tarea que deseas evaluar:", carpetas_tareas)
                    alumnos_lista = api_git(f"Entregas_Globales/{asig_eval}/{tarea_eval}")
                    id_alumnos = [a["name"] for a in alumnos_lista if a["type"] == "dir"]
                    
                    if id_alumnos:
                        alumno_eval = st.selectbox("Selecciona el alumno a calificar:", id_alumnos)
                        archivos_f = api_git(f"Entregas_Globales/{asig_eval}/{tarea_eval}/{alumno_eval}")
                        
                        url_doc, name_doc = "", ""
                        for f in archivos_f:
                            if f["name"] != "nota.json":
                                url_doc, name_doc = f["download_url"], f["name"]
                                
                        ruta_json_nota = f"Entregas_Globales/{asig_eval}/{tarea_eval}/{alumno_eval}/nota.json"
                        meta_n = api_git(ruta_json_nota)
                        nota_v, feedback_v = "Sin calificar", ""
                        
                        if isinstance(meta_n, dict) and "download_url" in meta_n:
                            res_d = requests.get(meta_n["download_url"])
                            if res_d.status_code == 200:
                                nota_v = res_d.json().get("nota", "Sin calificar")
                                feedback_v = res_d.json().get("feedback", "")
                                
                        st.markdown(f"""
                            <div style='background-color:#ffffff; border:1px solid #dadce0; padding:20px; border-radius:12px; margin-bottom:15px;'>
                                👤 <b>Estudiante:</b> {alumno_eval.replace('_',' ')}<br>
                                📄 <b>Archivo:</b> {name_doc.replace('_',' ')}<br><br>
                                <a href='{url_doc}' target='_blank'>📥 Descargar trabajo entregado</a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        input_n = st.text_input("Calificación final:", value=str(nota_v))
                        input_f = st.text_area("Comentarios pedagógicos (Feedback):", value=feedback_v)
                        
                        if st.button("💾 Publicar Nota en el Expediente"):
                            nueva_data = {"nota": input_n, "feedback": input_f, "fecha": datetime.now().strftime("%d/%m/%Y")}
                            if enviar_archivo(ruta_json_nota, json.dumps(nueva_data).encode("utf-8"), "Nota guardada"):
                                st.success("✔️ Calificación guardada.")
                                st.rerun()

        elif menu_admin == "🏫 ALTA DE NUEVAS ASIGNATURAS CON PORTADA":
            st.subheader("Alta de Clases y Configuración Estética")
            nueva_asig = st.text_input("Nombre de la nueva Asignatura (Ej: Historia de España):")
            
            # ¡NUEVA FUNCIÓN VISUAL! Permitir a la administradora subir la imagen que quiera para el tablón
            imagen_portada = st.file_uploader("Sube una imagen de portada para esta asignatura (.png o .jpg):", type=["png", "jpg", "jpeg"], key="u_portada_main")
            
            if st.button("Consolidar Asignatura en el Aula Virtual"):
                if nueva_asig and imagen_portada:
                    clean_asig = nueva_asig.strip().replace(" ", "_")
                    extension = imagen_portada.name.split(".")[-1]
                    ruta_img = f"{clean_asig}/portada_curso.{extension}"
                    
                    if enviar_archivo(f"{clean_asig}/.gitkeep", b"", "Alta") and enviar_archivo(ruta_img, imagen_portada.getvalue(), "Portada"):
                        st.success(f"✔️ ¡Éxito! La asignatura '{nueva_asig}' ha sido creada y su imagen de portada se configuró correctamente.")
                        st.rerun()
                else:
                    st.warning("Debes escribir el nombre y subir una imagen de portada.")
