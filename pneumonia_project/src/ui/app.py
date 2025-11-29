import streamlit as st
import os
from src.agent.brain import MedicalAgent
from src.config import TEMP_DIR

st.set_page_config(page_title="AI Radiologist", layout="wide")

st.title("🩻 Assistente Radiologo AI")

# Inizializza Session State
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = MedicalAgent()
if "processed_images" not in st.session_state:
    st.session_state.processed_images = [] # Lista per tenere traccia delle img elaborate

# --- SIDEBAR: UPLOAD IMMAGINI ---
with st.sidebar:
    st.header("Caricamento Raggi X")
    uploaded_files = st.file_uploader(
        "Carica una o più radiografie", 
        accept_multiple_files=True, 
        type=['png', 'jpg', 'jpeg']
    )
    
    if uploaded_files and st.button("Analizza Immagini"):
        with st.spinner("YOLO11 sta analizzando i polmoni..."):
            current_paths = []
            
            # 1. Salva le immagini caricate in TEMP
            for uploaded_file in uploaded_files:
                file_path = os.path.join(TEMP_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                current_paths.append(file_path)
            
            # 2. Passa le immagini a YOLO (tramite l'agente o tool diretto)
            results = st.session_state.agent.analyze_images(current_paths)
            
            # 3. Salva i risultati nello stato per mostrarli in chat
            st.session_state.processed_images = results
            
            # 4. Aggiungi un messaggio di sistema alla chat
            summary_text = "\n".join([f"- {res['diagnosis']}" for res in results])
            st.session_state.messages.append({
                "role": "system_display", # Ruolo speciale per la UI
                "content": results # Salviamo l'intero oggetto risultati
            })
            
            # Triggera l'LLM per commentare subito
            ai_comment = st.session_state.agent.chat(
                user_query="Ho appena caricato queste immagini. Cosa vedi?",
                context_data=summary_text
            )
            st.session_state.messages.append({"role": "assistant", "content": ai_comment})

# --- CHAT PRINCIPALE ---
for message in st.session_state.messages:
    
    # GESTIONE SPECIALE PER LE IMMAGINI
    if message["role"] == "system_display":
        # Se il messaggio contiene immagini elaborate, mostrale in una griglia
        results = message["content"]
        cols = st.columns(len(results))
        for idx, res in enumerate(results):
            with cols[idx]:
                st.image(res["processed"], caption=f"YOLO: {res['diagnosis']}")
    
    # GESTIONE MESSAGGI TESTUALI
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- INPUT UTENTE ---
if prompt := st.chat_input("Fai una domanda medica..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Recupera il contesto delle ultime immagini analizzate (se ci sono)
        context = ""
        if st.session_state.processed_images:
            context = str([res['diagnosis'] for res in st.session_state.processed_images])
            
        response = st.session_state.agent.chat(prompt, context_data=context)
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})