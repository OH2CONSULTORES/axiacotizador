import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from fpdf import FPDF
from configuracion import get_empresa
import os
import urllib.parse
# -------------------------------
# Configuración inicial
# -------------------------------
DB_PATH = "data/cotizaciones.db"
PDF_DIR = "cotizaciones_pdf"
os.makedirs(PDF_DIR, exist_ok=True)

# -------------------------------
# Funciones de clientes
# -------------------------------
def get_clientes():
    conn = sqlite3.connect("data/clientes.db")
    c = conn.cursor()
    c.execute("SELECT empresa FROM clientes")
    empresas = [row[0] for row in c.fetchall()]
    conn.close()
    return empresas

def get_cliente_info(empresa):
    conn = sqlite3.connect("data/clientes.db")
    c = conn.cursor()
    c.execute("SELECT * FROM clientes WHERE empresa = ?", (empresa,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "empresa": row[1],
            "ruc": row[2],
            "direccion": row[3],
            "telefono": row[4],
            "contacto": row[5],
            "cargo": row[6],
            "sector": row[7],
            "estado": row[8],
        }
    return None

# -------------------------------
# Funciones de persistencia
# -------------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS cotizaciones (
            numero TEXT PRIMARY KEY,
            cliente TEXT,
            ruc TEXT,
            direccion TEXT,
            telefono TEXT,
            contacto TEXT,
            cargo TEXT,
            sector TEXT,
            fecha TEXT,
            problematica TEXT,
            servicios TEXT,
            entregables TEXT,
            valor_agregado TEXT,
            condiciones TEXT,
            monto REAL,
            estado TEXT,
            logo TEXT,
            usuario TEXT  -- <-- nuevo campo para guardar quien registró
        )
    """)
    # Tabla de trazabilidad
    c.execute("""
        CREATE TABLE IF NOT EXISTS trazabilidad (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT,
            monto REAL,
            usuario TEXT,
            fecha TEXT
        )
    """)

    conn.commit()
    conn.close()

def cargar_cotizaciones():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM cotizaciones", conn)
    conn.close()

    # Asegurarse de que existan las columnas
    if "servicios" not in df.columns:
        df["servicios"] = "[]"
    if "entregables" not in df.columns:
        df["entregables"] = "[]"

    if not df.empty:
        df["servicios"] = df["servicios"].apply(lambda x: eval(x) if isinstance(x, str) else x)
        df["entregables"] = df["entregables"].apply(lambda x: eval(x) if isinstance(x, str) else x)

    return df

def guardar_cotizacion(cotizacion):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO cotizaciones 
        (numero, cliente, ruc, direccion, telefono, contacto, cargo, sector, fecha, 
         problematica, servicios, entregables, valor_agregado, condiciones, monto, estado, logo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        cotizacion["numero"],              # <-- usar minúscula
        cotizacion["cliente"],
        cotizacion["ruc"],
        cotizacion["direccion"],
        cotizacion["telefono"],
        cotizacion["contacto"],
        cotizacion["cargo"],
        cotizacion["sector"],
        cotizacion["fecha"],
        cotizacion["problematica"],
        str(cotizacion["servicios"]),
        str(cotizacion["entregables"]),
        cotizacion["valor_agregado"],
        cotizacion["condiciones"],
        cotizacion["monto"],
        cotizacion["estado"],
        cotizacion["logo"]
    ))
    conn.commit()
    conn.close()
# -------------------------------

def limpiar_texto(texto):
    if not texto:
        return ""
    texto = texto.replace("“", '"').replace("”", '"')
    texto = texto.replace("‘", "'").replace("’", "'")
    texto = texto.replace("–", "-").replace("→", "->")
    return texto



# Función para generar PDF
def generar_pdf(cotizacion):
    empresa = get_empresa() or {
        "nombre": "Empresa no configurada",
        "logo": "",
        "direccion": "",
        "telefono": "",
        "email": ""
    }

    pdf = FPDF()
    pdf.add_page()

    # -------------------------------
    # Función segura para escribir texto
    # -------------------------------
    import textwrap
    def escribir_texto_seguro(pdf, texto, altura=6):
        if not texto:
            return
        pdf_w = pdf.w - 2 * pdf.l_margin  # ancho útil
        pdf.set_x(pdf.l_margin)
        # Convertir todos los saltos de línea a \n
        texto = limpiar_texto(texto).replace("\r\n", "\n").replace("\r", "\n")
        # multi_cell automáticamente respeta los \n
        pdf.multi_cell(pdf_w, altura, texto)

    # -------------------------------
    # Logo
    # -------------------------------
    if empresa.get("logo") and os.path.exists(empresa["logo"]):
        try:
            pdf.image(empresa["logo"], x=160, y=8, w=40)
        except Exception as e:
            print("Error al cargar logo:", e)

    pdf.set_xy(10, 8)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(100, 8, empresa["nombre"], ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(100, 6, empresa["direccion"], ln=True)
    pdf.cell(100, 6, f'Tel: {empresa["telefono"]}', ln=True)
    pdf.cell(100, 6, f'Email: {empresa["email"]}', ln=True)
    pdf.ln(15)

    # -------------------------------
    # Datos cotización
    # -------------------------------
    pdf.set_font("Arial", "B", 13)
    pdf.cell(0, 10, f"Cotización: {cotizacion['numero']}", ln=True, align="C")
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"Fecha: {cotizacion['fecha']}", ln=True, align="R")
    

    pdf.ln(10)  
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, "Sobre Nosotros", ln=True)

    pdf.set_font("Arial", "", 11)
    texto_sobre = (
        "AX.IIA CONSULTORES S.A.C. es una firma consultora especializada en el diseño, "
        "optimización y estandarización de procesos comerciales y logísticos. Nuestro equipo "
        "está conformado por tres profesionales con experiencia en gestión comercial, mejora "
        "de procesos, logística y transformación digital.\n\n"
        "Contamos con sólida trayectoria apoyando a MYPEs e industrias en la implementación "
        "de metodologías de gestión eficientes, herramientas digitales y modelos de atención "
        "al cliente que permiten mejorar la productividad y generar crecimiento sostenible. "
        "Nuestro enfoque combina diagnóstico estratégico, acompañamiento cercano y soluciones "
        "prácticas adaptadas a la realidad de cada empresa."
    )

    pdf.multi_cell(0, 6, texto_sobre, align="J")  # Justificado
    pdf.ln(10)  



    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Datos de cliente:", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, f"Cliente: {cotizacion['cliente']}", ln=True)
    pdf.cell(0, 6, f"RUC: {cotizacion['ruc']}", ln=True)
    pdf.cell(0, 6, f"Dirección: {cotizacion['direccion']}", ln=True)
    pdf.cell(0, 6, f"Teléfono: {cotizacion['telefono']}", ln=True)
    pdf.cell(0, 6, f"Contacto: {cotizacion['contacto']} ({cotizacion['cargo']})", ln=True)
    pdf.cell(0, 6, f"Sector: {cotizacion['sector']}", ln=True)
    pdf.ln(5)

    # -------------------------------
    # Problemática
    # -------------------------------
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Problemática del cliente:", ln=True)
    pdf.set_font("Arial", "", 11)
    escribir_texto_seguro(pdf, cotizacion.get("problematica",""))
    pdf.ln(3)

    # -------------------------------
    # Servicios
    # -------------------------------
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Servicios:", ln=True)
    pdf.set_font("Arial", "", 11)
    for s in cotizacion.get("servicios", []):
        escribir_texto_seguro(pdf, f"- {s.get('nombre','')}")
    pdf.ln(3)

    # -------------------------------
    # Entregables
    # -------------------------------
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Entregables:", ln=True)
    pdf.set_font("Arial", "", 11)
    for e in cotizacion.get("entregables", []):
        nombre = e.get("nombre", "")
        descripcion = e.get("descripcion", "")
        
        # Nombre como viñeta principal
        escribir_texto_seguro(pdf, f"- {nombre}")
        
        # Descripción como subpunto con sangría
        if descripcion:
            pdf.set_x(15)  # mueve un poco a la derecha
            escribir_texto_seguro(pdf, f"   {descripcion}")

    pdf.ln(2)  # espacio entre entregables



                "total_horas": total_horas,
                "dias_estimados": dias_estimados,
                "sesiones": sesiones,
                "modalidad": modalidad,
                "requisitos_texto": requisitos_texto,


            }

            guardar_cotizacion(nueva)

            # ---------- Guardar trazabilidad ----------
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""
                INSERT INTO trazabilidad (numero, monto, usuario, fecha)
                VALUES (?, ?, ?, ?)
            """, (numero, monto, usuario_actual, date.today().strftime("%d/%m/%Y")))
            conn.commit()
            conn.close()

            st.session_state["cotizaciones"] = cargar_cotizaciones()
            st.success(f"Cotización {numero} guardada ✅")

            generar_pdf(nueva)
            st.session_state["mostrar_form"] = False
            st.session_state["editar_numero"] = None

        if cancelar:
            st.session_state["mostrar_form"] = False
            st.session_state["editar_numero"] = None
# -------------------------------
# Vista principal

def cotizaciones_view():
    st.title("📄 Cotizaciones")
    st.caption("Gestiona tus propuestas comerciales")

    # -------------------------------
    # Siempre cargar cotizaciones desde DB al inicio
    st.session_state["cotizaciones"] = cargar_cotizaciones()

    if st.button("🔄 Actualizar cotizaciones"):
        st.session_state["cotizaciones"] = cargar_cotizaciones()
        st.rerun()
    # Botón para crear nueva cotización
    # -------------------------------
    if st.button("➕ Nueva Cotización", key="nueva_cotizacion"):
        st.session_state["mostrar_form"] = True
        st.session_state["editar_numero"] = None
        st.session_state["servicios"] = []
        st.session_state["entregables"] = []

    # -------------------------------
    # Mostrar formulario si se está creando o editando
    # -------------------------------
    if st.session_state.get("mostrar_form", False):
        editar = None
        if st.session_state.get("editar_numero"):
            df = st.session_state["cotizaciones"]
            if not df.empty and st.session_state["editar_numero"] in df["numero"].values:
                editar = df[df["numero"] == st.session_state["editar_numero"]].iloc[0].to_dict()

                # --- Servicios ---
                servicios_edit = editar.get("servicios", [])
                if isinstance(servicios_edit, str):
                    try:
                        servicios_edit = eval(servicios_edit)
                    except:
                        servicios_edit = []
                st.session_state["servicios"] = servicios_edit

                # --- Entregables ---
                entregables_edit = editar.get("entregables", [])
                if isinstance(entregables_edit, str):
                    try:
                        entregables_edit = eval(entregables_edit)
                    except:
                        entregables_edit = []
                st.session_state["entregables"] = entregables_edit

        formulario_cotizacion(editar)

    st.markdown("---")

    # -------------------------------
    # -------------------------------
    # Mostrar tabla de cotizaciones existentes
    # -------------------------------
    df = st.session_state.get("cotizaciones", pd.DataFrame())
    if df.empty:
        st.info("📄 No hay cotizaciones registradas.")
        return

    for i, row in df.iterrows():
        with st.expander(f"{row.get('numero','')} - {row.get('cliente','')} - S/. {row.get('monto',0.0):.2f}"):
            st.write(f"📅 Fecha: {row.get('fecha','')}")

            # Estado dinámico con colores
            estado = row.get("estado", "Redactado")
            if estado == "Redactado":
                st.markdown("**🟢 Estado:** Redactado (lista internamente)")
            elif estado == "Por enviar":
                st.markdown("**🟡 Estado:** Por enviar (pendiente de WhatsApp)")
            elif estado == "Enviado":
                st.markdown("**🔵 Estado:** Enviado (cliente tiene la cotización)")
            elif estado == "Aceptada":
                st.markdown("**✅ Estado:** Aceptada")
            elif estado == "Rechazada":
                st.markdown("**❌ Estado:** Rechazada")
            elif estado == "Convertida":
                st.markdown("**📑 Estado:** Convertida en contrato")
            else:
                st.markdown(f"**Estado:** {estado}")

            # columnas: Editar / PDF / Eliminar / WhatsApp / Contrato
            col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 2, 2])

            # --- Botón Editar ---
            with col1:
                if st.button("✏️ Editar", key=f"edit_{i}"):
                    st.session_state["mostrar_form"] = True
                    st.session_state["editar_numero"] = row.get("numero","")
                    # ... (tu lógica de cargar servicios y entregables)
                    st.rerun()

            # --- Botón PDF ---
            with col2:
                if st.button("📄 PDF", key=f"pdf_{i}"):
                    generar_pdf(row.to_dict())
                    st.success(f"PDF generado para {row.get('numero','')}")

            # --- Botón Eliminar ---
            with col3:
                if st.button("❌ Eliminar", key=f"delete_{i}"):
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("DELETE FROM cotizaciones WHERE numero = ?", (row.get('numero',''),))
                    conn.commit()
                    conn.close()
                    st.session_state["cotizaciones"] = cargar_cotizaciones()
                    st.success(f"Cotización {row.get('numero','')} eliminada ✅")
                    st.rerun()

            # --- Botón WhatsApp ---
            with col4:
                numero_whatsapp = st.text_input("📱 WhatsApp (+51...)", key=f"wa_{i}")
                if st.button("📩 Enviar", key=f"wa_send_{i}"):
                    if not numero_whatsapp:
                        st.warning("Ingrese un número de WhatsApp válido")
                    else:
                        pdf_path = os.path.abspath(os.path.join(PDF_DIR, f"COT-{row.get('numero','')}.pdf"))
                        mensaje = f"Hola {row.get('cliente','')},\n\nAdjunto la cotización {row.get('numero')}.\n\nSaludos."
                        mensaje_codificado = urllib.parse.quote(mensaje)
                        link_whatsapp = f"https://wa.me/{numero_whatsapp}?text={mensaje_codificado}"
                        st.markdown(f"[Abrir WhatsApp]({link_whatsapp})", unsafe_allow_html=True)

                        # Actualizar estado a "Enviado"
                        conn = sqlite3.connect(DB_PATH)
                        c = conn.cursor()
                        c.execute("UPDATE cotizaciones SET estado=? WHERE numero=?", ("Enviado", row.get("numero","")))
                        conn.commit()
                        conn.close()
                        st.success("Estado actualizado a Enviado ✅")
                        st.rerun()

            # --- Botón Convertir a Contrato ---
            with col5:
                if st.button("📑 Convertir a Contrato", key=f"contrato_{i}"):
                    conn = sqlite3.connect("data/contratos.db")
                    c = conn.cursor()
                    c.execute("""
                        CREATE TABLE IF NOT EXISTS contratos (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            titulo TEXT,
                            cliente TEXT,
                            servicios TEXT,
                            entregables TEXT,
                            valor REAL,
                            estado TEXT,
                            fecha TEXT,
                            observaciones TEXT
                        )
                    """)
                    c.execute("""
                        INSERT INTO contratos (titulo, cliente, servicios, entregables, valor, estado, fecha, observaciones)
                        VALUES (?,?,?,?,?,?,?,?)
                    """, (
                        f"Contrato derivado de {row.get('numero','')}",
                        row.get("cliente",""),
                        str(row.get("servicios","")),
                        str(row.get("entregables","")),
                        row.get("monto",0.0),
                        "Por firmar",
                        row.get("fecha",""),
                        f"Generado desde cotización {row.get('numero','')}"
                    ))
                    conn.commit()
                    conn.close()

                    # Cambiar estado de la cotización
                    conn2 = sqlite3.connect(DB_PATH)
                    c2 = conn2.cursor()
                    c2.execute("UPDATE cotizaciones SET estado=? WHERE numero=?", ("Convertida", row.get("numero","")))
                    conn2.commit()
                    conn2.close()

                    # Guardar contrato creado en session_state para redirigir
                    st.session_state["nuevo_contrato"] = {
                        "titulo": f"Contrato derivado de {row.get('numero','')}",
                        "cliente": row.get("cliente",""),
                        "valor": row.get("monto",0.0)
                    }

                    st.success(f"Cotización {row.get('numero','')} convertida en contrato ✅")
                    st.rerun()


    st.markdown("---")
    st.subheader("📊 Trazabilidad de cotizaciones")

    conn = sqlite3.connect(DB_PATH)
    df_traza = pd.read_sql("SELECT * FROM trazabilidad ORDER BY fecha DESC", conn)
    conn.close()

    if df_traza.empty:
        st.info("No hay registros de trazabilidad.")
    else:
        st.dataframe(df_traza[["numero","monto","usuario","fecha"]])

    # -------------------------------
    # Tiempo y modalidad
    # -------------------------------
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Tiempo y Modalidad:", ln=True)
    pdf.set_font("Arial", "", 11)
    escribir_texto_seguro(pdf, f"Total de horas: {cotizacion.get('total_horas', 0)}")
    escribir_texto_seguro(pdf, f"Días estimados: {cotizacion.get('dias_estimados', 0)}")
    escribir_texto_seguro(pdf, f"Sesiones previstas: {cotizacion.get('sesiones', 0)}")
    escribir_texto_seguro(pdf, f"Modalidad: {', '.join(cotizacion.get('modalidad', []))}")
    pdf.ln(5)



    # -------------------------------
    # Requisitos Básicos
    # -------------------------------
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Requisitos Básicos para Iniciar la Consultoría:", ln=True)
    pdf.set_font("Arial", "", 11)
    escribir_texto_seguro(pdf, cotizacion.get("requisitos_texto", ""))
    pdf.ln(5)


    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Cláusula de Confidencialidad", ln=True)
    pdf.set_font("Arial", "", 11)
    escribir_texto_seguro(pdf, 
        "Toda la información proporcionada por el cliente será tratada con absoluta reserva y "
        "utilizada exclusivamente para el desarrollo del plan comercial. El consultor se compromete "
        "a mantener estricta confidencialidad y aplicar el máximo cuidado profesional en el manejo "
        "de datos sensibles relacionados con la organización."
    )
    pdf.ln(5)



    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Próximos Pasos:", ln=True)
    pdf.set_font("Arial", "", 11)
    pasos = [
        "1. Confirmación de interés por parte del cliente.",
        "2. Aprobación formal de la propuesta presentada.",
        "3. Coordinación y agendamiento de la primera sesión de trabajo.",
        "4. Inicio de la ejecución del proyecto en la fecha acordada."
    ]
    for paso in pasos:
        escribir_texto_seguro(pdf, paso)





    # -------------------------------
    # Valor agregado y condiciones
    # -------------------------------
    pdf.cell(0, 6, ".", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Valor agregado:", ln=True)
    pdf.set_font("Arial", "", 11)
    escribir_texto_seguro(pdf, f"{cotizacion.get('valor_agregado','')}")


    pdf.cell(0, 6, ".", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Condiciones de pago", ln=True)
    pdf.set_font("Arial", "", 11)
    escribir_texto_seguro(pdf, cotizacion.get("condiciones",""))
    pdf.ln(5)

    # -------------------------------
    # Total
    # -------------------------------
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 6, f"TOTAL A PAGAR NO FACTURADO: S/. {cotizacion['monto']:.2f}", ln=True)

    # 👇 Agregamos espacio antes del bloque de agradecimiento
    pdf.ln(10)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, "Gracias por la confianza. Estoy a disposición para cualquier duda adicional o coordinación.", ln=True, align="R")
    pdf.cell(0, 6, "Atentamente,", ln=True, align="R")

    # -------------------------------
    # Firma
    # -------------------------------
    pdf.ln(30)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 6, "Atentamente,", ln=True, align="C")
    pdf.ln(1)

    firma_path = "imagen/firma.png"  # Ruta a tu archivo de firma
    if os.path.exists(firma_path):
        # Para centrar la firma calculamos posición X
        firma_w = 40
        x_centro = (pdf.w - firma_w) / 2
        pdf.image(firma_path, x=x_centro, w=firma_w)
        pdf.ln(-1)

    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 6, "Encargada del Área Comercial", ln=True, align="C")
    pdf.cell(0, 6, "Lizeth M. Balboa Quichua", ln=True, align="C")


    # -------------------------------
    # Guardar PDF
    # -------------------------------
    nombre_pdf = os.path.join(PDF_DIR, f"COT-{cotizacion['numero']}.pdf")
    pdf.output(nombre_pdf)
    return nombre_pdf

# -------------------------------
# Inicializar sesión
# -------------------------------
init_db()
if "cotizaciones" not in st.session_state:
    st.session_state["cotizaciones"] = cargar_cotizaciones()
if "mostrar_form" not in st.session_state:
    st.session_state["mostrar_form"] = False
if "editar_numero" not in st.session_state:
    st.session_state["editar_numero"] = None
if "servicios" not in st.session_state:
    st.session_state["servicios"] = []
if "entregables" not in st.session_state:
    st.session_state["entregables"] = []

# -------------------------------
# Formulario de cotización
def formulario_cotizacion(editar=None):
    st.subheader("Crear / Editar Cotización")

    # --- Servicios ---
    st.markdown("### ➕ Servicios")
    if st.button("➕ Añadir servicio"):
        st.session_state["servicios"].append({"nombre": "", "horas": 0.0, "costo_hora": 0.0, "subtotal": 0.0})

    # Si viene edición, cargar servicios
    if editar and "servicios" in editar:
        servicios_edit = editar["servicios"]
        if isinstance(servicios_edit, str):
            servicios_edit = eval(servicios_edit)
        st.session_state["servicios"] = servicios_edit

    for i, servicio in enumerate(st.session_state["servicios"]):
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        with col1:
            servicio["nombre"] = st.text_input(f"Nombre servicio {i+1}", key=f"s_nombre_{i}", value=servicio.get("nombre", ""))
        with col2:
            servicio["horas"] = st.number_input(f"Horas {i+1}", min_value=0.0, step=0.5, key=f"s_horas_{i}", value=servicio.get("horas", 0.0))
        with col3:
            servicio["costo_hora"] = st.number_input(f"Costo/h {i+1}", min_value=0.0, step=10.0, key=f"s_costo_{i}", value=servicio.get("costo_hora", 0.0))
        with col4:
            if st.button(f"❌{i+1}", key=f"s_delete_{i}"):
                st.session_state["servicios"].pop(i)
                st.rerun()
        servicio["subtotal"] = servicio["horas"] * servicio["costo_hora"]

    # --- Entregables ---
    st.markdown("### 📦 Entregables")
    if st.button("➕ Añadir entregable"):
        st.session_state["entregables"].append({"nombre": "", "descripcion": "", "subtotal": 0.0})

    # Si viene edición, cargar entregables
    if editar and "entregables" in editar:
        entregables_edit = editar["entregables"]
        if isinstance(entregables_edit, str):
            entregables_edit = eval(entregables_edit)
        st.session_state["entregables"] = entregables_edit

    for i, ent in enumerate(st.session_state["entregables"]):
        col1, col2, col3, col4 = st.columns([3, 4, 2, 1])
        with col1:
            ent["nombre"] = st.text_input(f"Nombre entregable {i+1}", key=f"e_nombre_{i}", value=ent.get("nombre", ""))
        with col2:
            ent["descripcion"] = st.text_input(f"Descripción {i+1}", key=f"e_desc_{i}", value=ent.get("descripcion", ""))
        with col3:
            ent["subtotal"] = st.number_input(f"Costo {i+1}", min_value=0.0, step=10.0, key=f"e_costo_{i}", value=ent.get("subtotal", 0.0))
        with col4:
            if st.button(f"❌ {i+1}", key=f"e_delete_{i}"):
                st.session_state["entregables"].pop(i)
                st.rerun()

    # --- Formulario principal ---
    with st.form("cotizacion_form"):
        numero = st.text_input(
            "Número",
            value=editar["numero"] if editar else f"{len(st.session_state['cotizaciones'])+1:04d}"
        )

        clientes_existentes = get_clientes()
        cliente = st.selectbox(
            "Cliente",
            clientes_existentes,
            index=clientes_existentes.index(editar["cliente"]) if editar else 0
        )

        cliente_info = get_cliente_info(cliente)

        fecha = st.date_input(
            "Fecha",
            value=pd.to_datetime(editar["fecha"]) if editar else date.today()
        )
        problematica = st.text_area(
            "Problemática",
            value=editar["problematica"] if editar else ""
        )
        st.subheader("⏱️ Tiempo y Modalidad")

        total_horas = sum([s["horas"] for s in st.session_state["servicios"]])
        horas_por_jornada = st.number_input("Horas por jornada", min_value=1, value=8)
        dias_estimados = round(total_horas / horas_por_jornada, 2)

        sesiones = st.number_input("Número de sesiones", min_value=1, value=1)
        modalidad = st.multiselect("Modalidad", ["Presencial", "Virtual"], default=["Presencial"])

        requisitos_texto = st.text_area(
            "Requisitos básicos para iniciar",
            value=editar.get("requisitos_texto", "") if editar else ""
        )
        




        st.subheader("📌 Requisitos Básicos para Iniciar la Consultoría")

        requisitos_texto = st.text_area("Escribe aquí los requisitos", height=150, key="req_texto")

        procesar_ia = st.form_submit_button("✨ Procesar con IA")
        if procesar_ia and requisitos_texto.strip():
            requisitos_texto = "Versión ordenada: " + requisitos_texto
            st.success("Texto reorganizado con IA")




        valor_agregado = st.text_area(
            "Valor agregado",
            value=editar["valor_agregado"] if editar else ""
        )

        # ==============================
        #   Condiciones de pago
        # ==============================
        monto = sum([s["subtotal"] for s in st.session_state["servicios"]]) + sum([e["subtotal"] for e in st.session_state["entregables"]])
        adelanto_50 = monto * 0.5
        igv = monto * 0.18
        monto_total_con_igv = monto + igv

        st.subheader("📌 Condiciones de Pago")
        condiciones_default = f"""Para iniciar con el servicio de consultoría, deberá enviar como evidencia de aceptación el adelanto del 50% del monto al número de WhatsApp +51 986 854 141

        Cuentas:
        - Banco BCP: 19302836915059
        - Yape: 914854496 a nombre Omer Himler Olortegui Haro

        Monto total: S/. {monto:,.2f}
        50% Adelanto: S/. {adelanto_50:,.2f}
        IGV 18%: S/. {igv:,.2f}
        Total con IGV: S/. {monto_total_con_igv:,.2f}"""
        
        # Si ya había condiciones guardadas, las usamos
        condiciones_inicial = editar["condiciones"] if editar else condiciones_default

        # Guardamos en session_state para que se pueda sobreescribir
        if "condiciones_texto" not in st.session_state:
            st.session_state["condiciones_texto"] = condiciones_inicial

        # Campo editable
        condiciones = st.text_area(
            "Condiciones de pago",
            value=st.session_state["condiciones_texto"],
            key="condiciones_area",
            height=300
        )




        # Botón para regenerar condiciones con los nuevos montos
        if st.form_submit_button("🔄 Recalcular condiciones de pago"):
            st.session_state["condiciones_texto"] = condiciones_default
            st.rerun()

        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("✅ Guardar y Generar PDF")
        with col2:
            cancelar = st.form_submit_button("❌ Cancelar")

        if submit and cliente_info:
            empresa = get_empresa() or {"logo": ""}
            usuario_actual = st.session_state.get("usuario_actual", "Desconocido")  # <-- línea nueva

            nueva = {
                "numero": numero,
                "cliente": cliente_info["empresa"],
                "ruc": cliente_info["ruc"],
                "direccion": cliente_info["direccion"],
                "telefono": cliente_info["telefono"],
                "contacto": cliente_info["contacto"],
                "cargo": cliente_info["cargo"],
                "sector": cliente_info["sector"],
                "fecha": fecha.strftime("%d/%m/%Y"),
                "problematica": problematica,
                "servicios": st.session_state["servicios"],
                "entregables": st.session_state["entregables"],
                "valor_agregado": valor_agregado,
                "condiciones": condiciones,
                "monto": monto,
                "estado": "Enviada",
                "logo": empresa["logo"],
                "usuario": usuario_actual,  # <-- guardamos el usuario

                    # 👇 aquí agregamos lo nuevo

