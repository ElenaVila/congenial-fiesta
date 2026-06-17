import streamlit as st
import requests
import base64
import json
from datetime import datetime

# =========================================================================
# 1. IDENTIDAD VISUAL GOOGLE CLASSROOM (FUENTES, BANNERS Y BOTONES INTEGRADOS)
# =========================================================================
st.set_page_config(page_title="Google Classroom", layout="wide")

st.markdown("""
    <style>
    /* Importar la fuente oficial y limpia de Google */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Roboto', sans-serif !important;
        background-color: #ffffff !important;
    }
    
    /* Eliminar la tipografía de niño pequeño de todos los elementos */
    h1, h2, h3, h4, h5, h6, p, span, label {
        font-family: 'Roboto', sans-serif !important;
    }
    
    /* --- REDISEÑO DE TARJETAS ESTILO GOOGLE CLASSROOM --- */
    .classroom-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 24px;
        margin-top: 24px;
    }
    
    .classroom-card {
        background-color: #ffffff;
        border: 1px solid #dadce0;
        border-radius: 8px;
        width: 300px;
        height: 240px;
        overflow: hidden;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: none;
        transition: box-shadow 0.2s;
    }
    .classroom-card:hover {
        box-shadow: 0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15);
    }
    
    /* Banners superiores idénticos a los de la captura real */
    .banner-calculus { background: linear-gradient(135px, #d91b5c 0%, #e91e63 100%); }
    .banner-history { background: linear-gradient(135px, #5f6368 0%, #7fc4c2 100%); }
    .banner-biology { background: linear-gradient(135px, #673ab7 0%, #9c27b0 100%); }
    .banner-computer { background: linear-gradient(135px, #00796b 0%, #009688 100%); }
    .banner-spanish { background: linear-gradient(135px, #1565c0 0%, #2196f3 100%); }
    .banner-default { background: linear-gradient(135px, #1e3a8a 0%, #3b82f6 100%); }
    
    .card-top {
        color: white;
        padding: 16px;
        height: 110px;
        position: relative;
    }
    .card-title {
        font-size: 22px;
        font-weight: 500;
        margin: 0;
        color: white !important;
        line-height: 1.2;
    }
    .card-subtitle {
        font-size: 13px;
        opacity: 0.9;
        margin-top: 4px;
        color: white !important;
    }
    
    .card-bottom {
        padding: 16px;
        background-color: white;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        border-top: 1px solid #e8eaed;
    }
    
    /* --- REDISEÑO DE BOTONES PARA INTEGRARLOS EN LA TARJETA --- */
    div.stButton > button {
        background-color: transparent !important;
        color: #1a73e8 !important;
        border: 1px solid #dadce0 !important;
        border-radius: 4px !important;
        padding: 6px 16px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        width: auto !important;
        box-shadow: none !important;
        transition: background-color 0.2s, border-color 0.2s !important;
        margin-top: 5px !important;
    }
    div.stButton > button:hover {
        background-color: #f4f8fe !important;
        border-color: #1a73e8 !important;
    }
    
    /* --- DISEÑO INTERIOR DE LOS TEMAS (CLASSWORK) --- */
    .classwork-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .topic-section {
        border-bottom: 1px solid #e8eaed;
        padding-bottom: 16px;
        margin-top: 32px;
    }
    .topic-title-text {
        color: #1c1d22;
        font-size: 24px;
        font-weight: 400;
        margin-bottom: 16px;
    }
    .row-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 24px;
        border: 1px solid #dadce0;
        border-radius: 8px;
        background-color: #ffffff;
        margin-bottom: 8px;
        transition: background-color 0.1s;
    }
    .row-item:hover { background-color: #f8f9fa; }
    
    /* Mini etiquetas elegantes */
    .tag-task {
        font-size: 11px;
        background-color: #fee2e2;
        color: #c53030;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 500;
    }
    .tag-material {
        font-size: 11px;
        background-color: #e6f4ea;
        color: #137333;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión Segura con GitHub Secrets
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "MATEMATICAS"
TOKEN_GITHUB = st.secrets["TOKEN_GITHUB"]

# =========================================================================
# 2. CORE: CONECTIVIDAD TOTAL CON GITHUB API
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
# 3. NAVEGACIÓN LATERAL MINIMALISTA
# =========================================================================
st.sidebar.markdown("<h3 style='color: #5f6368; font-weight:500; margin-bottom:20px;'>≡ Google Classroom</h3>", unsafe_allow_html=True)
navegacion = st.sidebar.radio("Navegación:", [
    "📚 Clases",
    "📅 Calendario",
    "👩‍🏫 Panel del Profesor"
])

if navegacion != "📚 Clases":
    st.session_state["curso_activo"] = None

# -------------------------------------------------------------------------
# VISTA A: PANEL PRINCIPAL DE CLASES (REPLICANDO LA CAPTURA DE CLASSROOM)
# -------------------------------------------------------------------------
if navegacion == "📚 Clases":
    
    # 🏠 CASO 1: CUADRÍCULA DE TARJETAS LIMPIAS
    if st.session_state["curso_activo"] is None:
        st.markdown("<h3 style='color: #5f6368; font-weight: 400; margin-top:10px;'>Cursos activos</h3>", unsafe_allow_html=True)
        st.write("---")
        
        asignaturas = listar_directorios()
        
        if asignaturas:
            cols = st.columns(3)
            for idx, asig in enumerate(asignaturas):
                with cols[idx % 3]:
                    
                    # Asignación de banners reales idénticos a los de Google Classroom
                    nombre_lower = asig.lower()
                    if "calculus" in nombre_lower or "matematica" in nombre_lower or "funciones" in nombre_lower:
                        clase_banner = "banner-calculus"
                        sub_info = "Cálculo y Álgebra"
                    elif "history" in nombre_lower or "historia" in nombre_lower:
                        clase_banner = "banner-history"
                        sub_info = "Historia del Arte"
                    elif "biology" in nombre_lower or "biologia" in nombre_lower:
                        clase_banner = "banner-biology"
                        sub_info = "Anatomía celular"
                    elif "computer" in nombre_lower or "tecnologia" in nombre_lower:
                        clase_banner = "banner-computer"
                        sub_info = "Computer Science"
                    elif "spanish" in nombre_lower or "lengua" in nombre_lower:
                        clase_banner = "banner-spanish"
                        sub_info = "Gramática y Literatura"
                    else:
                        clase_banner = "banner-default"
                        sub_info = "Curso General"
                        
                    # Renderizado HTML puro de la tarjeta al estilo exacto de Google
                    st.markdown(f"""
                        <div class='classroom-card'>
                            <div class='card-top {clase_banner}'>
                                <h3 class='card-title'>{asig.replace('_', ' ')}</h3>
                                <div class='card-subtitle'>{sub_info}</div>
                            </div>
                            <div class='card-bottom'>
                                <div style='font-size: 13px; color: #70757a;'>Revisar tareas pendientes</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # El botón de entrada ya no es tosco, se alinea de forma elegante
                    if st.button("Ver tablón", key=f"entrar_{asig}"):
                        st.session_state["curso_activo"] = asig
                        st.rerun()
        else:
            st.info("No hay clases creadas en el tablón todavía.")

    # 📖 CASO 2: TRABAJO DE CLASE (DENTRO DEL CURSO)
    else:
        asig_actual = st.session_state["curso_activo"]
        
        if st.button("← Volver a Clases"):
            st.session_state["curso_activo"] = None
            st.rerun()
            
        st.markdown(f"""
            <div style='border-bottom: 1px solid #e8eaed; padding-bottom: 10px; margin-top:15px;'>
                <h1 style='color: #1a73e8; font-weight: 400; margin:0;'>{asig_actual.replace('_', ' ')}</h1>
                <p style='color: #5f6368; font-size: 14px; margin: 4px 0 0 0;'>Trabajo de clase</p>
            </div>
        """, unsafe_allow_html=True)
        
        temas = listar_directorios(asig_actual)
        
        if temas:
            # Estructura limpia y correlativa centrada
            for tema in temas:
                st.markdown(f"<div class='topic-section'><div class='topic-title-text'>{tema.replace('_', ' ')}</div></div>", unsafe_allow_html=True)
                
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
                                <div class='row-item'>
                                    <div>
                                        <span class='tag-task'>📋 Tarea</span>
                                        <b style='margin-left:12px; color: #3c4043;'>{t_nombre}</b>
                                    </div>
                                    <div style='font-size: 13px; color: #70757a;'>
                                        Fecha límite: {f_limite} | <a href='{el['download_url']}' target='_blank' style='color:#1a73e8; text-decoration:none; font-weight:500;'>Abrir</a>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                            
                            with st.expander(f"Entregar: {t_nombre}"):
                                with st.form(f"f_entrega_{el['name']}", clear_on_submit=True):
                                    nombre_al = st.text_input("Nombre del Alumno:")
                                    archivo_al = st.file_uploader("Adjuntar solución:", type=["pdf","png","jpg","jpeg"])
                                    
                                    if st.form_submit_button("Enviar solución"):
                                        if nombre_al and archivo_al:
                                            id_al = nombre_al.strip().replace(" ", "_")
                                            id_tar = el["name"].split(".")[0]
                                            
                                            ruta_file = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/{archivo_al.name}"
                                            ruta_json = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/nota.json"
                                            meta = {"nota": "Sin calificar", "feedback": "Pendiente.", "fecha": datetime.now().strftime("%d/%m/%Y")}
                                            
                                            if enviar_archivo(ruta_file, archivo_al.getvalue(), "Entrega") and enviar_archivo(ruta_json, json.dumps(meta).encode("utf-8"), "Meta"):
                                                st.success(f"✔️ Archivo '{archivo_al.name}' entregado correctamente.")
                        else:
                            nombre_mat = el["name"].replace("_", " ").split(".")[0]
                            st.markdown(f"""
                                <div class='row-item'>
                                    <div>
                                        <span class='tag-material'>📖 Material</span>
                                        <span style='margin-left:12px; color: #3c4043;'>{nombre_mat}</span>
                                    </div>
                                    <div>
                                        <a href='{el['download_url']}' target='_blank' style='color:#1a73e8; text-decoration:none; font-weight:500;'>Descargar</a>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)
                else:
                    st.write("<p style='color:#70757a; font-size:13px; padding-left:10px;'>No hay materiales asignados.</p>", unsafe_allow_html=True)
        else:
            st.info("No hay unidades temáticas configuradas.")

# -------------------------------------------------------------------------
# VISTA B: CALENDARIO ESCOLAR AUTOMÁTICO
# -------------------------------------------------------------------------
elif navegacion == "📅 Calendario":
    st.title("📅 Calendario Escolar")
    st.write("Seguimiento de plazos automáticos fijados en las tareas de clase.")
    st.write("---")
    
    todas_asig = listar_directorios()
    tareas_totales = False
    
    for asig in todas_asig:
        todos_temas = listar_directorios(asig)
        for tem in todos_temas:
            elementos_tem = api_git(f"{asig}/{tem}")
            if isinstance(elementos_tem, list):
                for e in elementos_tem:
                    if e["type"] == "file" and e["name"].startswith("TAREA_"):
                        tareas_totales = True
                        partes = e["name"].split("_", 2)
                        f_limite = partes[1] if len(partes) > 1 else "Sin fecha"
                        t_nombre = partes[2].replace("_", " ").split(".")[0] if len(partes) > 2 else "Tarea"
                        
                        st.markdown(f"""
                            <div class='cal-card-auto'>
                                ⏰ <b>Vencimiento: {f_limite}</b> — 📋 {t_nombre} (Materia: {asig.replace('_',' ')})
                            </div>
                        """, unsafe_allow_html=True)
    if not tareas_totales:
        st.info("No tienes tareas programadas en el calendario.")

# -------------------------------------------------------------------------
# VISTA C: PANEL DE LA PROFESORA
# -------------------------------------------------------------------------
elif navegacion == "👩‍🏫 Panel del Profesor":
    st.title("👩‍🏫 Panel de Control Docente")
    password = st.text_input("Contraseña de acceso:", type="password")
    
    if password == "profe2026":
        st.success("Acceso confirmado.")
        st.write("---")
        
        menu_admin = st.selectbox("Módulo:", ["🛠️ Crear tema y subir archivos", "📥 Ver entregas", "🏫 Crear asignatura"])
        
        if menu_admin == "🛠️ Crear tema y subir archivos":
            asig_list = listar_directorios()
            if asig_list:
                asig_sel_profe = st.selectbox("Asignatura:", asig_list)
                gestion_tema = st.radio("Acción:", ["Crear tema nuevo", "Añadir a tema existente"])
                
                if gestion_tema == "Crear tema nuevo":
                    nombre_t = st.text_input("Nombre del Tema:")
                    tema_ruta_final = nombre_t.strip().replace(" ", "_")
                else:
                    temas_ex = listar_directorios(asig_sel_profe)
                    tema_ruta_final = st.selectbox("Tema:", temas_ex) if temas_ex else None
                    
                if tema_ruta_final:
                    tipo_archivo = st.radio("Tipo:", ["📖 Material", "📋 Tarea"])
                    
                    if tipo_archivo == "📋 Tarea":
                        f_limite_p = st.date_input("Fecha límite:")
                        fichero_p = st.file_uploader("Ficha de Tarea:")
                        
                        if st.button("Publicar Tarea") and fichero_p:
                            nombre_archivo_git = f"TAREA_{str(f_limite_p)}_{fichero_p.name.replace(' ', '_')}"
                            ruta_complete = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            if enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init") and enviar_archivo(ruta_complete, fichero_p.getvalue(), "Carga"):
                                st.success(f"✔️ Tarea '{fichero_p.name}' publicada correctamente en {tema_ruta_final.replace('_',' ')}.")
                    else:
                        fichero_p = st.file_uploader("Apuntes / PDF:")
                        if st.button("Publicar Material") and fichero_p:
                            nombre_archivo_git = fichero_p.name.replace(' ', '_')
                            ruta_complete = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            if enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init") and enviar_archivo(ruta_complete, fichero_p.getvalue(), "Carga"):
                                st.success(f"✔️ Material '{fichero_p.name}' publicado con éxito.")
                                
        elif menu_admin == "📥 Ver entregas":
            asig_list = listar_directorios()
            if asig_list:
                asig_eval = st.selectbox("Asignatura:", asig_list)
                entregas_raiz = api_git(f"Entregas_Globales/{asig_eval}")
                carpetas_tareas = [c["name"] for c in entregas_raiz if c["type"] == "dir"]
                
                if carpetas_tareas:
                    tarea_eval = st.selectbox("Tarea:", carpetas_tareas)
                    alumnos_lista = api_git(f"Entregas_Globales/{asig_eval}/{tarea_eval}")
                    id_alumnos = [a["name"] for a in alumnos_lista if a["type"] == "dir"]
                    
                    if id_alumnos:
                        alumno_eval = st.selectbox("Alumno:", id_alumnos)
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
                            <div style='background-color:#ffffff; border:1px solid #dadce0; padding:16px; border-radius:8px; margin-bottom:15px;'>
                                Alumno: <b>{alumno_eval.replace('_',' ')}</b><br>
                                Archivo: {name_doc.replace('_',' ')}<br><br>
                                <a href='{url_doc}' target='_blank' style='color:#1a73e8; text-decoration:none; font-weight:bold;'>📥 Abrir documento entregado</a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        input_n = st.text_input("Calificación:", value=str(nota_v))
                        input_f = st.text_area("Feedback:", value=feedback_v)
                        
                        if st.button("Guardar Nota"):
                            nueva_data = {"nota": input_n, "feedback": input_f, "fecha": datetime.now().strftime("%d/%m/%Y")}
                            if enviar_archivo(ruta_json_nota, json.dumps(nueva_data).encode("utf-8"), "Nota"):
                                st.success(f"✔️ Nota guardada correctamente.")
                                
        elif menu_admin == "🏫 Crear asignatura":
            nueva_asig = st.text_input("Nombre de la asignatura:")
            if st.button("Crear Asignatura"):
                if nueva_asig:
                    clean_asig = nueva_asig.strip().replace(" ", "_")
                    if enviar_archivo(f"{clean_asig}/.gitkeep", b"", "Alta"):
                        st.success(f"✔️ Asignatura '{nueva_asig}' creada correctamente.")
