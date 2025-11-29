import os
import random

class MedicalAgent:
    def __init__(self):
        # Percorso base dove si trova questo file
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        # Percorso della cartella contenente i file di testo
        self.kb_dir = os.path.join(self.base_path, "knowledge_base")
        # Caricamento della conoscenza
        self.knowledge = self._load_knowledge()

    def _load_knowledge(self):
        """Legge TUTTI i file .txt nella cartella knowledge_base"""
        kb = {}
        
        # 1. Controlla se la cartella esiste
        if not os.path.exists(self.kb_dir):
            print(f"⚠️ Cartella Knowledge Base non trovata: {self.kb_dir}")
            return {}

        print(f"📂 Scansione Knowledge Base in corso...")

        # 2. Ciclo su tutti i file della cartella
        for filename in os.listdir(self.kb_dir):
            if filename.endswith(".txt"):
                file_path = os.path.join(self.kb_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                        # 3. Parsing: Cerca i blocchi tra parentesi [TITOLO]
                        sections = content.split("[")
                        for sec in sections:
                            if "]" in sec:
                                title, body = sec.split("]", 1)
                                kb[title.strip()] = body.strip()
                                print(f"   📘 Caricato: [{title.strip()}] da {filename}")
                                
                except Exception as e:
                    print(f"❌ Errore lettura file {filename}: {e}")
        
        return kb

    def generate_report(self, num_boxes, max_score):
        """Genera un report ricco usando diverse fonti della Knowledge Base"""
        
        # CASO 1: PAZIENTE SANO
        if num_boxes == 0:
            return {
                "titolo": "REFERTO RADIOLOGICO: NEGATIVO",
                "colore": "#10b981", # Verde
                "testo": self.knowledge.get("SANO", "Nessuna anomalia rilevata.")
            }

        # CASO 2: PAZIENTE MALATO
        # Recuperiamo informazioni da DIVERSI file
        # Nota: Se vedi "N/D", controlla che i titoli nei file txt siano scritti esattamente così
        
        info_sintomi = self.knowledge.get("SINTOMI_COMUNI", "Dati non disponibili.")
        info_trattamento = self.knowledge.get("LINEE_GUIDA_AIFA", "Protocollo non trovato.")
        info_rischi = self.knowledge.get("COMPLICAZIONI_POLMONARI", "Nessun rischio specifico segnalato.")
        
        livello_confidenza = "ALTA" if max_score > 0.8 else "MEDIA"
        
        # Costruiamo il report completo
        testo_report = f"""
        RILEVAMENTI VISIVI (Faster R-CNN):
        • Identificate {num_boxes} aree di opacità polmonare.
        • Affidabilità diagnosi: {max_score:.1%} ({livello_confidenza}).
        
        QUADRO CLINICO ATTESO (Fonte: Knowledge Base):
        {info_sintomi}
        
        PROTOCOLLO TERAPEUTICO UFFICIALE (Fonte: AIFA):
        {info_trattamento}
        
        ⚠️ NOTE SU PROGNOSI E RISCHI:
        {info_rischi}
        
        RACCOMANDAZIONE AGENTE:
        Si consiglia valutazione pneumologica urgente.
        """

        return {
            "titolo": f"⚠️ RILEVATA POSSIBILE POLMONITE",
            "colore": "#ef4444", # Rosso
            "testo": testo_report
        }