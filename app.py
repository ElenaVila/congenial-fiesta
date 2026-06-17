import streamlit as st
import requests
import base64
import json
from datetime import datetime

# =========================================================================
# 1. DISEÑO ESTÉTICO REVOLUCIONARIO: COLORES, VIDA Y BALANCE VISUAL
# =========================================================================
st.set_page_config(page_title="Aula Virtual - Campus Escolar", layout="wide")

# Inyección de estilos CSS globales para fondos, botones del instituto y textos
st.markdown("""
    <style>
    /* Fondo general del campus con un tono azulado muy limpio */
    .main { background-color: #f0f4f8; }
    
    /* Forzar que los títulos de Streamlit tengan fuentes escolares atractivas */
    h1, h2, h3, h4 {
        font-family: 'Comic Sans MS', 'Segoe UI', sans-serif !important;
        font-weight: bold !important;
    }
    
    /* Botones de las asignaturas estilizados y con colores vivos */
    div.stButton > button {
        background: linear-gradient(135px, #3b82f6 0%, #1d4ed8 100%) !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        padding: 10px 24px !important;
        font-weight: bold !important;
        width: 100% !important;
        box-shadow: 0 4px 6px rgba(29, 78, 216, 0.2) !important;
        transition: all 0.3s ease !important;
    }
    div.stButton > button:hover {
        transform: scale(1.03) !important;
        box-shadow: 0 6px 12px rgba(29, 78, 216, 0.3) !important;
    }
    
    /* Elementos decorativos dentro de los expanders correlativos */
    .item-doc {
        padding: 10px;
        background-color: #f8fafc;
        border-radius: 8px;
        border-left: 5px solid #10b981;
        margin-bottom: 8px;
    }
    .item-tarea {
        padding: 10px;
        background-color: #fff5f5;
        border-radius: 8px;
        border-left: 5px solid #ef4444;
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
# 2. CORE: CONECTIVIDAD INVISIBLE (MANTIENE LA UTILIDAD SIN TOCARLA)
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
# 3. MENÚ DESPLEGABLE VERTICAL GLOBAL (SIDEBAR ESTILIZADA)
# =========================================================================
st.sidebar.markdown("<h1 style='text-align: center; color: #1e3a8a; font-size: 28px;'>🏫 Menú Escolar</h1>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; color: #64748b; font-size: 13px;'>Instituto / Colegio Virtual</p>", unsafe_allow_html=True)
st.sidebar.write("---")

navegacion = st.sidebar.radio("Navegación del Campus:", [
    "📚 Mis Asignaturas",
    "📅 Calendario de Entregas",
    "👩‍🏫 Panel de Gestión Docente"
])

if navegacion != "📚 Mis Asignaturas":
    st.session_state["curso_activo"] = None

# -------------------------------------------------------------------------
# VISTA A: MIS ASIGNATURAS (REDISEÑO VISUAL ABSOLUTO)
# -------------------------------------------------------------------------
if navegacion == "📚 Mis Asignaturas":
    
    # 🏠 CASO 1: LA PORTADA PRINCIPAL (CON TITULOS REALES Y COLOR)
    if st.session_state["curso_activo"] is None:
        
        # Corregido el banner gigante vacío de la imagen image_89791f.png usando st.container nativo con color
        with st.container(border=True):
            st.markdown("<h1 style='color: #1e3a8a; margin: 0; font-size: 36px;'>🏫 Aula Virtual — Centro Educativo</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #4b5563; font-size: 16px; margin-top: 5px;'>¡Bienvenido de nuevo! Selecciona una de tus asignaturas para ver el tablón y los temas del curso.</p>", unsafe_allow_html=True)
        
        st.write("")
        st.write("")
        
        asignaturas = listar_directorios()
        
        if asignaturas:
            cols = st.columns(3)
            for idx, asig in enumerate(asignaturas):
                with cols[idx % 3]:
                    
                    # Filtramos el nombre para aplicar portadas escolares con colores vivos y temáticos
                    nombre_lower = asig.lower()
                    if "matematica" in nombre_lower or "funciones" in nombre_lower:
                        color_fondo = "#fce7f3"  # Fondo rosa chicle alegre
                        color_borde = "#ec4899"  # Borde rosa fuerte
                        color_texto = "#9d174d"  # Texto oscuro
                        icono = "📐"
                        imagen_subtitulo = "Álgebra, Cálculo y Geometría"
                    elif "ciencia" in nombre_lower or "fisica" in nombre_lower or "quimica" in nombre_lower:
                        color_fondo = "#d1fae5"  # Fondo verde menta
                        color_borde = "#10b981"  # Borde verde
                        color_texto = "#065f46"  # Texto oscuro
                        icono = "🔬"
                        imagen_subtitulo = "Laboratorio y Experimentación"
                    elif "tarea" in nombre_lower:
                        color_fondo = "#ffedd5"  # Fondo naranja suave
                        color_borde = "#f97316"  # Borde naranja
                        color_texto = "#9a3412"  # Texto oscuro
                        icono = "📂"
                        imagen_subtitulo = "Buzón de Entregas Alumnos"
                    else:
                        color_fondo = "#e0f2fe"  # Fondo azul cielo
                        color_borde = "#3b82f6"  # Borde azul
                        color_texto = "#1e40af"  # Texto oscuro
                        icono = "📘"
                        imagen_subtitulo = "Curso General Formativo"
                    
                    # Creamos la portada con un contenedor nativo estilizado por colores
                    with st.container(border=True):
                        st.markdown(f"""
                            <div style='background-color: {color_fondo}; border: 2px solid {color_borde}; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 15px;'>
                                <span style='font-size: 50px;'>{icono}</span>
                                <h3 style='color: {color_texto}; margin: 10px 0 0 0; font-size: 20px;'>{asig.replace('_', ' ')}</h3>
                                <p style='color: {color_texto}; opacity: 0.8; font-size: 13px; margin: 5px 0 0 0;'>{imagen_subtitulo}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # El botón de acción integrado de forma perfecta justo debajo de la portada a color
                        if st.button(f"Entrar a la Clase", key=f"btn_{asig}"):
                            st.session_state["curso_activo"] = asig
                            st.rerun()
        else:
            st.info("No hay asignaturas creadas en el sistema educativo todavía.")

    # 📖 CASO 2: EL INTERIOR DEL CURSO (TEMAS VERTICALES DE COLEGIO)
    else:
        asig_actual = st.session_state["curso_activo"]
        
        if st.button("⬅️ Volver a las Asignaturas"):
            st.session_state["curso_activo"] = None
            st.rerun()
            
        with st.container(border=True):
            st.markdown(f"<h1 style='color: #2563eb; margin: 0;'>📘 Aula: {asig_actual.replace('_', ' ')}</h1>", unsafe_allow_html=True)
            st.markdown("<p style='color: #4b5563; font-size: 14px; margin: 5px 0 0 0;'>Unidades didácticas organizadas de forma secuencial y correlativa para el alumno.</p>", unsafe_allow_html=True)
        
        st.write("---")
        
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
                                    <div class='item-tarea'>
                                        <span style='background-color: #ef4444; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;'>OBLIGATORIO</span>
                                        <b style='margin-left: 10px;'>📋 {t_nombre}</b> — <span style='font-size: 12px; color: #b91c1c;'>Fecha límite: {f_limite}</span>
                                        <span style='float: right;'><a href='{el['download_url']}' target='_blank' style='color: #dc2626; font-weight: bold; text-decoration: none;'>📥 Descargar Ficha</a></span>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Formulario dentro del expander
                                with st.form(f"f_entrega_{el['name']}", clear_on_submit=True):
                                    st.markdown("🔒 **Zona de Entrega de Tarea para el Alumno:**")
                                    nombre_al = st.text_input("Apellidos y Nombre completo del estudiante:")
                                    archivo_al = st.file_uploader("Adjunta tu boletín completado (PDF o Imagen):", type=["pdf","png","jpg","jpeg"])
                                    
                                    if st.form_submit_button("Subir Ejercicio Completado"):
                                        if nombre_al and archivo_al:
                                            id_al = nombre_al.strip().replace(" ", "_")
                                            id_tar = el["name"].split(".")[0]
                                            
                                            ruta_file = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/{archivo_al.name}"
                                            ruta_json = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/nota.json"
                                            meta = {"nota": "Sin calificar", "feedback": "Pendiente de revisión.", "fecha": datetime.now().strftime("%d/%m/%Y")}
                                            
                                            if enviar_archivo(ruta_file, archivo_al.getvalue(), "Entrega") and enviar_archivo(ruta_json, json.dumps(meta).encode("utf-8"), "Meta"):
                                                st.success(f"✔️ ¡Felicidades! Tu documento '{archivo_al.name}' ha sido entregado en secretaría virtual de forma correcta.")
                            else:
                                nombre_mat = el["name"].replace("_", " ").split(".")[0]
                                st.markdown(f"""
                                    <div class='item-doc'>
                                        <span style='background-color: #10b981; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;'>APUNTES</span>
                                        <b style='margin-left: 10px;'>📖 {nombre_mat}</b>
                                        <span style='float: right;'><a href='{el['download_url']}' target='_blank' style='color: #047857; font-weight: bold; text-decoration: none;'>📥 Descargar Material</a></span>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("Esta carpeta temática no tiene documentos publicados todavía.")
        else:
            st.info("No se han registrado unidades de estudio en este curso.")

# -------------------------------------------------------------------------
# VISTA B: CALENDARIO DE ENTREGAS
# -------------------------------------------------------------------------
elif navegacion == "📅 Calendario de Entregas":
    st.title("📅 Calendario Escolar y Agenda")
    st.write("---")
    
    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        st.markdown("<h3 style='color: #1e3a8a;'>📆 Fechas Oficiales de Exámenes y Tareas</h3>", unsafe_allow_html=True)
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
                                    <b>⏰ LÍMITE: {f_limite}</b> — 📋 Actividad: <u>{t_nombre}</u> en la materia {asig.replace('_',' ')}
                                </div>
                            """, unsafe_allow_html=True)
        if not tareas_totales:
            st.info("¡Estás al día! No hay tareas programadas en el calendario escolar.")
            
    with col_c2:
        st.markdown("<h3 style='color: #1e3a8a;'>📌 Mis Notas Rápidas</h3>", unsafe_allow_html=True)
        if "notas_personales" not in st.session_state:
            st.session_state["notas_personales"] = []
            
        with st.form("form_nota_rapida", clear_on_submit=True):
            rec = st.text_input("Añadir recordatorio:")
            f_rec = st.date_input("Para el día:")
            if st.form_submit_button("Guardar"):
                if rec:
                    st.session_state["notas_personales"].append({"nota": rec, "fecha": str(f_rec)})
                    st.rerun()
                    
        for r in st.session_state["notas_personales"]:
            st.markdown(f"<div class='cal-card-manual'><b>⏱️ {r['fecha']}</b><br>{r['nota']}</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# VISTA C: GESTIÓN DOCENTE (PROFESORADO)
# -------------------------------------------------------------------------
elif navegacion == "👩‍🏫 Panel de Gestión Docente":
    st.title("👩‍🏫 Despacho de Dirección y Profesorado")
    password = st.text_input("Código de Validación:", type="password")
    
    if password == "profe2026":
        st.success("🔒 Sesión administrativa autorizada.")
        st.write("---")
        
        menu_admin = st.selectbox("Módulo a gestionar:", [
            "🛠️ PUBLICAR TEMAS Y RECURSOS",
            "📥 BANDEJA DE CORRECCIÓN (Ver Respuestas)",
            "🏫 ALTA DE ASIGNATURAS"
        ])
        
        if menu_admin == "🛠️ PUBLICAR TEMAS Y RECURSOS":
            st.subheader("Carga y Publicación Correlativa")
            asig_list = listar_directorios()
            
            if asig_list:
                asig_sel_profe = st.selectbox("Selecciona asignatura:", asig_list)
                gestion_tema = st.radio("Acción:", ["Crear una carpeta/tema nuevo", "Añadir recursos a un tema existente"])
                
                if gestion_tema == "Crear una carpeta/tema nuevo":
                    nombre_t = st.text_input("Nombre de la unidad (Ej: Tema 2 Derivadas):")
                    tema_ruta_final = nombre_t.strip().replace(" ", "_")
                else:
                    temas_ex = listar_directorios(asig_sel_profe)
                    tema_ruta_final = st.selectbox("Elige el tema:", temas_ex) if temas_ex else None
                    
                if tema_ruta_final:
                    tipo_archivo = st.radio("Tipo de Recurso:", ["📖 Material (Apuntes, PDF)", "📋 Tarea (Para entregar con fecha)"])
                    
                    if tipo_archivo == "📋 Tarea (Para entregar con fecha)":
                        f_limite_p = st.date_input("Fijar vencimiento escolar:")
                        fichero_p = st.file_uploader("Adjunta el archivo del enunciado:")
                        
                        if st.button("🚀 Publicar Tarea de forma Oficial") and fichero_p:
                            nombre_archivo_git = f"TAREA_{str(f_limite_p)}_{fichero_p.name.replace(' ', '_')}"
                            ruta_complete = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            
                            with st.spinner("Subiendo tarea..."):
                                enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init")
                                if enviar_archivo(ruta_complete, fichero_p.getvalue(), "Carga"):
                                    st.success(f"✔️ ¡Acción completada! El Tema '{tema_ruta_final.replace('_',' ')}' ha sido actualizado con éxito y la Tarea '{fichero_p.name}' ya es visible.")
                                    st.rerun()
                    else:
                        fichero_p = st.file_uploader("Adjunta los apuntes o guías:")
                        if st.button("🚀 Publicar Material Didáctico") and fichero_p:
                            nombre_archivo_git = fichero_p.name.replace(' ', '_')
                            ruta_complete = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            
                            with st.spinner("Subiendo apuntes..."):
                                enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init")
                                if enviar_archivo(ruta_complete, fichero_p.getvalue(), "Carga"):
                                    st.success(f"✔️ ¡Acción completada! El Material docente '{fichero_p.name}' ha sido inyectado con éxito.")
                                    st.rerun()

        elif menu_admin == "📥 BANDEJA DE CORRECCIÓN (Ver Respuestas)":
            st.subheader("Revisión de Ejercicios Entregados")
            asig_list = listar_directorios()
            
            if asig_list:
                asig_eval = st.selectbox("Selecciona Asignatura:", asig_list)
                entregas_raiz = api_git(f"Entregas_Globales/{asig_eval}")
                carpetas_tareas = [c["name"] for c in entregas_raiz if c["type"] == "dir"]
                
                if carpetas_tareas:
                    tarea_eval = st.selectbox("Selecciona la Tarea:", carpetas_tareas)
                    alumnos_lista = api_git(f"Entregas_Globales/{asig_eval}/{tarea_eval}")
                    id_alumnos = [a["name"] for a in alumnos_lista if a["type"] == "dir"]
                    
                    if id_alumnos:
                        alumno_eval = st.selectbox("Selecciona el alumno:", id_alumnos)
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
                                👤 <b>Estudiante evaluado:</b> {alumno_eval.replace('_',' ')}<br>
                                📄 <b>Archivo enviado:</b> {name_doc.replace('_',' ')}<br><br>
                                <a href='{url_doc}' target='_blank'><button style='background-color:#3b82f6; color:white; border:none; padding:10px 18px; border-radius:6px; font-weight:bold; cursor:pointer;'>📥 Descargar trabajo entregado</button></a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col_e1, col_e2 = st.columns([1, 2])
                        with col_e1:
                            input_n = st.text_input("Calificación final:", value=str(nota_v))
                        with col_e2:
                            input_f = st.text_area("Feedback pedagógico:", value=feedback_v)
                            
                        if st.button("💾 Publicar Nota"):
                            nueva_data = {"nota": input_n, "feedback": input_f, "fecha": datetime.now().strftime("%d/%m/%Y")}
                            if enviar_archivo(ruta_json_nota, json.dumps(nueva_data).encode("utf-8"), "Nota guardada"):
                                st.success(f"✔️ Calificación del alumno '{alumno_eval.replace('_',' ')}' registrada correctamente.")
                                st.rerun()

        elif menu_admin == "🏫 CREAR NUEVA ASIGNATURA":
            st.subheader("Alta de Clases")
            nueva_asig = st.text_input("Nombre de la asignatura (Ej: Historia 1º Bach):")
            if st.button("Consolidar en el Registro Central"):
                if nueva_asig:
                    clean_asig = nueva_asig.strip().replace(" ", "_")
                    if enviar_archivo(f"{clean_asig}/.gitkeep", b"", "Alta"):
                        st.success(f"✔️ ¡Éxito! La asignatura '{nueva_asig}' ha sido creada correctamente.")
                        st.rerun()
