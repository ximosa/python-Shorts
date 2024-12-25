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
   Actúa como un guionista experto en videos cortos para YouTube (Shorts). Tu objetivo es adaptar el siguiente texto para un video de 60 segundos, priorizando la máxima información posible en el menor tiempo. Sigue estas pautas estrictamente:

- **Máxima Concisión:** Reduce el texto a sus ideas más esenciales, eliminando cualquier detalle innecesario o redundante. El objetivo es transmitir la mayor información posible en el menor espacio.

- **Frases Muy Cortas y Directas:** Divide el texto en frases extremadamente cortas y directas, diseñadas para mostrarse en pantalla durante unos pocos segundos cada una. Cada frase debe ser autónoma y fácilmente comprensible.

- **Lenguaje Sencillo:** Utiliza un lenguaje muy simple, directo y fácil de entender. Evita cualquier tipo de frase compleja o palabras poco comunes.

- **Estructura de Narración:** Organiza el texto como si estuvieras contando una historia o presentando una idea de forma rápida y dinámica, pero manteniendo una estructura lógica.

- **Evita Nombres y Lugares Específicos:** Refiérete a personas y lugares como "una persona," "un lugar," etc., a menos que sea imprescindible mencionarlos para la comprensión.

- **Foco en el Mensaje Central:** Asegúrate de que el mensaje principal del texto original se transmita de forma eficaz, rápida y clara.

- **Optimización para Lectura de Voz:** Adapta el texto para que sea ideal para ser leído por un sintetizador de voz, evitando frases complejas o poco naturales.

- **Límites de Caracteres:**
  *   Cada frase individual debe tener un máximo de **300 caracteres**, incluyendo espacios.
  *   El resultado final, debe tener un máximo de **1200 caracteres** incluyendo espacios.

- **Formato:** Genera el texto sin negritas, asteriscos, encabezados o cualquier otro tipo de formato. Solo el texto plano.
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
