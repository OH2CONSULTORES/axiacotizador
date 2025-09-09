# auth.py
import pandas as pd
import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import base64
DB_AUTH = "usuarios.db"

# ========================
# Funciones auxiliares
# ========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_users_table():
    conn = sqlite3.connect(DB_AUTH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            correo TEXT UNIQUE,
            password TEXT,
            rol TEXT DEFAULT 'usuario',
            ultimo_login TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_user(nombre, correo, password, rol="usuario"):
    conn = sqlite3.connect(DB_AUTH)
    c = conn.cursor()
    c.execute("INSERT INTO usuarios (nombre, correo, password, rol) VALUES (?,?,?,?)",
              (nombre, correo, hash_password(password), rol))
    conn.commit()
    conn.close()

def validate_user(correo, password):
    conn = sqlite3.connect(DB_AUTH)
    c = conn.cursor()
    c.execute("SELECT * FROM usuarios WHERE correo=? AND password=?", (correo, hash_password(password)))
    user = c.fetchone()
    if user:
        # Actualizar último login
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.execute("UPDATE usuarios SET ultimo_login=? WHERE id=?", (fecha, user[0]))
        conn.commit()
    conn.close()
    return user

def get_all_users():
    conn = sqlite3.connect(DB_AUTH)
    query = "SELECT id, nombre, correo, rol, ultimo_login FROM usuarios"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def delete_user(user_id):
    conn = sqlite3.connect(DB_AUTH)
    c = conn.cursor()
    c.execute("DELETE FROM usuarios WHERE id=?", (user_id,))
    conn.commit()
    conn.close()

# ========================
# Interfaz principal
# ========================
def login_view():
    create_users_table()
        # Cargar video en base64 para que se muestre en HTML
    video_path = "imagen/logo.mp4"
    with open(video_path, "rb") as f:
        video_bytes = f.read()
    video_base64 = base64.b64encode(video_bytes).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .video-container {{
            width: 100%;
            height: 180px; /* 👈 Ajusta aquí la altura */
            display: flex;               /* activa flexbox */
            justify-content: center;     /* centra horizontal */
            align-items: center;         /* centra vertical */
            overflow: hidden;
            border-radius: 12px;
        }}
        .video-container video {{
            width: 40%;    /* 👈 proporción del ancho */
            height: auto;  /* mantiene proporción natural del video */
            object-fit: cover;
        }}
        </style>

        <div class="video-container">
            <video id="myVideo" autoplay loop muted playsinline>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Tu navegador no soporta el video.
            </video>
        </div>

        <script>
        // Acelerar la velocidad del video
        var vid = document.getElementById("myVideo");
        vid.playbackRate =80; 
        </script>
        """,
        unsafe_allow_html=True
    )


    # Centrar el contenido en 3 columnas
    col1, col2, col3 = st.columns([3, 5, 3])  # proporción: col2 más ancha

    with col2:
        
        st.markdown("<p style='text-align:center;'>Inicia sesión en tu cuenta</p>", unsafe_allow_html=True)

        with st.form("login_form"):
            correo = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            submitted = st.form_submit_button("Iniciar Sesión")

            if submitted:
                user = validate_user(correo, password)
                if user:
                    st.success(f"Bienvenido {user[1]} 👋")
                    # Guardar datos de sesión
                    st.session_state["user"] = user       # registro completo
                    st.session_state["usuario"] = user[1] # nombre
                    st.session_state["correo"] = user[2]  # correo
                    st.session_state["menu"] = "Dashboard"  # 👈 ir al Dashboard
                    st.rerun()  # refrescar y cargar la interfaz
                else:
                    st.error("Correo o contraseña incorrectos ❌")

        st.write("¿No tienes cuenta? [Regístrate aquí](#)")
# ========================
# Módulo de Administración
# # ========================
# Módulo de Administración
# ========================
def admin_view():
    st.title("⚙️ Administración de Usuarios")

    # Crear nuevo usuario
    with st.expander("➕ Crear Usuario"):
        with st.form("crear_usuario"):
            nombre = st.text_input("Nombre de usuario")
            correo = st.text_input("Correo")
            password = st.text_input("Contraseña", type="password")
            rol = st.selectbox("Rol", ["usuario", "admin"])
            submitted = st.form_submit_button("Guardar")
            if submitted:
                try:
                    add_user(nombre, correo, password, rol)
                    st.success("Usuario creado con éxito ✅")
                except Exception as e:
                    st.error(f"Error: {e}")

    # Listar usuarios
    st.subheader("👥 Lista de Usuarios")
    df = get_all_users()
    st.dataframe(df, use_container_width=True)

    # Eliminar usuario
    user_id = st.number_input("ID de usuario a eliminar", step=1)
    if st.button("Eliminar Usuario"):
        delete_user(user_id)
        st.success("Usuario eliminado ✅")

    # 📋 Cartillas de Roles
    with st.expander("📋 Ver Cartillas de Roles AXIA CONSULTORES"):
        st.markdown("### Roles del Equipo de Consultores")

        col1, col2, col3 = st.columns(3)

        # --- Rol Comercial ---
        with col1:
            st.image("imagen/image.png", width=120, caption="Foto Comercial")
            nombre_com = st.text_input("Nombre (Comercial)", key="nombre_com")
            fono_com = st.text_input("Teléfono (Comercial)", key="fono_com")

            st.markdown("### 👨‍💼 Rol Comercial")
            st.markdown("**Misión:** Atraer clientes, gestionar relaciones y asegurar el crecimiento de las ventas.")
            st.markdown("**Funciones principales:**")
            st.markdown("""
            - Captar y registrar prospectos de clientes.  
            - Gestionar el pipeline de ventas y oportunidades.  
            - Preparar y dar seguimiento a cotizaciones.  
            - Coordinar con el área de Procesos la viabilidad técnica de proyectos.  
            - Realizar seguimiento postventa y evaluar satisfacción del cliente.  
            - Apoyar en campañas de marketing y posicionamiento digital.  
            """)
            st.markdown("**Módulos asignados:** 👥 Clientes · 🧲 Marketing/Leads · 💰 Cotizaciones · 📑 Contratos")
            st.markdown("**KPIs sugeridos:** Leads generados · Conversión · Satisfacción postventa")

        # --- Rol de Procesos ---
        with col2:
            st.image("imagen/image.png", width=120, caption="Foto Procesos")
            nombre_proc = st.text_input("Nombre (Procesos)", key="nombre_proc")
            fono_proc = st.text_input("Teléfono (Procesos)", key="fono_proc")

            st.markdown("### 🛠️ Rol de Procesos")
            st.markdown("**Misión:** Ejecutar proyectos de consultoría garantizando calidad, eficiencia y valor al cliente.")
            st.markdown("**Funciones principales:**")
            st.markdown("""
            - Planificar y ejecutar proyectos de mejora en clientes.  
            - Supervisar cronogramas, entregables y recursos asignados.  
            - Asegurar el cumplimiento de metodologías Lean.  
            - Controlar y documentar la calidad de los proyectos.  
            - Mantener un repositorio de plantillas y lecciones aprendidas.  
            - Generar reportes de desempeño y KPIs.  
            """)
            st.markdown("**Módulos asignados:** 📂 Proyectos · ✅ Calidad · 📚 Documentación")
            st.markdown("**KPIs sugeridos:** Cumplimiento de plazos · Satisfacción · Auditorías positivas")

        # --- Rol Financiero ---
        with col3:
            st.image("imagen/image.png", width=120, caption="Foto Finanzas")
            nombre_fin = st.text_input("Nombre (Financiero)", key="nombre_fin")
            fono_fin = st.text_input("Teléfono (Financiero)", key="fono_fin")

            st.markdown("### 💵 Rol Financiero")
            st.markdown("**Misión:** Garantizar la sostenibilidad económica y la rentabilidad de la empresa.")
            st.markdown("**Funciones principales:**")
            st.markdown("""
            - Elaborar presupuestos por cliente/proyecto.  
            - Controlar costos directos e indirectos.  
            - Administrar contratos y condiciones de pago.  
            - Emitir facturas, notas de crédito y control de cobranzas.  
            - Monitorear flujo de caja y estados financieros.  
            - Preparar reportes financieros para la gerencia.  
            """)
            st.markdown("**Módulos asignados:** 💵 Finanzas · 📉 Presupuestos/Costos · 💳 Tesorería · 📑 Contratos")
            st.markdown("**KPIs sugeridos:** Rentabilidad · Días de cobranza · Flujo de caja disponible")

        # --- Dirección General ---
        st.divider()
        st.image("imagen/image.png", width=120, caption="Foto Dirección General")
        nombre_dir = st.text_input("Nombre (Dirección)", key="nombre_dir")
        fono_dir = st.text_input("Teléfono (Dirección)", key="fono_dir")

        st.markdown("### 📊 Dirección General ")
        st.markdown("**Misión:** Supervisar la empresa como estratega e inversionista, sin intervención operativa directa.")
        st.markdown("**Funciones principales:**")
        st.markdown("""
        - Revisar reportes consolidados de cada área.  
        - Definir estrategias de crecimiento.  
        - Aprobar decisiones clave (expansión, nuevas herramientas, alianzas).  
        - Velar por la independencia y escalabilidad de la consultoría.  
        """)
        st.markdown("**Módulos asignados:** 📊 Dashboard · 📈 Reportes · ⚙️ Configuración General")
        st.markdown("**KPIs sugeridos:** Crecimiento anual · Rentabilidad global · Satisfacción general")
