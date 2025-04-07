import streamlit as st
import pandas as pd
import requests

API_KEY = "05281534ec3871021494e7b97911409f"
BASE_URL = "https://v3.football.api-sports.io"

headers = {
    "x-apisports-key": API_KEY
}

st.title("⚽ Predicción con Datos Reales - API Football")
st.markdown("Ingresa dos equipos reales y obtén estadísticas vivas directamente desde la API.")

# Entrada de equipos
team1 = st.text_input("🔵 Equipo Local", value="Bayern Munich")
team2 = st.text_input("🔴 Equipo Visitante", value="Inter Milan")

# Buscar equipo por nombre
def buscar_equipo(nombre):
    url = f"{BASE_URL}/teams?search={nombre}"
    r = requests.get(url, headers=headers)
    data = r.json()
    if data['response']:
        return data['response'][0]['team']['id'], data['response'][0]['team']['name']
    return None, nombre

# Obtener últimos partidos
def obtener_forma(team_id):
    url = f"{BASE_URL}/fixtures?team={team_id}&last=5"
    r = requests.get(url, headers=headers)
    data = r.json()
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

if team1 and team2:
    id1, name1 = buscar_equipo(team1)
    id2, name2 = buscar_equipo(team2)

    if id1 and id2:
        st.subheader(f"📊 Estadísticas: {name1} vs {name2}")

        stats1 = obtener_forma(id1)
        stats2 = obtener_forma(id2)

        df_stats = pd.DataFrame({
            "Estadística": ["Goles a favor (prom)", "Goles en contra (prom)", "Partidos ganados (últimos 5)"],
            name1: [round(stats1['prom_goles_favor'], 2), round(stats1['prom_goles_contra'], 2), stats1['partidos_ganados']],
            name2: [round(stats2['prom_goles_favor'], 2), round(stats2['prom_goles_contra'], 2), stats2['partidos_ganados']],
        })

        st.table(df_stats)

        # Simple predicción probabilística
        score1 = stats1['prom_goles_favor'] - stats1['prom_goles_contra'] + stats1['partidos_ganados']
        score2 = stats2['prom_goles_favor'] - stats2['prom_goles_contra'] + stats2['partidos_ganados']
        total = score1 + score2
        empate = 0.15
        prob1 = (score1 / total) * (1 - empate)
        prob2 = (score2 / total) * (1 - empate)
        prob_draw = empate

        df_pred = pd.DataFrame({
            "Resultado": [f"Victoria {name1}", "Empate", f"Victoria {name2}"],
            "Probabilidad (%)": [
                round(prob1 * 100, 1),
                round(prob_draw * 100, 1),
                round(prob2 * 100, 1)
            ]
        })

        st.markdown("### 🔮 Predicción Probabilística")
        st.table(df_pred)
    else:
        st.error("No se encontraron uno o ambos equipos.")
