import streamlit as st
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
CARPETA_BASE_DATOS = "./cerebro_legal"

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def obtener_cerebro():
    vectorstore = Chroma(
        persist_directory=CARPETA_BASE_DATOS, 
        embedding_function=embeddings
    )
    return vectorstore

def asegurar_conocimiento_base():
    vectorstore = obtener_cerebro()
    if len(vectorstore.get()['ids']) == 0:
        if os.path.exists("ley_base.pdf"):
            print("🧠 Aprendiendo Ley Base...")
            aprender_pdf("ley_base.pdf")
            print("✅ ¡Ley aprendida!")
        else:
            print("⚠️ No encontré 'ley_base.pdf'.")

def aprender_pdf(ruta_pdf):
    loader = PyPDFLoader(ruta_pdf)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_documents(docs)
    vectorstore = obtener_cerebro()
    vectorstore.add_documents(documents=splits)
    return True

def configurar_qa_chain():
    asegurar_conocimiento_base()
    vectorstore = obtener_cerebro()

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.3,
        google_api_key=GOOGLE_API_KEY
    )

    template = """Eres un experto abogado peruano especializado en Delitos Informáticos.
    Usa los siguientes fragmentos de contexto recuperados de la Ley N° 30096 para responder la pregunta del usuario al final.
    
    Reglas:
    1. Responde SIEMPRE en español.
    2. Si la respuesta no está en el contexto, di "No encuentro esa información específica en los documentos que tengo".
    3. Cita el número de artículo si es posible.
    4. Sé claro y profesional.

    Contexto:
    {context}

    Pregunta: {question}
    Respuesta útil:"""
    
    QA_CHAIN_PROMPT = PromptTemplate(
        input_variables=["context", "question"],
        template=template,
    )
    # -----------------------------------------------
    
    qa_chain = RetrievalQA.from_chain_type(
        llm, 
        retriever=vectorstore.as_retriever(search_kwargs={"k": 7}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": QA_CHAIN_PROMPT}
    )
    return qa_chain