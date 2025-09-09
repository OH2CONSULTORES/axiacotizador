# dashboard.py
import streamlit as st

def dashboard_view():
    st.write("### 📊 Dashboard")
    
    col1, col2 = st.columns([2,1])
    
    with col1:
        st.info("Gráfico de ingresos próximamente 📈")
    
    with col2:
        st.markdown("#### 🔔 Actividad reciente")
        st.write("👤 **Nuevo cliente registrado** - Empresa ABC (hace 2 horas)")
        st.write("📄 **Cotización enviada** - Empresa XYZ (hace 4 horas)")
        st.write("📑 **Contrato firmado** - Cliente (hace 1 día)")
        st.markdown("[Ver toda la actividad](#)")
    
    st.markdown("### ⚡ Acciones rápidas")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("➕ Nuevo Cliente"):
            st.success("Formulario de nuevo cliente")
    with c2:
        if st.button("📄 Nueva Cotización", key="btn_nueva_cotizacion_sidebar"):
            st.success("Formulario de cotización")
    with c3:
        if st.button("📑 Nuevo Contrato"):
            st.success("Generar contrato")
    with c4:
        if st.button("📊 Ver Reportes"):
            st.success("Análisis de métricas")
