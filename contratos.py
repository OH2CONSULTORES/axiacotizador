# contratos.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from fpdf import FPDF
import os

# ==============================
# Carpetas para PDFs y evidencias
# ==============================
PDF_FOLDER = "data/contratos_pdf"
EVIDENCIA_FOLDER = "data/evidencias"
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(EVIDENCIA_FOLDER, exist_ok=True)

# ==============================
# Conexión a base de datos
# ==============================
DB_PATH = "data/contratos.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
            fecha DATE,
            evidencia_pago TEXT,
            firma_cliente TEXT,
            firma_empresa TEXT,
            observaciones TEXT,
            fecha_fin DATE,
            forma_pago TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==============================
# Clase PDF personalizada
# ==============================
class ContratoPDF(FPDF):
    def header(self):
        if os.path.exists("imagen/logo.png"):
            self.image("imagen/logo.png", 10, 8, 33)
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "CONTRATO DE SERVICIOS DE CONSULTORÍA", border=0, ln=True, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Página {self.page_no()}", align="C")

# ==============================
# Generar PDF del contrato
# ==============================
def generar_pdf(contrato):
    pdf = ContratoPDF()
    pdf.add_page()
    pdf.set_font("Arial", "", 11)

    # --- Datos de las partes ---
    pdf.multi_cell(0, 8, 
    f"""Entre **AX.IIA CONSULTORES S.A.C.**, con domicilio en Lima, en adelante "LA CONSULTORA",
y **{contrato['cliente']}**, en adelante "EL CLIENTE",
se acuerda lo siguiente:""")
    pdf.ln(5)

    # --- Objeto del contrato ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "1. Objeto del Contrato", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, contrato['titulo'])

    pdf.ln(3)
    # --- Servicios y entregables ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "2. Servicios y Entregables", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, f"Servicios: {contrato.get('servicios','No especificado')}")
    pdf.multi_cell(0, 8, f"Entregables: {contrato.get('entregables','No especificado')}")

    pdf.ln(3)
    # --- Condiciones económicas ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "3. Condiciones Económicas", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, 
    f"""El CLIENTE pagará a LA CONSULTORA la suma de S/. {contrato['valor']:.2f}.
Forma de pago: {contrato.get('forma_pago','Depósito bancario')}.""")

    pdf.ln(3)
    # --- Plazos ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "4. Plazos y Vigencia", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, 
    f"Inicio: {contrato['fecha']}  -  Fin: {contrato.get('fecha_fin','Por definir')}.")

    pdf.ln(3)
    # --- Obligaciones ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "5. Obligaciones de las Partes", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, 
    "- LA CONSULTORA: Cumplir con los entregables acordados en tiempo y forma.\n"
    "- EL CLIENTE: Proporcionar la información necesaria y efectuar los pagos en las fechas acordadas."
    )

    pdf.ln(3)
    # --- Confidencialidad ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "6. Confidencialidad", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, "Toda la información compartida será tratada de manera confidencial.")

    pdf.ln(3)
    # --- Terminación ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "7. Terminación", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, "Este contrato podrá resolverse por incumplimiento de cualquiera de las partes.")

    pdf.ln(5)
    # --- Firmas ---
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "8. Firmas", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, 
    f"""En señal de conformidad, ambas partes firman el presente contrato en Lima, a la fecha {contrato['fecha']}.

_________________________                _________________________
AX.IIA CONSULTORES S.A.C.                {contrato['cliente']}
Firma Empresa: {contrato.get('firma_empresa','________________')}
Firma Cliente: {contrato.get('firma_cliente','________________')}
""")

    # Observaciones
    if contrato.get("observaciones"):
        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 8, "Observaciones adicionales:", ln=True)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 8, contrato.get("observaciones",""))

    # Guardar PDF
    filename = os.path.join(PDF_FOLDER, f"Contrato_{contrato['id']}.pdf")
    pdf.output(filename)
    return filename

# ==============================
# Vista principal de contratos
# ==============================
def contratos_view():
    st.title("📑 Gestión de Contratos")
    st.write("Administra todos los contratos de consultoría")

    # Crear nuevo contrato
    st.subheader("➕ Crear/Registrar Contrato")
    with st.form("crear_contrato"):
        titulo = st.text_input("Título del Contrato / Objeto")
        cliente = st.text_input("Cliente")
        servicios = st.text_area("Servicios a Prestar (tomar de cotización)")
        entregables = st.text_area("Entregables / Resultados (tomar de cotización)")
        valor = st.number_input("Monto del Contrato", min_value=0.0, step=1.0)
        forma_pago = st.text_input("Forma de pago", value="Depósito bancario")
        fecha_fin = st.date_input("Fecha de finalización", value=None)
        evidencia_pago = st.file_uploader("Adjuntar evidencia de pago (PDF/Imagen)", type=["pdf","png","jpg","jpeg"])
        observaciones = st.text_area("Observaciones adicionales")
        submitted = st.form_submit_button("Registrar Contrato")

        if submitted:
            if cliente.strip() == "" or titulo.strip() == "" or valor <= 0:
                st.error("Debes completar todos los campos obligatorios")
            else:
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()

                evidencia_path = None
                if evidencia_pago:
                    evidencia_path = os.path.join(EVIDENCIA_FOLDER, f"{cliente}_{date.today().strftime('%Y%m%d')}_{evidencia_pago.name}")
                    with open(evidencia_path, "wb") as f:
                        f.write(evidencia_pago.getbuffer())

                c.execute("""
                    INSERT INTO contratos (titulo, cliente, servicios, entregables, valor, estado, fecha, evidencia_pago, observaciones, fecha_fin, forma_pago)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (titulo, cliente, servicios, entregables, valor, "Activo", date.today(), evidencia_path, observaciones, str(fecha_fin), forma_pago))
                conn.commit()
                contrato_id = c.lastrowid
                conn.close()

                contrato = {
                    "id": contrato_id,
                    "titulo": titulo,
                    "cliente": cliente,
                    "servicios": servicios,
                    "entregables": entregables,
                    "valor": valor,
                    "estado": "Activo",
                    "fecha": str(date.today()),
                    "observaciones": observaciones,
                    "fecha_fin": str(fecha_fin),
                    "forma_pago": forma_pago
                }
                pdf_file = generar_pdf(contrato)
                st.success(f"Contrato registrado ✅ PDF generado: {pdf_file}")

    st.markdown("---")
    st.subheader("📄 Contratos Existentes")

    # Mostrar contratos
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM contratos", conn)
    conn.close()

    if df.empty:
        st.info("No hay contratos registrados.")
        return

    # Filtros
    col_search, col_filter = st.columns([3,1])
    with col_search:
        search = st.text_input("🔍 Buscar por cliente o título...")
    with col_filter:
        estado_filter = st.selectbox("Filtrar por estado", ["Todos","Activo","Completado"])

    df_filtered = df.copy()
    if search:
        df_filtered = df_filtered[df_filtered["cliente"].str.contains(search, case=False) |
                                  df_filtered["titulo"].str.contains(search, case=False)]
    if estado_filter != "Todos":
        df_filtered = df_filtered[df_filtered["estado"]==estado_filter]

    for _, row in df_filtered.iterrows():
        with st.expander(f"{row['cliente']} - {row['titulo']} (S/. {row['valor']:,.2f})"):
            st.write(f"**Estado:** {row['estado']}")
            st.write(f"**Fecha:** {row['fecha']}")
            st.write(f"**Observaciones:** {row['observaciones']}")
            if row["evidencia_pago"]:
                st.write(f"📎 Evidencia de pago: {row['evidencia_pago']}")

            firma_cliente = st.text_input("Firma Cliente", value=row.get("firma_cliente",""), key=f"fc_{row['id']}")
            firma_empresa = st.text_input("Firma Empresa", value=row.get("firma_empresa",""), key=f"fe_{row['id']}")

            if st.button("Guardar cambios / firmar", key=f"guardar_{row['id']}"):
                conn = sqlite3.connect(DB_PATH)
                c = conn.cursor()
                c.execute("""
                    UPDATE contratos
                    SET firma_cliente=?, firma_empresa=?
                    WHERE id=?
                """, (firma_cliente, firma_empresa, row['id']))
                conn.commit()
                conn.close()

                contrato = dict(row)
                contrato["firma_cliente"] = firma_cliente
                contrato["firma_empresa"] = firma_empresa
                generar_pdf(contrato)
                st.success("Contrato actualizado y PDF regenerado ✅")
