import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Telesalud Hidalgo", layout="wide")

# Título
st.title("Análisis de Unidades de Telesalud en Hidalgo")

# Cargar datos
@st.cache_data
def load_data():
    file = "files/Especificaciones de las Unidades de Telesalud y Telemedicina_HGO_Implementadas_281125.xlsx"
    df = pd.read_excel(file)
    df_unidades = df[["Municipio","CLUES", "Nombre de la Unidad","Tipo de Unidad","Estatde la unidad"]].copy()
    df_unidades["Municipio"] = df_unidades["Municipio"].str.strip()
    return df_unidades

df_unidades = load_data()

# Mostrar métricas
col1, col2 = st.columns(2)
with col1:
    st.metric("Total de Municipios", df_unidades["Municipio"].nunique())
with col2:
    st.metric("Total de Unidades", len(df_unidades))

# Gráfico principal
st.subheader("Unidades por Municipio")

unidades_por_municipio = df_unidades.groupby('Municipio').size().reset_index(name='Cantidad de Unidades')
unidades_por_municipio = unidades_por_municipio.sort_values('Cantidad de Unidades', ascending=False)

fig = px.bar(unidades_por_municipio, 
             y='Municipio', 
             x='Cantidad de Unidades',
             title='Distribución de Unidades de Telesalud por Municipio',
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
st.subheader("Detalle de Unidades")
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
