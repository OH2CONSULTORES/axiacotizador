import sqlite3
import streamlit as st

# ==============================
#   📊 FUNCIONES BASE DE DATOS
# ==============================
def create_empresa_table():
    conn = sqlite3.connect("configuracion.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS empresa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            logo TEXT,
            direccion TEXT,
            telefono TEXT,
            email TEXT
        )
    """)
    # 🔧 Verificar si existen las nuevas columnas, si no, agregarlas
    try:
        c.execute("ALTER TABLE empresa ADD COLUMN sobre_nosotros TEXT")
    except sqlite3.OperationalError:
        pass  # La columna ya existe
    try:
        c.execute("ALTER TABLE empresa ADD COLUMN texto_ventas TEXT")
    except sqlite3.OperationalError:
        pass  # La columna ya existe

    conn.commit()
    conn.close()

def save_empresa(nombre, logo, direccion, telefono, email, sobre_nosotros, texto_ventas):
    conn = sqlite3.connect("configuracion.db")
    c = conn.cursor()
    c.execute("DELETE FROM empresa")  # Solo se guarda un registro (la empresa principal)
    c.execute(
        """INSERT INTO empresa 
           (nombre, logo, direccion, telefono, email, sobre_nosotros, texto_ventas) 
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (nombre, logo, direccion, telefono, email, sobre_nosotros, texto_ventas)
    )
    conn.commit()
    conn.close()

def get_empresa():
    conn = sqlite3.connect("configuracion.db")
    c = conn.cursor()
    c.execute("SELECT nombre, logo, direccion, telefono, email, sobre_nosotros, texto_ventas FROM empresa LIMIT 1")
    empresa = c.fetchone()
    conn.close()
    if empresa:
        return {
            "nombre": empresa[0],
            "logo": empresa[1],
            "direccion": empresa[2],
            "telefono": empresa[3],
            "email": empresa[4],
            "sobre_nosotros": empresa[5],
            "texto_ventas": empresa[6]
        }
    else:
        return None

# ==============================
#   ⚙️ VISTA DE CONFIGURACIÓN
# ==============================
def configuracion_empresa_view():
    st.subheader("⚙️ Configuración de Empresa")

    # Crear tabla si no existe (y corregir si faltan columnas)
    create_empresa_table()

    # Obtener datos actuales (si existen)
    empresa = get_empresa() or {}

    with st.form("empresa_form"):
        nombre = st.text_input("🏢 Nombre de la Empresa", value=empresa.get("nombre", ""))
        direccion = st.text_input("📍 Dirección", value=empresa.get("direccion", ""))
        telefono = st.text_input("📞 Teléfono", value=empresa.get("telefono", ""))
        email = st.text_input("📧 Correo", value=empresa.get("email", ""))
        logo = st.text_input("🖼️ Ruta del Logo (ej. imagen/logo.png)", value=empresa.get("logo", ""))
        sobre_nosotros = st.text_area("ℹ️ Sobre Nosotros", value=empresa.get("sobre_nosotros", ""), height=120)
        texto_ventas = st.text_area("💼 Texto de Ventas", value=empresa.get("texto_ventas", ""), height=120)

        submit = st.form_submit_button("💾 Guardar Datos")
        if submit:
            save_empresa(nombre, logo, direccion, telefono, email, sobre_nosotros, texto_ventas)
            st.success("✅ Datos de la empresa guardados correctamente")

    # Mostrar vista previa de los datos
    empresa = get_empresa()
    if empresa:
        st.markdown("---")
        st.markdown("### 📌 Vista Previa")
        if empresa["logo"]:
            st.image(empresa["logo"], width=150)
        st.write(f"**Nombre:** {empresa['nombre']}")
        st.write(f"**Dirección:** {empresa['direccion']}")
        st.write(f"**Teléfono:** {empresa['telefono']}")
        st.write(f"**Correo:** {empresa['email']}")
        st.markdown("#### ℹ️ Sobre Nosotros")
        st.write(empresa["sobre_nosotros"])
        st.markdown("#### 💼 Texto de Ventas")
        st.write(empresa["texto_ventas"])
