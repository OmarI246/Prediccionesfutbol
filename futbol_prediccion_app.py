import streamlit as st
import pandas as pd

# Datos simulados de equipos
equipos_data = {
    "Bayern de Múnich":        [9.0, 8.5, 9.0, 5.0, 6.0, 8.5],
    "Inter de Milán":          [8.0, 7.0, 6.5, 6.0, 8.5, 7.0],
    "Manchester City":         [9.5, 9.0, 9.0, 4.5, 9.0, 9.0],
    "Real Madrid":             [9.0, 9.0, 8.5, 4.0, 8.5, 9.0],
    "Boca Juniors":            [6.5, 6.0, 7.5, 6.0, 6.5, 6.0],
    "Cruz Azul":               [6.0, 5.5, 6.0, 6.5, 6.0, 5.5]
}

# Encabezados de los factores
factores = ["Forma reciente", "Historial directo", "Condición de local", "Lesiones y ausencias", "Defensa del rival", "Cuotas de apuestas"]
ponderaciones = [0.2, 0.15, 0.2, 0.1, 0.15, 0.2]

# Título e instrucciones
st.title("⚽ Predicción de Partidos de Fútbol - Nivel 2")
st.markdown("Compara dos equipos y genera predicciones basadas en datos dinámicos simulados.")

# Entradas de usuario
equipo_local = st.text_input("🔵 Equipo Local", value="Bayern de Múnich")
equipo_visitante = st.text_input("🔴 Equipo Visitante", value="Inter de Milán")

if equipo_local and equipo_visitante:
    # Obtener datos de los equipos
    datos_local = equipos_data.get(equipo_local, [6.0]*6)
    datos_visitante = equipos_data.get(equipo_visitante, [6.0]*6)

    # Crear DataFrame comparativo
    df = pd.DataFrame({
        "Factor": factores,
        equipo_local: datos_local,
        equipo_visitante: datos_visitante,
        "Ponderación": ponderaciones
    })

    # Calcular score ponderado
    df["Score " + equipo_local] = df[equipo_local] * df["Ponderación"]
    df["Score " + equipo_visitante] = df[equipo_visitante] * df["Ponderación"]
    score_local = df["Score " + equipo_local].sum()
    score_visitante = df["Score " + equipo_visitante].sum()

    st.markdown("### 📊 Comparativa de Factores")
    st.dataframe(df[["Factor", equipo_local, equipo_visitante]])

    # Calcular predicción
    total = score_local + score_visitante
    empate = 0.15
    prob_local = (score_local / total) * (1 - empate)
    prob_visitante = (score_visitante / total) * (1 - empate)
    prob_empate = empate

    st.markdown("### 🔮 Predicción del Resultado")
    pred_df = pd.DataFrame({
        "Resultado": [f"Victoria {equipo_local}", "Empate", f"Victoria {equipo_visitante}"],
        "Probabilidad (%)": [
            round(prob_local * 100, 1),
            round(prob_empate * 100, 1),
            round(prob_visitante * 100, 1)
        ]
    })
    st.table(pred_df)

    # Recomendación
    if prob_local > prob_visitante:
        st.success(f"📌 {equipo_local} tiene una ventaja en este enfrentamiento.")
    elif prob_visitante > prob_local:
        st.success(f"📌 {equipo_visitante} parece más fuerte en los datos.")
    else:
        st.info("📌 ¡Partido muy parejo! Podría ser empate.")

else:
    st.warning("Por favor, ingresa ambos equipos para comenzar el análisis.")
