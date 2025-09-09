import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

# --- Crear carpeta data y base de datos si no existe ---
if not os.path.exists("data"):
    os.makedirs("data")

conn = sqlite3.connect("data/clientes.db", check_same_thread=False)
c = conn.cursor()

# --- Tabla de clientes ---
c.execute("""
CREATE TABLE IF NOT EXISTS clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    empresa TEXT,
    ruc TEXT,
    direccion TEXT,
    telefono TEXT,
    contacto TEXT,
    cargo TEXT,
    sector TEXT,
    estado TEXT,
    creado_por TEXT,
    fecha_creacion TEXT
)
""")

# --- Tabla de historial de cambios ---
c.execute("""
CREATE TABLE IF NOT EXISTS historial (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cliente_id INTEGER,
    accion TEXT,
    usuario TEXT,
    fecha TEXT,
    FOREIGN KEY (cliente_id) REFERENCES clientes (id)
)
""")
conn.commit()

# --- Funciones de BD ---
def insertar_cliente(empresa, ruc, direccion, telefono, contacto, cargo, sector, estado, usuario):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    INSERT INTO clientes (empresa, ruc, direccion, telefono, contacto, cargo, sector, estado, creado_por, fecha_creacion)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (empresa, ruc, direccion, telefono, contacto, cargo, sector, estado, usuario, fecha))
    conn.commit()

    # guardar acción en historial
    cliente_id = c.lastrowid
    registrar_historial(cliente_id, "Creación", usuario)

def cargar_clientes():
    return pd.read_sql("SELECT * FROM clientes", conn)

def registrar_historial(cliente_id, accion, usuario):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("""
    INSERT INTO historial (cliente_id, accion, usuario, fecha)
    VALUES (?, ?, ?, ?)
    """, (cliente_id, accion, usuario, fecha))
    conn.commit()

def cargar_historial():
    return pd.read_sql("SELECT * FROM historial", conn)

# --- Vista de clientes ---
def clientes_view():
    st.subheader("📊 Administra tu cartera de clientes")

    # Simulación de login (usuario activo)
    if "usuario" not in st.session_state:
        st.session_state["usuario"] = "admin"  # en un login real se setea aquí

    # --- Estado para mostrar formulario ---
    if "mostrar_form_cliente" not in st.session_state:
        st.session_state["mostrar_form_cliente"] = False

    # --- Botón Nuevo Cliente ---
    if st.button("➕ Nuevo Cliente"):
        st.session_state["mostrar_form_cliente"] = True

    # --- Formulario ---
    if st.session_state["mostrar_form_cliente"]:
        with st.form("nuevo_cliente"):
            st.subheader("Agregar Cliente")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                empresa = st.text_input("Nombre de la empresa")
                ruc = st.text_input("RUC")
            with col2:
                direccion = st.text_input("Dirección")
                telefono = st.text_input("Teléfono")
            with col3:
                contacto = st.text_input("Persona de contacto")
                cargo = st.text_input("Cargo")
            with col4:
                sector = st.selectbox("Sector", ["Tecnología", "Salud", "Educación", "Finanzas", "Industrial", "Otro"])
                estado = st.selectbox("Estado", ["Prospecto", "Quiere cotización", "Firmó contrato", "Inactivo"])

            submit = st.form_submit_button("Guardar")

            if submit and empresa and contacto:
                insertar_cliente(
                    empresa, ruc, direccion, telefono,
                    contacto, cargo, sector, estado,
                    st.session_state["usuario"]
                )
                st.success(f"✅ Cliente **{empresa}** agregado correctamente por {st.session_state['usuario']}")
                st.session_state["mostrar_form_cliente"] = False
                st.rerun()

    st.markdown("---")

    # --- Cargar clientes ---
    df = cargar_clientes()

    # --- Filtros ---
    col1, col2, col3, col4 = st.columns([2,1,1,1])
    with col1:
        buscar = st.text_input("Buscar", placeholder="Nombre, contacto, empresa o teléfono...")
    with col2:
        filtro_estado = st.selectbox("Estado", ["Todos", "Prospecto", "Quiere cotización", "Firmó contrato", "Inactivo"])
    with col3:
        filtro_sector = st.selectbox("Sector", ["Todos", "Tecnología", "Salud", "Educación", "Finanzas", "Industrial", "Otro"])
    with col4:
        filtrar = st.button("Filtrar", use_container_width=True)

    df_filtrado = df.copy()

    # Aplicar filtros
    if filtrar:
        if buscar:
            df_filtrado = df_filtrado[
                df_filtrado["empresa"].str.contains(buscar, case=False, na=False) |
                df_filtrado["contacto"].str.contains(buscar, case=False, na=False) |
                df_filtrado["telefono"].str.contains(buscar, case=False, na=False)
            ]
        if filtro_estado != "Todos":
            df_filtrado = df_filtrado[df_filtrado["estado"] == filtro_estado]
        if filtro_sector != "Todos":
            df_filtrado = df_filtrado[df_filtrado["sector"] == filtro_sector]

    # --- Resumen ---
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Total", len(df_filtrado))
    with col2:
        st.metric("✅ Firmó contrato", len(df_filtrado[df_filtrado["estado"]=="Firmó contrato"]))
    with col3:
        st.metric("🟡 Prospectos", len(df_filtrado[df_filtrado["estado"]=="Prospecto"]))
    with col4:
        st.metric("📩 Cotización", len(df_filtrado[df_filtrado["estado"]=="Quiere cotización"]))

    st.markdown("---")

    # --- Listado de clientes ---
    if len(df_filtrado) == 0:
        st.info("👥 No hay clientes.\n\nAgrega tu primer cliente con el botón **'Nuevo Cliente'**.")
    else:
        st.dataframe(df_filtrado, use_container_width=True)

    # --- Mostrar historial ---
    st.markdown("### 📝 Historial de cambios")
    df_hist = cargar_historial()
    st.dataframe(df_hist, use_container_width=True)

# --- Para probar ---
if __name__ == "__main__":
    clientes_view()
