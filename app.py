import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import geopandas as gpd
import json

# Configuración de la página
st.set_page_config(page_title="Telesalud Hidalgo", layout="wide")

# Título
st.title("Análisis de Unidades de Telesalud en Hidalgo")

# Cargar datos
@st.cache_data
def load_data():
    file = "files/Especificaciones de las Unidades de Telesalud y Telemedicina_HGO_Implementadas_281125.xlsx"
    df = pd.read_excel(file)
    df_unidades = df[["Municipio","CLUES", "Nombre de la Unidad"]].copy()
    df_unidades["Municipio"] = df_unidades["Municipio"].str.strip()
    df_unidades["CLUES"] = df_unidades["CLUES"].str.strip()
    
    # Cargar coordenadas
    file_coor = "files/catalogo_clues_limpio.csv"
    df_coor = pd.read_csv(file_coor)
    df_coor["CLUES"] = df_coor["CLUES"].str.strip()
    df_merged = pd.merge(df_unidades, df_coor, on="CLUES", how="left")
    
    return df_merged

df_unidades = load_data()

# Mostrar métricas
col1, col2 = st.columns(2)
with col1:
    st.metric("Total de Municipios", df_unidades["Municipio"].nunique())
with col2:
    st.metric("Total de Unidades", len(df_unidades))

# Mapa de ubicaciones
st.subheader("📍 Mapa de Unidades de Telesalud")

df_mapa = df_unidades.dropna(subset=['LATITUD', 'LONGITUD'])

# Crear figura base
fig_mapa = go.Figure()

# Agregar el contorno de Hidalgo
file_contorno = "files/13ent.shp"
contorno_hgo = gpd.read_file(file_contorno).to_crs(epsg=4326)

# Extraer coordenadas del polígono
for geometry in contorno_hgo.geometry:
    if geometry.geom_type == 'Polygon':
        x, y = geometry.exterior.xy
        fig_mapa.add_trace(go.Scattermap(
            lon=list(x),
            lat=list(y),
            mode='lines',
            line=dict(width=3, color='darkgreen'),
            fill='toself',
            fillcolor='rgba(76, 175, 80, 0.2)',
            name='Hidalgo',
            hoverinfo='skip'
        ))
    elif geometry.geom_type == 'MultiPolygon':
        for poly in geometry.geoms:
            x, y = poly.exterior.xy
            fig_mapa.add_trace(go.Scattermap(
                lon=list(x),
                lat=list(y),
                mode='lines',
                line=dict(width=3, color='darkgreen'),
                fill='toself',
                fillcolor='rgba(76, 175, 80, 0.2)',
                name='Hidalgo',
                hoverinfo='skip',
                showlegend=False
            ))

# Agregar puntos de unidades por municipio con emojis
municipios_unicos = df_mapa['Municipio'].unique()
colors = px.colors.qualitative.Light24

for i, municipio in enumerate(municipios_unicos):
    df_temp = df_mapa[df_mapa['Municipio'] == municipio]
    
    # Primero agregar círculos de fondo
    fig_mapa.add_trace(go.Scattermap(
        lon=df_temp['LONGITUD'],
        lat=df_temp['LATITUD'],
        mode='markers',
        marker=dict(
            size=20,
            color=colors[i % len(colors)],
            opacity=0.7
        ),
        hovertext=[f"<b>{nombre}</b><br>Municipio: {municipio}<br>CLUES: {clues}<br>Localidad: {loc}" 
                   for nombre, clues, loc in zip(df_temp['Nombre de la Unidad'], 
                                                   df_temp['CLUES'], 
                                                   df_temp['LOCALIDAD'])],
        hoverinfo='text',
        name=municipio,
        showlegend=True
    ))
    
    # Luego agregar emojis encima
    fig_mapa.add_trace(go.Scattermap(
        lon=df_temp['LONGITUD'],
        lat=df_temp['LATITUD'],
        mode='text',
        text='🏥',
        textfont=dict(size=16),
        hoverinfo='skip',
        showlegend=False
    ))

fig_mapa.update_layout(
    map=dict(
        style='open-street-map',
        center=dict(lat=20.0911, lon=-98.7625),
        zoom=8
    ),
    height=700,
    margin={"r":0,"t":50,"l":0,"b":80},
    showlegend=True,
    legend=dict(
        orientation="h",  # Horizontal
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5,
        bgcolor="rgba(255, 255, 255, 0.9)",
        bordercolor="gray",
        borderwidth=1,
        font=dict(size=9, color='black')
    ),
    title='Ubicación de las Unidades en el Estado de Hidalgo'
)

st.plotly_chart(fig_mapa, width='stretch')

# Gráfico de barras
st.subheader("📊 Distribución por Municipio")

unidades_por_municipio = df_unidades.groupby('Municipio').size().reset_index(name='Cantidad de Unidades')
unidades_por_municipio = unidades_por_municipio.sort_values('Cantidad de Unidades', ascending=False)

fig = px.bar(unidades_por_municipio, 
             y='Municipio', 
             x='Cantidad de Unidades',
             title='Número de Unidades por Municipio',
             orientation='h',
             color='Cantidad de Unidades',
             color_continuous_scale='Cividis',
             text='Cantidad de Unidades')

fig.update_traces(textposition='outside')
fig.update_layout(
    height=1200,
    yaxis={
        'categoryorder':'total ascending',
        'tickfont': {'size': 10}
    },
    xaxis_title='Cantidad de Unidades',
    yaxis_title='Municipio',
    showlegend=False,
    margin=dict(l=150, r=50, t=80, b=50)
)

st.plotly_chart(fig, width='stretch')

# Filtro para la tabla
st.subheader("📋 Detalle de Unidades")
municipios_disponibles = ["Todos"] + sorted(df_unidades["Municipio"].unique().tolist())
municipio_seleccionado = st.selectbox(
    "Filtrar tabla por municipio:",
    municipios_disponibles
)

# Filtrar datos según selección
if municipio_seleccionado != "Todos":
    df_filtrado = df_unidades[df_unidades["Municipio"] == municipio_seleccionado]
else:
    df_filtrado = df_unidades

# Mostrar tabla filtrada
st.dataframe(df_filtrado, width='stretch')
st.info(f"📊 Mostrando {len(df_filtrado)} unidades de {municipio_seleccionado}")
