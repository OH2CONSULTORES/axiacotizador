import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense

st.set_page_config(page_title="Simulación de OEE con Red Neuronal", layout="wide")

st.title("📊 Simulación de OEE con Red Neuronal")
st.markdown("### Propuesta Lean Manufacturing - Imprenta de Avíos Textiles")

# -----------------------------
# Generar datos de simulación
# -----------------------------
st.sidebar.header("⚙️ Parámetros de Simulación")
n_datos = st.sidebar.slider("Cantidad de registros simulados", 50, 500, 200)

# Datos aleatorios simulados
tiempo_disponible = np.random.randint(400, 500, n_datos)  # minutos disponibles
tiempo_operacion = tiempo_disponible - np.random.randint(10, 100, n_datos)  # paradas
piezas_producidas = np.random.randint(800, 1200, n_datos)
piezas_buenas = piezas_producidas - np.random.randint(0, 100, n_datos)
piezas_teoricas = np.random.randint(1000, 1200, n_datos)

# Calcular métricas
disponibilidad = tiempo_operacion / tiempo_disponible
rendimiento = piezas_producidas / piezas_teoricas
calidad = piezas_buenas / piezas_producidas
oee = disponibilidad * rendimiento * calidad

# DataFrame
df = pd.DataFrame({
    "Tiempo Disponible": tiempo_disponible,
    "Tiempo Operación": tiempo_operacion,
    "Piezas Producidas": piezas_producidas,
    "Piezas Buenas": piezas_buenas,
    "Piezas Teóricas": piezas_teoricas,
    "Disponibilidad": disponibilidad,
    "Rendimiento": rendimiento,
    "Calidad": calidad,
    "OEE": oee
})

st.subheader("📋 Datos Simulados")
st.dataframe(df.head(10))

# -----------------------------
# Entrenar Red Neuronal
# -----------------------------
X = df[["Disponibilidad", "Rendimiento", "Calidad"]].values
y = df["OEE"].values

model = Sequential([
    Dense(8, input_dim=3, activation='relu'),
    Dense(4, activation='relu'),
    Dense(1, activation='linear')
])

model.compile(optimizer='adam', loss='mse')
model.fit(X, y, epochs=50, batch_size=10, verbose=0)

predicciones = model.predict(X).flatten()
df["OEE_Predicho"] = predicciones

# -----------------------------
# Visualización
# -----------------------------
st.subheader("📈 Comparación OEE Real vs Predicho")
fig, ax = plt.subplots()
ax.plot(df["OEE"].values[:50], label="OEE Real", marker="o")
ax.plot(df["OEE_Predicho"].values[:50], label="OEE Predicho (Red Neuronal)", marker="x")
ax.set_ylabel("OEE")
ax.legend()
st.pyplot(fig)

# -----------------------------
# Interpretación automática
# -----------------------------
st.subheader("📌 Interpretación Automática de Resultados")

prom_disp = np.mean(disponibilidad) * 100
prom_rend = np.mean(rendimiento) * 100
prom_cal = np.mean(calidad) * 100
prom_oee = np.mean(oee) * 100

st.markdown(f"""
**Resumen Promedios de la Simulación:**
- Disponibilidad: **{prom_disp:.2f}%**
- Rendimiento: **{prom_rend:.2f}%**
- Calidad: **{prom_cal:.2f}%**
- OEE Global: **{prom_oee:.2f}%**
""")

# Consejos automáticos según resultados
if prom_oee >= 85:
    interpretacion = "✅ Excelente nivel de OEE. El sistema es altamente productivo."
elif 60 <= prom_oee < 85:
    interpretacion = "⚠️ Nivel medio de OEE. Existen oportunidades de mejora en Disponibilidad, Rendimiento o Calidad."
else:
    interpretacion = "❌ Bajo nivel de OEE. Se requiere aplicar herramientas Lean de manera urgente."

st.info(f"**Interpretación del OEE:** {interpretacion}")

st.markdown("""
### 💡 Consejos de Mejora Continua:
- **Si la Disponibilidad es baja:** revisar tiempos muertos, aplicar TPM (mantenimiento preventivo).
- **Si el Rendimiento es bajo:** aplicar SMED, balanceo de línea y mejora de flujos.
- **Si la Calidad es baja:** aplicar Poka-Yoke, controles de calidad en línea y capacitación al personal.
""")

st.caption("Este simulador forma parte de la tesis: **'Propuesta de implementación de herramientas Lean Manufacturing para mejorar la productividad en una imprenta de avíos textiles'**.")
