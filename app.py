import streamlit as st
import requests
import base64
import json
from datetime import datetime

# =========================================================================
# 1. IDENTIDAD VISUAL PREMIUM: CSS DE ALTO IMPACTO PARA INSTI/COLEGIO
# =========================================================================
st.set_page_config(page_title="Aula Virtual - Campus Escolar", layout="wide")

st.markdown("""
    <style>
    /* Importar tipografía moderna */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    * { font-family: 'Poppins', sans-serif; }
    
    /* Fondo general estilo Campus Moderno */
    .main { background-color: #f0f4f8; }
    
    /* Gran Banner Institucional Principal */
    .school-header {
        background: linear-gradient(135px, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 40px;
        border-radius: 16px;
        margin-bottom: 30px;
        box-shadow: 0 10px 25px rgba(30, 58, 138, 0.15);
        border-bottom: 5px solid #f59e0b;
        position: relative;
        overflow: hidden;
    }
    
    /* Contenedor Mosaico de Asignaturas */
    .subject-container {
        display: flex;
        flex-wrap: wrap;
        gap: 25px;
        margin-top: 20px;
    }
    
    /* Tarjetas de Asignaturas con Portadas Vivas */
    .subject-card {
        background-color: white;
        border-radius: 14px;
        width: 330px;
        min-height: 220px;
        overflow: hidden;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
        border: 1px solid #e2e8f0;
    }
    .subject-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    }
    
    /* Portadas con colores degradados vivos de instituto */
    .banner-math { background: linear-gradient(135px, #ec4899 0%, #f43f5e 100%); }
    .banner-science { background: linear-gradient(135px, #10b981 0%, #059669 100%); }
    .banner-tech { background: linear-gradient(135px, #8b5cf6 0%, #6d28d9 100%); }
    .banner-default { background: linear-gradient(135px, #3b82f6 0%, #1d4ed8 100%); }
    
    .card-banner {
        color: white;
        padding: 20px;
        min-height: 110px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .card-body {
        padding: 20px;
        background-color: white;
        color: #475569;
        font-size: 14px;
    }

    /* Filas Escolares para Materiales y Tareas */
    .classwork-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 16px 24px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .classwork-item:hover { 
        background-color: #f8fafc;
        border-color: #cbd5e1;
    }
    
    /* Badges de Colores Llamativos */
    .badge-task {
        background-color: #fee2e2;
        color: #dc2626;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        border: 1px solid #fca5a5;
    }
    .badge-material {
        background-color: #d1fae5;
        color: #065f46;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        border: 1px solid #6ee7b7;
    }
    
    /* Bloques Estilizados del Calendario */
    .cal-card-auto {
        background: linear-gradient(to right, #eff6ff, #dbeafe);
        border-left: 6px solid #3b82f6;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        color: #1e40af;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    .cal-card-manual {
        background: linear-gradient(to right, #fffdf5, #fef3c7);
        border-left: 6px solid #f59e0b;
        padding: 16px;
        border-radius: 10px;
        margin-bottom: 12px;
        color: #92400e;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    
    /* Cajas de notas corregidas */
    .grade-card {
        background: linear-gradient(to right, #f0fdf4, #dcfce7);
        border: 1px solid #bbf7d0;
        border-left: 6px solid #16a34a;
        padding: 20px;
        border-radius: 12px;
        color: #14532d;
        margin-bottom: 12px;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión Segura con GitHub Secrets
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "MATEMATICAS"
TOKEN_GITHUB = st.secrets["TOKEN_GITHUB"]

# =========================================================================
# 2. CORE: SISTEMA DE COMUNICACIÓN CON LA API DE GITHUB
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

# Inicializador de estado
if "curso_activo" not in st.session_state:
    st.session_state["curso_activo"] = None

# =========================================================================
# 3. INTERFAZ LATERAL: MENÚ DESPLEGABLE VERTICAL GLOBAL (SIDEBAR)
# =========================================================================
st.sidebar.markdown("<h2 style='text-align: center; color: #1e3a8a;'>🏫 Menú Escolar</h2>", unsafe_allow_html=True)
st.sidebar.write("---")
navegacion = st.sidebar.radio("Navegación del Campus:", [
    "📚 Mis Asignaturas",
    "📅 Calendario de Entregas",
    "👩‍🏫 Panel de Gestión Docente"
])

# Reseteo del curso activo si salimos de la sección
if navegacion != "📚 Mis Asignaturas":
    st.session_state["curso_activo"] = None

# -------------------------------------------------------------------------
# SECCIÓN A: EXPLORADOR VISUAL DE ASIGNATURAS (CON PORTADAS CON COLOR)
# -------------------------------------------------------------------------
if navegacion == "📚 Mis Asignaturas":
    
    # 🏠 CASO 1: VISTA DE LAS TARJETAS CON PORTADA DE COLORES VIVOS
    if st.session_state["curso_activo"] is None:
        st.markdown("""
            <div class='school-header'>
                <h1 style='margin:0; font-size:32px; font-weight:700;'>🏫 Campus Digital — Centro Educativo</h1>
                <p style='margin:8px 0 0 0; font-size:16px; opacity:0.9;'>Bienvenido a tu plataforma escolar. Selecciona una de tus asignaturas activas.</p>
            </div>
        """, unsafe_allow_html=True)
        
        asignaturas = listar_directorios()
        
        if asignaturas:
            st.markdown("<div class='subject-container'>", unsafe_allow_html=True)
            cols = st.columns(3)
            
            for idx, asig in enumerate(asignaturas):
                # Asignar dinámicamente un degradado de color según el nombre
                nombre_lower = asig.lower()
                if "matematica" in nombre_lower:
                    clase_banner = "banner-math"
                    icono = "📐"
                elif "ciencia" in nombre_lower or "fisica" in nombre_lower or "quimica" in nombre_lower:
                    clase_banner = "banner-science"
                    icono = "🔬"
                elif "tecnologia" in nombre_lower or "informatica" in nombre_lower:
                    clase_banner = "banner-tech"
                    icono = "💻"
                else:
                    clase_banner = "banner-default"
                    icono = "📘"
                
                with cols[idx % 3]:
                    st.markdown(f"""
                        <div class='subject-card'>
                            <div class='card-banner {clase_banner}'>
                                <span style='font-size: 32px;'>{icono}</span>
                                <h3 style='margin:0; font-size:20px; font-weight:600; color:white;'>{asig.replace('_', ' ')}</h3>
                            </div>
                            <div class='card-body'>
                                🏛️ <b>Curso Escolar Activo</b><br>
                                <span style='font-size:12px; color:#64748b;'>Haz clic abajo para desplegar el temario secuencial.</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Entrar al Aula de {asig.replace('_', ' ')}", key=f"entrar_{asig}"):
                        st.session_state["curso_activo"] = asig
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("El centro educativo aún no ha registrado ninguna asignatura en el sistema.")

    # 📖 CASO 2: INTERIOR DE LA MATERIA (TEMAS CORRELATIVOS VERTICALES)
    else:
        asig_actual = st.session_state["curso_activo"]
        
        if st.button("⬅️ Volver al Panel de Asignaturas"):
            st.session_state["curso_activo"] = None
            st.rerun()
            
        st.markdown(f"""
            <div style='background: linear-gradient(135px, #0f172a 0%, #1e293b 100%); color: white; padding: 25px; border-radius: 12px; margin-bottom: 25px; border-bottom: 4px solid #10b981;'>
                <h1 style='margin:0; font-size:26px;'>📘 Aula de Recursos: {asig_actual.replace('_', ' ')}</h1>
                <p style='margin:4px 0 0 0; opacity:0.8; font-size:14px;'>Estructura Curricular — Unidades Temáticas Correlativas</p>
            </div>
        """, unsafe_allow_html=True)
        
        temas = listar_directorios(asig_actual)
        if temas:
            for tema in temas:
                with st.expander(f"📁 {tema.replace('_', ' ')}", expanded=False):
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
                                    <div class='classwork-item' style='border-left: 5px solid #ef4444;'>
                                        <div>
                                            <span class='badge-task'>📋 Actividad Obligatoria</span>
                                            <b style='margin-left:12px; color:#1e293b; font-size:15px;'>{t_nombre}</b>
                                        </div>
                                        <div>
                                            <span style='font-size:13px; color:#64748b; margin-right:15px;'>Plazo límite: <b>{f_limite}</b></span>
                                            <a href='{el['download_url']}' target='_blank' style='color:#3b82f6; font-weight:600; text-decoration:none;'>📥 Ver Enunciado</a>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Formulario Escolar integrado de entrega
                                with st.form(f"f_entrega_{el['name']}", clear_on_submit=True):
                                    st.markdown("📬 **Entrega tu archivo de ejercicios resueltos:**")
                                    nombre_al = st.text_input("Apellidos y Nombre del Alumno:")
                                    archivo_al = st.file_uploader("Adjunta tu trabajo finalizado (PDF o Imagen):", type=["pdf","png","jpg","jpeg"])
                                    
                                    if st.form_submit_button("Enviar Ejercicio al Profesorado"):
                                        if nombre_al and archivo_al:
                                            id_al = nombre_al.strip().replace(" ", "_")
                                            id_tar = el["name"].split(".")[0]
                                            
                                            ruta_file = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/{archivo_al.name}"
                                            ruta_json = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/nota.json"
                                            meta = {"nota": "Sin calificar", "feedback": "Pendiente de revisión.", "fecha": datetime.now().strftime("%d/%m/%Y")}
                                            
                                            with st.spinner("Subiendo archivo al servidor de secretaría..."):
                                                if enviar_archivo(ruta_file, archivo_al.getvalue(), "Entrega") and enviar_archivo(ruta_json, json.dumps(meta).encode("utf-8"), "Meta"):
                                                    st.success(f"✔️ ¡Excelente! El documento '{archivo_al.name}' ha sido entregado correctamente. Se ha notificado al profesorado.")
                                        else:
                                            st.warning("Completa tu nombre y adjunta un archivo antes de enviar.")
                            else:
                                nombre_mat = el["name"].replace("_", " ").split(".")[0]
                                st.markdown(f"""
                                    <div class='classwork-item' style='border-left: 5px solid #10b981;'>
                                        <div>
                                            <span class='badge-material'>📖 Material Didáctico</span>
                                            <b style='margin-left:12px; color:#1e293b; font-size:15px;'>{nombre_mat}</b>
                                        </div>
                                        <div>
                                            <a href='{el['download_url']}' target='_blank' style='color:#3b82f6; font-weight:600; text-decoration:none;'>📥 Descargar Apuntes</a>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("Esta unidad temática aún no contiene materiales publicados.")
        else:
            st.info("No hay bloques temáticos dados de alta en esta asignatura.")

# -------------------------------------------------------------------------
# SECCIÓN B: CALENDARIO GLOBAL ESCOLAR
# -------------------------------------------------------------------------
elif navegacion == "📅 Calendario de Entregas":
    st.title("📅 Calendario y Agenda de Tareas del Campus")
    st.write("Mantén tus asignaciones académicas al día consultando las fechas asignadas automáticamente.")
    st.write("---")
    
    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        st.markdown("<h4 style='color:#1e3a8a;'>📆 Entregas Obligatorias Programadas</h4>", unsafe_allow_html=True)
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
                                    <span style='font-size:13px; font-weight:600; text-transform:uppercase;'>📌 Fecha de entrega: {f_limite}</span><br>
                                    <span style='font-size:16px; font-weight:700;'>Actividad: {t_nombre}</span> <br>
                                    <small>Asignatura: {asig.replace('_',' ')}</small>
                                </div>
                            """, unsafe_allow_html=True)
        if not tareas_totales:
            st.info("¡Estás al día! No hay actividades obligatorias agendadas.")
            
    with col_c2:
        st.markdown("<h4 style='color:#1e3a8a;'>✏️ Mi Planificador Personal</h4>", unsafe_allow_html=True)
        if "notas_personales" not in st.session_state:
            st.session_state["notas_personales"] = []
            
        with st.form("form_nota_rapida", clear_on_submit=True):
            rec = st.text_input("Añadir recordatorio personal:")
            f_rec = st.date_input("Día fijado:")
            if st.form_submit_button("Añadir a mi Agenda"):
                if rec:
                    st.session_state["notas_personales"].append({"nota": rec, "fecha": str(f_rec)})
                    st.toast("Recordatorio guardado con éxito.")
                    st.rerun()
                    
        for r in st.session_state["notas_personales"]:
            st.markdown(f"<div class='cal-card-manual'><b>⏱️ {r['fecha']}</b><br>📌 {r['nota']}</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# SECCIÓN C: DESPACHO PEDAGÓGICO DE GESTIÓN (DOCENTES)
# -------------------------------------------------------------------------
elif navegacion == "👩‍🏫 Panel de Gestión Docente":
    st.title("👩‍🏫 Despacho de Gestión y Calificaciones")
    password = st.text_input("Código de Validación Docente:", type="password")
    
    if password == "profe2026":
        st.success("🔒 Sesión de administración iniciada con éxito.")
        st.write("---")
        
        menu_admin = st.selectbox("Selecciona el módulo de gestión:", [
            "🛠️ PUBLICAR TEMAS Y RECURSOS ACADÉMICOS",
            "📥 BANDEJA DE CORRECCIÓN (Ver Respuestas Alumnos)",
            "🏫 ALTA DE NUEVAS ASIGNATURAS"
        ])
        
        # --- 1. SECCIÓN DE CREAR ESTRUCTURA ---
        if menu_admin == "🛠️ PUBLICAR TEMAS Y RECURSOS ACADÉMICOS":
            st.subheader("Carga y Publicación Correlativa")
            asig_list = listar_directorios()
            
            if asig_list:
                asig_sel_profe = st.selectbox("Selecciona la asignatura a gestionar:", asig_list)
                gestion_tema = st.radio("¿Qué deseas hacer?", ["Crear una nueva unidad temática (Carpeta nueva)", "Añadir recursos a una unidad ya existente"])
                
                if gestion_tema == "Crear una nueva unidad temática (Carpeta nueva)":
                    nombre_t = st.text_input("Nombre de la unidad (Ej: Tema 2 Derivadas):")
                    tema_ruta_final = nombre_t.strip().replace(" ", "_")
                else:
                    temas_ex = listar_directorios(asig_sel_profe)
                    tema_ruta_final = st.selectbox("Elige el tema:", temas_ex) if temas_ex else None
                    
                if tema_ruta_final:
                    tipo_archivo = st.radio("Clasificación del Recurso Escolar:", ["📖 Material Formativo (Apuntes, PDF)", "📋 Tarea Evaluante (Con entrega y fecha)"])
                    
                    if tipo_archivo == "📋 Tarea Evaluante (Con entrega y fecha)":
                        f_limite_p = st.date_input("Fijar fecha de vencimiento escolar:")
                        fichero_p = st.file_uploader("Adjunta el archivo del enunciado para los estudiantes:")
                        
                        if st.button("🚀 Publicar Tarea de forma Oficial") and fichero_p:
                            nombre_archivo_git = f"TAREA_{str(f_limite_p)}_{fichero_p.name.replace(' ', '_')}"
                            ruta_completa = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            
                            with st.spinner("Subiendo tarea al servidor central..."):
                                enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init")
                                if enviar_archivo(ruta_completa, fichero_p.getvalue(), "Carga"):
                                    st.success(f"✔️ ¡Proceso completado! La carpeta/tema '{tema_ruta_final.replace('_',' ')}' se ha actualizado. Archivo de tarea '{fichero_p.name}' subido con éxito y fecha fijada en el calendario.")
                                    st.rerun()
                    else:
                        fichero_p = st.file_uploader("Adjunta los apuntes o guías académicas:")
                        if st.button("🚀 Publicar Material Didáctico") and fichero_p:
                            nombre_archivo_git = fichero_p.name.replace(' ', '_')
                            ruta_completa = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            
                            with st.spinner("Subiendo material didáctico..."):
                                enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init")
                                if enviar_archivo(ruta_completa, fichero_p.getvalue(), "Carga"):
                                    st.success(f"✔️ ¡Proceso completado! El Material docente '{fichero_p.name}' ha sido inyectado con éxito en el Tema '{tema_ruta_final.replace('_',' ')}'.")
                                    st.rerun()
            else:
                st.warning("Debes dar de alta una asignatura primero.")

        # --- 2. SECCIÓN DE CORREGIR TAREAS INTEGRADAS ---
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
                            <div style='background-color:#ffffff; border:1px solid #dadce0; padding:20px; border-radius:12px; margin-bottom:15px; box-shadow:0 4px 6px rgba(0,0,0,0.02);'>
                                👤 <b>Estudiante evaluado:</b> {alumno_eval.replace('_',' ')}<br>
                                📄 <b>Archivo de solución enviado:</b> {name_doc.replace('_',' ')}<br><br>
                                <a href='{url_doc}' target='_blank'><button style='background-color:#3b82f6; color:white; border:none; padding:10px 18px; border-radius:6px; font-weight:600; cursor:pointer;'>📥 Descargar trabajo entregado</button></a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col_e1, col_e2 = st.columns([1, 2])
                        with col_e1:
                            input_n = st.text_input("Calificación final:", value=str(nota_v))
                        with col_e2:
                            input_f = st.text_area("Comentarios pedagógicos (Feedback):", value=feedback_v)
                            
                        if st.button("💾 Publicar Nota en el Expediente"):
                            nueva_data = {"nota": input_n, "feedback": input_f, "fecha": datetime.now().strftime("%d/%m/%Y")}
                            if enviar_archivo(ruta_json_nota, json.dumps(nueva_data).encode("utf-8"), "Nota guardada"):
                                st.success(f"✔️ ¡Calificación guardada! La nota del alumno '{alumno_eval.replace('_',' ')}' ha sido registrada correctamente en el boletín privado.")
                                st.rerun()
                    else:
                        st.warning("No hay entregas para esta tarea.")
                else:
                    st.info("No hay histórico de tareas entregadas en esta asignatura.")
            else:
                st.warning("No hay asignaturas configuradas.")

        # --- 3. SECCIÓN DE ASIGNATURAS NUEVAS ---
        elif menu_admin == "🏫 CREAR NUEVA ASIGNATURA":
            st.subheader("Alta de Clases y Asignaturas")
            nueva_asig = st.text_input("Nombre de la nueva Asignatura (Ej: Matematicas 1º Bach):")
            if st.button("Consolidar en el Sistema Central"):
                if nueva_asig:
                    clean_asig = nueva_asig.strip().replace(" ", "_")
                    if enviar_archivo(f"{clean_asig}/.gitkeep", b"", "Alta"):
                        st.success(f"✔️ ¡Éxito! La asignatura '{nueva_asig}' ha sido creada y guardada correctamente en el registro central escolar.")
                        st.rerun()
