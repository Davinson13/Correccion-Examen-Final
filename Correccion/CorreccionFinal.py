import os
import streamlit as st
import pandas as pd
import plotly.express as px
from groq import Groq
from dotenv import load_dotenv
import time

load_dotenv()

# Configuración del cliente de Groq
qclient = Groq()


def analyze_voting_intention(text):
    """Analiza el texto para determinar la intención de voto"""
    text = str(text).lower()
    if 'noboa' in text:
        return 'Voto Noboa'
    elif 'luisa' in text:
        return 'Voto Luisa'
    else:
        return 'Voto Nulo'


def main():
    # Pantalla de bienvenida con los colores de la bandera de Ecuador
    st.markdown("""
    <style>
    .welcome-container {
        background: linear-gradient(90deg, #FFEC00, #0061C2, #E60012); /* Colores de la bandera de Ecuador */
        color: white;
        padding: 20px;
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        border-radius: 10px;
    }
    .title-container {
        text-align: center;
        padding: 50px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="welcome-container">Predicción Electoral 2025</div>', unsafe_allow_html=True)

    # Agregar un pequeño delay para la pantalla de bienvenida
    time.sleep(2)

    # Título de la aplicación
    st.title("🗳 Predicción Electoral")
    st.markdown("### Sistema de Análisis de Intención de Voto")

    # Requisito 1: Recibir input de xlsx
    uploaded_file = st.file_uploader('Cargar archivo de datos (XLSX)', type="xlsx")

    if uploaded_file:
        # Cargar el DataFrame y asegurarse de que existe la columna 'text'
        df = pd.read_excel(uploaded_file)
        if 'text' not in df.columns:
            st.error("El archivo debe contener una columna llamada 'text' con las respuestas de los votantes")
            return

        # Requisito 2: Muestra aleatoria
        sample_size = st.slider("Seleccionar tamaño de muestra",
                                min_value=1,
                                max_value=len(df),
                                value=min(10, len(df)))

        sample_df = df.sample(n=sample_size)

        # Mostrar muestra de textos originales
        st.write("Muestra de respuestas:", sample_df[['text']])

        # Requisito 4: Etiquetar votos basado en el texto
        df['intencion_voto'] = df['text'].apply(analyze_voting_intention)

        # Requisito 8: Gráfico de barras y pastel de intención de voto
        vote_counts = df['intencion_voto'].value_counts()

        # Gráfico de barras
        bar_fig = px.bar(
            x=vote_counts.index,
            y=vote_counts.values,
            title="Distribución de Intención de Voto (Barras)",
            labels={'x': 'Candidato', 'y': 'Cantidad de Menciones'},
            color=vote_counts.index,
            color_discrete_map={
                'Voto Noboa': '#FFEC00',
                'Voto Luisa': '#0061C2',
                'Voto Nulo': '#E60012'
            }
        )
        st.plotly_chart(bar_fig)

        # Gráfico de pastel
        pie_fig = px.pie(
            names=vote_counts.index,
            values=vote_counts.values,
            title="Distribución de Intención de Voto (Pastel)",
            color=vote_counts.index,
            color_discrete_map={
                'Voto Noboa': '#FFEC00',
                'Voto Luisa': '#0061C2',
                'Voto Nulo': '#E60012'
            }
        )
        st.plotly_chart(pie_fig)

        # Requisito 9: Análisis de votos nulos
        votos_nulos = vote_counts.get('Voto Nulo', 0)
        total_votos = len(df)
        porcentaje_nulos = (votos_nulos / total_votos) * 100

        st.markdown("### Análisis de Resultados")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total de respuestas", total_votos)
        with col2:
            st.metric("Votos nulos", votos_nulos)
        with col3:
            st.metric("Porcentaje nulos", f"{porcentaje_nulos:.1f}%")

        # Mostrar conclusión
        st.markdown("### Conclusión")
        ganador = vote_counts.index[0] if not vote_counts.empty else "No hay datos suficientes"
        st.write(f"Según el análisis de las respuestas:")
        st.write(f"- Candidato con más menciones: {ganador}")
        st.write(f"- Porcentaje de respuestas no clasificables: {porcentaje_nulos:.1f}%")

        # Requisito 10: Preguntas al bot
        st.markdown("### Consultas sobre los datos")
        user_question = st.text_input("Realiza una pregunta sobre los resultados:")

        if user_question:
            with st.spinner("Analizando..."):
                # Preparar un resumen de los datos para el contexto
                data_summary = f"""
                Total de respuestas analizadas: {total_votos}
                Distribución de votos:
                {vote_counts.to_string()}
                Porcentaje de votos nulos: {porcentaje_nulos:.1f}%
                """

                response = qclient.chat.completions.create(
                    messages=[{
                        "role": "system",
                        "content": "Eres un analista electoral. Responde preguntas sobre los resultados de la predicción electoral basándote en los datos proporcionados."
                    }, {
                        "role": "user",
                        "content": f"Datos del análisis:\n{data_summary}\n\nPregunta: {user_question}"
                    }],
                    model="llama3-8B-8192",
                    stream=False
                )
                st.write("Respuesta:", response.choices[0].message.content)


if __name__ == "__main__":
    main()
