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
]

dados = []

for item in cidades:

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={item['lat']}"
        f"&longitude={item['lon']}"
        "&current=temperature_2m"
    )

    resposta = requests.get(url)

    if resposta.status_code == 200:

        json_dados = resposta.json()

        temperatura = json_dados["current"]["temperature_2m"]

        dados.append({
            "cidade": item["cidade"],
            "latitude": item["lat"],
            "longitude": item["lon"],
            "temperatura": temperatura
        })

        df = pd.DataFrame(dados)

print(df)

mapa = folium.Map(
    location=[-15.00, -55.00],
    zoom_start=4
)

t_min = df["temperatura"].min()
t_max = df["temperatura"].max()
faixa = t_max - t_min

heat_data = []

for _, row in df.iterrows():

    if faixa > 0:
        rel = (row["temperatura"] - t_min) / faixa
        peso = 0.18 + 0.82 * rel
    else:
        peso = 1.0

    heat_data.append([
        row["latitude"],
        row["longitude"],
        peso
    ])

    HeatMap(
    heat_data,
    radius=30,
    blur=18,
    min_opacity=0.35,
).add_to(mapa)

for _, row in df.iterrows():

    lat, lon = row["latitude"], row["longitude"]
    cidade = row["cidade"]
    temp = row["temperatura"]
    temp_txt = f"{temp:g}°C"

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

    mapa.save("output/mapa_calor_temperaturas.html")

print("\nMapa gerado com sucesso!")
