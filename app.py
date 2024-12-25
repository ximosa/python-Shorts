import streamlit as st
import google.generativeai as genai
import os
import textwrap

# Obtener la API Key de las variables de entorno
try:
    GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
    genai.configure(api_key=GOOGLE_API_KEY)
    MODEL = "gemini-pro"
except KeyError:
    st.error("La variable de entorno GOOGLE_API_KEY no está configurada.")
    st.stop()  # Detener la app si no hay API Key


def dividir_texto(texto, max_tokens=1500):
    """Divide el texto en fragmentos más pequeños."""
    tokens = texto.split()
    fragmentos = []
    fragmento_actual = []
    cuenta_tokens = 0

    for token in tokens:
        cuenta_tokens += 1
        if cuenta_tokens <= max_tokens:
            fragmento_actual.append(token)
        else:
            fragmentos.append(" ".join(fragmento_actual))
            fragmento_actual = [token]
            cuenta_tokens = 1
    if fragmento_actual:
        fragmentos.append(" ".join(fragmento_actual))
    return fragmentos


def limpiar_transcripcion_gemini(texto):
    """
    Limpia una transcripción usando Gemini para Shorts.

    Args:
        texto (str): La transcripción sin formato.

    Returns:
        str: La transcripción formateada y adaptada para un Short.
    """
    prompt = f"""
    Actúa como un guionista experto en videos cortos para YouTube (Shorts). Tu objetivo es adaptar el siguiente texto para un video de 60 segundos. Sigue estas pautas:

    - **Prioriza la concisión:** Reduce el texto a sus ideas más esenciales. Un Short debe ser directo y rápido.
    - **Adapta la estructura:** Divide el texto en frases cortas y directas, ideales para mostrar en pantalla con una lectura de voz. Cada frase debe ser comprensible por sí sola y durar unos segundos.
    - **Usa un lenguaje claro y directo:** Evita las frases largas y complejas, y prioriza palabras sencillas y fáciles de entender.
    - **Estructura tipo narración:** Escribe como si estuvieras narrando una historia o presentando una idea.
    - **Evita nombres y lugares específicos:** Refiérete a ellos como "una persona", "un lugar", "otro personaje", etc., a menos que sean esenciales para la comprensión del texto.
    - **Enfócate en el mensaje principal:** Asegúrate de que el mensaje central del texto original se transmita de manera efectiva en este formato conciso.
     - **Adapta el texto:** El texto tiene que ser adaptable para ser leido por un sintetizador de voz.
    - **Genera el texto sin negritas, asteriscos ni encabezados.
        {texto}

        Texto adaptado:
    """
    try:
        model = genai.GenerativeModel(MODEL)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error al procesar con Gemini: {e}")
        return None

def procesar_transcripcion(texto):
    """Procesa el texto dividiendo en fragmentos y usando Gemini."""
    fragmentos = dividir_texto(texto)
    texto_limpio_completo = ""
    for i, fragmento in enumerate(fragmentos):
        st.write(f"Procesando fragmento {i + 1}/{len(fragmentos)}")
        texto_limpio = limpiar_transcripcion_gemini(fragmento)
        if texto_limpio:
            texto_limpio_completo += texto_limpio + " "  # Agregar espacio para evitar que las frases se unan
    return texto_limpio_completo.strip()


def descargar_texto(texto_formateado):
    """
    Genera un enlace de descarga para el texto formateado.

    Args:
        texto_formateado (str): El texto formateado.

    Returns:
        streamlit.components.v1.html: Enlace de descarga.
    """
    return st.download_button(
        label="Descargar Texto",
        data=texto_formateado.encode('utf-8'),
        file_name="transcripcion_formateada.txt",
        mime="text/plain"
    )


st.title("Adaptador de Texto para Shorts con Gemini")

transcripcion = st.text_area("Pega aquí tu transcripción sin formato:")

if transcripcion:
    with st.spinner("Procesando con Gemini..."):
        texto_limpio = procesar_transcripcion(transcripcion)
        if texto_limpio:
            st.subheader("Texto Adaptado para Short:")
            st.write(texto_limpio)
            descargar_texto(texto_limpio)
