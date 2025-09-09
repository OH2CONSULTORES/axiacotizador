# proyectos.py
import streamlit as st
from datetime import date

# ==============================
# Inicialización segura de clientes
# ==============================
if "clientes" not in st.session_state or not isinstance(st.session_state.clientes, list):
    st.session_state.clientes = []

# ==============================
# Vista principal de proyectos / CRM
# ==============================
def proyectos_view():
    st.title("📊 Seguimiento de Consultoría")
    st.write("Gestiona y monitorea todos los proyectos de consultoría")

    # Etapas del flujo profesional de ventas
    etapas = [
        "Contacto Inicial",
        "Reunión Exploratoria",
        "Pendiente Cotización",
        "Cotización Enviada",
        "Contrato Realizado",
        "Proyecto En Ejecución",
        "Proyecto Completado"
    ]

    # ==============================
    # Crear nuevo cliente / proyecto
    # ==============================
    st.subheader("➕ Crear nuevo cliente / proyecto")
    with st.form("crear_cliente"):
        nombre = st.text_input("Nombre del Cliente")
        empresa = st.text_input("Empresa")
        fuente = st.text_input("¿Cómo se enteró del servicio?")
        observacion = st.text_area("Observaciones iniciales")
        submitted = st.form_submit_button("Crear Cliente")

        if submitted:
            if nombre.strip() == "":
                st.error("Debes ingresar el nombre del cliente.")
            else:
                cliente = {
                    "id": len(st.session_state.clientes) + 1,
                    "nombre": nombre,
                    "empresa": empresa,
                    "fuente": fuente,
                    "observaciones": [{"etapa": "Contacto Inicial", "nota": observacion}],
                    "etapa_actual": "Contacto Inicial",
                    "fecha_reunion": None,
                    "fecha_cotizacion": None,
                    "fecha_contrato": None,
                    "progreso": 0
                }
                st.session_state.clientes.append(cliente)
                st.success(f"Cliente {nombre} creado y asignado a 'Contacto Inicial'")
                st.rerun()

    st.markdown("---")

    # ==============================
    # Mostrar clientes por etapa
    # ==============================
    for etapa in etapas:
        st.subheader(f"📌 {etapa}")
        clientes_etapa = [c for c in st.session_state.clientes if c.get("etapa_actual") == etapa]

        if not clientes_etapa:
            st.info("No hay clientes en esta etapa")
            continue

        for cliente in clientes_etapa:
            with st.expander(f"{cliente['nombre']} - {cliente['empresa']}"):
                st.write(f"**Fuente:** {cliente['fuente']}")

                # Mostrar observaciones de la etapa actual
                notas = [o["nota"] for o in cliente["observaciones"] if o["etapa"] == etapa]
                for n in notas:
                    st.markdown(f"- {n}")

                # Formulario para agregar nueva observación
                nueva_nota = st.text_area("Agregar observación / registro", key=f"nota_{cliente['id']}_{etapa}")
                if st.button("Guardar nota", key=f"guardar_{cliente['id']}_{etapa}") and nueva_nota.strip() != "":
                    cliente["observaciones"].append({"etapa": etapa, "nota": nueva_nota})
                    st.rerun()

                # Botón para avanzar a la siguiente etapa
                indice_actual = etapas.index(etapa)
                if indice_actual + 1 < len(etapas):
                    siguiente_etapa = etapas[indice_actual + 1]
                    if st.button(f"Avanzar a '{siguiente_etapa}'", key=f"siguiente_{cliente['id']}"):
                        cliente["etapa_actual"] = siguiente_etapa

                        # Registrar fechas según la etapa
                        if siguiente_etapa == "Reunión Exploratoria":
                            cliente["fecha_reunion"] = date.today()
                        elif siguiente_etapa == "Pendiente Cotización":
                            cliente["fecha_cotizacion"] = date.today()
                        elif siguiente_etapa == "Contrato Realizado":
                            cliente["fecha_contrato"] = date.today()

                        st.rerun()

    # ==============================
    # KPIs resumidos
    # ==============================
    st.markdown("---")
    st.subheader("📊 Resumen general")
    total_clientes = len(st.session_state.clientes)
    st.metric("Total Clientes", total_clientes)

    for etapa in etapas:
        count = len([c for c in st.session_state.clientes if c.get("etapa_actual") == etapa])
        st.metric(etapa, count)
