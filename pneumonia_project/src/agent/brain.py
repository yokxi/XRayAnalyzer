# File: src/agent/brain.py

from langchain_groq import ChatGroq
from src.config import GROQ_API_KEY
from src.tools.vision import YoloTool
from src.tools.rag import RagTool

# Inizializzazione dei Tool (Singleton per efficienza)
# Se YoloTool fallisce (es. modello non trovato), gestiamo l'errore nel tool stesso
try:
    yolo_tool = YoloTool()
except Exception as e:
    print(f"⚠️ Errore caricamento YOLO: {e}")
    yolo_tool = None

rag_tool = RagTool()

class MedicalAgent:
    def __init__(self):
        # Usiamo Llama 3 70B (o 8B) via Groq: è velocissimo e gratis
        self.llm = ChatGroq(
            temperature=0, 
            groq_api_key=GROQ_API_KEY, 
            model_name="llama-3.3-70b-versatile" # Modello molto potente
        )

    def analyze_images(self, image_paths):
        """
        Ponte tra l'interfaccia e YOLO.
        """
        if yolo_tool:
            return yolo_tool.analyze(image_paths)
        else:
            return [{"diagnosis": "Errore: Modello YOLO non attivo.", "processed": image_paths[0]}]

    def chat(self, user_query, context_data=""):
        """
        Il cuore del ragionamento.
        user_query: La domanda dell'utente.
        context_data: Il risultato testuale dell'analisi di YOLO (se presente).
        """
        
        # 1. Recuperiamo informazioni dal RAG (Conoscenza)
        rag_context = rag_tool.search(user_query)
        
        # 2. Costruiamo il Prompt di Sistema Dinamico
        # Se c'è un'immagine analizzata, la includiamo. Altrimenti no.
        visual_context_str = context_data if context_data else "Nessuna immagine analizzata in questa richiesta."

        system_prompt = f"""
        Sei un Assistente Radiologo AI esperto e professionale.
        Il tuo compito è assistere l'utente nell'interpretazione di radiografie toraciche e fornire consulti basati su linee guida.

        --- DATI VISIVI (Analisi AI YOLO) ---
        {visual_context_str}

        --- DATI DI CONTESTO (Linee Guida RAG) ---
        {rag_context}

        --- ISTRUZIONI ---
        1. Se l'analisi visiva riporta 'Pneumonia', spiega dove si trova e consiglia i prossimi passi.
        2. Se l'analisi visiva è negativa (Nessuna polmonite), rassicura l'utente ma consiglia sempre il parere di un medico umano.
        3. Usa un tono professionale, empatico e chiaro.
        4. Rispondi in Italiano.
        """
        
        # 3. Invio a Groq
        # LangChain accetta tuple (ruolo, contenuto)
        messages = [
            ("system", system_prompt),
            ("human", user_query),
        ]
        
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            return f"⚠️ Errore di comunicazione con Groq: {str(e)}"