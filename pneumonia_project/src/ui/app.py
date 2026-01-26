import streamlit as st
import os
from PIL import Image
from src.agent.brain import MedicalAgent

st.set_page_config(page_title="AI Radiologist Chat", layout="wide")

# Caching dell'agente (carica i modelli una volta sola)
@st.cache_resource
def load_medical_agent():
    return MedicalAgent()

agent = load_medical_agent()

st.title("🩻 Assistente Radiologo AI Multimodale")
st.sidebar.header("Dettagli Clinici (Opzionali)")
user_pos = st.sidebar.selectbox("Proiezione:", ["Nessuna", "AP (Supino/Letto)", "PA (Standard/Eretto)"])

uploaded_file = st.file_uploader("Carica Radiografia Torace (CXR)", type=['png', 'jpg', 'jpeg'])

if uploaded_file:
    # Salvataggio temporaneo
    temp_path = f"/app/temp/{uploaded_file.name}"
    os.makedirs("/app/temp", exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(uploaded_file, caption="Immagine Originale", use_container_width=True)

    # --- PIPELINE XAI VISIBILE ---
    with st.status("🔍 Avvio Pipeline Diagnostica...", expanded=True) as status:
        st.write("1. ⚙️ Pre-processing CLAHE...")
        
        # Esecuzione pipeline tramite il Brain
        metadata = user_pos if user_pos != "Nessuna" else None
        reasoning, processed_img, detections, cls_data = agent.run_full_pipeline(
            temp_path, "Analisi Radiografica Completa", metadata
        )
        
        st.write(f"2. 🔬 Swin-B: {'POSITIVO' if cls_data['is_positive'] else 'NEGATIVO'} (Conf: {cls_data['confidence']:.2f})")
        st.write(f"3. 🎯 YOLO11: Trovati {len(detections)} box sospetti.")
        st.write("4. 🧠 Ragionamento HPC (Qwen-72B) e Protocolli RAG...")
        
        status.update(label="✅ Analisi Completata", state="complete", expanded=False)

    with col2:
        st.image(processed_img, caption="Analisi Visione (Stage 1 & 2)", use_container_width=True)

    st.subheader("📝 Ragionamento Clinico dell'Agente (Explainable AI)")
    st.info(reasoning)