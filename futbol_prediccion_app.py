import streamlit as st
import pandas as pd
import requests

API_KEY = "05281534ec3871021494e7b97911409f"
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": API_KEY
}

# Países europeos con ligas populares
paises_europa = [
    "Spain", "England", "Italy", "Germany", "France", "Portugal",
    "Netherlands", "Belgium", "Turkey", "Switzerland", "Austria"
]

st.title("🌍 Predicción por Liga y Temporada - Europa")
st.markdown("Selecciona un país europeo, una liga activa y dos equipos para comparar sus datos reales.")

# Obtener temporada actual desde API
def obtener_temporada_actual():
    url = f"{BASE_URL}/leagues"
    r = requests.get(url, headers=headers)
    data = r.json()
    if data['response']:
        return data['response'][0]['seasons'][-1]['year']
    return 2024

temporada = obtener_temporada_actual()
st.info(f"📅 Temporada detectada automáticamente: {temporada}")

# Seleccionar país
pais = st.selectbox("🌐 Selecciona un país europeo", paises_europa)

# Obtener ligas del país
def obtener_ligas(pais):
    url = f"{BASE_URL}/leagues?country={pais}&season={temporada}"
    r = requests.get(url, headers=headers)
    data = r.json()
    ligas = []
    for l in data['response']:
        ligas.append({
            "nombre": l['league']['name'],
            "id": l['league']['id']
        })
    return ligas

ligas = obtener_ligas(pais)
liga_nombres = [l['nombre'] for l in ligas]
liga_seleccionada = st.selectbox("🏆 Selecciona una liga", liga_nombres)

liga_id = next((l['id'] for l in ligas if l['nombre'] == liga_seleccionada), None)

# Obtener equipos por liga y temporada
def obtener_equipos(liga_id):
    url = f"{BASE_URL}/teams?league={liga_id}&season={temporada}"
    r = requests.get(url, headers=headers)
    data = r.json()
    equipos = []
    for e in data['response']:
        equipos.append({
            "id": e['team']['id'],
            "nombre": e['team']['name']
        })
    return equipos

equipos = obtener_equipos(liga_id)
nombres_equipos = [e['nombre'] for e in equipos]

equipo1 = st.selectbox("🔵 Equipo Local", nombres_equipos)
equipo2 = st.selectbox("🔴 Equipo Visitante", nombres_equipos)

id1 = next((e['id'] for e in equipos if e['nombre'] == equipo1), None)
id2 = next((e['id'] for e in equipos if e['nombre'] == equipo2), None)

# Obtener datos de forma
def obtener_forma(team_id):
    url = f"{BASE_URL}/fixtures?team={team_id}&last=5"
    r = requests.get(url, headers=headers)
    data = r.json()
    if not data['response']:
        return None
    goles_favor = 0
    goles_contra = 0
    ganados = 0
    for match in data['response']:
        if match['teams']['home']['id'] == team_id:
            goles_favor += match['goals']['home']
            goles_contra += match['goals']['away']
            if match['teams']['home']['winner']:
                ganados += 1
        else:
            goles_favor += match['goals']['away']
            goles_contra += match['goals']['home']
            if match['teams']['away']['winner']:
                ganados += 1
    return {
        "prom_goles_favor": goles_favor / 5,
        "prom_goles_contra": goles_contra / 5,
        "partidos_ganados": ganados
    }

if equipo1 != equipo2:
    stats1 = obtener_forma(id1)
    stats2 = obtener_forma(id2)

    if stats1 and stats2:
        st.subheader(f"📊 Estadísticas comparativas: {equipo1} vs {equipo2}")

        df_stats = pd.DataFrame({
            "Estadística": ["Goles a favor (prom)", "Goles en contra (prom)", "Partidos ganados (últimos 5)"],
            equipo1: [round(stats1['prom_goles_favor'], 2), round(stats1['prom_goles_contra'], 2), stats1['partidos_ganados']],
            equipo2: [round(stats2['prom_goles_favor'], 2), round(stats2['prom_goles_contra'], 2), stats2['partidos_ganados']],
        })

        st.table(df_stats)

        # Cálculo de predicción
        score1 = stats1['prom_goles_favor'] - stats1['prom_goles_contra'] + stats1['partidos_ganados']
        score2 = stats2['prom_goles_favor'] - stats2['prom_goles_contra'] + stats2['partidos_ganados']
        total = score1 + score2

        if total == 0:
            st.warning("No hay datos suficientes para generar una predicción.")
        else:
            empate = 0.15
            prob1 = (score1 / total) * (1 - empate)
            prob2 = (score2 / total) * (1 - empate)
            prob_draw = empate

            df_pred = pd.DataFrame({
                "Resultado": [f"Victoria {equipo1}", "Empate", f"Victoria {equipo2}"],
                "Probabilidad (%)": [
                    round(prob1 * 100, 1),
                    round(prob_draw * 100, 1),
                    round(prob2 * 100, 1)
                ]
            })

            st.markdown("### 🔮 Predicción Probabilística")
            st.table(df_pred)
    else:
        st.warning("Uno de los equipos no tiene datos recientes disponibles.")
else:
    st.info("Selecciona dos equipos diferentes para continuar.")
