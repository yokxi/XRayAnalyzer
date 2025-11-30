import os
import random
from rag_tool import RagTool  

class MedicalAgent:
    def __init__(self):
        self.rag = RagTool()

    def generate_report(self, num_boxes, max_score):
        
        if num_boxes == 0:
            return {
                "titolo": "REFERTO RADIOLOGICO: NEGATIVO",
                "colore": "#10b981", 
                "testo": "Nessuna anomalia rilevata. I polmoni appaiono liberi."
            }

        
        # Chiediamo i sintomi
        info_sintomi = self.rag.search("Quali sono i sintomi tipici della polmonite?")
        
        # Chiediamo la cura (specificando antibiotici)
        info_trattamento = self.rag.search("Qual è il protocollo terapeutico antibiotico consigliato?")
        
        # Chiediamo i rischi
        info_rischi = self.rag.search("Quali sono le complicazioni o i rischi se non curata?")
        
        livello_confidenza = "ALTA" if max_score > 0.8 else "MEDIA"
        
        testo_report = f"""
        RILEVAMENTI VISIVI (Faster R-CNN):
        • Identificate {num_boxes} aree di opacità polmonare.
        • Affidabilità diagnosi: {max_score:.1%} ({livello_confidenza}).
        
        QUADRO CLINICO (Ricerca Semantica):
        {info_sintomi}
        
        PROTOCOLLO SUGGERITO (RAG):
        {info_trattamento}
        
        ⚠️ RISCHI E COMPLICAZIONI:
        {info_rischi}
        
        RACCOMANDAZIONE AGENTE:
        Si consiglia valutazione pneumologica urgente.
        """

        return {
            "titolo": f"⚠️ RILEVATA POSSIBILE POLMONITE",
            "colore": "#ef4444", 
            "testo": testo_report
        }