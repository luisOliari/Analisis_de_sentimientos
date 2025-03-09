import streamlit as st
# Librería para acceder a Google Gemini
import google.generativeai as genai # pip install -q -U google-generativeai
import pandas as pd
import json
import os  # Agrega esta línea
# from dotenv import load_dotenv  # Agrega esta línea
import plotly.express as px
import time  # <-- Añade al inicio del código


# Cargar las variables de entorno desde el archivo .env
# load_dotenv()

st.set_page_config(
    page_title="Análisis de Sentimiento con Google Gemini",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def darColorResultado(x):
    style_rojo = "background-color: #F7A4A4;font-weight: bold;"
    style_naranja = "background-color: #FEBE8C; font-weight: bold;"
    style_verde = "background-color: #B6E2A1; font-weight: bold;"
    if x=="POSITIVO":
        resultado= style_verde
    elif x=="NEUTRAL":
        resultado= style_naranja
    elif x=="NEGATIVO":
        resultado= style_rojo

    return resultado


#Prompt del sistema
systemPrompt=""" Eres un analizador de sentimientos. El usuario te dará comentarios.
**Instrucciones estrictas:**
1. Analiza cada comentario.
2. Clasifícalo como POSITIVO, NEUTRAL o NEGATIVO.
3. Devuelve SOLO un JSON válido (sin texto adicional) con este formato:
[
    {"comentario": "texto 1", "sentimiento": "POSITIVO"},
    {"comentario": "texto 2", "sentimiento": "NEGATIVO"}
] """

# Cargamos la API Key de secrets.toml
# GOOGLE_API_KEY="_API_KEY_COPIADA_DE_GOOGLE_AI_STUDIO"
# La API se obtiene de https://aistudio.google.com/
# genai.configure(api_key = st.secrets["GOOGLE_API_KEY"])

# Configurar la API key
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("No se encontró la API key en las variables de entorno")

genai.configure(api_key=api_key)

# Cargamos el modelo con el prompt del sistema
model = genai.GenerativeModel('gemini-1.5-pro-latest',system_instruction=systemPrompt)

st.header('Analizador de sentimientos con :blue[Google Gemini]')
c1,c2=st.columns(2)
with c1:
    txtComentarios = st.text_area("Comentarios para revisar",height=600)
    btnConsultar = st.button("Consultar",type='primary')
with c2:    

    if btnConsultar:
        prompt=[
            {
            "role": "user",
            "parts": [
                txtComentarios,
            ],
            }]
        with st.spinner("Procesando..."): #Usamos el spinner para mostrar que el proceso está corriendo
            try:
            # Enviamos el prompt
                response = model.generate_content(prompt)
                time.sleep(2)  # <-- Espera 2 segundos entre consultas
            # Cargamos el resultado como JSON
                respuesta_limpia = response.text.replace('```json', '').replace('```', '').strip()
                resultado = json.loads(respuesta_limpia)
            # Convertimos el resultado en dataframe
                dfElementos = pd.DataFrame(resultado)  
            # Calculamos las métricas
                negativos = len(dfElementos[dfElementos["sentimiento"]=="NEGATIVO"])
                neutrales = len(dfElementos[dfElementos["sentimiento"]=="NEUTRAL"])
                positivos = len(dfElementos[dfElementos["sentimiento"]=="POSITIVO"])
            
            # Mostrar métricas
                c1,c2,c3 =  st.columns(3)
                with c1:
                    st.metric("😊 Positivos",positivos)
                with c2:
                    st.metric("😐 Neutrales",neutrales)
                with c3:
                    st.metric("😠 Negativos",negativos)

            # Crear gráficos
                st.subheader("Visualización de Resultados")
                
                # Gráfico de barras
                fig_bar = px.bar(
                    pd.DataFrame({
                        'Sentimiento': ['POSITIVO', 'NEUTRAL', 'NEGATIVO'],
                        'Cantidad': [positivos, neutrales, negativos]
                    }),
                    x='Sentimiento',
                    y='Cantidad',
                    color='Sentimiento',
                    color_discrete_map={
                        'POSITIVO': '#B6E2A1',
                        'NEUTRAL': '#FEBE8C',
                        'NEGATIVO': '#F7A4A4'
                    },
                    height=400,
                    title='Distribución de Sentimientos'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
                # Gráfico circular
                fig_pie = px.pie(
                    pd.DataFrame({
                        'Sentimiento': ['POSITIVO', 'NEUTRAL', 'NEGATIVO'],
                        'Cantidad': [positivos, neutrales, negativos]
                    }),
                    names='Sentimiento',
                    values='Cantidad',
                    color='Sentimiento',
                    color_discrete_map={
                        'POSITIVO': '#B6E2A1',
                        'NEUTRAL': '#FEBE8C',
                        'NEGATIVO': '#F7A4A4'
                    },
                    hole=0.3,
                    title='Proporción de Sentimientos'
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            # tabs:
                tabTabla,tabJson = st.tabs(["Resultados","Json"]) 
                with tabTabla:
                    st.dataframe(dfElementos.style.applymap(darColorResultado,subset="sentimiento"),use_container_width=True)        
                with tabJson:
                    st.json(response.text)

            except json.JSONDecodeError as e:
                st.error(f"Error al decodificar la respuesta JSON: {str(e)}")
                st.write("Respuesta cruda:", response.text)
            except Exception as e:
                st.error(f"Error inesperado: {str(e)}")
