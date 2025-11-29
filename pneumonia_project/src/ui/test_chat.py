import streamlit as st
import os
from dotenv import load_dotenv

# Importiamo LangChain e Groq direttamente qui
# Se questo fallisce, significa che le librerie non sono installate
try:
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
except ImportError as e:
    st.error(f"Errore critico: Librerie mancanti! {e}")
    st.stop()

# 1. SETUP CONFIGURAZIONE
st.set_page_config(page_title="Test Chat Groq (No YOLO)", page_icon="🧪")

# Carica variabili d'ambiente
load_dotenv()

st.title("🧪 Test Isolato: Chat con Groq")
st.caption("Questo test verifica solo la connessione con l'LLM, ignorando YOLO e RAG.")

# 2. GESTIONE API KEY (Robusta)
# Cerca la chiave nell'ambiente, se non c'è chiede all'utente (utile per debug)
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.warning("⚠️ Chiave GROQ_API_KEY non trovata nel file .env o nelle variabili d'ambiente.")
    api_key = st.text_input("Inserisci qui la tua chiave Groq (gsk_...) per testare al volo:", type="password")

if not api_key:
    st.info("Inserisci una chiave per iniziare.")
    st.stop()

# 3. INIZIALIZZAZIONE LLM
# Definiamo la classe 'Agente' qui dentro per non dipendere da file esterni
class SimpleChatAgent:
    def __init__(self, key):
        self.llm = ChatGroq(
            temperature=0.5,
            groq_api_key=key,
            model_name="llama-3.3-70b-versatile" # Modello potente e veloce
        )
    
    def generate_response(self, chat_history):
        # Chiama Groq passando la storia dei messaggi
        return self.llm.invoke(chat_history)

# Inizializza l'agente nello stato
if "simple_agent" not in st.session_state:
    try:
        st.session_state.simple_agent = SimpleChatAgent(api_key)
        st.success("✅ Connessione a Groq inizializzata con successo!")
    except Exception as e:
        st.error(f"Errore inizializzazione Groq: {e}")

# 4. GESTIONE STORIA CHAT
if "messages" not in st.session_state:
    st.session_state.messages = [
        SystemMessage(content="Sei un assistente medico intelligente. Rispondi in modo professionale e conciso.")
    ]

# 5. INTERFACCIA CHAT
# Mostra i messaggi precedenti (escludendo il SystemMessage iniziale per pulizia visiva)
for msg in st.session_state.messages:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(msg.content)

# 6. INPUT UTENTE
if prompt := st.chat_input("Scrivi qualcosa per testare l'LLM..."):
    
    # Visualizza messaggio utente
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Aggiungi alla storia
    st.session_state.messages.append(HumanMessage(content=prompt))

    # Genera risposta
    with st.chat_message("assistant"):
        with st.spinner("Llama3 sta pensando..."):
            try:
                response = st.session_state.simple_agent.generate_response(st.session_state.messages)
                st.markdown(response.content)
                
                # Aggiungi risposta alla storia
                st.session_state.messages.append(response)
            except Exception as e:
                st.error(f"Errore durante la generazione: {e}")