from typing import List
import os
import glob

from src import config

from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

class RagTool:
    def __init__(self):
        self.kb_path = config.KB_PATH
        self.db_path = config.VECTOR_DB_PATH
        
        print(f"[RAG] DB Path: {self.db_path}")
        
        # 1. Embeddings Multilingua
        print("[RAG] Inizializzazione FastEmbed (Multilingual-E5)...")
        self.embeddings = FastEmbedEmbeddings(model_name="intfloat/multilingual-e5-large")
        
        # 2. LA MEMORIA (ChromaDB)
        self.vector_db = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embeddings,
            collection_name="medical_knowledge"
        )
        
        # Controllo se il database è vuoto o se la cartella DB non esiste
        if not os.path.exists(self.db_path) or len(self.vector_db.get()['ids']) == 0:
            self._build_index()
        else:
            print(f"[RAG] Database caricato con {len(self.vector_db.get()['ids'])} documenti.")

    def _build_index(self):
        print(f"[RAG] Indicizzazione Knowledge Base da: {self.kb_path}")
        all_splits = []
        md_files = glob.glob(os.path.join(self.kb_path, "*.md"))
        
        if not md_files:
            print(f"[RAG] ATTENZIONE: Nessun file .md trovato in {self.kb_path}")
            return

        # TODO RICONTROLLARE QUESTA LOGICA DATE LE MODIFICHE FATTE AI FILE .MD
        # Splitter basato sulla struttura del referto medico
        headers_to_split_on = [
            ("#", "Category"), 
            ("##", "Topic"), 
            ("###", "Action")
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)

        for file_path in md_files:
            file_name = os.path.basename(file_path)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    splits = markdown_splitter.split_text(text)
                    
                    for split in splits:
                        split.metadata["source"] = file_name
                    
                    all_splits.extend(splits)
                    print(f"[RAG] Elaborato: {file_name} ({len(splits)} sezioni)")
            except Exception as e:
                print(f"[RAG] Errore nella lettura di {file_name}: {e}")

        if all_splits:
            self.vector_db.add_documents(all_splits)
            print(f"[RAG] Indice creato con successo. Totale sezioni: {len(all_splits)}")

    def search(self, query: str, k: int = 4):
        """
        Cerca le informazioni più rilevanti basandosi sulla query.
        Usa MMR (Max Marginal Relevance) per evitare risultati ripetitivi.
        """
        print(f"[RAG] Ricerca in corso per: '{query}'")
        
        # MMR aiuta a prendere pezzi di testo diversi tra loro (es: un po' di Fleischner e un po' di Tecnica)
        docs = self.vector_db.max_marginal_relevance_search(query, k=k, fetch_k=10)
        
        context_text = ""
        for doc in docs:
            source = doc.metadata.get("source", "Protocollo")
            context_text += f"\n--- PROTOCOLLO DA: {source} ---\n{doc.page_content}\n"
            
        if not context_text:
            return "Nessuna linea guida specifica trovata per questa ricerca."
            
        return context_text