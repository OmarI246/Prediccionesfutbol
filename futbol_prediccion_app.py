import streamlit as st
import pandas as pd
import requests
from datetime import datetime

API_KEY = "05281534ec3871021494e7b97911409f"
BASE_URL = "https://v3.football.api-sports.io"
HEADERS = {"x-apisports-key": API_KEY}

st.title("⚽ Predicción por Liga y Temporada")
st.markdown("Selecciona un país, una liga y dos equipos para comparar sus datos reales.")

# Detectar temporada actual automáticamente
def temporada_actual():
    hoy = datetime.today()
    return hoy.year if hoy.month >= 8 else hoy.year - 1

TEMPORADA = temporada_actual()
st.markdown(f"📅 Temporada detectada automáticamente: **{TEMPORADA}**")

# Obtener lista de países
@st.cache_data
def obtener_paises():
    url = f"{BASE_URL}/countries"
    res = requests.get(url, headers=HEADERS).json()
    return sorted([c["name"] for c in res["response"]])

# Obtener ligas por país
def obtener_ligas(pais):
    url = f"{BASE_URL}/leagues?country={pais}"
    res = requests.get(url, headers=HEADERS).json()
    ligas = []
    for l in res["response"]:
        nombre = l["league"]["name"]
        id_liga = l["league"]["id"]
        if l["seasons"]:
            temporadas = [t["year"] for t in l["seasons"]]
            if TEMPORADA in temporadas:
                ligas.append((nombre, id_liga))
    return ligas

# Obtener equipos en la liga
def obtener_equipos(league_id):
    url = f"{BASE_URL}/teams?league={league_id}&season={TEMPORADA}"
    res = requests.get(url, headers=HEADERS).json()
    return {t["team"]["name"]: t["team"]["id"] for t in res["response"]}

# Obtener forma reciente
def obtener_forma(team_id, league_id):
    url = f"{BASE_URL}/fixtures?team={team_id}&season={TEMPORADA}&league={league_id}"
    r = requests.get(url, headers=HEADERS)
    data = r.json()
    partidos = data['response'][-5:]  # últimos 5
    if not partidos:
        return None
    goles_favor = 0
    goles_contra = 0
    ganados = 0
    for match in partidos:
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

# UI país → liga → equipos
pais = st.selectbox("🌍 Selecciona un país", obtener_paises())

ligas_disponibles = obtener_ligas(pais)
liga_nombre = st.selectbox("🏆 Selecciona una liga", [l[0] for l in ligas_disponibles])
liga_id = [l[1] for l in ligas_disponibles if l[0] == liga_nombre][0]

equipos = obtener_equipos(liga_id)
equipo1 = st.selectbox("🔵 Equipo Local", list(equipos.keys()))
equipo2 = st.selectbox("🔴 Equipo Visitante", list(equipos.keys()), index=1 if len(equipos) > 1 else 0)

# Ejecutar análisis
if equipo1 and equipo2 and equipo1 != equipo2:
    id1 = equipos[equipo1]
    id2 = equipos[equipo2]

    st.subheader(f"📊 Estadísticas: {equipo1} vs {equipo2} ({liga_nombre} {TEMPORADA})")

    stats1 = obtener_forma(id1, liga_id)
    stats2 = obtener_forma(id2, liga_id)

    if stats1 is None or stats2 is None:
        st.warning("Uno o ambos equipos no tienen partidos recientes registrados.")
    else:
        df_stats = pd.DataFrame({
            "Estadística": ["Goles a favor (prom)", "Goles en contra (prom)", "Partidos ganados (últimos 5)"],
            equipo1: [round(stats1['prom_goles_favor'], 2), round(stats1['prom_goles_contra'], 2), stats1['partidos_ganados']],
            equipo2: [round(stats2['prom_goles_favor'], 2), round(stats2['prom_goles_contra'], 2), stats2['partidos_ganados']],
        })

        st.table(df_stats)

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
    st.info("Selecciona dos equipos diferentes para continuar.")
