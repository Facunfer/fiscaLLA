import pandas as pd
import plotly.graph_objects as go
import requests
import geopandas as gpd
import json
import plotly.express as px
import streamlit as st
from plotly.subplots import make_subplots

df = pd.read_csv("https://raw.githubusercontent.com/Facunfer/Streamlit/refs/heads/main/df.csv", low_memory=False)

llatot = df.loc[df['agrupacion_nombre'] == 'LA LIBERTAD AVANZA', ['seccion_nombre','circuito_nombre', 'agrupacion_nombre', 'votos_cantidad']]
jxctot = df.loc[df['agrupacion_nombre'] == 'JUNTOS POR EL CAMBIO', ['seccion_nombre','circuito_nombre', 'agrupacion_nombre', 'votos_cantidad']]
uxptot = df.loc[df['agrupacion_nombre'] == 'UNION POR LA PATRIA', ['seccion_nombre','circuito_nombre', 'agrupacion_nombre', 'votos_cantidad']]
fittot = df.loc[df['agrupacion_nombre'] == 'FRENTE DE IZQUIERDA Y DE TRABAJADORES - UNIDAD', ['seccion_nombre','circuito_nombre', 'agrupacion_nombre', 'votos_cantidad']]
hcctot = df.loc[df['agrupacion_nombre'] == 'HACEMOS POR NUESTRO PAIS', ['seccion_nombre','circuito_nombre', 'agrupacion_nombre', 'votos_cantidad']]
blancotot = df.loc[df['votos_tipo'] == 'EN BLANCO', ['seccion_nombre','circuito_nombre', 'votos_tipo', 'votos_cantidad']]
nulotot = df.loc[df['votos_tipo'] == 'NULO', ['seccion_nombre','circuito_nombre', 'votos_tipo', 'votos_cantidad']]
# Filtro DataFrame

totvotos = df.groupby(['seccion_nombre','circuito_nombre'])['votos_cantidad'].sum()
llavotos = llatot.groupby(['seccion_nombre','circuito_nombre'])['votos_cantidad'].sum()
jxcvotos = jxctot.groupby(['seccion_nombre','circuito_nombre'])['votos_cantidad'].sum()
uxpvotos = uxptot.groupby(['seccion_nombre','circuito_nombre'])['votos_cantidad'].sum()
fitvotos = fittot.groupby(['seccion_nombre','circuito_nombre'])['votos_cantidad'].sum()
hccvotos = hcctot.groupby(['seccion_nombre','circuito_nombre'])['votos_cantidad'].sum()
blancovotos = blancotot.groupby(['seccion_nombre','circuito_nombre'])['votos_cantidad'].sum()
nulovotos = nulotot.groupby(['seccion_nombre','circuito_nombre'])['votos_cantidad'].sum()
# agrupo votos de espacios por circuito

lista1 = []

for a, b, c, d, e, f, g, h, i, j in zip(totvotos.index.get_level_values(0), totvotos.index.get_level_values(1), totvotos.values, llavotos.values,jxcvotos.values,uxpvotos.values,fitvotos.values, hccvotos.values, blancovotos.values, nulovotos.values):
 lista1.append([a, b, c, d, e, f, g, h, i, j])
# Creo la Lista

columnas = ['seccion_nombre', 'circuito_nombre', 'totvotos', 'llavotos', 'jxcvotos', 'uxpvotos','fitvotos','hcfvotos','blancovotos','nulovotos']
#Le asigno nombres de columna

resultados2 = pd.DataFrame(lista1, columns=columnas)
resultados2["%LLA"] = resultados2["llavotos"] / resultados2["totvotos"] * 100
resultados2["%JXC"] = resultados2["jxcvotos"] / resultados2["totvotos"] * 100
resultados2["%UXP"] = resultados2["uxpvotos"] / resultados2["totvotos"] * 100
resultados2["%FIT"] = resultados2["fitvotos"] / resultados2["totvotos"] * 100
resultados2["%HCf"] = resultados2["hcfvotos"] / resultados2["totvotos"] * 100
resultados2["%Blanco"] = resultados2["blancovotos"] / resultados2["totvotos"] * 100
resultados2["%Nulo"] = resultados2["nulovotos"] / resultados2["totvotos"] * 100


def agregar_ceros(circuito_nombre):
    numero = int(circuito_nombre)  # Convertir a entero
    if numero < 10:        # Un dígito
        return f'0000{circuito_nombre}'
    elif numero < 100:      # Dos dígitos
        return f'000{circuito_nombre}'
    else:                   # Tres dígitos
        return f'00{circuito_nombre}'

# Aplicamos la función a la columna
resultados2['circuitomapa'] = resultados2['circuito_nombre'].apply(agregar_ceros)

resultados2['comuna_id'] = resultados2['seccion_nombre'].str.extract('(\d+)').astype(int)

def agregar(comuna_id):
    numero = int(comuna_id)
    if numero < 10:
        return f'00{comuna_id}'
    else:
        return f'0{comuna_id}'

resultados2['comuna_id'] = resultados2['comuna_id'].apply(agregar)

geojson="https://raw.githubusercontent.com/tartagalensis/circuitos_electorales_AR/main/geojson/CABA.geojson"
response = requests.get(geojson)
geojson_data1 = response.json()

gdf = gpd.GeoDataFrame.from_features(geojson_data1['features'])
merged_data = gdf.merge(resultados2, left_on='circuito', right_on='circuitomapa')
geojson_merged = json.loads(merged_data.to_json())


df1 = pd.read_csv("https://raw.githubusercontent.com/Facunfer/fiscaLLA/refs/heads/main/Establecimientos%20CABA%202023%20-%20Hoja%2010%20(1).csv", low_memory=False)

def agregar22(COMUNAID):
    numero = int(COMUNAID)
    if numero < 10:
        return f'00{COMUNAID}'
    else:
        return f'0{COMUNAID}'

df1['comuna_id1'] = df1['COMUNA ID'].apply(agregar22)





st.markdown(
    """
    <style>
    .stApp {
        background-color: #9370DB;  /* Color de fondo violeta */
        padding: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)




comunas_seleccionadas = st.multiselect('Selecciona Comunas', ['Todas las Comunas'] + resultados2['comuna_id'].unique().tolist())
tipo_capa = st.selectbox('Selecciona el tipo de capa', ['Votos por Circuito', 'Porcentaje por Circuito'])
if 'Todas las Comunas' in comunas_seleccionadas:
        resultados_filtrados = resultados2
        colegio_filtrado = df1

else:
        resultados_filtrados = resultados2[resultados2['comuna_id'].isin(comunas_seleccionadas)]
        colegio_filtrado = df1[df1['comuna_id1'].isin(comunas_seleccionadas)]
if 'Votos' in tipo_capa:
        color_column = 'llavotos'
        legend_name = 'Votos de LLA por Comuna'
else:
        color_column = '%LLA'
        legend_name = 'Porcentaje de Votos LLA'

colegio_filtrado['tooltip_info'] = (
    "📍 <b>Establecimiento:</b> " + colegio_filtrado['Establecimiento'] + "<br>" +
    "<b>Dirección:</b> " + colegio_filtrado['Direccion_establecimiento'] + "<br>" +
    "<b>Mesas Nacionales Nacionales:</b> " + colegio_filtrado['Total Nacionales'].astype(str) + "<br>" +
    "<b>Mesas Extranjeros:</b> " + colegio_filtrado['Total Extranjeros'].astype(str)+ "<br>" +
    "<b>Total de Mesas:</b> " + colegio_filtrado['Total Mesas'].astype(str)
     )


min_nacionales, max_nacionales = int(df1['Total Nacionales'].min()), int(df1['Total Nacionales'].max())
min_extranjeros, max_extranjeros = int(df1['Total Extranjeros'].min()), int(df1['Total Extranjeros'].max())
min_total, max_total = int(df1['Total Mesas'].min()), int(df1['Total Mesas'].max())

# Widgets en Streamlit para seleccionar rangos
filtro_nacionales = st.slider('Filtrar por Mesas Nacionales:', min_nacionales, max_nacionales, (min_nacionales, max_nacionales))
filtro_extranjeros = st.slider('Filtrar por Mesas Extranjeros:', min_extranjeros, max_extranjeros, (min_extranjeros, max_extranjeros))
filtro_total = st.slider('Filtrar por Total de Mesas:', min_total, max_total, (min_total, max_total))

# Aplicar los filtros al dataframe de colegios
colegio_filtrado = colegio_filtrado[
    (colegio_filtrado['Total Nacionales'] >= filtro_nacionales[0]) & (colegio_filtrado['Total Nacionales'] <= filtro_nacionales[1]) &
    (colegio_filtrado['Total Extranjeros'] >= filtro_extranjeros[0]) & (colegio_filtrado['Total Extranjeros'] <= filtro_extranjeros[1]) &
    (colegio_filtrado['Total Mesas'] >= filtro_total[0]) & (colegio_filtrado['Total Mesas'] <= filtro_total[1])
]

color_continuous_scale = [
        (0.0, "red"),
        (0.25, "orange"),
        (0.5, "yellow"),
        (0.75, "lightgreen"),
        (1.0, "green"),
    ]

    # Crear el mapa
mapa_fig = px.choropleth_mapbox(
        resultados_filtrados,
        geojson=geojson_merged,
        locations='circuitomapa',
        featureidkey="properties.circuitomapa",
        color=color_column,
        color_continuous_scale=color_continuous_scale,
        range_color=(resultados_filtrados[color_column].min(), resultados_filtrados[color_column].max()),
        labels={color_column: legend_name},
        title=f"{legend_name} - {', '.join(comunas_seleccionadas)}",
        mapbox_style="open-street-map",
        center={"lat": -34.6118, "lon": -58.3773},
        zoom=12,
        opacity=0.6
    )

mapa_fig.update_coloraxes(showscale=False)
mapa_fig.update_geos(fitbounds="locations", visible=False)
mapa_fig.update_layout(
        mapbox_zoom=12,
        mapbox_center={"lat": -34.6118, "lon": -58.3773},
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        uirevision='constant'
    )


mapa_fig.add_trace(go.Scattermapbox(
            lat=colegio_filtrado['Latitud '],
            lon=colegio_filtrado['Longitud'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=10,
                color="blue"
            ),
            text=colegio_filtrado['tooltip_info'],
            hoverinfo='text',
            showlegend=False  # Desactiva el indicador de escala en puntos
        ))
    # Mostrar el mapa en Streamlit
st.plotly_chart(mapa_fig)
