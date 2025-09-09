import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

# --- Inicialización ---
if "cotizaciones" not in st.session_state:
    st.session_state["cotizaciones"] = pd.DataFrame(columns=[
        "Número", "Título", "Cliente", "Estado", "Items", "Monto"
    ])

if "items_temp" not in st.session_state:
    st.session_state["items_temp"] = []  # Items temporales para la proforma

if "mostrar_form" not in st.session_state:
    st.session_state["mostrar_form"] = False


# --- Función para generar PDF ---
def generar_pdf(numero, cliente, items, total):
    filename = f"cotizacion_{numero}.pdf"
    c = canvas.Canvas(filename, pagesize=A4)
    width, height = A4

    # Logo
    logo_path = "imagen/LOGO CMYK.png"
    if os.path.exists(logo_path):
        c.drawImage(logo_path, 40, height - 100, width=100, height=60)

    # Encabezado
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 50, "COTIZACIÓN")
    c.setFont("Helvetica", 12)
    c.drawString(40, height - 130, f"Número: {numero}")
    c.drawString(40, height - 150, f"Cliente: {cliente}")

    # Tabla de items
    y = height - 200
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "Descripción")
    c.drawString(350, y, "Monto ($)")
    y -= 20

    c.setFont("Helvetica", 12)
    for desc, monto in items:
        c.drawString(40, y, desc)
        c.drawRightString(450, y, f"{monto:,.2f}")
        y -= 20

    # Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y - 20, f"TOTAL: ${total:,.2f}")

    # Firma
    c.line(300, 100, 500, 100)
    c.drawString(350, 85, "Firma y Sello")

    c.save()
    return filename


# --- Vista Cotizaciones ---
def cotizaciones_view():
    st.title("📄 Cotizaciones")
    st.caption("Gestiona tus propuestas comerciales")

    # --- Botón Nueva Cotización ---
    if st.button("➕ Nueva Cotización"):
        st.session_state["mostrar_form"] = True
        st.session_state["items_temp"] = []

    # --- Formulario Cotización ---
    if st.session_state["mostrar_form"]:
        with st.form("nueva_cotizacion"):
            st.subheader("Crear Cotización")
            numero = st.text_input("Número de cotización", value=f"COT-{len(st.session_state['cotizaciones'])+1:04d}")
            titulo = st.text_input("Título")
            cliente = st.text_input("Cliente")
            estado = st.selectbox("Estado", ["Enviada", "Aceptada", "Rechazada"])

            st.write("### Items de la proforma")
            desc = st.text_input("Descripción del servicio/producto")
            monto = st.number_input("Monto ($)", min_value=0.0, step=100.0)

            if st.form_submit_button("➕ Agregar Item"):
                if desc and monto > 0:
                    st.session_state["items_temp"].append((desc, monto))
                    st.success("Item agregado ✅")

            # Mostrar items
            if st.session_state["items_temp"]:
                st.table(pd.DataFrame(st.session_state["items_temp"], columns=["Descripción", "Monto"]))

            col1, col2 = st.columns(2)
            with col1:
                guardar = st.form_submit_button("✅ Guardar Cotización")
            with col2:
                cancelar = st.form_submit_button("❌ Cancelar")

            if guardar and titulo and cliente and st.session_state["items_temp"]:
                total = sum(m for _, m in st.session_state["items_temp"])
                nueva = pd.DataFrame([[numero, titulo, cliente, estado, st.session_state["items_temp"], total]], 
                                     columns=["Número", "Título", "Cliente", "Estado", "Items", "Monto"])
                st.session_state["cotizaciones"] = pd.concat(
                    [st.session_state["cotizaciones"], nueva], ignore_index=True
                )

                # Generar PDF
                pdf_file = generar_pdf(numero, cliente, st.session_state["items_temp"], total)
                with open(pdf_file, "rb") as f:
                    st.download_button("📥 Descargar PDF", f, file_name=pdf_file)

                # WhatsApp
                msg = f"Hola {cliente}, te envío la cotización {numero} por un total de ${total:,.2f}."
                whatsapp_url = f"https://wa.me/?text={msg}"
                st.markdown(f"[📲 Enviar por WhatsApp]({whatsapp_url})")

                st.success(f"Cotización **{numero}** creada con éxito ✅")
                st.session_state["mostrar_form"] = False

            if cancelar:
                st.session_state["mostrar_form"] = False

    st.markdown("---")

    # --- Filtros en la barra lateral ---
    with st.sidebar:
        st.image("logo.png", use_container_width=True)
        st.title("🏢 CRM")
        st.subheader("🔍 Filtros")
        buscar = st.text_input("Buscar por número o título")
        estados = ["Todos"] + st.session_state["cotizaciones"]["Estado"].unique().tolist()
        filtro_estado = st.selectbox("Estado", estados)
        clientes = ["Todos"] + st.session_state["cotizaciones"]["Cliente"].unique().tolist()
        filtro_cliente = st.selectbox("Cliente", clientes)
        aplicar = st.checkbox("Aplicar filtros", value=True)

    # --- Listado con filtros ---
    df = st.session_state["cotizaciones"].copy()

    if aplicar:
        if buscar:
            df = df[df["Número"].str.contains(buscar, case=False, na=False) |
                    df["Título"].str.contains(buscar, case=False, na=False)]
        if filtro_estado != "Todos":
            df = df[df["Estado"] == filtro_estado]
        if filtro_cliente != "Todos":
            df = df[df["Cliente"] == filtro_cliente]

    # --- Resumen ---
    if not df.empty:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1: st.metric("📄 Total", len(df))
        with col2: st.metric("🟡 Enviadas", len(df[df["Estado"]=="Enviada"]))
        with col3: st.metric("✅ Aceptadas", len(df[df["Estado"]=="Aceptada"]))
        with col4: st.metric("❌ Rechazadas", len(df[df["Estado"]=="Rechazada"]))
        with col5: st.metric("💲 Valor Total", f"${df['Monto'].sum():,.2f}")

    st.markdown("---")

    # --- Listado final ---
    if len(df) == 0:
        st.info("📄 No hay cotizaciones.")
    else:
        st.dataframe(df.drop(columns=["Items"]), use_container_width=True)


# --- Ejecutar vista ---
cotizaciones_view()
