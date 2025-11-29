# File: src/tools/rag.py

class RagTool:
    def __init__(self):
        # In futuro qui caricheremo FAISS o ChromaDB
        pass

    def search(self, query: str):
        """
        Funzione segnaposto per il RAG.
        Restituisce un testo generico finché non collegheremo i PDF reali.
        """
        # Simuliamo una risposta basata su linee guida generiche
        return (
            "NOTA DAL DATABASE MEDICO (RAG): "
            "Attualmente il database delle linee guida non è connesso. "
            "Rispondi basandoti sulla tua conoscenza medica generale e sull'analisi visiva fornita."
        )