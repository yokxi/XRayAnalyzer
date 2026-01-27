import os
import glob
import json
import hashlib
from typing import List
from src import config

from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter

class RagTool:
    def __init__(self):
        self.kb_path = config.KB_PATH
        self.db_path = config.VECTOR_DB_PATH
        self.status_file = os.path.join(self.db_path, "db_status.json")
        
        # 1. Inizializzazione Embeddings (Caricamento modello in memoria)
        print("[RAG] Inizializzazione FastEmbed (Multilingual-E5)...")
        self.embeddings = FastEmbedEmbeddings(model_name="intfloat/multilingual-e5-large")
        
        # 2. Connessione a ChromaDB
        self.vector_db = Chroma(
            persist_directory=self.db_path,
            embedding_function=self.embeddings,
            collection_name="medical_knowledge"
        )
        
        # 3. Controllo per Rebuild
        if self._should_rebuild():
            self._build_index()
        else:
            print(f"[RAG] Knowledge Base aggiornata. Caricate {len(self.vector_db.get()['ids'])} sezioni.")

    def _get_kb_fingerprint(self):
        """Crea un'impronta digitale della cartella MD (nomi file + date modifica)."""
        md_files = glob.glob(os.path.join(self.kb_path, "*.md"))
        fingerprint = {}
        for f in md_files:
            # Usiamo la data di ultima modifica e la dimensione del file
            stats = os.stat(f)
            fingerprint[os.path.basename(f)] = f"{stats.st_mtime}-{stats.st_size}"
        return fingerprint

    def _should_rebuild(self):
        """Verifica se il database deve essere ricostruito."""
        # Se la cartella del DB non esiste o è vuota
        if not os.path.exists(self.db_path) or len(self.vector_db.get()['ids']) == 0:
            return True
        
        # Se manca il file di stato
        if not os.path.exists(self.status_file):
            return True
            
        try:
            with open(self.status_file, 'r') as f:
                old_fingerprint = json.load(f)
            
            new_fingerprint = self._get_kb_fingerprint()
            
            # Confronto: se i file sono diversi o le date di modifica sono cambiate
            return old_fingerprint != new_fingerprint
        except:
            return True

    def _build_index(self):
        print(f"[RAG] Rebuild in corso: Indicizzazione Knowledge Base...")
        
        # Svuotiamo il database esistente per evitare duplicati
        ids = self.vector_db.get()['ids']
        if ids:
            self.vector_db.delete(ids)
            
        all_splits = []
        md_files = glob.glob(os.path.join(self.kb_path, "*.md"))
        
        # TODO RICONTROLLARE QUESTA LOGICA DATE LE MODIFICHE FATTE AI FILE .MD
        # Splitter ottimizzato per la nuova logica algoritmica
        headers_to_split_on = [
            ("#", "Category"),   # es. PROTOCOLLO ANALISI TECNICA
            ("##", "Topic"),     # es. FASE 1: IDENTIFICAZIONE
            ("###", "Action")    # es. Analisi Scapole
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
            except Exception as e:
                print(f"[RAG] Errore lettura {file_name}: {e}")

        if all_splits:
            self.vector_db.add_documents(all_splits)
            
            # Salviamo il nuovo stato
            fingerprint = self._get_kb_fingerprint()
            with open(self.status_file, 'w') as f:
                json.dump(fingerprint, f)
                
            print(f"[RAG] Indice ricostruito con successo ({len(all_splits)} sezioni).")

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