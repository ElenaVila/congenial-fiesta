import streamlit as st
import requests
import base64
import json
from datetime import datetime

# =========================================================================
# 1. CONFIGURACIÓN VISUAL ESTILO GOOGLE CLASSROOM (LMS CLEAN DESIGN)
# =========================================================================
st.set_page_config(page_title="Google Classroom Avanzado", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    
    /* Banner superior estilo Classroom */
    .classroom-banner {
        background: linear-gradient(135px, #111827, #1f2937);
        color: white;
        padding: 30px;
        border-radius: 12px;
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    /* Encabezados de Temas */
    .topic-header {
        color: #1f2937;
        font-size: 22px;
        font-weight: bold;
        border-bottom: 2px solid #e5e7eb;
        padding-bottom: 6px;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    
    /* Filas de Materiales / Tareas */
    .classwork-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 20px;
        border-radius: 8px;
        margin-bottom: 8px;
        border: 1px solid #e5e7eb;
        background-color: #ffffff;
    }
    .classwork-row:hover { background-color: #f9fafb; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    
    /* Tarjeta de Calendario y Recordatorios */
    .agenda-card {
        background-color: #fef3c7;
        border-left: 5px solid #d97706;
        padding: 12px 15px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .agenda-auto-card {
        background-color: #eff6ff;
        border-left: 5px solid #3b82f6;
        padding: 12px 15px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión Segura con GitHub Secrets
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "MATEMATICAS"
TOKEN_GITHUB = st.secrets["TOKEN_GITHUB"]

# =========================================================================
# 2. CORE: CONECTIVIDAD TOTAL CON GITHUB API (SIN ERRORES ANTERIORES)
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

# =========================================================================
# 3. INTERFAZ DE USUARIO: ESTRUCTURA CLASSROOM INTEGRADA
# =========================================================================
st.markdown("""
    <div class='classroom-banner'>
        <h1 style='margin:0; font-size:30px;'>🎓 Aula Virtual — Gestión Educativa Avanzada</h1>
        <p style='margin:5px 0 0 0; opacity:0.85;'>Centro Escolar Digital | Entorno Sincronizado</p>
    </div>
""", unsafe_allow_html=True)

pestana_trabajo, pestana_agenda, pestana_notas, pestana_profesora = st.tabs([
    "📚 Trabajo de Clase", 
    "📅 Mi Agenda y Calendario", 
    "📋 Mis Calificaciones",
    "👩‍🏫 Despacho de la Profesora"
])

# -------------------------------------------------------------------------
# 1️⃣ TRABAJO DE CLASE: ASIGNATURAS -> TEMAS -> (MATERIALES Y TAREAS INTEGRADOS)
# -------------------------------------------------------------------------
with pestana_trabajo:
    st.write("")
    asignaturas = listar_directorios()
    
    if asignaturas:
        asig_sel = st.selectbox("📚 Selecciona tu Asignatura:", asignaturas)
        st.write("---")
        
        temas = listar_directorios(asig_sel)
        if temas:
            for tema in temas:
                st.markdown(f"<div class='topic-header'>📁 {tema.replace('_', ' ')}</div>", unsafe_allow_html=True)
                
                elementos = api_git(f"{asig_sel}/{tema}")
                archivos_validos = [e for e in elementos if e["type"] == "file" and e["name"] != ".gitkeep"]
                
                if archivos_validos:
                    for el in archivos_validos:
                        # Detectar si el archivo es una tarea integrada
                        es_tarea = el["name"].startswith("TAREA_")
                        
                        if es_tarea:
                            # Formato: TAREA_2026-06-30_Nombre_De_La_Tarea.pdf
                            partes_tarea = el["name"].split("_", 2)
                            fecha_limite = partes_tarea[1] if len(partes_tarea) > 1 else "Sin fecha"
                            nombre_tarea_limpio = partes_tarea[2].replace("_", " ").split(".")[0] if len(partes_tarea) > 2 else "Tarea"
                            
                            st.markdown(f"""
                                <div class='classwork-row' style='border-left: 5px solid #ef4444;'>
                                    <div>
                                        <span style='font-size:18px; margin-right:10px;'>📋</span>
                                        <b style='color:#1f2937;'>{nombre_tarea_limpio}</b>
                                        <span style='font-size:11px; background-color:#fee2e2; color:#991b1b; padding:2px 6px; border-radius:4px; margin-left:10px; font-weight:bold;'>Fecha límite: {fecha_limite}</span>
                                    </div>
                                    <div>
                                        <a href='{el['download_url']}' target='_blank' style='color:#2563eb; text-decoration:none; font-weight:bold; font-size:14px; margin-right:15px;'>📥 Ver Instrucciones</a>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            # Buzón desplegable dentro del propio tema
                            with st.expander(f"📥 Entregar solución a: {nombre_tarea_limpio}"):
                                with st.form(f"form_{el['name']}", clear_on_submit=True):
                                    alumno = st.text_input("Nombre y Apellidos del Alumno:")
                                    archivo_solucion = st.file_uploader("Adjunta tu PDF o Imagen:", type=["pdf","png","jpg","jpeg"])
                                    
                                    if st.form_submit_button("Enviar a la Profesora"):
                                        if alumno and archivo_solucion:
                                            id_alu = alumno.strip().replace(" ", "_")
                                            id_tar = el["name"].split(".")[0]
                                            
                                            ruta_ent = f"Entregas_Globales/{id_tar}/{id_alu}/{archivo_solucion.name}"
                                            ruta_js = f"Entregas_Globales/{id_tar}/{id_alu}/nota.json"
                                            meta = {"nota": "Sin calificar", "feedback": "Pendiente de revisión.", "fecha": datetime.now().strftime("%d/%m/%Y")}
                                            
                                            if enviar_archivo(ruta_ent, archivo_solucion.getvalue(), f"Entrega") and enviar_archivo(ruta_js, json.dumps(meta).encode("utf-8"), "Meta"):
                                                st.success("¡Entrega registrada correctamente en este tema!")
                                        else:
                                            st.warning("Completa los datos.")
                        else:
                            # Es un material didáctico normal
                            nombre_mat_limpio = el["name"].replace("_", " ").split(".")[0]
                            st.markdown(f"""
                                <div class='classwork-row' style='border-left: 5px solid #10b981;'>
                                    <div>
                                        <span style='font-size:18px; margin-right:10px;'>📖</span>
                                        <b style='color:#1f2937;'>{nombre_mat_limpio}</b>
                                        <span style='font-size:11px; background-color:#d1fae5; color:#065f46; padding:2px 6px; border-radius:4px; margin-left:10px;'>Material Didáctico</span>
                                    </div>
                                    <div>
                                        <a href='{el['download_url']}' target='_blank' style='color:#2563eb; text-decoration:none; font-weight:bold; font-size:14px; margin-right:15px;'>📥 Descargar</a>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("<i style='color:#6b7280; padding-left:20px;'>No hay recursos subidos en este tema.</i>", unsafe_allow_html=True)
        else:
            st.info("Esta asignatura aún no tiene temas creados.")
    else:
        st.info("Aún no se han creado asignaturas en el aula virtual.")

# -------------------------------------------------------------------------
# 2️⃣ AGENDA Y CALENDARIO: DETECCIÓN AUTOMÁTICA DE FECHAS DE TAREAS + MANUAL
# -------------------------------------------------------------------------
with pestana_agenda:
    st.write("")
    st.markdown("<h3 style='color:#1f2937;'>📅 Tu Agenda Escolar Integrada</h3>", unsafe_allow_html=True)
    
    col_ag1, col_ag2 = st.columns([2, 1])
    
    with col_ag1:
        st.write("🔔 **Tareas y Plazos del Colegio (Detectados Automáticamente):**")
        
        # Escaneo automático de todas las carpetas buscando archivos con prefijo TAREA_
        todas_asignaturas = listar_directorios()
        tareas_detectadas = False
        
        for asig in todas_asignaturas:
            todos_temas = listar_directorios(asig)
            for tem in todos_temas:
                elementos_tem = api_git(f"{asig}/{tem}")
                if isinstance(elementos_tem, list):
                    for e in elementos_tem:
                        if e["type"] == "file" and e["name"].startswith("TAREA_"):
                            tareas_detectadas = True
                            partes = e["name"].split("_", 2)
                            f_limite = partes[1] if len(partes) > 1 else "Sin fecha"
                            t_nombre = partes[2].replace("_", " ").split(".")[0] if len(partes) > 2 else "Tarea"
                            
                            st.markdown(f"""
                                <div class='agenda-auto-card'>
                                    <b>📅 {f_limite}</b> — 📝 Tarea Obligatoria: <u>{t_nombre}</u> ({asig.replace('_',' ')})
                                </div>
                            """, unsafe_allow_html=True)
                            
        if not tareas_detectadas:
            st.info("¡Perfecto! No tienes tareas obligatorias programadas en el aula virtual.")
            
    with col_ag2:
        st.write("✍️ **Tus Recordatorios Personales:**")
        if "recordatorios_privados" not in st.session_state:
            st.session_state["recordatorios_privados"] = [
                {"nota": "Repasar apuntes de vectores", "fecha": "2026-06-22"}
            ]
            
        with st.form("form_rec", clear_on_submit=True):
            texto_rec = st.text_input("¿Qué necesitas recordar?")
            fecha_rec = st.date_input("¿Para qué día?")
            if st.form_submit_button("➕ Añadir"):
                if texto_rec:
                    st.session_state["recordatorios_privados"].append({"nota": texto_rec, "fecha": str(fecha_rec)})
                    st.rerun()
                    
        for r in st.session_state["recordatorios_privados"]:
            st.markdown(f"""
                <div class='agenda-card'>
                    <small>⏱️ {r['fecha']}</small><br><b>📌 {r['nota']}</b>
                </div>
            """, unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 3️⃣ BOLETÍN DE CALIFICACIONES (VISTA DEL ALUMNO)
# -------------------------------------------------------------------------
with pestana_notas:
    st.write("")
    st.subheader("📋 Consulta tus Notas Oficiales")
    alumno_buscar = st.text_input("Introduce tus Apellidos y Nombre (igual que al entregar):")
    
    if alumno_buscar:
        id_busca = alumno_buscar.strip().replace(" ", "_")
        entregas_raiz = api_git("Entregas_Globales")
        
        encontrado = False
        if isinstance(entregas_raiz, list):
            for carpeta_t in entregas_raiz:
                ruta_nota = f"Entregas_Globales/{carpeta_t['name']}/{id_busca}/nota.json"
                meta_js = api_git(ruta_nota)
                
                if isinstance(meta_js, dict) and "download_url" in meta_js:
                    encontrado = True
                    res_js = requests.get(meta_js["download_url"])
                    if res_js.status_code == 200:
                        data_nota = res_js.json()
                        nombre_t_bonito = carpeta_t["name"].split("_", 2)[-1].replace("_", " ") if "TAREA_" in carpeta_t["name"] else carpeta_t["name"].replace("_"," ")
                        
                        st.markdown(f"""
                            <div style='background-color:#f0fdf4; border:1px solid #bbf7d0; padding:15px; border-radius:8px; margin-bottom:10px; color:#166534;'>
                                <h4 style='margin:0;'>📊 Tarea: {nombre_t_bonito}</h4>
                                <p style='margin:5px 0;'><b>Calificación:</b> <span style='font-size:16px; font-weight:bold;'>{data_nota['nota']}</span></p>
                                <p style='margin:0;'><b>Feedback de Elena:</b> {data_nota['feedback']}</p>
                            </div>
                        """, unsafe_allow_html=True)
            if not encontrado:
                st.info("No se han cargado notas asociadas a ese nombre en el sistema.")

# -------------------------------------------------------------------------
# 4️⃣ DESPACHO DE LA PROFESORA: GESTIÓN INTEGRADA (CARPETAS, ARCHIVOS Y TAREAS)
# -------------------------------------------------------------------------
with pestana_profesora:
    st.write("")
    password = st.text_input("Clave de acceso al Despacho Docente:", type="password")
    
    if password == "profe2026":
        st.success("Acceso confirmado. Buenas tardes, Elena.")
        st.write("---")
        
        accion_docente = st.selectbox("¿Qué gestión deseas realizar hoy?", [
            "🛠️ CREAR UN NUEVO TEMA DESDE CERO (Con Archivos o Tareas)",
            "📥 CUADERNO DE CALIFICACIONES (Corregir entregas)",
            "🏫 CREAR NUEVA ASIGNATURA"
        ])
        
        # --- ACCION 1: CREAR TEMA, SUBIR ARCHIVOS Y PONER TAREAS DE UN SOLO GOLPE ---
        if accion_docente == "🛠️ CREAR UN NUEVO TEMA DESDE CERO (Con Archivos o Tareas)":
            st.subheader("Diseño de Bloques y Unidades Didácticas")
            
            asignaturas_raiz = listar_directorios()
            if asignaturas_raiz:
                asig_elegida = st.selectbox("¿En qué Asignatura?", asignaturas_raiz)
                
                tipo_tema = st.radio("¿El tema ya existe o es totalmente nuevo?", ["Es un Tema Nuevo", "Es un Tema existente (Añadir más cosas)"])
                
                if tipo_tema == "Es un Tema Nuevo":
                    nombre_tema_input = st.text_input("Nombre del nuevo Tema (Ej: Tema 3 Trigonometria):")
                    tema_final_ruta = nombre_tema_input.strip().replace(" ", "_")
                else:
                    temas_existentes = listar_directorios(asig_elegida)
                    if temas_existentes:
                        tema_final_ruta = st.selectbox("Selecciona el tema existente:", temas_existentes)
                    else:
                        st.warning("No hay temas creados en esta asignatura todavía.")
                        tema_final_ruta = None
                        
                if tema_final_ruta:
                    st.write("---")
                    st.write("💼 **¿Qué tipo de recurso deseas publicar en este Tema?**")
                    tipo_recurso = st.radio("Clasificación del recurso:", ["📖 Material Didáctico (Apuntes, PDF, Guía)", "📋 Tarea Evaluables (Con entrega y fecha límite)"])
                    
                    if tipo_recurso == "📋 Tarea Evaluables (Con entrega y fecha límite)":
                        fecha_limite_input = st.date_input("Establecer Fecha Límite de entrega:")
                        archivo_docente = st.file_uploader("Sube la ficha o enunciado de la Tarea:")
                        
                        if st.button("🚀 Publicar Tarea en el Tema") and archivo_docente:
                            # Estructura de nombre automático: TAREA_AAAA-MM-DD_NombreArchivo.pdf
                            nombre_archivo_git = f"TAREA_{str(fecha_limite_input)}_{archivo_docente.name.replace(' ', '_')}"
                            ruta_completa_git = f"{asig_elegida}/{tema_final_ruta}/{nombre_archivo_git}"
                            
                            with st.spinner("Sincronizando tarea y calendario..."):
                                # Subimos un .gitkeep por si el tema es nuevo, para consolidar la carpeta
                                enviar_archivo(f"{asig_elegida}/{tema_final_ruta}/.gitkeep", b"", "Crear Tema")
                                if enviar_archivo(ruta_completa_git, archivo_docente.getvalue(), "Nueva Tarea Integrada"):
                                    st.success(f"¡Tarea publicada con éxito dentro del tema! Además, se ha indexado de forma automática en el Calendario de los alumnos.")
                                    st.rerun()
                    else:
                        archivo_docente = st.file_uploader("Sube los apuntes o documento didáctico:")
                        if st.button("🚀 Publicar Material en el Tema") and archivo_docente:
                            nombre_archivo_git = archivo_docente.name.replace(' ', '_')
                            ruta_completa_git = f"{asig_elegida}/{tema_final_ruta}/{nombre_archivo_git}"
                            
                            with st.spinner("Subiendo material didáctico..."):
                                enviar_archivo(f"{asig_elegida}/{tema_final_ruta}/.gitkeep", b"", "Crear Tema")
                                if enviar_archivo(ruta_completa_git, archivo_docente.getvalue(), "Nuevo Material Integrado"):
                                    st.success(f"¡Material '{archivo_docente.name}' añadido correctamente en su tema correspondiente!")
                                    st.rerun()
            else:
                st.warning("Primero debes dar de alta una Asignatura Raíz.")
                
        # --- ACCION 2: CORREGIR TAREAS Y MANDAR NOTAS ---
        elif accion_docente == "📥 CUADERNO DE CALIFICACIONES (Corregir entregas)":
            st.subheader("Bandeja de Entrada Escolar")
            directorios_entregas = api_git("Entregas_Globales")
            opciones_t = [d["name"] for d in directorios_entregas if d["type"] == "dir"]
            
            if opciones_t:
                tarea_a_corregir = st.selectbox("Selecciona la tarea recibida:", opciones_t)
                alumnos_entregados = api_git(f"Entregas_Globales/{tarea_a_corregir}")
                opciones_a = [a["name"] for a in alumnos_entregados if a["type"] == "dir"]
                
                if opciones_a:
                    alumno_a_corregir = st.selectbox("Selecciona el estudiante:", opciones_a)
                    archivos = api_git(f"Entregas_Globales/{tarea_a_corregir}/{alumno_a_corregir}")
                    
                    doc_url, doc_name = "", ""
                    for f in archivos:
                        if f["name"] != "nota.json":
                            doc_url, doc_name = f["download_url"], f["name"]
                            
                    ruta_json_nota = f"Entregas_Globales/{tarea_a_corregir}/{alumno_a_corregir}/nota.json"
                    meta_n = api_git(ruta_json_nota)
                    nota_val, feedback_val = "Sin calificar", ""
                    
                    if isinstance(meta_n, dict) and "download_url" in meta_n:
                        res_n = requests.get(meta_n["download_url"])
                        if res_n.status_code == 200:
                            nota_val = res_n.json().get("nota", "Sin calificar")
                            feedback_val = res_n.json().get("feedback", "")
                            
                    st.markdown(f"""
                        <div style='background-color:#f9fafb; padding:15px; border:1px solid #e5e7eb; border-radius:8px; margin-bottom:15px;'>
                            👤 <b>Estudiante:</b> {alumno_a_corregir.replace('_', ' ')} <br>
                            📄 <b>Archivo enviado:</b> {doc_name.replace('_',' ')} <br><br>
                            <a href='{doc_url}' target='_blank'><button style='background-color:#2563eb; color:white; border:none; padding:8px 15px; border-radius:4px; font-weight:bold; cursor:pointer;'>📥 Abrir Trabajo del Alumno</button></a>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    col_n, col_f = st.columns([1, 2])
                    with col_n:
                        n_input = st.text_input("Calificación (ej: 9.2/10):", value=str(nota_val))
                    with col_f:
                        f_input = st.text_area("Feedback Pedagógico:", value=feedback_val)
                        
                    if st.button("Guardar Calificación Oficial"):
                        datos_actualizados = {"nota": n_input, "feedback": f_input, "fecha": datetime.now().strftime("%d/%m/%Y")}
                        if enviar_archivo(ruta_json_nota, json.dumps(datos_actualizados).encode("utf-8"), "Guardar nota"):
                            st.success("Nota enviada de forma privada al boletín del alumno.")
                            st.rerun()
                else:
                    st.info("No hay entregas de alumnos para este recurso.")
            else:
                st.info("No se registran entregas en el servidor escolar.")
                
        # --- ACCION 3: CREAR ASIGNATURA ---
        elif accion_docente == "🏫 CREAR NUEVA ASIGNATURA":
            st.subheader("Alta de Materias Raíz")
            nueva_asig_nombre = st.text_input("Nombre de la Asignatura (Ej: Matematicas 1 Bachillerato):")
            if st.button("Dar de Alta Asignatura") and nueva_asig_nombre:
                asig_clean = nueva_asig_nombre.strip().replace(" ", "_")
                if enviar_archivo(f"{asig_clean}/.gitkeep", b"", "Alta Asignatura"):
                    st.success(f"Asignatura '{nueva_asig_nombre}' guardada en el registro central.")
                    st.rerun()
