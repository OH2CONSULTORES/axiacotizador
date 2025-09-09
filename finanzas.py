# finanzas.py
import streamlit as st
import sqlite3
import pandas as pd

DB_COTIZACIONES = "cotizaciones.db"
DB_FINANZAS = "finanzas.db"

def finanzas_view():
    st.title("📊 Finanzas")

    menu_fin = st.radio("Selecciona sección:", ["Finanzas de Clientes", "Finanzas de la Empresa"])

    # ------------------------
    # FINANZAS DE CLIENTES
    # ------------------------
    if menu_fin == "Finanzas de Clientes":
        st.subheader("👥 Control de Pagos de Clientes")

        conn = sqlite3.connect(DB_COTIZACIONES)
        c = conn.cursor()
        # ✅ Creamos la tabla si no existe
        c.execute("""
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente TEXT,
                total REAL,
                adelanto REAL DEFAULT 0,
                pagado REAL DEFAULT 0,
                fecha TEXT
            )
        """)
        conn.commit()

        # Cargamos datos
        df = pd.read_sql_query("SELECT * FROM cotizaciones", conn)

        if df.empty:
            st.info("No hay cotizaciones registradas.")
        else:
            df["Saldo Pendiente"] = df["total"] - df.get("adelanto", 0) - df.get("pagado", 0)

            tab1, tab2, tab3 = st.tabs(["✅ Pagos Completos", "💰 Adelantos", "⏳ Pendientes"])

            with tab1:
                st.write("### Clientes que ya pagaron todo")
                df_completo = df[df["Saldo Pendiente"] <= 0]
                st.dataframe(df_completo)

            with tab2:
                st.write("### Clientes con adelantos")
                df_adelanto = df[(df.get("adelanto", 0) > 0) & (df["Saldo Pendiente"] > 0)]
                st.dataframe(df_adelanto)

            with tab3:
                st.write("### Clientes con saldo pendiente")
                df_pendiente = df[df["Saldo Pendiente"] > 0]
                st.dataframe(df_pendiente)

        conn.close()

    # ------------------------
    # FINANZAS DE LA EMPRESA
    # ------------------------
    elif menu_fin == "Finanzas de la Empresa":
        st.subheader("🏢 Control Financiero de la Empresa")

        conn = sqlite3.connect(DB_FINANZAS)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS finanzas_empresa (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT, -- 'ingreso' o 'egreso'
                descripcion TEXT,
                monto REAL,
                fecha TEXT
            )
        """)
        conn.commit()

        with st.form("nuevo_movimiento"):
            st.write("➕ Registrar Movimiento")
            tipo = st.selectbox("Tipo", ["ingreso", "egreso"])
            descripcion = st.text_input("Descripción")
            monto = st.number_input("Monto", min_value=0.0, step=0.1)
            fecha = st.date_input("Fecha")
            submitted = st.form_submit_button("Guardar")
            if submitted and descripcion and monto > 0:
                c.execute("INSERT INTO finanzas_empresa (tipo, descripcion, monto, fecha) VALUES (?,?,?,?)",
                          (tipo, descripcion, monto, str(fecha)))
                conn.commit()
                st.success("Movimiento registrado con éxito ✅")

        # Mostrar datos
        df_fin = pd.read_sql_query("SELECT * FROM finanzas_empresa", conn)
        conn.close()

        if df_fin.empty:
            st.info("No hay movimientos financieros registrados.")
        else:
            ingresos = df_fin[df_fin["tipo"] == "ingreso"]["monto"].sum()
            egresos = df_fin[df_fin["tipo"] == "egreso"]["monto"].sum()
            saldo = ingresos - egresos

            col1, col2, col3 = st.columns(3)
            col1.metric("💵 Ingresos", f"S/ {ingresos:,.2f}")
            col2.metric("📉 Egresos", f"S/ {egresos:,.2f}")
            col3.metric("📊 Saldo Neto", f"S/ {saldo:,.2f}")

            st.write("### 📑 Detalle de Movimientos")
            st.dataframe(df_fin)
