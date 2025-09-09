import streamlit as st
from datetime import datetime
import pandas as pd
from login import login_view, admin_view
from configuracion import configuracion_empresa_view

# --- Configuración de página ---
st.set_page_config(page_title="CRM- AXIA CONSULTORES", page_icon="imagen/LOGO CMYK.png", layout="wide")

# --- Inicializar estado del menú ---
if "menu" not in st.session_state:
    st.session_state["menu"] = "login"   # 👈 ahora arranca en login

if "user" not in st.session_state:
    st.session_state["user"] = None

if "clientes" not in st.session_state:
    st.session_state["clientes"] = pd.DataFrame(columns=["Nombre", "Email", "Estado", "Sector"])

if "cotizaciones" not in st.session_state:
    st.session_state["cotizaciones"] = pd.DataFrame(columns=[
        "Número", "Título", "Cliente", "Estado", "Monto"
    ])

if "mostrar_form" not in st.session_state:
    st.session_state["mostrar_form"] = False

# --- Estilos CSS ---
st.markdown("""
    <style>
    /* Estilo general del sidebar */
    .sidebar .sidebar-content {
        background-color: #f5f7fa;
        padding: 20px;
    }

    /* Estilo de botones 3D */
    .stButton button {
        width: 100%;
        margin: 8px 0;
        padding: 12px;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        font-size: 16px;
        color: white;
        background: linear-gradient(145deg, #3b82f6, #1e40af);
        box-shadow: 4px 4px 8px #c1c1c1, -4px -4px 8px #ffffff;
        transition: all 0.2s ease-in-out;
    }

    /* Hover efecto */
    .stButton button:hover {
        background: linear-gradient(145deg, #2563eb, #1d4ed8);
        transform: translateY(-2px);
        box-shadow: 6px 6px 10px #c1c1c1, -6px -6px 10px #ffffff;
    }

    /* Botón presionado */
    .stButton button:active {
        transform: translateY(2px);
        box-shadow: inset 4px 4px 8px #c1c1c1, inset -4px -4px 8px #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# --- Ocultar header y footer de Streamlit ---
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden; height: 0px;}
    footer {visibility: hidden; height: 0px;}
    div.block-container {padding-top: 0rem;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ================================
# 🔹 1) Mostrar login si no hay usuario
# ================================
if st.session_state["menu"] == "login" or st.session_state["user"] is None:
    login_view()
# ================================
else:
    # --- Barra lateral ---
    with st.sidebar:
        st.subheader(" ...CRM-EMPRESARIAL...")
        st.markdown("---")
        st.image("imagen/LOGO CMYK.png", width=190) 
        
        if st.button("📊 Dashboard"):
            st.session_state["menu"] = "Dashboard"
        if st.button("👥 Clientes"):
            st.session_state["menu"] = "Clientes"
        if st.button("💰 Cotizaciones"):
            st.session_state["menu"] = "Cotizaciones"
        if st.button("📑 Contratos"):
            st.session_state["menu"] = "Contratos"
        if st.button("📂 Proyectos"):
            st.session_state["menu"] = "Proyectos"
        if st.button("💵 Finanzas"):
            st.session_state["menu"] = "Finanzas"
        if st.button("🔐 Usuarios"):
            st.session_state["menu"] = "usuarios"
        if st.button("🚪 Cerrar sesión"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("Sesión cerrada correctamente. Vuelve a iniciar sesión.")
            st.session_state["menu"] = "login"
            st.stop()

    # --- Encabezado usuario ---
    col1, col2, col3 = st.columns([6,1,1])
    with col1:
        st.subheader(st.session_state.get("menu", "Menú Principal"))   # Menú dinámico
    with col2:
        st.markdown("<span style='color:green; font-weight:bold;'>🟢 En línea</span>", unsafe_allow_html=True)
    with col3:
        user = st.session_state.get("user")
        if user:
            st.caption(f"👤 Usuario: {user[1]}")   # 👈 nombre del usuario logueado
        else:
            st.caption("👤 Usuario: Invitado")

    st.markdown("---")

    # --- Menú de navegación ---
    if st.session_state["menu"] == "Dashboard":
        from dashboard import dashboard_view
        dashboard_view()

    elif st.session_state["menu"] == "Clientes":
from clientes import clientes_view
        clientes_view()

    elif st.session_state["menu"] == "Cotizaciones":
from cotizaciones import cotizaciones_view
        cotizaciones_view()

    elif st.session_state["menu"] == "Contratos":
from contratos import contratos_view
        contratos_view()

    elif st.session_state["menu"] == "Proyectos":
from proyectos import proyectos_view
        proyectos_view()

    elif st.session_state["menu"] == "Finanzas":
from finanzas import finanzas_view
        finanzas_view()

    elif st.session_state["menu"] == "usuarios":
        admin_view()
        # Dentro del menú de Configuración
        configuracion_empresa_view()

   
