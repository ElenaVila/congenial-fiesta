import streamlit as st
import requests
import base64
import json
from datetime import datetime
import pandas as pd

# =========================================================================
# 1. IDENTIDAD VISUAL INSTITUCIONAL Y CONFIGURACIÓN GENERAL
# =========================================================================
st.set_page_config(page_title="Campus Escolar - Aula Virtual", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Segoe+UI:wght@400;600;700&display=swap');
    html, body, [data-testid="stAppViewContainer"] {
        font-family: 'Segoe UI', sans-serif !important;
        background-color: #f8fafc !important;
    }
    .main-title { color: #1e3a8a; font-weight: 700; margin-bottom: 20px; }
    .recurso-bloque {
        padding: 18px;
        background-color: #ffffff;
        border-radius: 10px;
        border-left: 6px solid #3b82f6;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .status-entregado {
        background-color: #f0fdf4;
        border: 1px solid #bbf7d0;
        color: #15803d;
        padding: 12px 16px;
        border-radius: 8px;
        font-weight: 600;
        margin-top: 10px;
    }
    .grade-box {
        background: linear-gradient(135px, #ffffff 0%, #f0fdf4 100%);
        border: 1px solid #bbf7d0;
        border-left: 6px solid #16a34a;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    </style>
""", unsafe_allow_html=True)

# Conexión Segura con GitHub Secrets
USUARIO_GIT = "ElenaVila"
REPOSITORIO_GIT = "congenial-fiesta"
RAMA = "MATEMATICAS"
TOKEN_GITHUB = st.secrets["TOKEN_GITHUB"]

# Base de datos local de alumnos integrada para el Login (Puedes ampliarla como quieras)
DB_USUARIOS = {
    "alumno1": {"clave": "mates123", "nombre": "Juan Pérez"},
    "alumno2": {"clave": "mates456", "nombre": "Ana Gómez"},
    "alumno3": {"clave": "mates789", "nombre": "Carlos Rodríguez"},
    "admin": {"clave": "profe2026", "nombre": "Elena Vila (Dirección)"}
}

# =========================================================================
# 2. MAQUINARIA DE COMUNICACIÓN CON LA API DE GITHUB
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

# Inicializador de variables de sesión
if "usuario_identificado" not in st.session_state:
    st.session_state["usuario_identificado"] = None
if "curso_activo" not in st.session_state:
    st.session_state["curso_activo"] = None

# =========================================================================
# 3. CONTROL DE ACCESO GLOBAL: LOGIN PROFESIONAL CON CREDENCIALES
# =========================================================================
st.sidebar.markdown("<h2 style='color:#1e3a8a; font-weight:700;'>🔑 Control de Accesos</h2>", unsafe_allow_html=True)

if st.session_state["usuario_identificado"] is None:
    with st.sidebar.form("form_login"):
        input_user = st.text_input("Usuario de acceso:")
        input_pass = st.text_input("Contraseña:", type="password")
        boton_login = st.form_submit_button("Iniciar Sesión")
        
        if boton_login:
            if input_user in DB_USUARIOS and DB_USUARIOS[input_user]["clave"] == input_pass:
                st.session_state["usuario_identificado"] = input_user
                st.sidebar.success(f"Bienvenido/a, {DB_USUARIOS[input_user]['nombre']}")
                st.rerun()
            else:
                st.sidebar.error("Credenciales inválidas o no registradas.")
else:
    st.sidebar.info(f"Sesión activa: \n**{DB_USUARIOS[st.session_state['usuario_identificado']]['nombre']}**")
    if st.sidebar.button("🔒 Cerrar Sesión"):
        st.session_state["usuario_identificado"] = None
        st.session_state["curso_activo"] = None
        st.rerun()

# =========================================================================
# 4. GESTIÓN DE VISTAS SEGÚN EL ROL AUTENTICADO
# =========================================================================
user_sesion = st.session_state["usuario_identificado"]

if user_sesion is None:
    # --- PANTALLA DE BIENVENIDA SI NO HAY LOGIN ---
    st.markdown("<h1 class='main-title'>🏫 Bienvenido al Campus Escolar Digital</h1>", unsafe_allow_html=True)
    st.info("Por favor, inicia sesión en el panel de la barra lateral izquierda introduciendo tus credenciales oficiales para desbloquear el aula virtual, el calendario y tus asignaturas.")

# -------------------------------------------------------------------------
# ROL DOCENTE: PANEL DE ADMINISTRACIÓN TOTAL (ELENA)
# -------------------------------------------------------------------------
elif user_sesion == "admin":
    st.markdown(f"<h1 class='main-title'>👩‍🏫 Despacho de Dirección y Gestión Académica</h1>", unsafe_allow_html=True)
    st.write("---")
    
    modulo = st.selectbox("Módulo a gestionar:", [
        "📥 CUADERNO DE CALIFICACIONES (Corregir entregas y mandar Feedback)",
        "🛠️ CREAR TEMAS Y SUBIR MATERIALES",
        "🏫 ALTA DE ASIGNATURAS CON PORTADA"
    ])
    
    if modulo == "🛠️ CREAR TEMAS Y SUBIR RECURSOS ACADÉMICOS" or modulo == "🛠️ CREAR TEMAS Y SUBIR MATERIALES":
        asig_list = listar_directorios()
        if asig_list:
            asig_sel = st.selectbox("Asignatura:", asig_list)
            gestion_t = st.radio("Acción:", ["Crear una nueva unidad temática", "Añadir recursos a una unidad ya existente"])
            
            if gestion_t == "Crear una nueva unidad temática":
                nombre_t = st.text_input("Nombre de la unidad (Ej: Tema 2 Derivadas):")
                tema_ruta_final = nombre_t.strip().replace(" ", "_")
            else:
                temas_ex = listar_directorios(asig_sel)
                tema_ruta_final = st.selectbox("Elige el tema:", temas_ex) if temas_ex else None
                
            if tema_ruta_final:
                tipo_archivo = st.radio("Clasificación del Recurso Escolar:", ["📖 Material Formativo", "📋 Tarea Evaluante"])
                
                if tipo_archivo == "📋 Tarea Evaluante":
                    f_limite_p = st.date_input("Fijar fecha de vencimiento:")
                    fichero_p = st.file_uploader("Adjunta el archivo del enunciado:", key="u_tarea_doc")
                    
                    if st.button("🚀 Publicar Tarea de forma Oficial") and fichero_p:
                        nombre_archivo_git = f"TAREA_{str(f_limite_p)}_{fichero_p.name.replace(' ', '_')}"
                        ruta_completa = f"{asig_sel}/{tema_ruta_final}/{nombre_archivo_git}"
                        
                        if enviar_archivo(f"{asig_sel}/{tema_ruta_final}/.gitkeep", b"", "Init") and enviar_archivo(ruta_completa, fichero_p.getvalue(), "Carga"):
                            st.success(f"✔️ ¡Proceso completado! Tarea subida con éxito.")
                            st.rerun()
                else:
                    fichero_p = st.file_uploader("Adjunta los apuntes o guías académicas:", key="u_mat_doc")
                    if st.button("🚀 Publicar Material Didáctico") and fichero_p:
                        nombre_archivo_git = fichero_p.name.replace(' ', '_')
                        ruta_completa = f"{asig_sel}/{tema_ruta_final}/{nombre_archivo_git}"
                        
                        if enviar_archivo(f"{asig_sel}/{tema_ruta_final}/.gitkeep", b"", "Init") and enviar_archivo(ruta_completa, fichero_p.getvalue(), "Carga"):
                            st.success(f"✔️ ¡Proceso completado! Material subido con éxito.")
                            st.rerun()
                            
    elif modulo == "📥 CUADERNO DE CALIFICACIONES (Corregir entregas y mandar Feedback)":
        asig_list = listar_directorios()
        if asig_list:
            asig_eval = st.selectbox("Selecciona Asignatura para corregir:", asig_list)
            entregas_raiz = api_git(f"Entregas_Globales/{asig_eval}")
            carpetas_tareas = [c["name"] for c in entregas_raiz if c["type"] == "dir"]
            
            if carpetas_tareas:
                tarea_eval = st.selectbox("Selecciona la Tarea:", carpetas_tareas)
                alumnos_lista = api_git(f"Entregas_Globales/{asig_eval}/{tarea_eval}")
                id_alumnos = [a["name"] for a in alumnos_lista if a["type"] == "dir"]
                
                if id_alumnos:
                    # Mostrar nombres de la base de datos para mapear los IDs de usuario limpia
                    opciones_combo = {uid: DB_USUARIOS[uid]["nombre"] for uid in id_alumnos if uid in DB_USUARIOS}
                    alumno_eval_uid = st.selectbox("Selecciona el alumno a evaluar:", list(opciones_combo.keys()), format_func=lambda x: opciones_combo[x])
                    
                    archivos_f = api_git(f"Entregas_Globales/{asig_eval}/{tarea_eval}/{alumno_eval_uid}")
                    url_doc, name_doc = "", ""
                    for f in archivos_f:
                        if f["name"] != "nota.json":
                            url_doc, name_doc = f["download_url"], f["name"]
                            
                    ruta_json_nota = f"Entregas_Globales/{asig_eval}/{tarea_eval}/{alumno_eval_uid}/nota.json"
                    meta_n = api_git(ruta_json_nota)
                    nota_v, feedback_v = "Sin calificar", ""
                    
                    if isinstance(meta_n, dict) and "download_url" in meta_n:
                        res_d = requests.get(meta_n["download_url"])
                        if res_d.status_code == 200:
                            nota_v = res_d.json().get("nota", "Sin calificar")
                            feedback_v = res_d.json().get("feedback", "")
                            
                    st.markdown(f"""
                        <div style='background-color:#ffffff; border:1px solid #dadce0; padding:20px; border-radius:12px; margin-bottom:15px;'>
                            👤 <b>Estudiante:</b> {opciones_combo[alumno_eval_uid]} <br>
                            📄 <b>Archivo enviado:</b> {name_doc} <br><br>
                            <a href='{url_doc}' target='_blank'>📥 Descargar trabajo entregado</a>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    input_n = st.text_input("Calificación oficial:", value=str(nota_v))
                    input_f = st.text_area("Feedback pedagógico (Comentarios para el alumno):", value=feedback_v)
                    
                    if st.button("💾 Publicar e indexar Nota en su boletín"):
                        nueva_data = {"nota": input_n, "feedback": input_f, "fecha_correccion": datetime.now().strftime("%d/%m/%Y")}
                        if enviar_archivo(ruta_json_nota, json.dumps(nueva_data).encode("utf-8"), "Nota"):
                            st.success(f"✔️ Calificación para {opciones_combo[alumno_eval_uid]} guardada.")
                            st.rerun()
                else:
                    st.info("No hay entregas registradas para esta tarea.")
            else:
                st.info("No se han enviado tareas en esta materia todavía.")
                
    elif modulo == "AQUÍ_PONDREMOS_TU_OPCION" or modulo == "AQUÍ_PONDREMOS_TU_OPCION_2" or "PORTADA" in modulo:
        st.subheader("Alta de Clases")
        nueva_asig = st.text_input("Nombre de la nueva Asignatura:")
        imagen_portada = st.file_uploader("Sube una imagen de portada (.png o .jpg):", type=["png", "jpg", "jpeg"])
        
        if st.button("Consolidar Asignatura"):
            if nueva_asig and imagen_portada:
                clean_asig = nueva_asig.strip().replace(" ", "_")
                extension = imagen_portada.name.split(".")[-1]
                if enviar_archivo(f"{clean_asig}/.gitkeep", b"", "Alta") and enviar_archivo(f"{clean_asig}/portada_curso.{extension}", imagen_portada.getvalue(), "Portada"):
                    st.success(f"✔️ Asignatura '{nueva_asig}' creada correctamente.")
                    st.rerun()

# -------------------------------------------------------------------------
# ROL ALUMNO: INTERFAZ SEGURA COMPLETA (JUAN, ANA, CARLOS...)
# -------------------------------------------------------------------------
else:
    nombre_pantalla_alumno = DB_USUARIOS[user_sesion]["nombre"]
    
    pestana_clases, pestana_calendario, pestana_boletin = st.tabs([
        "📚 Mis Asignaturas",
        "📅 Calendario de Entregas",
        "📊 Mi Boletín y Correcciones"
    ])
    
    # --- PESTAÑA 1: RECURSOS Y BLOQUEO DE ENVÍOS ÚNICOS ---
    with pestana_clases:
        if st.session_state["curso_activo"] is None:
            st.markdown(f"<h1 class='main-title'>📚 Mis Cursos Activos — Hola, {nombre_pantalla_alumno}</h1>", unsafe_allow_html=True)
            asignaturas = listar_directorios()
            
            if asignaturas:
                cols = st.columns(3)
                for idx, asig in enumerate(asignaturas):
                    with cols[idx % 3]:
                        archivo_portada = api_git(f"{asig}/portada_curso.png")
                        if not archivo_portada or isinstance(archivo_portada, list):
                            archivo_portada = api_git(f"{asig}/portada_curso.jpg")
                            
                        with st.container(border=True):
                            if isinstance(archivo_portada, dict) and "download_url" in archivo_portada:
                                st.image(archivo_portada["download_url"], use_container_width=True)
                            else:
                                st.markdown("<div style='background:linear-gradient(135px, #3b82f6 0%, #1d4ed8 100%); height:120px; border-radius:6px;'></div>", unsafe_allow_html=True)
                            
                            st.markdown(f"<h3 style='margin:10px 0 5px 0;'>{asig.replace('_', ' ')}</h3>", unsafe_allow_html=True)
                            if st.button("Entrar al Aula", key=f"open_{asig}"):
                                st.session_state["curso_activo"] = asig
                                st.rerun()
            else:
                st.info("No hay asignaturas disponibles.")
        else:
            asig_actual = st.session_state["curso_activo"]
            if st.button("⬅️ Volver a mis asignaturas"):
                st.session_state["curso_activo"] = None
                st.rerun()
                
            st.markdown(f"<h1 class='main-title'>📖 Asignatura: {asig_actual.replace('_', ' ')}</h1>", unsafe_allow_html=True)
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
                                    id_tar = el["name"].split(".")[0]
                                    
                                    st.markdown(f"""
                                        <div class='recurso-bloque' style='border-left-color: #ef4444; background-color: #fef2f2;'>
                                            <span style='background-color:#ef4444; color:white; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold;'>TAREA OBLIGATORIA</span>
                                            <h4 style='margin:5px 0;'>📋 {t_nombre}</h4>
                                            <p style='margin:0; font-size:13px; color:#5f6368;'>Fecha límite: <b>{f_limite}</b></p>
                                            <p style='margin-top:5px;'><a href='{el['download_url']}' target='_blank' style='color:#ef4444; font-weight:bold;'>📥 Descargar Enunciado de la Actividad</a></p>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    # --- SISTEMA DE VERIFICACIÓN DE ENTREGA ÚNICA ---
                                    ruta_json_comprobar = f"Entregas_Globales/{asig_actual}/{id_tar}/{user_sesion}/nota.json"
                                    ya_entregado = api_git(ruta_json_comprobar)
                                    
                                    if isinstance(ya_entregado, dict) and "download_url" in ya_entregado:
                                        # SI YA EXISTE ENTREGA: Bloqueamos formulario y mostramos mensaje inalterable
                                        st.markdown(f"""
                                            <div class='status-entregado'>
                                                ✔️ Tarea entregada con éxito. Ya no se permiten más envíos para esta actividad.
                                            </div>
                                        """, unsafe_allow_html=True)
                                    else:
                                        # SI NO EXISTE ENTREGA: Permitimos el envío normal
                                        with st.container(border=True):
                                            st.write("📬 **Formulario de entrega oficial:**")
                                            archivo_al = st.file_uploader("Selecciona tu archivo de solución (PDF o Imagen):", type=["pdf","png","jpg","jpeg"], key=f"f_u_{el['name']}")
                                            
                                            if st.button("Enviar Tarea", key=f"b_s_{el['name']}"):
                                                if archivo_al:
                                                    ruta_file = f"Entregas_Globales/{asig_actual}/{id_tar}/{user_sesion}/{archivo_al.name}"
                                                    meta_init = {"nota": "Sin calificar", "feedback": "Pendiente de revisión por la profesora.", "fecha": datetime.now().strftime("%d/%m/%Y")}
                                                    
                                                    if enviar_archivo(ruta_file, archivo_al.getvalue(), "Entrega") and enviar_archivo(ruta_json_comprobar, json.dumps(meta_init).encode("utf-8"), "Meta"):
                                                        st.success("✔️ Tarea enviada y registrada correctamente.")
                                                        st.rerun()
                                                else:
                                                    st.warning("Adjunta un documento.")
                                else:
                                    nombre_mat = el["name"].replace("_", " ").split(".")[0]
                                    st.markdown(f"""
                                        <div class='recurso-bloque' style='border-left-color: #10b981; background-color: #f0fdf4;'>
                                            <span style='background-color:#10b981; color:white; padding:2px 6px; border-radius:4px; font-size:11px; font-weight:bold;'>MATERIAL DE ESTUDIO</span>
                                            <h4 style='margin:5px 0;'>📖 {nombre_mat}</h4>
                                            <p style='margin:0;'><a href='{el['download_url']}' target='_blank' style='color:#10b981; font-weight:bold;'>📥 Descargar Apuntes</a></p>
                                        </div>
                                    """, unsafe_allow_html=True)
            else:
                st.info("No hay temas creados.")

    # --- PESTAÑA 2: CALENDARIO ESCOLAR CENTRALIZADO EN REJILLA ---
    with pestana_calendario:
        st.markdown("<h3 style='color:#1e3a8a;'>📅 Agenda Automatizada de Entregas</h3>", unsafe_allow_html=True)
        todas_asig = listar_directorios()
        datos_cal = []
        
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
                            datos_cal.append({"📅 FECHA LÍMITE": f_limite, "📚 ASIGNATURA": asig.replace('_',' '), "📋 TAREA": t_nombre})
                            
        if datos_cal:
            st.data_editor(pd.DataFrame(datos_cal), use_container_width=True, disabled=True)
        else:
            st.info("No hay plazos agendados.")

    # --- PESTAÑA 3: BOLETÍN PRIVADO AUTOMÁTICO TRAS EL LOGIN ---
    with pestana_boletin:
        st.markdown(f"<h3 style='color:#1e3a8a;'>📋 Expediente y Notas de {nombre_pantalla_alumno}</h3>", unsafe_allow_html=True)
        st.write("Historial oficial de evaluaciones cargadas de forma privada por tu profesora:")
        st.write("---")
        
        asignaturas_totales = listar_directorios()
        hubo_registros = False
        
        for asig in asignaturas_totales:
            # Buscamos en la bandeja si este alumno tiene notas de esa asignatura
            entregas_asig = api_git(f"Entregas_Globales/{asig}")
            if isinstance(entregas_asig, list):
                for task_folder in entregas_asig:
                    ruta_json_nota = f"Entregas_Globales/{asig}/{task_folder['name']}/{user_sesion}/nota.json"
                    meta_js = api_git(ruta_json_nota)
                    
                    if isinstance(meta_js, dict) and "download_url" in meta_js:
                        hubo_registros = True
                        res_js = requests.get(meta_js["download_url"])
                        if res_js.status_code == 200:
                            data_nota = res_js.json()
                            nombre_t_limpio = task_folder["name"].split("_", 2)[-1].replace("_", " ") if "TAREA_" in task_folder["name"] else task_folder["name"].replace("_"," ")
                            
                            st.markdown(f"""
                                <div class='grade-box'>
                                    <h4 style='margin:0; color:#1e3a8a;'>📚 {asig.replace('_',' ')} — Actividad: {nombre_t_limpio}</h4>
                                    <p style='margin:8px 0 4px 0;'><b>Nota Oficial:</b> <span style='font-size:16px; color:#16a34a; font-weight:700;'>{data_nota['nota']}</span></p>
                                    <p style='margin:0; color:#475569;'><b>Comentarios y Feedback Docente:</b><br><i>{data_nota['feedback']}</i></p>
                                    <small style='color:#94a3b8;'>Fecha de corrección: {data_nota.get('fecha_correccion', data_nota.get('fecha'))}</small>
                                </div>
                            """, unsafe_allow_html=True)
        if not hubo_registros:
            st.info("Aún no se registran tareas evaluadas en tu expediente digital.")
