import requests
import pandas as pd
import folium
from folium.plugins import HeatMap


cidades = [
    {"cidade": "Rio de Janeiro", "lat": -22.90, "lon": -43.17},
    {"cidade": "São Paulo", "lat": -23.55, "lon": -46.63},
    {"cidade": "Brasília", "lat": -15.79, "lon": -47.88},
    {"cidade": "Salvador", "lat": -12.97, "lon": -38.50},
    {"cidade": "Manaus", "lat": -3.10, "lon": -60.02},
    {"cidade": "Curitiba", "lat": -25.42, "lon": -49.27},
    {"cidade": "Recife", "lat": -8.05, "lon": -34.88},
    {"cidade": "Bangu", "lat": -22.87, "lon": -43.46},
]
ano = 2025

data_inicio = f"{ano}-01-01"
data_fim = f"{ano}-12-31"

resultados = []
for item in cidades:

    cidade = item["cidade"]
    latitude = item["lat"]
    longitude = item["lon"]

    print(f"Consultando dados de {cidade}...")

    url = (
        "https://archive-api.open-meteo.com/v1/archive"
        f"?latitude={latitude}"
        f"&longitude={longitude}"
        f"&start_date={data_inicio}"
        f"&end_date={data_fim}"
        "&daily=temperature_2m_mean"
        "&timezone=America/Sao_Paulo"
    )

    resposta = requests.get(url)

    if resposta.status_code != 200:
        print(f"Erro ao consultar {cidade}")
        continue

    dados_json = resposta.json()

    df = pd.DataFrame({
        "data": dados_json["daily"]["time"],
        "temperatura_media_diaria": dados_json["daily"]["temperature_2m_mean"]
    })

    df["data"] = pd.to_datetime(df["data"])

    temperatura_media_anual = df["temperatura_media_diaria"].mean()

    resultados.append({
        "cidade": cidade,
        "latitude": latitude,
        "longitude": longitude,
        "temperatura_media_anual": temperatura_media_anual
    })
    df_resultado = pd.DataFrame(resultados)

print("\nTemperatura média anual por cidade:")
print(df_resultado)

df_resultado.to_csv("output/temperatura_media_anual_cidades.csv", index=False)

mapa = folium.Map(
    location=[-15.0, -55.0],
    zoom_start=4
)
t_min = df_resultado["temperatura_media_anual"].min()
t_max = df_resultado["temperatura_media_anual"].max()
faixa = t_max - t_min

heat_data = []

for _, linha in df_resultado.iterrows():

    temp = linha["temperatura_media_anual"]

    if faixa > 0:
        rel = (temp - t_min) / faixa
        peso = 0.18 + 0.82 * rel
    else:
        peso = 1.0

    heat_data.append([
        linha["latitude"],
        linha["longitude"],
        peso
    ])

HeatMap(
    heat_data,
    radius=30,
    blur=18,
    min_opacity=0.35,
).add_to(mapa)
for _, linha in df_resultado.iterrows():

    lat = linha["latitude"]
    lon = linha["longitude"]
    cidade = linha["cidade"]
    temp = linha["temperatura_media_anual"]
    temp_txt = f"{temp:.1f}°C"

    folium.CircleMarker(
        location=[lat, lon],
        radius=58,
        stroke=False,
        fill=True,
        fill_color="#ffffff",
        fill_opacity=0.012,
        tooltip=folium.Tooltip(
            f"<b>{cidade}</b><br>{temp_txt}",
            sticky=True,
        ),
    ).add_to(mapa)

    folium.Marker(
        location=[lat, lon],
        icon=folium.DivIcon(
            icon_size=(80, 22),
            icon_anchor=(40, 11),
            html=(
                "<div style=\""
                "font-size:13px;font-weight:700;color:#fff;"
                "text-align:center;line-height:22px;width:80px;"
                "text-shadow:0 0 4px #000,0 0 10px #000;"
                "pointer-events:none;\">"
                f"{temp_txt}</div>"
            ),
        ),
    ).add_to(mapa)

mapa.save("output/mapa_calor_temperatura_media_anual.html")

print("\nMapa de calor gerado com sucesso!")
print("Arquivo criado: mapa_calor_temperatura_media_anual.html")
