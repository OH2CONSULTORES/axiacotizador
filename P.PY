# app.py
import streamlit as st
import pandas as pd
import plotly.express as px

# =======================
# DATOS BASE DEL TABLERO
# =======================
estrategias = {
    "Desarrollo profesional": [
        ("Cursos/certificaciones completadas", "Lean Six Sigma black Belt"),
        ("Cursos/certificaciones completadas", "Inglés"),
        ("Cursos/certificaciones completadas", "Scrum")
    ],
    "Resultados en el trabajo": [
        ("Cumplimiento a entregas", "95%"),
        ("Reducción de cartera vencida", "18 clientes")
    ],
    "Personalidad, Salud y Energía": [
        ("Horas de ejercicio por semana", "4 hrs de ejercicio semanales"),
        ("Hablar en Publico", "Dar 3 presentaciones en 2026"),
        ("Imagen Profesional", "Actualizar guardarropa antes de marzo 2026 + retro de 2 colegas")
    ],
    "Finanzas personales y crecimiento económico": [
        ("Ahorro mensual acumulado", "Ahorro de 6 meses de salario"),
        ("Ingreso Mensual por sueldo", "Incrementar 15% en 2026"),
        ("Ingreso Mensual con emprendimiento", "Lograr un 20% adicional al salario")
    ],
    "Relaciones y networking": [
        ("Número de contactos nuevos", "24 contactos profesionales por mes"),
        ("Reuniones de networking", "1 cada 3 meses")
    ]
}

# =======================
# INICIO APP
# =======================
st.set_page_config(page_title="📊 Tablero de Control Personal", layout="wide")
st.title("📊 Tablero de Control Personal 2026 - 2027")

# Crear dataframe base en session_state
if "df" not in st.session_state:
    rows = []
    for estrategia, kpis in estrategias.items():
        for kpi, meta in kpis:
            rows.append([estrategia, kpi, meta, "🟥 Rojo", 0, ""])
    st.session_state.df = pd.DataFrame(rows, columns=["Estrategia", "KPI", "Meta", "Semáforo", "Progreso", "Comentarios"])

df = st.session_state.df

# =======================
# FORMULARIO DE SEGUIMIENTO
# =======================
st.sidebar.header("➕ Agregar / Actualizar Progreso")
estrategia_sel = st.sidebar.selectbox("Estrategia", list(estrategias.keys()))
kpi_sel = st.sidebar.selectbox("KPI asociado", [k[0] + " - " + k[1] for k in estrategias[estrategia_sel]])
progreso = st.sidebar.slider("Progreso (%)", 0, 100, 0)
comentario = st.sidebar.text_area("Comentarios / Acciones")
semaforo = st.sidebar.selectbox("Semáforo", ["🟥 Rojo", "🟨 Amarillo", "🟩 Verde"])

if st.sidebar.button("Guardar actualización"):
    # extraer solo el KPI (parte izquierda antes del guión)
    kpi_name = kpi_sel.split(" - ")[0]
    # actualizar DataFrame
    df.loc[df["KPI"] == kpi_name, ["Progreso", "Comentarios", "Semáforo"]] = [progreso, comentario, semaforo]
    st.success("✅ Registro actualizado correctamente.")

# =======================
# TABLERO PRINCIPAL
# =======================
st.subheader("📋 Tablero Actualizado")
st.dataframe(df, use_container_width=True)

# =======================
# GRÁFICOS KPI
# =======================
st.subheader("📈 Visualización de KPIs")

fig = px.bar(df, x="KPI", y="Progreso", color="Semáforo",
             title="Progreso por KPI", text="Progreso")
fig.update_traces(texttemplate='%{text}%', textposition="outside")
st.plotly_chart(fig, use_container_width=True)

# =======================
# RESUMEN GENERAL
# =======================
st.subheader("📊 Resumen General")
resumen = df.groupby("Semáforo").size().reset_index(name="Cantidad")
st.dataframe(resumen)

pie = px.pie(resumen, values="Cantidad", names="Semáforo", title="Estado General del Tablero")
st.plotly_chart(pie, use_container_width=True)
