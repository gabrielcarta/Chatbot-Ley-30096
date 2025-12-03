import streamlit as st
import os
import tempfile
from rag import configurar_qa_chain, aprender_pdf

st.set_page_config(page_title="Experto en Delitos Informáticos", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Asistente Legal: Ley N° 30096")
st.markdown("Soy especialista en la Ley de Delitos Informáticos del Perú. **Ya conozco la ley.** Pregúntame lo que quieras.")

# --- BARRA LATERAL (Para añadir más conocimiento) ---
with st.sidebar:
    st.header("🧠 Ampliar Conocimiento")
    st.info("Si la respuesta no está en la ley base, sube un documento extra (reglamentos, casos, etc.) y lo aprenderé.")
    archivo_nuevo = st.file_uploader("Subir PDF Extra", type="pdf")
    
    if archivo_nuevo:
        with st.spinner("Aprendiendo documento nuevo..."):
            # Guardar temporalmente
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(archivo_nuevo.getvalue())
                ruta = tmp.name
            
            # Llamamos a la función de aprender
            aprender_pdf(ruta)
            st.success("¡Información guardada en memoria permanente!")
            os.remove(ruta)

# --- INICIAR EL CEREBRO AL ARRANCAR ---
if "qa_chain" not in st.session_state:
    with st.spinner("Cargando memoria legal..."):
        st.session_state.qa_chain = configurar_qa_chain()

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []

# --- CHAT ---
for msj in st.session_state.mensajes:
    with st.chat_message(msj["rol"]):
        st.markdown(msj["contenido"])

prompt = st.chat_input("Ej: ¿Cuál es la pena por hackear un correo?")

if prompt:
    st.session_state.mensajes.append({"rol": "user", "contenido": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Consultando la Ley 30096 y base de datos..."):
            respuesta = st.session_state.qa_chain.invoke({"query": prompt})
            texto = respuesta["result"]
            
            # (Opcional) Mostrar qué artículos usó
            fuentes = set()
            for doc in respuesta["source_documents"]:
                # Intentamos sacar la página o el nombre del archivo
                pagina = doc.metadata.get("page", "?")
                fuente = doc.metadata.get("source", "desconocido")
                fuentes.add(f"{os.path.basename(fuente)} (pág {pagina})")
            
            st.markdown(texto)
            st.caption(f"📚 Fuentes consultadas: {', '.join(fuentes)}")
            
    st.session_state.mensajes.append({"rol": "assistant", "contenido": texto})