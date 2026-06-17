import streamlit as st
import requests
import base64
import json
from datetime import datetime

# =========================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS CSS PROFESIONALES
# =========================================================================
st.set_page_config(page_title="Aula Virtual - Colegio", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    
    /* Tarjetas de Asignaturas */
    .subject-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 6px solid #4f46e5;
        text-align: center;
        margin-bottom: 20px;
    }
    .subject-title { color: #1e1b4b; font-size: 20px; font-weight: bold; margin-bottom: 10px; }
    
    /* Tablón de Anuncios */
    .announcement-box {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
    }
    
    /* Cajas de Recursos y Estado */
    .resource-box {
        background-color: #ffffff;
        padding: 12px 18px;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        margin-bottom: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .feedback-card {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        padding: 15px;
        border-radius: 8px;
        margin-top: 10px;
    }
    .task-submitted {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-left: 5px solid #f59e0b;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión con los Secrets de Streamlit
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "MATEMATICAS"
TOKEN_GITHUB = st.secrets["TOKEN_GITHUB"]

# =========================================================================
# 2. CORE: FUNCIONES DE COMUNICACIÓN CON LA API DE GITHUB
# =========================================================================
def peticion_github(ruta="", metodo="GET", datos=None):
    url = f"https://api.github.com/repos/{USUARIO_GIT}/{REPOSITORIO_GIT}/contents/{ruta}?ref={RAMA}"
    headers = {
        "Authorization": f"token {TOKEN_GITHUB}",
        "Accept": "application/vnd.github.v3+json"
    }
    if metodo == "GET":
        r = requests.get(url, headers=headers)
        return r.json() if r.status_code == 200 else []
    elif metodo == "PUT":
        url_put = f"https://api.github.com/repos/{USUARIO_GIT}/{REPOSITORIO_GIT}/contents/{ruta}"
        r = requests.put(url_put, headers=headers, json=datos)
        return r.status_code in [200, 201]
    return []

def listar_carpetas_limpias(ruta=""):
    elementos = peticion_github(ruta)
    if isinstance(elementos, list):
        return [item["name"] for item in elementos if item["type"] == "dir" and item["name"] not in ["Tareas_Alumnos", "Anuncios_Sistema"]]
    return []

def publicar_archivo(ruta_destino, contenido_bytes, mensaje_commit):
    contenido_base64 = base64.b64encode(contenido_bytes).decode("utf-8")
    datos = {"message": mensaje_commit, "content": contenido_base64, "branch": RAMA}
    chequeo = peticion_github(ruta_destino)
    if isinstance(chequeo, dict) and "sha" in chequeo:
        datos["sha"] = chequeo["sha"]
    return peticion_github(ruta_destino, metodo="PUT", datos=datos)

# =========================================================================
# 3. INTERFAZ: MENÚ DE NAVEGACIÓN PRINCIPAL
# =========================================================================
st.title("🏫 Centro Educativo Digital - Aula Virtual")

menu_principal = st.sidebar.radio("Navegación del Colegio", [
    "🏠 Inicio y Tablón de Anuncios",
    "📚 Mis Asignaturas",
    "📤 Buzón y Notas de Tareas",
    "👩‍🏫 Despacho de Profesora (Gestión)"
])

# -------------------------------------------------------------------------
# PÁGINA A: INICIO Y TABLÓN DE ANUNCIOS
# -------------------------------------------------------------------------
if menu_principal == "🏠 Inicio y Tablón de Anuncios":
    st.markdown("<h2 style='color:#1e3a8a;'>📣 Tablón de Anuncios del Curso</h2>", unsafe_allow_html=True)
    
    anuncios = peticion_github("Anuncios_Sistema")
    if anuncios and isinstance(anuncios, list):
        archivos_txt = [f for f in anuncios if f["type"] == "file" and f["name"].endswith(".txt")]
        archivos_txt.reverse() 
        
        for archivo in archivos_txt:
            contenido_res = requests.get(archivo["download_url"])
            if contenido_res.status_code == 200:
                texto_anuncio = contenido_res.text
                fecha_anuncio = archivo["name"].split("_")[0]
                titulo_anuncio = archivo["name"].replace(".txt", "").split("_", 1)[1].replace("_", " ")
                
                st.markdown(f"""
                    <div class='announcement-box'>
                        <h4 style='margin:0; color:#1d4ed8;'>📌 {titulo_anuncio}</h4>
                        <small style='color:#6b7280;'>Publicado el: {fecha_anuncio}</small>
                        <p style='margin-top:10px; color:#374151;'>{texto_anuncio}</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No hay anuncios publicados en este momento.")

# -------------------------------------------------------------------------
# PÁGINA B: EXPLORADOR DE ASIGNATURAS
# -------------------------------------------------------------------------
elif menu_principal == "📚 Mis Asignaturas":
    st.markdown("<h2 style='color:#1e3a8a;'>📚 Tus Asignaturas Disponibles</h2>", unsafe_allow_html=True)
    asignaturas = listar_carpetas_limpias()
    
    if asignaturas:
        if "asignatura_activa" not in st.session_state:
            st.session_state["asignatura_activa"] = None
            
        cols = st.columns(3)
        for i, asigna in enumerate(asignaturas):
            with cols[i % 3]:
                st.markdown(f"<div class='subject-card'><div style='font-size: 40px;'>📘</div><div class='subject-title'>{asigna}</div></div>", unsafe_allow_html=True)
                if st.button(f"Entrar a {asigna}", key=f"btn_{asigna}"):
                    st.session_state["asignatura_activa"] = asigna
                    
        if st.session_state["asignatura_activa"]:
            asigna_sel = st.session_state["asignatura_activa"]
            st.write("---")
            st.markdown(f"<h3 style='color:#4f46e5;'>📂 Contenidos de: {asigna_sel}</h3>", unsafe_allow_html=True)
            
            temas = peticion_github(asigna_sel)
            subcarpetas_temas = [t["name"] for t in temas if t["type"] == "dir"]
            archivos_raiz = [t for t in temas if t["type"] == "file" and t["name"] != ".gitkeep"]
            
            if subcarpetas_temas:
                tema_sel = st.selectbox("Seleccionar Bloque o Tema:", subcarpetas_temas)
                contenido_tema = peticion_github(f"{asigna_sel}/{tema_sel}")
                
                archivos_tema = [f for f in contenido_tema if f["type"] == "file" and f["name"] != ".gitkeep"]
                if archivos_tema:
                    for arch in archivos_tema:
                        st.markdown(f"<div class='resource-box'><span>📝 <b>{arch['name']}</b></span><a href='{arch['download_url']}' target='_blank' style='background-color:#4f46e5; color:white; text-decoration:none; padding:6px 12px; border-radius:4px; font-size:13px;'>📥 Descargar</a></div>", unsafe_allow_html=True)
                else:
                    st.info("Este tema aún no contiene archivos.")
            
            if archivos_raiz:
                st.write("📎 **Documentos Generales:**")
                for arch in archivos_raiz:
                    st.markdown(f"<div class='resource-box'><span>📋 {arch['name']}</span><a href='{arch['download_url']}' target='_blank' style='background-color:#4f46e5; color:white; text-decoration:none; padding:6px 12px; border-radius:4px; font-size:13px;'>📥 Descargar</a></div>", unsafe_allow_html=True)
    else:
        st.info("No hay asignaturas creadas todavía.")

# -------------------------------------------------------------------------
# PÁGINA C: BUZÓN DE ENTREGAS Y CONSULTA DE NOTAS (ALUMNOS)
# -------------------------------------------------------------------------
elif menu_principal == "📤 Buzón y Notas de Tareas":
    st.markdown("<h2 style='color:#1e3a8a;'>📤 Buzón de Actividades y Calificaciones</h2>", unsafe_allow_html=True)
    
    opcion_alumno = st.radio("¿Qué deseas hacer?", ["Enviar una nueva tarea", "Consultar mis notas y feedback"])
    
    if opcion_alumno == "Enviar una nueva tarea":
        with st.form("form_entrega_colegio", clear_on_submit=True):
            col_al1, col_al2 = st.columns(2)
            with col_al1:
                nombre_estudiante = st.text_input("Nombre completo del Alumno:")
            with col_al2:
                codigo_tarea = st.text_input("Nombre/Código de la Tarea:")
                
            archivo_adjunto = st.file_uploader("Documento de solución (PDF o Imagen):", type=["pdf", "png", "jpg", "jpeg", "docx"])
            enviar_tarea_btn = st.form_submit_button("Subir Tarea Oficial")
            
            if enviar_tarea_btn:
                if nombre_estudiante and codigo_tarea and archivo_adjunto:
                    marca_tiempo = datetime.now().strftime("%Y-%m-%d_%H-%M")
                    estudiante_id = nombre_estudiante.strip().replace(" ", "_")
                    tarea_id = codigo_tarea.strip().replace(" ", "_")
                    
                    # Subimos el archivo del alumno
                    ruta_final_entrega = f"Tareas_Alumnos/{tarea_id}/{estudiante_id}/{estudiante_id}_{archivo_adjunto.name}"
                    
                    # Creamos una plantilla de nota vacía en JSON para que la profe la rellene luego
                    ruta_json_nota = f"Tareas_Alumnos/{tarea_id}/{estudiante_id}/calificacion.json"
                    datos_nota_inicial = {"nota": "Sin calificar", "feedback": "Pendiente de revisión por la profesora.", "fecha_entrega": marca_tiempo}
                    
                    with st.spinner("Registrando entrega..."):
                        subir_archivo_a_git = publicar_archivo(ruta_final_entrega, archivo_adjunto.getvalue(), f"Entrega de {nombre_estudiante}")
                        subir_json_a_git = publicar_archivo(ruta_json_nota, json.dumps(datos_nota_inicial, indent=4).encode("utf-8"), "Registro de nota inicial")
                        
                        if subir_archivo_a_git and subir_json_a_git:
                            st.success(f"🎉 ¡Perfecto, {nombre_estudiante}! Tu tarea '{codigo_tarea}' ha sido entregada. Ya está en la bandeja de la profesora.")
                else:
                    st.warning("Completa todos los datos antes de realizar el envío.")
                    
    elif opcion_alumno == "Consultar mis notas y feedback":
        st.subheader("📋 Consulta tu Boletín Personal")
        busqueda_nombre = st.text_input("Introduce tu Nombre Completo (exactamente como lo escribiste al entregar):")
        
        if busqueda_nombre:
            id_busqueda = busqueda_nombre.strip().replace(" ", "_")
            tareas_sistema = peticion_github("Tareas_Alumnos")
            carpetas_tareas = [t["name"] for t in tareas_sistema if t["type"] == "dir"]
            
            encontrado = False
            for tarea in carpetas_tareas:
                # Comprobamos si este alumno tiene una carpeta dentro de esta tarea
                ruta_alumno_tarea = f"Tareas_Alumnos/{tarea}/{id_busqueda}/calificacion.json"
                chequeo_nota = peticion_github(ruta_alumno_tarea)
                
                if isinstance(chequeo_nota, dict) and "download_url" in chequeo_nota:
                    encontrado = True
                    res_json = requests.get(chequeo_nota["download_url"])
                    if res_json.status_code == 200:
                        datos_evaluacion = res_json.json()
                        
                        # Mostramos la calificación en pantalla de forma bonita
                        color_nota = "#b45309" if datos_evaluacion['nota'] == "Sin calificar" else "#047857"
                        st.markdown(f"""
                            <div class='feedback-card'>
                                <h4 style='margin:0; color:#1e3a8a;'>📝 Actividad: {tarea.replace('_', ' ')}</h4>
                                <p style='margin: 5px 0;'><b>Estado / Calificación:</b> <span style='color:{color_nota}; font-weight:bold;'>{datos_evaluacion['nota']}</span></p>
                                <p style='margin: 5px 0; color:#374151;'><b>Comentarios pedagógicos (Feedback):</b><br><i>{datos_evaluacion['feedback']}</i></p>
                            </div>
                        """, unsafe_allow_html=True)
            if not encontrado:
                st.info("No se han encontrado registros ni entregas para ese nombre.")

# -------------------------------------------------------------------------
# PÁGINA D: DESPACHO DE LA PROFESORA (EVALUACIÓN INTEGRAL)
# -------------------------------------------------------------------------
elif menu_principal == "👩‍🏫 Despacho de Profesora (Gestión)":
    st.markdown("<h2 style='color:#1e3a8a;'>👩‍🏫 Panel de Control Técnico y Docente</h2>", unsafe_allow_html=True)
    clave = st.text_input("Introduce la contraseña del despacho:", type="password")
    
    if clave == "profe2026":
        st.success("Acceso autorizado. Buenas tardes, profesora Elena.")
        st.write("---")
        
        herramienta = st.selectbox("Selecciona qué panel de control deseas abrir:", [
            "📥 CUADERNO DE NOTAS (Corregir y enviar Feedback)",
            "📢 PUBLICAR NUEVO ANUNCIO",
            "🛠️ GESTIONAR ASIGNATURAS Y TEMAS",
            "📁 SUBIR MATERIAL DIDÁCTICO"
        ])
        
        # -----------------------------------------------------------------
        # GESTIÓN 1: CUADERNO DE NOTAS (CORRECCIÓN Y REVISIÓN)
        # -----------------------------------------------------------------
        if herramienta == "📥 CUADERNO DE NOTAS (Corregir y enviar Feedback)":
            st.subheader("📊 Calificación y Retroalimentación de Entregas")
            
            tareas_existentes = peticion_github("Tareas_Alumnos")
            carpetas_de_actividades = [t["name"] for t in tareas_existentes if t["type"] == "dir"]
            
            if carpetas_de_actividades:
                actividad_sel = st.selectbox("Seleccionar Tarea a evaluar:", carpetas_de_actividades)
                
                # Listar alumnos que han entregado esta tarea
                alumnos_carpetas = peticion_github(f"Tareas_Alumnos/{actividad_sel}")
                lista_alumnos = [a["name"] for a in alumnos_carpetas if a["type"] == "dir"]
                
                if lista_alumnos:
                    alumno_sel = st.selectbox("Seleccionar Alumno a Corregir:", lista_alumnos)
                    
                    # Leer ficheros del alumno seleccionado
                    archivos_alumno = peticion_github(f"Tareas_Alumnos/{actividad_sel}/{alumno_sel}")
                    
                    # Separar el documento entregado del JSON de notas
                    archivo_entrega_url = ""
                    nombre_archivo_entrega = ""
                    for arch in archivos_alumno:
                        if arch["name"] != "calificacion.json" and arch["type"] == "file":
                            archivo_entrega_url = arch["download_url"]
                            nombre_archivo_entrega = arch["name"]
                    
                    # Cargar estado actual del JSON para ver si ya tiene nota guardada
                    ruta_json = f"Tareas_Alumnos/{actividad_sel}/{alumno_sel}/calificacion.json"
                    json_meta = peticion_github(ruta_json)
                    
                    nota_actual = "Sin calificar"
                    feedback_actual = ""
                    if isinstance(json_meta, dict) and "download_url" in json_meta:
                        res_json_descarga = requests.get(json_meta["download_url"])
                        if res_json_descarga.status_code == 200:
                            dict_nota = res_json_descarga.json()
                            nota_actual = dict_nota.get("nota", "Sin calificar")
                            feedback_actual = dict_nota.get("feedback", "")
                    
                    # --- DISEÑO DEL EVALUADOR ---
                    st.markdown(f"""
                        <div class='task-submitted'>
                            <h4>👤 Alumno: {alumno_sel.replace('_', ' ')}</h4>
                            <p><b>Archivo enviado:</b> {nombre_archivo_entrega.replace('_', ' ')}</p>
                            <a href='{archivo_entrega_url}' target='_blank'><button style='background-color:#4f46e5; color:white; border:none; padding:8px 15px; border-radius:5px; cursor:pointer; font-weight:bold;'>📥 Descargar y Revisar Trabajo</button></a>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.write("### ✍️ Formulario de Calificación")
                    col_n1, col_n2 = st.columns([1, 3])
                    with col_n1:
                        nueva_nota = st.text_input("Calificación (Ej: 8.5/10 o Sobresaliente):", value=str(nota_actual))
                    with col_n2:
                        nuevo_feedback = st.text_area("Comentarios pedagógicos y Feedback para el alumno:", value=feedback_actual)
                        
                    if st.button("💾 Guardar y Publicar Calificación"):
                        datos_actualizados = {
                            "nota": nueva_nota.strip(),
                            "feedback": nuevo_feedback.strip(),
                            "fecha_correccion": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        with st.spinner("Subiendo nota al expediente digital..."):
                            if publicar_archivo(ruta_json, json.dumps(datos_actualizados, indent=4).encode("utf-8"), f"Calificación de {alumno_sel}"):
                                st.success(f"¡Nota guardada! El alumno {alumno_sel.replace('_', ' ')} ya puede ver su feedback.")
                                st.rerun()
                else:
                    st.warning("No hay subcarpetas de alumnos en este bloque.")
            else:
                st.info("Nadie ha enviado trabajos para corregir todavía.")
                
        # -----------------------------------------------------------------
        # GESTIÓN 2: PUBLICAR ANUNCIOS
        # -----------------------------------------------------------------
        elif herramienta == "📢 PUBLICAR NUEVO ANUNCIO":
            st.subheader("Crear Comunicado Oficial")
            titulo_comunicado = st.text_input("Título del Anuncio:")
            cuerpo_comunicado = st.text_area("Mensaje:")
            
            if st.button("Difundir Anuncio") and titulo_comunicado and cuerpo_comunicado:
                fecha_clean = datetime.now().strftime("%d-%m-%Y")
                titulo_clean = titulo_comunicado.strip().replace(" ", "_")
                if publicar_archivo(f"Anuncios_Sistema/{fecha_clean}_{titulo_clean}.txt", cuerpo_comunicado.encode("utf-8"), "Aviso escolar"):
                    st.success("Anuncio colgado.")
                    st.rerun()
                    
        # -----------------------------------------------------------------
        # GESTIÓN 3: CREAR ASIGNATURAS Y TEMAS
        # -----------------------------------------------------------------
        elif herramienta == "🛠️ GESTIONAR ASIGNATURAS Y TEMAS":
            st.subheader("Diseño Curricular")
            tipo_creacion = st.radio("¿Qué deseas crear?", ["Nueva Asignatura (Carpeta Raíz)", "Nuevo Tema (Subcarpeta)"])
            
            if tipo_creacion == "Nueva Asignatura (Carpeta Raíz)":
                nombre_asig = st.text_input("Nombre de la Materia:")
                if st.button("Crear Asignatura") and nombre_asig:
                    if publicar_archivo(f"{nombre_asig.strip()}/.gitkeep", b"", "Crear asignatura"):
                        st.success("Asignatura creada.")
                        st.rerun()
            else:
                lista_asig = listar_carpetas_limpias()
                if lista_asig:
                    asig_padre = st.selectbox("¿A qué asignatura pertenece?", lista_asig)
                    nombre_nuevo_tema = st.text_input("Nombre del Tema:")
                    if st.button("Dar de Alta Tema") and nombre_nuevo_tema:
                        if publicar_archivo(f"{asig_padre}/{nombre_nuevo_tema.strip()}/.gitkeep", b"", "Crear tema"):
                            st.success("Tema integrado.")
                            st.rerun()
                else:
                    st.warning("No hay asignaturas.")
                    
        # -----------------------------------------------------------------
        # GESTIÓN 4: SUBIR ARCHIVOS PEDAGÓGICOS
        # -----------------------------------------------------------------
        elif herramienta == "📁 SUBIR MATERIAL DIDÁCTICO":
            st.subheader("Carga de Material Docente")
            lista_asig = listar_carpetas_limpias()
            
            if lista_asig:
                asig_destino = st.selectbox("Selecciona Asignatura:", lista_asig)
                elementos_asig = peticion_github(asig_destino)
                temas_destino = [t["name"] for t in elementos_asig if t["type"] == "dir"]
                
                if temas_destino:
                    tema_final = st.selectbox("Selecciona el Tema:", ["(Raíz de la asignatura)"] + temas_destino)
                    ruta_carga = asig_destino if tema_final == "(Raíz de la asignatura)" else f"{asig_destino}/{tema_final}"
                else:
                    ruta_carga = asig_destino
                    
                documento_profe = st.file_uploader("Elige el documento de tu PC:")
                if st.button("Subir Material") and documento_profe:
                    if publicar_archivo(f"{ruta_carga}/{documento_profe.name}", documento_profe.getvalue(), "Subida de material"):
                        st.success("Documento publicado.")
                        st.rerun()
