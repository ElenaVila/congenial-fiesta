import streamlit as st
import requests
import base64
import json
from datetime import datetime

# =========================================================================
# 1. CONFIGURACIÓN VISUAL Y HOJA DE ESTILOS (GOOGLE CLASSROOM DESIGN)
# =========================================================================
st.set_page_config(page_title="Google Classroom Real-Time", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    
    /* Cuadrícula de Asignaturas de la Página Principal */
    .subject-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 20px;
        margin-top: 20px;
    }
    
    /* Tarjeta Grande de Asignatura */
    .classroom-card {
        background: linear-gradient(135px, #1a73e8, #1557b0);
        color: white;
        padding: 24px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    
    /* Filas de materiales y tareas dentro de los temas */
    .resource-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 12px 16px;
        border-bottom: 1px solid #e8eaed;
        background-color: #ffffff;
    }
    .resource-row:hover { background-color: #f8f9fa; }
    
    /* Tarjetas del Calendario */
    .calendar-item {
        background-color: #e8f0fe;
        border-left: 4px solid #1a73e8;
        padding: 10px 15px;
        border-radius: 4px;
        margin-bottom: 8px;
        color: #1967d2;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión Segura con GitHub (Secrets de Streamlit)
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "MATEMATICAS"
TOKEN_GITHUB = st.secrets["TOKEN_GITHUB"]

# =========================================================================
# 2. CORE: FUNCIONES DE CONEXIÓN CON GITHUB API
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

# Inicializar Estados de la app
if "clase_seleccionada" not in st.session_state:
    st.session_state["clase_seleccionada"] = None

# =========================================================================
# 3. INTERFAZ PRINCIPAL: MURO DE ASIGNATURAS / ENTRADA PRINCIPAL
# =========================================================================
if st.session_state["clase_seleccionada"] is None:
    st.title("🏫 Mis Clases de Google Classroom")
    st.write("Selecciona una asignatura para acceder al tablón de anuncios, contenidos de clase y tareas.")
    
    asignaturas = listar_directorios()
    
    if asignaturas:
        # Mostramos las asignaturas en formato de cuadrícula grande
        col1, col2, col3 = st.columns(3)
        for i, asig in enumerate(asignaturas):
            col_actual = [col1, col2, col3][i % 3]
            with col_actual:
                st.markdown(f"""
                    <div class='classroom-card'>
                        <div>
                            <h3 style='margin:0; font-size:22px;'>📐 {asig.replace('_', ' ')}</h3>
                            <p style='margin:5px 0 0 0; font-size:14px; opacity:0.8;'>Curso Actual — Elena Vila</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                if st.button(f"Entrar a la clase", key=f"open_{asig}"):
                    st.session_state["clase_seleccionada"] = asig
                    st.rerun()
    else:
        st.info("No hay asignaturas dadas de alta en el centro educativo en este momento.")
        
# =========================================================================
# 4. INTERFAZ INTERIOR: DENTRO DE UNA ASIGNATURA SELECCIONADA
# =========================================================================
else:
    asignatura_activa = st.session_state["clase_seleccionada"]
    
    # Botón para volver al tablón general de asignaturas
    if st.button("⬅️ Volver a mis Clases"):
        st.session_state["clase_seleccionada"] = None
        st.rerun()
        
    st.markdown(f"""
        <div style='background: linear-gradient(135px, #1e3a8a, #3b82f6); color: white; padding: 25px; border-radius: 8px; margin-bottom: 20px;'>
            <h1 style='margin:0;'>📘 Asignatura: {asignatura_activa.replace('_', ' ')}</h1>
            <p style='margin:5px 0 0 0; opacity:0.9;'>Profesorado: Elena Vila | Plan de Estudios Correlativo</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Pestañas oficiales interiores estilo Classroom
    pestana_trabajo, pestana_agenda, pestana_notas, pestana_profesora = st.tabs([
        "📚 Trabajo de Clase (Temas correlativos)", 
        "📅 Calendario de la Asignatura", 
        "📋 Mis Calificaciones",
        "👩‍🏫 Panel de Gestión (Elena)"
    ])

    # -------------------------------------------------------------------------
    # PESTAÑA 1: TRABAJO DE CLASE - TEMAS CORRELATIVOS DESPLEGABLES
    # -------------------------------------------------------------------------
    with pestana_trabajo:
        st.write("")
        temas = listar_directorios(asignatura_activa)
        
        if temas:
            st.info("Haz clic sobre cada tema para desplegar sus recursos didácticos y buzones de entrega.")
            # Listado correlativo uno debajo de otro
            for tema in temas:
                with st.expander(f"📁 {tema.replace('_', ' ')}", expanded=False):
                    elementos = api_git(f"{asignatura_activa}/{tema}")
                    archivos = [e for e in elementos if e["type"] == "file" and e["name"] != ".gitkeep"]
                    
                    if archivos:
                        for el in archivos:
                            es_tarea = el["name"].startswith("TAREA_")
                            
                            if es_tarea:
                                partes = el["name"].split("_", 2)
                                f_limite = partes[1] if len(partes) > 1 else "Sin fecha"
                                t_nombre = partes[2].replace("_", " ").split(".")[0] if len(partes) > 2 else "Tarea"
                                
                                st.markdown(f"""
                                    <div class='resource-row' style='border-left: 4px solid #ef4444;'>
                                        <div>
                                            <span>📋</span> <b>{t_nombre}</b> 
                                            <span style='font-size:11px; background-color:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:4px; margin-left:10px;'>Fecha Límite: {f_limite}</span>
                                        </div>
                                        <div>
                                            <a href='{el['download_url']}' target='_blank' style='color:#1a73e8; text-decoration:none; font-weight:bold;'>📥 Descargar Enunciado</a>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Subformulario de entregas integrado dentro del tema correlativo
                                with st.form(f"entrega_{el['name']}", clear_on_submit=True):
                                    st.write(f"📝 **Formulario de entrega para:** {t_nombre}")
                                    alumno = st.text_input("Apellidos y Nombre completo:")
                                    archivo_adjunto = st.file_uploader("Adjunta tu trabajo (PDF o Imagen):", type=["pdf","png","jpg","jpeg"])
                                    
                                    if st.form_submit_button("Enviar Tarea"):
                                        if alumno and archivo_adjunto:
                                            id_al = alumno.strip().replace(" ", "_")
                                            id_tar = el["name"].split(".")[0]
                                            
                                            ruta_file = f"Entregas_Globales/{asignatura_activa}/{id_tar}/{id_al}/{archivo_adjunto.name}"
                                            ruta_json = f"Entregas_Globales/{asignatura_activa}/{id_tar}/{id_al}/nota.json"
                                            meta_inicial = {"nota": "Sin calificar", "feedback": "Pendiente de corrección.", "fecha": datetime.now().strftime("%d/%m/%Y")}
                                            
                                            if enviar_archivo(ruta_file, archivo_adjunto.getvalue(), "Entrega") and enviar_archivo(ruta_json, json.dumps(meta_inicial).encode("utf-8"), "Meta"):
                                                st.success(f"🎉 ¡Éxito! Tu documento '{archivo_adjunto.name}' ha sido enviado y guardado correctamente en la carpeta de la profesora.")
                                        else:
                                            st.warning("Por favor, rellena tu nombre y adjunta tu archivo.")
                            else:
                                # Es un material docente regular
                                nombre_mat = el["name"].replace("_", " ").split(".")[0]
                                st.markdown(f"""
                                    <div class='resource-row' style='border-left: 4px solid #10b981;'>
                                        <div><span>📖</span> <b>{nombre_mat}</b></div>
                                        <div><a href='{el['download_url']}' target='_blank' style='color:#1a73e8; text-decoration:none; font-weight:bold;'>📥 Descargar Material</a></div>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.write("<i style='color:#70757a; padding-left:10px;'>Este tema aún no contiene archivos cargados.</i>", unsafe_allow_html=True)
        else:
            st.info("No se han configurado bloques de estudio dentro de esta asignatura.")

    # -------------------------------------------------------------------------
    # PESTAÑA 2: CALENDARIO AUTOMÁTICO DE ENTREGAS
    # -------------------------------------------------------------------------
    with pestana_agenda:
        st.write("")
        st.subheader("📅 Cronograma Automatizado")
        
        temas_agenda = listar_directorios(asignatura_activa)
        hubo_tareas = False
        
        for t in temas_agenda:
            elementos_t = api_git(f"{asignatura_activa}/{t}")
            if isinstance(elementos_t, list):
                for el in elementos_t:
                    if el["type"] == "file" and el["name"].startswith("TAREA_"):
                        hubo_tareas = True
                        partes = el["name"].split("_", 2)
                        f_limite = partes[1] if len(partes) > 1 else "Sin fecha"
                        t_nombre = partes[2].replace("_", " ").split(".")[0] if len(partes) > 2 else "Tarea"
                        
                        st.markdown(f"""
                            <div class='calendar-item'>
                                <b>⏰ Entrega programada para el {f_limite}:</b> Tarea Evaluativa — <i>{t_nombre}</i> (U.D: {t.replace('_',' ')})
                            </div>
                        """, unsafe_allow_html=True)
                        
        if not hubo_tareas:
            st.info("¡Todo al día! No se registran entregas obligatorias próximas para esta asignatura.")

    # -------------------------------------------------------------------------
    # PESTAÑA 3: EXPEDIENTE PRIVADO DEL ESTUDIANTE
    # -------------------------------------------------------------------------
    with pestana_notas:
        st.write("")
        st.subheader("📋 Registro de Calificaciones Personales")
        alumno_buscar = st.text_input("Escribe tus Apellidos y Nombre exactos:")
        
        if alumno_buscar:
            id_busca = alumno_buscar.strip().replace(" ", "_")
            entregas_raiz = api_git(f"Entregas_Globales/{asignatura_activa}")
            
            encontrado = False
            if isinstance(entregas_raiz, list):
                for carp_t in entregas_raiz:
                    ruta_nota = f"Entregas_Globales/{asignatura_activa}/{carp_t['name']}/{id_busca}/nota.json"
                    meta_js = api_git(ruta_nota)
                    
                    if isinstance(meta_js, dict) and "download_url" in meta_js:
                        encontrado = True
                        res_js = requests.get(meta_js["download_url"])
                        if res_js.status_code == 200:
                            data_nota = res_js.json()
                            nombre_t_bonito = carp_t["name"].split("_", 2)[-1].replace("_", " ") if "TAREA_" in carp_t["name"] else carp_t["name"].replace("_"," ")
                            
                            st.markdown(f"""
                                <div style='background-color:#f0fdf4; border:1px solid #bbf7d0; padding:15px; border-radius:8px; margin-bottom:10px; color:#166534;'>
                                    <h4 style='margin:0;'>📊 Tarea: {nombre_t_bonito}</h4>
                                    <p style='margin:5px 0;'><b>Calificación asignada:</b> {data_nota['nota']}</p>
                                    <p style='margin:0;'><b>Feedback pedagógico:</b> {data_nota['feedback']}</p>
                                </div>
                            """, unsafe_allow_html=True)
            if not encontrado:
                st.info("No se han localizado notas publicadas para los datos proporcionados.")

    # -------------------------------------------------------------------------
    # PESTAÑA 4: DESPACHO GESTIÓN DE LA PROFESORA
    # -------------------------------------------------------------------------
    with pestana_profesora:
        st.write("")
        clave = st.text_input("Introduce clave del Despacho Docente:", type="password")
        
        if clave == "profe2026":
            st.success("Acceso autorizado. Panel docente activado.")
            st.write("---")
            
            herramienta = st.selectbox("Elige la gestión que deseas tramitar:", [
                "🛠️ PUBLICAR NUEVO TEMA O AGREGAR CONTENIDOS",
                "📥 VER RESPUESTAS Y CORREGIR TAREAS",
                "🏫 CREAR NUEVA ASIGNATURA GENERAL"
            ])
            
            # --- 1. AÑADIR CONTENIDOS Y CREAR CARPETAS ---
            if herramienta == "🛠️ PUBLICAR NUEVO TEMA O AGREGAR CONTENIDOS":
                st.subheader("Carga y Estructuración de Unidades Curriculares")
                
                estado_tema = st.radio("¿Qué deseas realizar?", ["Configurar una Nueva Unidad/Tema desde Cero", "Añadir archivos a un Tema existente"])
                
                if estado_tema == "Configurar una Nueva Unidad/Tema desde Cero":
                    nombre_nuevo = st.text_input("Escribe el nombre del Tema (Ej: Tema 4 Vectores):")
                    tema_ruta_final = nombre_nuevo.strip().replace(" ", "_")
                else:
                    temas_actuales = listar_directorios(asignatura_activa)
                    if temas_actuales:
                        tema_ruta_final = st.selectbox("Selecciona la carpeta del tema:", temas_actuales)
                    else:
                        st.warning("No existen temas creados previamente en esta asignatura.")
                        tema_ruta_final = None
                        
                if tema_ruta_final:
                    st.markdown("##### ⚙️ Configuración y Tipo de Visibilidad")
                    visibilidad = st.checkbox("Visibilidad Activa (Publicar y hacer visible para todos los alumnos en este instante)", value=True)
                    
                    tipo_rec = st.radio("Clasificación del Archivo:", ["📖 Material de Lectura/Apuntes", "📋 Tarea Evualuable Obligatoria"])
                    
                    if tipo_rec == "📋 Tarea Evualuable Obligatoria":
                        fecha_limite = st.date_input("Establecer Fecha de Vencimiento para el calendario:")
                        fichero = st.file_uploader("Carga las instrucciones o guía de la Tarea:")
                        
                        if st.button("🚀 Publicar Tarea en el Aula Virtual") and fichero:
                            nombre_git = f"TAREA_{str(fecha_limite)}_{fichero.name.replace(' ', '_')}"
                            ruta_git = f"{asignatura_activa}/{tema_ruta_final}/{nombre_git}"
                            
                            with st.spinner("Creando recursos en el servidor..."):
                                enviar_archivo(f"{asignatura_activa}/{tema_ruta_final}/.gitkeep", b"", "Init")
                                if enviar_archivo(ruta_git, fichero.getvalue(), "Carga de Tarea"):
                                    st.success(f"✔️ ¡Confirmado! La carpeta/tema '{tema_ruta_final}' ha sido actualizada. Archivo de tarea '{fichero.name}' subido con éxito y fecha fijada en el calendario.")
                                    st.rerun()
                    else:
                        fichero = st.file_uploader("Elige el documento didáctico (PDF, Word, Imagen):")
                        if st.button("🚀 Publicar Material Docente") and fichero:
                            nombre_git = fichero.name.replace(' ', '_')
                            ruta_git = f"{asignatura_activa}/{tema_ruta_final}/{nombre_git}"
                            
                            with st.spinner("Subiendo material didáctico..."):
                                enviar_archivo(f"{asignatura_activa}/{tema_ruta_final}/.gitkeep", b"", "Init")
                                if enviar_archivo(ruta_git, fichero.getvalue(), "Carga de Apuntes"):
                                    st.success(f"✔️ ¡Confirmado! Carpeta de tema actualizada con éxito. Material formativo '{fichero.name}' publicado e indexado en el tablón del alumnado.")
                                    st.rerun()

            # --- 2. RESPUESTAS DE ALUMNOS INTEGRADAS ---
            elif herramienta == "📥 VER RESPUESTAS Y CORREGIR TAREAS":
                st.subheader("Bandeja de Respuestas y Calificaciones")
                
                # Buscamos qué tareas globales registran datos
                entregas_existentes = api_git(f"Entregas_Globales/{asignatura_activa}")
                carpetas_tareas = [c["name"] for c in entregas_existentes if c["type"] == "dir"]
                
                if carpetas_tareas:
                    tarea_elegida = st.selectbox("Selecciona la Tarea para auditar las respuestas de los alumnos:", carpetas_tareas)
                    
                    # Al elegir la tarea, aparecen inmediatamente las entregas vinculadas
                    alumnos_lista = api_git(f"Entregas_Globales/{asignatura_activa}/{tarea_elegida}")
                    id_alumnos = [a["name"] for a in alumnos_lista if a["type"] == "dir"]
                    
                    if id_alumnos:
                        st.info(f"Se han recibido {len(id_alumnos)} entregas para este ejercicio:")
                        alumno_select = st.selectbox("Selecciona el alumno para revisar su respuesta enviada:", id_alumnos)
                        
                        archivos_alumno = api_git(f"Entregas_Globales/{asignatura_activa}/{tarea_elegida}/{alumno_select}")
                        url_documento, nombre_documento = "", ""
                        for f in archivos_alumno:
                            if f["name"] != "nota.json":
                                url_documento, nombre_documento = f["download_url"], f["name"]
                                
                        # Extraer meta de nota actual
                        ruta_nota_json = f"Entregas_Globales/{asignatura_activa}/{tarea_elegida}/{alumno_select}/nota.json"
                        meta_nota_act = api_git(ruta_nota_json)
                        nota_v, feedback_v = "Sin calificar", ""
                        
                        if isinstance(meta_nota_act, dict) and "download_url" in meta_nota_act:
                            res_desc = requests.get(meta_nota_act["download_url"])
                            if res_desc.status_code == 200:
                                nota_v = res_desc.json().get("nota", "Sin calificar")
                                feedback_v = res_desc.json().get("feedback", "")
                                
                        st.markdown(f"""
                            <div style='background-color:#f8f9fa; border:1px solid #dadce0; padding:15px; border-radius:6px; margin-bottom:15px;'>
                                👤 <b>Estudiante evaluado:</b> {alumno_select.replace('_',' ')}<br>
                                📄 <b>Archivo de solución enviado:</b> {nombre_documento.replace('_',' ')}<br><br>
                                <a href='{url_documento}' target='_blank'><button style='background-color:#1a73e8; color:white; border:none; padding:8px 12px; border-radius:4px; font-weight:bold; cursor:pointer;'>📥 Abrir y Evaluar Documento</button></a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col_nt, col_fd = st.columns([1, 2])
                        with col_nt:
                            nota_input = st.text_input("Calificación oficial (Ej: 8.75/10):", value=str(nota_v))
                        with col_fd:
                            feedback_input = st.text_area("Feedback pedagógico:", value=feedback_v)
                            
                        if st.button("💾 Publicar Calificación Oficial"):
                            nueva_data = {"nota": nota_input, "feedback": feedback_input, "fecha": datetime.now().strftime("%d/%m/%Y")}
                            if enviar_archivo(ruta_nota_json, json.dumps(nueva_data).encode("utf-8"), "Nota guardada"):
                                st.success("✔️ Calificación guardada con éxito y publicada de forma privada en el expediente del alumno.")
                                st.rerun()
                    else:
                        st.warning("No se registran respuestas ni archivos enviados por parte de ningún alumno para esta tarea.")
                else:
                    st.info("No hay registros ni histórico de tareas entregadas en el aula virtual de esta asignatura.")

            # --- 3. CREAR NUEVA ASIGNATURA ---
            elif herramienta == "🏫 CREAR NUEVA ASIGNATURA GENERAL":
                st.subheader("Registro Central de Asignaturas")
                nueva_asig = st.text_input("Nombre completo de la Materia (Ej: Fisica 1 Bachillerato):")
                if st.button("Consolidar Nueva Asignatura"):
                    if nueva_asig:
                        clean_asig = nueva_asig.strip().replace(" ", "_")
                        if enviar_archivo(f"{clean_asig}/.gitkeep", b"", "Nueva asignatura"):
                            st.success(f"✔️ ¡Confirmado! La asignatura '{nueva_asig}' ha sido guardada con éxito en el servidor central.")
                            st.rerun()
