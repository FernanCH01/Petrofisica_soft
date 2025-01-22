# Import Python Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
from pathlib import Path
import lasio
import welly
import matplotlib.pyplot as plt

# icono
icon = Image.open('logo/icono.jpg')

st.set_page_config(page_title="Petrophysics App", page_icon=icon)
# Insert css codes to improve the design of the app
st.markdown(
    """
<style>
h1 {text-align: center;
}
body {background-color: #DCE3D5;
      width: 1400px;
      margin: 15px auto;
}
footer {
  display: none;
}
</style>""",
    unsafe_allow_html=True,
)

# Insert title for app
st.title("Petrophysics App")

st.write("---")

logo = Image.open("logo/logo_stech.jpg")
st.image(logo, width=100, use_container_width=True)

# Add information of the app
st.markdown(
    """

Petrophysics App es una solución integral enfocada en la gestión y análisis de datos de pozos petroleros. Proporciona herramientas especializadas para evaluar registros eléctricos, sónicos, de densidad y porosidad, permitiendo una caracterización precisa de los yacimientos y la identificación eficiente de áreas con potencial productivo."""

)

# Add additional information
expander = st.expander("Information")
expander.write(
    "Petrophysics App es una aplicación web de código abierto, desarrollada completamente en Python, diseñada para analizar y optimizar datos de registros de pozos. Facilita la interpretación de parámetros petrofísicos como porosidad, saturación de fluidos y permeabilidad, apoyando la toma de decisiones en tiempo real y la caracterización de yacimientos."
)

# Insert subheader
st.subheader("*¿Qué son los registros de pozos?*")

st.markdown(
    """

Los registros de pozos son mediciones obtenidas con herramientas especiales dentro de un pozo perforado. Estas registran propiedades físicas como resistividad, densidad, porosidad y velocidad sónica, ayudando a analizar las características del subsuelo y los yacimientos."""

)

registro = Image.open("logo/registro_pozo.jpg")
st.image(registro, width=100, use_container_width=True)

# Sección para importar y explorar archivos LAS
st.subheader("Importar y explorar archivos LAS")


# Función para calcular parámetros petrofísicos
def calcular_parametros(las_df):
    # Volument de arcilla (Vshale)
    las_df["SWIRR"] = las_df["SW"] * las_df["BVW"]

    # Porosidad efectiva
    las_df["PHIE"] = las_df["PHIF"] * (1 - las_df["SWIRR"])
    return las_df


# Subir archivo LAS

# Cargar archivo LAS
uploaded_file = st.file_uploader("Cargar archivo LAS", type=["las"])

if uploaded_file is not None:
    try:
        # Convertir archivo cargado a formato compatible con lasio
        las = lasio.read(uploaded_file.read().decode("utf-8"))

        # Mostrar metadatos
        st.write("### Metadatos del archivo LAS")
        st.write("Campo: Volve (Noruega)")
        st.text(f"Versión: {las.version[0].value}")
        st.text(f"Pozo: {las.well.WELL.value}")

        # Mostrar canales disponibles
        st.write("### Canales disponibles")
        st.text(", ".join(las.keys()))

        # Convertir datos del archivo LAS a DataFrame
        las_df = las.df()

        # Mostrar DataFrame
        st.write("### Vista previa de los datos")
        st.dataframe(las_df.head(10))

        # Agregar descarga del DataFrame en formato CSV
        csv = las_df.to_csv().encode('utf-8')
        st.download_button(
            label="Descargar datos como CSV",
            data=csv,
            file_name="datos_volve.csv",
            mime="text/csv",
        )

        # Sección para cálculos petrofísicos
        st.write("## Cálculos Petrofísicos")
        las_df = calcular_parametros(las_df)
        st.write("### Resultados de Cálculos Petrofísicos")
        st.dataframe(las_df[["PHIE", "SWIRR"]].head(10))

        # Agregar sección para graficar registros petrofísicos
        st.write("## Gráficos de registros petrofísicos")
        disponibles = list(las.keys())
        tracks = st.multiselect("Selecciona los tracks que deseas graficar",
                                disponibles,
                                default=["KLOGH", "PHIF", "SAND_FLAG", "SW", "VSH"])

        if tracks:
            fig, axes = plt.subplots(1, len(tracks), figsize=(20, 40))

            for ind, track in enumerate(tracks):
                try:
                    datos = las[track]
                    profundidad = las.index  # Profundidad como índice

                    # Graficar el track seleccionado
                    axes[ind].plot(datos, profundidad)
                    axes[ind].invert_yaxis()  # Eje Y invertido
                    axes[ind].set_title(track)

                except KeyError:
                    st.error(f"No se encontró el track: {track}")

            axes[0].set_ylabel("Profundidad (m)", fontsize=14)
            fig.suptitle("Registros Petrofísicos", fontsize=16)
            fig.tight_layout()

            # Mostrar gráfico en Streamlit
            st.pyplot(fig)
        else:
            st.warning("Por favor, selecciona al menos un track para graficar.")

    except Exception as e:
        st.error(f"Error al procesar el archivo LAS: {e}")
else:
    st.info("Por favor, sube un archivo LAS para explorar los datos.")

# Generar archivo requirements.txt
with open('requirements.txt', 'w') as f:
    f.write("streamlit\n")
    f.write("pandas\n")
    f.write("plotly\n")
    f.write("Pillow\n")
    f.write("lasio\n")
    f.write("welly\n")
    f.write("numpy\n")
    f.write("matplotlib\n")
