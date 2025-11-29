import os
import random

class MedicalAgent:
    def __init__(self):
        # Carica il file di testo al'avvio
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        self.kb_path = os.path.join(self.base_path, "knowledge_base", "info_mediche.txt")
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self):
        """Legge il file txt e lo divide in sezioni"""
        kb = {}
        try:
            with open(self.kb_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Parsing molto semplice basato sui titoli [TITOLO]
                sections = content.split("[")
                for sec in sections:
                    if "]" in sec:
                        title, body = sec.split("]", 1)
                        kb[title.strip()] = body.strip()
            return kb
        except Exception as e:
            print(f"⚠️ Errore caricamento KB: {e}")
            return {}

    def generate_report(self, num_boxes, max_score):
        """
        Questa funzione simula il ragionamento dell'Agente.
        Input: Dati dal tuo modello Faster R-CNN (Visione)
        Output: Report medico testuale (RAG)
        """
        
        # CASO 1: PAZIENTE SANO
        if num_boxes == 0:
            return {
                "titolo": "REFERTO RADIOLOGICO: NEGATIVO",
                "colore": "#10b981", # Verde
                "testo": self.knowledge.get("SANO", "Nessuna anomalia rilevata.")
            }

        # CASO 2: PAZIENTE MALATO (POLMONITE)
        # Recuperiamo le info mediche dalla memoria (RAG simulato)
        info_cliniche = self.knowledge.get("POLMONITE_BATTERICA", "Dati non disponibili.")
        
        # Costruiamo il report in modo dinamico
        livello_confidenza = "ALTA" if max_score > 0.8 else "MEDIA"
        
        testo_report = f"""
        RILEVAMENTI VISIVI (Faster R-CNN):
        • Identificate {num_boxes} aree di consolidamento parenchimale.
        • Confidenza del modello: {max_score:.1%} ({livello_confidenza}).
        
        NOTE CLINICHE E PROTOCOLLO (da Knowledge Base):
        {info_cliniche}
        
        RACCOMANDAZIONE AGENTE:
        Si consiglia correlazione clinico-strumentale urgente data la presenza di opacità.
        """

        return {
            "titolo": f"⚠️ RILEVATA POSSIBILE POLMONITE",
            "colore": "#ef4444", # Rosso
            "testo": testo_report
        }