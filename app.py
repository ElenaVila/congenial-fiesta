import streamlit as st
import requests
import base64
import json
from datetime import datetime

# =========================================================================
# 1. DISEÑO DE INTERFAZ PROFESIONAL (CSS GOOGLE CLASSROOM)
# =========================================================================
st.set_page_config(page_title="Google Classroom - Aula Virtual", layout="wide")

st.markdown("""
    <style>
    /* Estilo del contenedor principal */
    .main { background-color: #f8f9fa; }
    
    /* Grid y Tarjetas de Asignaturas de la página de inicio */
    .subject-container {
        display: flex;
        flex-wrap: wrap;
        gap: 24px;
        margin-top: 20px;
    }
    .subject-card {
        background-color: white;
        border: 1px solid #dadce0;
        border-radius: 8px;
        width: 320px;
        min-height: 180px;
        overflow: hidden;
        box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .subject-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 4px 8px 0 rgba(60,64,67,0.3), 0 2px 6px 2px rgba(60,64,67,0.15);
    }
    .subject-banner {
        background: linear-gradient(135px, #1a73e8, #1557b0);
        color: white;
        padding: 16px;
        min-height: 90px;
    }
    .subject-body {
        padding: 16px;
        background-color: white;
        color: #3c4043;
        font-size: 14px;
    }

    /* Filas de materiales y tareas dentro de los temas */
    .classwork-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 20px;
        background-color: #ffffff;
        border: 1px solid #dadce0;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .classwork-item:hover { background-color: #f8f9fa; }
    
    /* Etiquetas visuales */
    .badge-task {
        background-color: #fee2e2;
        color: #b91c1c;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-material {
        background-color: #d1fae5;
        color: #065f46;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 12px;
    }
    
    /* Tarjetas del Calendario */
    .cal-card-auto {
        background-color: #e8f0fe;
        border-left: 5px solid #1a73e8;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 10px;
        color: #1967d2;
    }
    .cal-card-manual {
        background-color: #fffde7;
        border-left: 5px solid #fbc02d;
        padding: 15px;
        border-radius: 6px;
        margin-bottom: 10px;
        color: #f57f17;
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

# Manejo del estado del curso seleccionado
if "curso_activo" not in st.session_state:
    st.session_state["curso_activo"] = None

# =========================================================================
# 3. MENÚ DESPLEGABLE VERTICAL GLOBAL (SIDEBAR)
# =========================================================================
st.sidebar.title("📌 Menú Escolar")
navegacion = st.sidebar.radio("Ir a la sección:", [
    "📚 Mis Asignaturas",
    "📅 Calendario Global",
    "👩‍🏫 Panel de la Profesora"
])

# Reiniciar curso si cambiamos de pestaña principal en el menú vertical
if navegacion != "📚 Mis Asignaturas":
    st.session_state["curso_activo"] = None

# -------------------------------------------------------------------------
# VISTA A: MIS ASIGNATURAS (TABLÓN PRINCIPAL DE ENTRADA O INTERIOR DEL CURSO)
# -------------------------------------------------------------------------
if navegacion == "📚 Mis Asignaturas":
    
    # 🏠 CASO 1: EL ALUMNO ESTÁ EN LA RAÍZ (VE LAS TARJETAS GRANDES)
    if st.session_state["curso_activo"] is None:
        st.title("🏫 Mis Clases de Google Classroom")
        st.write("Selecciona una de tus materias asignadas para ver los contenidos correlativos.")
        
        asignaturas = listar_directorios()
        
        if asignaturas:
            # Renderizado estético de las tarjetas con CSS
            st.markdown("<div class='subject-container'>", unsafe_allow_html=True)
            cols = st.columns(3)
            for idx, asig in enumerate(asignaturas):
                with cols[idx % 3]:
                    st.markdown(f"""
                        <div class='subject-card'>
                            <div class='subject-banner'>
                                <h3 style='margin:0; font-size:20px; font-weight:500;'>📐 {asig.replace('_', ' ')}</h3>
                                <p style='margin:4px 0 0 0; font-size:12px; opacity:0.8;'>Curso 2026 — Elena Vila</p>
                            </div>
                            <div class='subject-body'>
                                📝 Profesor Titular: Elena Vila<br>
                                <span style='font-size:11px; color:#70757a;'>Haga clic abajo para desplegar unidades</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Entrar a {asig.replace('_', ' ')}", key=f"entrar_{asig}"):
                        st.session_state["curso_activo"] = asig
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No hay asignaturas registradas todavía.")

    # 📖 CASO 2: EL ALUMNO YA HIZO CLIC EN UNA ASIGNATURA (ENTRA A VER LOS TEMAS CORRELATIVOS)
    else:
        asig_actual = st.session_state["curso_activo"]
        
        if st.button("⬅️ Volver a todas las asignaturas"):
            st.session_state["curso_activo"] = None
            st.rerun()
            
        st.title(f"📘 Curso: {asig_actual.replace('_', ' ')}")
        st.write("A continuación dispones de los temas ordenados de manera correlativa. Despliégalos para ver su contenido.")
        st.write("---")
        
        temas = listar_directorios(asig_actual)
        if temas:
            for tema in temas:
                # Estructura correlativa vertical usando expanders de Streamlit
                with st.expander(f"📁 {tema.replace('_', ' ')}", expanded=False):
                    elementos_tema = api_git(f"{asig_actual}/{tema}")
                    archivos = [e for e in elementos_tema if e["type"] == "file" and e["name"] != ".gitkeep"]
                    
                    if archivos:
                        for el in archivos:
                            es_tarea = el["name"].startswith("TAREA_")
                            
                            if es_tarea:
                                # Desglosar formato TAREA_YYYY-MM-DD_Nombre
                                partes = el["name"].split("_", 2)
                                f_limite = partes[1] if len(partes) > 1 else "Sin fecha"
                                t_nombre = partes[2].replace("_", " ").split(".")[0] if len(partes) > 2 else "Tarea"
                                
                                st.markdown(f"""
                                    <div class='classwork-item'>
                                        <div>
                                            <span class='badge-task'>📋 Tarea Evaluante</span>
                                            <b style='margin-left:10px; color:#202124;'>{t_nombre}</b>
                                        </div>
                                        <div>
                                            <span style='font-size:13px; color:#70757a; margin-right:15px;'>Vence el: <b>{f_limite}</b></span>
                                            <a href='{el['download_url']}' target='_blank' style='color:#1a73e8; font-weight:bold; text-decoration:none;'>📥 Abrir Ficha</a>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Formulario de entrega integrado directamente bajo la tarea en su expander
                                with st.form(f"f_entrega_{el['name']}", clear_on_submit=True):
                                    st.write("✏️ **Buzón de entrega para el alumno:**")
                                    nombre_al = st.text_input("Introduce tus Apellidos y Nombre:")
                                    archivo_al = st.file_uploader("Sube tu archivo de resolución (PDF o Imagen):", type=["pdf","png","jpg","jpeg"])
                                    
                                    if st.form_submit_button("Subir Entrega Oficial"):
                                        if nombre_al and archivo_al:
                                            id_al = nombre_al.strip().replace(" ", "_")
                                            id_tar = el["name"].split(".")[0]
                                            
                                            ruta_file = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/{archivo_al.name}"
                                            ruta_json = f"Entregas_Globales/{asig_actual}/{id_tar}/{id_al}/nota.json"
                                            meta = {"nota": "Sin calificar", "feedback": "Pendiente de revisión.", "fecha": datetime.now().strftime("%d/%m/%Y")}
                                            
                                            with st.spinner("Subiendo trabajo al servidor escolar..."):
                                                if enviar_archivo(ruta_file, archivo_al.getvalue(), "Entrega") and enviar_archivo(ruta_json, json.dumps(meta).encode("utf-8"), "Meta"):
                                                    st.success(f"🎉 ¡Tu documento '{archivo_al.name}' ha sido enviado con éxito! Tu profesora ya puede revisarlo.")
                                        else:
                                            st.warning("Debes rellenar tu nombre y adjuntar un archivo.")
                            else:
                                # Es un material de apuntes regular
                                nombre_mat = el["name"].replace("_", " ").split(".")[0]
                                st.markdown(f"""
                                    <div class='classwork-item'>
                                        <div>
                                            <span class='badge-material'>📖 Material</span>
                                            <b style='margin-left:10px; color:#202124;'>{nombre_mat}</b>
                                        </div>
                                        <div>
                                            <a href='{el['download_url']}' target='_blank' style='color:#1a73e8; font-weight:bold; text-decoration:none;'>📥 Descargar apuntes</a>
                                        </div>
                                    </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("Este bloque temático aún no tiene materiales publicados.")
        else:
            st.info("Esta asignatura aún no tiene temas correlativos cargados.")

# -------------------------------------------------------------------------
# VISTA B: CALENDARIO GLOBAL Y BOLETÍN DE NOTAS
# -------------------------------------------------------------------------
elif navegacion == "📅 Calendario Global":
    st.title("📅 Calendario y Seguimiento del Alumnado")
    
    col_c1, col_c2 = st.columns([2, 1])
    
    with col_c1:
        st.subheader("⏱️ Fechas Límites del Curso (Automático)")
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
                                    <b>📅 {f_limite}</b> — 📋 <b>{t_nombre}</b> (Materia: {asig.replace('_',' ')})
                                </div>
                            """, unsafe_allow_html=True)
        if not tareas_totales:
            st.info("No hay tareas obligatorias programadas en el calendario.")
            
    with col_c2:
        st.subheader("📌 Mis Recordatorios")
        if "notas_personales" not in st.session_state:
            st.session_state["notas_personales"] = []
            
        with st.form("form_nota_rapida", clear_on_submit=True):
            rec = st.text_input("¿Qué tienes pendiente?")
            f_rec = st.date_input("Fecha:")
            if st.form_submit_button("Guardar"):
                if rec:
                    st.session_state["notas_personales"].append({"nota": rec, "fecha": str(f_rec)})
                    st.success("Recordatorio apuntado.")
                    st.rerun()
                    
        for r in st.session_state["notas_personales"]:
            st.markdown(f"<div class='cal-card-manual'><b>⏱️ {r['fecha']}</b><br>{r['nota']}</div>", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# VISTA C: DESPACHO Y PANEL DE CONTROL DE LA PROFESORA
# -------------------------------------------------------------------------
elif navegacion == "👩‍🏫 Panel de la Profesora":
    st.title("👩‍🏫 Despacho de Administración — Profesora Elena Vila")
    password = st.text_input("Introduce el código de acceso:", type="password")
    
    if password == "profe2026":
        st.success("🔒 Identidad confirmada de forma segura.")
        st.write("---")
        
        menu_admin = st.selectbox("Elige la herramienta de gestión:", [
            "🛠️ CREAR TEMAS Y SUBIR RECURSOS",
            "📥 CORREGIR ENTREGAS DE ALUMNOS",
            "🏫 ALTA DE ASIGNATURAS"
        ])
        
        # --- 1. SECCIÓN DE CREAR ESTRUCTURA ---
        if menu_admin == "🛠️ CREAR TEMAS Y SUBIR RECURSOS":
            st.subheader("Carga y Publicación Correlativa")
            asig_list = listar_directorios()
            
            if asig_list:
                asig_sel_profe = st.selectbox("Selecciona la asignatura a gestionar:", asig_list)
                gestion_tema = st.radio("¿Qué deseas hacer?", ["Crear una carpeta/tema nuevo", "Añadir recursos a un tema existente"])
                
                if gestion_tema == "Crear una carpeta/tema nuevo":
                    nombre_t = st.text_input("Nombre de la unidad (Ej: Tema 2 Derivadas):")
                    tema_ruta_final = nombre_t.strip().replace(" ", "_")
                else:
                    temas_ex = listar_directorios(asig_sel_profe)
                    tema_ruta_final = st.selectbox("Elige el tema:", temas_ex) if temas_ex else None
                    
                if tema_ruta_final:
                    tipo_archivo = st.radio("¿Qué tipo de recurso vas a colgar?", ["📖 Material (Apuntes, PDF)", "📋 Tarea (Para que entreguen con fecha)"])
                    
                    if tipo_archivo == "📋 Tarea (Para que entreguen con fecha)":
                        f_limite_p = st.date_input("Fijar fecha de vencimiento en el calendario:")
                        fichero_p = st.file_uploader("Adjunta el archivo de enunciado:")
                        
                        if st.button("🚀 Publicar Tarea Oficial") and fichero_p:
                            nombre_archivo_git = f"TAREA_{str(f_limite_p)}_{fichero_p.name.replace(' ', '_')}"
                            ruta_completa = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            
                            with st.spinner("Subiendo tarea..."):
                                enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init")
                                if enviar_archivo(ruta_completa, fichero_p.getvalue(), "Carga"):
                                    st.success(f"✔️ ¡Acción completada! El Tema '{tema_ruta_final.replace('_',' ')}' ha sido actualizado con éxito y la Tarea '{fichero_p.name}' ya es visible en el calendario.")
                                    st.rerun()
                    else:
                        fichero_p = st.file_uploader("Adjunta los apuntes o guías de estudio:")
                        if st.button("🚀 Publicar Material Formativo") and fichero_p:
                            nombre_archivo_git = fichero_p.name.replace(' ', '_')
                            ruta_completa = f"{asig_sel_profe}/{tema_ruta_final}/{nombre_archivo_git}"
                            
                            with st.spinner("Subiendo apuntes..."):
                                enviar_archivo(f"{asig_sel_profe}/{tema_ruta_final}/.gitkeep", b"", "Init")
                                if enviar_archivo(ruta_completa, fichero_p.getvalue(), "Carga"):
                                    st.success(f"✔️ ¡Acción completada! El Material formativo '{fichero_p.name}' ha sido inyectado con éxito en el Tema '{tema_ruta_final.replace('_',' ')}'.")
                                    st.rerun()
            else:
                st.warning("Debes dar de alta una asignatura primero.")

        # --- 2. SECCIÓN DE CORREGIR TAREAS INTEGRADAS ---
        elif menu_admin == "📥 CORREGIR ENTREGAS DE ALUMNOS":
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
                            <div style='background-color:#ffffff; border:1px solid #dadce0; padding:20px; border-radius:8px; margin-bottom:15px;'>
                                👤 <b>Estudiante:</b> {alumno_eval.replace('_',' ')}<br>
                                📄 <b>Archivo enviado:</b> {name_doc.replace('_',' ')}<br><br>
                                <a href='{url_doc}' target='_blank'><button style='background-color:#1a73e8; color:white; border:none; padding:10px 16px; border-radius:4px; font-weight:bold; cursor:pointer;'>📥 Descargar e inspeccionar ejercicio</button></a>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        col_e1, col_e2 = st.columns([1, 2])
                        with col_e1:
                            input_n = st.text_input("Calificación oficial:", value=str(nota_v))
                        with col_e2:
                            input_f = st.text_area("Feedback pedagógico:", value=feedback_v)
                            
                        if st.button("💾 Publicar Nota en el Expediente"):
                            nueva_data = {"nota": input_n, "feedback": input_f, "fecha": datetime.now().strftime("%d/%m/%Y")}
                            if enviar_archivo(ruta_json_nota, json.dumps(nueva_data).encode("utf-8"), "Nota guardada"):
                                st.success(f"✔️ Calificación del alumno '{alumno_eval.replace('_',' ')}' guardada correctamente y enviada a su boletín privado.")
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
            nueva_asig = st.text_input("Nombre de la asignatura (Ej: Matematicas 1º Bach):")
            if st.button("Consolidar Clase"):
                if nueva_asig:
                    clean_asig = nueva_asig.strip().replace(" ", "_")
                    if enviar_archivo(f"{clean_asig}/.gitkeep", b"", "Alta"):
                        st.success(f"✔️ ¡Proceso completado con éxito! La asignatura '{nueva_asig}' ha sido creada y guardada en el registro central escolar.")
                        st.rerun()
